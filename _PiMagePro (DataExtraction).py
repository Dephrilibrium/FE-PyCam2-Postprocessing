##################################################################################
# Data Extractor for 16bit grayscale PNGs made with PyCam2-Server.               #
#                                                                                #
# How to use (variable explanation):                                             #
# xCmd:             Path to the 7-zip executable.                                #
# parentDir:        Folder which is scanned recursevly for measurement-files.    #
# picDir:           Foldername of the subdir where the images for the data-      #
#                    extraction are stored (mean-images of                       #
#                    _ConvertBayerToGrayScale.py)                                #
# saveDir:          The second argument of the replace-function determines the   #
#                    folder in which the extraction results are stored.          #
#                    This can be used to separate source and destination folder. #
# opt:              Is an instance of the PiMagePro options. This class has a    #
#                    built in store-function to have the used extraction-option  #
#                    as file on disk (see options below).                        #
# LogFilePath:      If a filename is given, a logger-instance is created which   #
#                    print the console messages to console as wall as to a file. #
# LogLen:           Defines the length of a log-line (so that all logs have the  #
#                    same length).                                               #
#                                                                                #
# 2023 © haum (OTH-Regensburg)                                                   #
##################################################################################



from genericpath import exists
import os
import sys
import shutil
from threading import local
import time
import numpy as np
import pickle
import matplotlib.pyplot as plt

from FieldEmission import ReadSweepFile
from FieldEmission import DataProvider

import cv2 as cv

from misc import bcolors
from misc import DiffTime
from misc import DiffToNow
from misc import Time2Human
from misc import Logger
from misc import LogLine
from misc import LogLineOK

from PMPLib.ImgFileHandling import BlackFormat, ImageFormat, LoadFileTypes, SaveFileType, SS_Index
from PMPLib.ImgFileHandling import GrabSSFromFilenames
from PMPLib.ImgFileHandling import ReadImages
from PMPLib.ImgFileHandling import SaveImageCollection

from PMPLib.ImgManipulation import MeanImages
from PMPLib.ImgManipulation import SubtractFromImgCollection
from PMPLib.ImgManipulation import ConvertBitsPerPixel
from PMPLib.ImgManipulation import BuildThreshold
from PMPLib.ImgManipulation import DrawCircleAroundEachSpot
from PMPLib.ImgManipulation import DrawCircleAroundEachXYKey

from PMPLib.CircleDetectAndXYSort import DetectSpots
from PMPLib.CircleDetectAndXYSort import CollectCirclesAsXYKeys
from PMPLib.CircleDetectAndXYSort import CorrectXYSortKeys
from PMPLib.CircleDetectAndXYSort import CrossCheckXYKeys
from PMPLib.CircleDetectAndXYSort import SortXYFromLUtoRL

# from PMPLib.DataProcessing import DataExtractionAndUpscaling
from PMPLib.DataProcessing import SubareaImagesAndSensorsignalInfo
from PMPLib.DataProcessing import PixelcountAndOverexposureInfo
from PMPLib.DataProcessing import MergeSensorsignalVectors


from PMPLib.PiMageOptions import PiMageOptions








###### USER AREA ######
# Paths
parentDir = r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList"
# parentDir = r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_185401 1000V IMax1V - 15m (fully sat.)"
# parentDir = r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\99_01 TestPoints"

picDir = "Pics"

saveDir = str.replace(parentDir, "Messungen", "Auswertung")
if not os.path.exists(saveDir):
  os.makedirs(saveDir)


### Options/Parameters ###
opt = PiMageOptions()

# LogFile
LogFilePath = os.path.join(saveDir, "PiMage.log")
_logger = Logger(LogFilePath) # Keep instance for closing logger
LogLen = 80


# PiMage-sequence
opt.PiMage_SkipBadSubdirs = True                                        # If a parent folder is marked as bad (postfix: _XX) measurement, the subdirectories also skipped!y
opt.PiMage_ForceOverride = True                                         # False = Checks for already processed and skips in case; True = Won't check if a measurement is already processed!


# Visualization
opt.ShowImages_Read = False                                             # True = show each image (during debugging); False = Silent process
opt.ShowImages_Mean = False                                             # True = show each image (during debugging); False = Silent process
opt.ShowImages_SpotDetection = False                                    # True = show each image (during debugging); False = Silent process
opt.ShowImages_Draw = False                                             # True = show each image (during debugging); False = Silent process


# SS Autodetection
opt.DetectSS_AllowedPercentDeviation = 2.5                              # Is the detected SS within the range of an already known SS its counted as the same SS (untested, as AGC not working correctly for electron signals)


# Image processing
opt.Image_CropWin = None                                                # None/False: Images not cropped; [x, y, w, h]   -   x, y: left upper corner   -   w, h: size of window
opt.Image_bThresh = 35*255                                              # 16bit brightness Threshold value. It's only used, when the threshold of autodetect-algorithm (Image_ThreshType) is smaller than this one!
opt.Image_ThreshType = cv.THRESH_OTSU                                   # cv.THRESH_OTSU:                     Tries otsu
                                                                        # cv.ADAPTIVE_THRESH_GAUSSIAN_C:      Adaptive won't work with 16bit
                                                                        # cv.ADAPTIVE_THRESH_MEAN_C:          Adaptive won't work with 16bit
                                                                        # Other else:                         Uses fixed bThres-Value
opt.Image_AutoThresDiv = 8                                              # When ThrehType is used for auto-thresh, the returend threshold is divided by AutoThreshDiv and used to build the actual threshold (used for fine-tuning of threshhold)
opt.Image_UseForMeanNPoints = ".swp"                                    # <int>: Means together n measurement-points; ".swp": Tryies to find a sweep-file where it can extract the number of n measurement points
opt.Image_MeanNPicsPerSS = 1                                            # Means n pics (in row) together
opt.Image_OverexposedBrightness = 0xFFF0                                # Defines at which 16bit value a pixel counts as overexposed
opt.Image_MinBright2CountArea = 3* 0xFF                                 # Defines at which 16bit value a pixel counts as brightness-contributing pixel


# Spot-detection
opt.SpotDetect_Dilate = 10                                               # Detected image-contours (on thresh-images) are extended by n pixel-rows (entire circumfence) to close small gaps between a splitted spot
opt.SpotDetect_Erode = opt.SpotDetect_Dilate                            # The dilated image-contours are reduced by n pixel-rows (entire circumfence) (if erode=dilate the resulting spot should be the same as initially but whitout missing pixels within)
opt.SpotDetect_pxMinRadius = 4                                          # Minimum radius for a valid spot: pxMinRadius <= r <= pxMaxRadius; Used to avoid artifacts detected as spots
opt.SpotDetect_pxMaxRadius = 50                                         # Maximum radius for a valid spot: pxMinRadius <= r <= pxMaxRadius; Used to avoid the detection of spots bigger than being estimated


# Spot-Draw on Images
opt.CircleDraw_pxRadius = opt.SpotDetect_pxMaxRadius                    # Draws a circle using pxRadius to visualize the detected spots on the "circle-draw-images"
opt.CircleDraw_AddPxRadius = False                                      # When enabled, the circles detected spot-radius is added to pxRadius


# SensorSignal-Extraction
# opt.bDetect_SpotBrightFromAllImgs = True                              # When enabled, the brightness is extracted from ALL images based on the xy-key position! (NOTE: This ensures, that all vectors have the same)
# opt.bDetect_pxSideLen = 2 * opt.SpotDetect_pxMaxRadius                # Sidelength of a square around the circle center from which the circle-brightness is extracted
# opt.bDetect_AddPxSideLen = False                                      # When enabled, the circles radius is added to bDetect_pxSideLen
opt.SesExtraction_pxSideLen = 2 * opt.SpotDetect_pxMaxRadius            # Sidelength of a square around the circle center from which the circle-brightness is extracted
opt.SesExtraction_AddPxSideLen = False                                  # When enabled, the circles radius is added to bDetect_pxSideLen


# XY-Keys: Detected spots are collected as a XYKey-pair (x,y) when being near together (see tolerances of SEnsorSignal Extraction above)
opt.XYKeys_pxCollectRadius = opt.SpotDetect_pxMaxRadius                 # Valid radius around a xy-coordinate a detected image-spot is collected under, when located within this area.
opt.XYKeys_AddPxCollectRadius = False                                   # When enabled, the image-spots radius is added to SpotDetect_pxMaxRadius
opt.XYKeys_FollowSpots = True                                           # When enabled, the xy-key follows the related circle-centers by meaning them
opt.XYKeys_pxCorrectionRadius = opt.XYKeys_pxCollectRadius              # For each SS a set of XY-Key-Pairs can be found. To assign them together, this radius is used as a tolerance and is then re-attached to ssData.
opt.XYKeys_CrossCheckKeys = True                                        # This option defines if the XYKeys are iterated again and combined if they are in range of each other (range = opt.XYKeys_pxCorrectionRadius)


# XY-Key Sorting
opt.XYKeySort_Rowdistance = opt.SpotDetect_pxMaxRadius                # Each leftmost spot of a row does a horizontal raycast to the right. XYKeySort_Rowdistance (in [px]) defines the vertical distance to that ray, in which a spot needs to be located to count as part of the row.


# Dump, Save & Datacopy
opt.PngDump_16bitGrayScale                          = True              # Dump imagecollection of the raw 16-bit images as PNGs                                                   (highest SS only)
opt.PngDump_8bitThreshhold                          = False             # Dump imagecollection of the raw threshhold images as PNGs                                               (highest SS only)
opt.PngDump_8bitCircleDetect                        = True              # Dump imagecollection of the dilated and eroded threshhold images, used for the circle-detection as PNGs (highest SS only)
opt.PngDump_8bitCircleDrawAroundEachDetection       = True              # Dump imagecollection of the 8-bit images with a cirlce drawn around each detected spot as PNGs          (highest SS only)
opt.PngDump_8bitXYKeyDrawAroundEachXYKey            = True              # Dump imagecollection of the 8-bit images with cirlces drawn around each XYKey as PNGs                   (highest SS only)

opt.PklDump_imgContainer                            = False             # Dump the entire image-container as pickle-binary (all images incl. subarea-images -> HUGE filesize)
opt.PklDump_cirContainer                            = False             # Dump the circle-container as pickle-binary (all circle data)
opt.PklDump_pcoContainer                            = True              # Dump the PixelCount- and Overexposureinfo-container as pickle-binary
opt.PklDump_sesContainer                            = True              # Dump the SEnsorSignal-container as pickle-binary
opt.PklDump_mssContainer                            = True              # Dump the MergedSensorSignal-container as pickle-binary (combination of the sensor signals on the different SS-images)

opt.Copy_FEMDAQData                                 = True                      # Creates copies of the relevant FEMDAQ-data (if FEMDAQ was used as measurement-tool!)





# # # opt.SaveSSImagePkl                          = False                     # Save internal raw ssData structure
# # # opt.Save_ImgSets4Brightness                 = False                     # Save "Imageset"                                             for Brightnesses and it's correction as pickle
# # # opt.Save_BrightSets4Brightness              = True                      # Save "Brightnesses"                                         from Imageset as pickle
# # # opt.Save_PxAreaCnts4Brightness              = True                      # Save "PixelArea-Counts & -Factors"                          from Imageset as pickle
# # # opt.Save_DivFactors4Brightness              = True                      # Save "Division-Correction-Factors"                          from BrightSets as pickle
# # # opt.Save_ScaledAnyPxImgs                    = False                     # Save "Any upscaled pixelcorrected images"                   as pickle (huge!)
# # # opt.Save_ScaledAnyBrightnesses              = True                      # Save "Any upscaled spotbrightness"                          as pickle
# # # opt.Save_ScaledWhereOverexposedPxImgs       = False                     # Save "Any upscaled spotbrightness images"                   as pickle
# # # opt.Save_ScaledWhereOverexposedBrightnesses = True                      # Save "Upscaled spotbrightness where overexposure occured"   as pickle
# # # opt.Save_FEMDAQCopies                       = True                      # Creates copies of the relevant FEMDAQ-data (if FEMDAQ was used as measurement-tool!)








###### DO NOT TOUCH AREA ######
# Iterate through entire measurement-folder
t0 = time.time()
LogLine(t0, "Starting", bcolors.BOLD + "----- PiMagePro -----" + bcolors.ENDC, yFill=15, wFill=0, end="\n")
LogLine(t0, "Toolname:", "Raspberry " + bcolors.OKBLUE + "Pi" + bcolors.ENDC + "-i" + bcolors.OKBLUE + "Mage Pro"+ bcolors.ENDC + "cessor", yFill=15, wFill=30, end="\n")
LogLine(t0, "Programmer:", "haum", yFill=15, wFill=30, end="\n")
LogLine(t0, "Affiliation:", "OTH-Regensburg", yFill=15, wFill=30, end="\n")
LogLine(t0, "Year:", "2022", yFill=15, wFill=30, end="\n")

if "_logger" in locals():
  print("\n\n")
  LogLine(t0, "Logger active - writing to: ", LogFilePath, wFill=0, end="\n")

_XXBadDirs = list()
for root, dirs, files in os.walk(parentDir):
  # Firstly check if path contains one of the already marked bad measurement-folders
  if any(root.__contains__(_bDir) for _bDir in _XXBadDirs):
    LogLine(None, "Bad parent - skipped: ", root, wFill=0, end="\n")
    continue
  # Folder marked as bad measurement -> Skip
  if root.endswith("_XX"):
    if opt.PiMage_SkipBadSubdirs == True:
      _XXBadDirs.append(root)
    LogLine(None, "Marked as bad - skipped: ", root, wFill=0, end="\n")
    continue

  print("")
  LogLine(None, "Entering: ", root, wFill=0, end="\n")

  #Check if current directory contains measurement-files
  #  Directory found when it contains a Pics directory and *.dat files
  if not dirs.__contains__(picDir) or not any(f.endswith(".dat") for f in files):
    LogLine(None, "Nothing interesting here...", wFill=0, end="\n")
  else:
    LogLine(t0, "Possible directory found: ", root, end="\n")

    cSaveDir = root.replace(parentDir, saveDir)

    if not os.path.exists(cSaveDir):
      LogLine(t0, "Created Savedirectory: ", cSaveDir, wFill=0, end="\n")
      os.makedirs(cSaveDir)

    LogLine(t0, "Checking: ", "Already processed?")
    cSavFiles = os.listdir(cSaveDir)
    if opt.PiMage_ForceOverride == True:
      LogLineOK("Force override -> Process measurement")
    else:
      if any(f.endswith(".opt") for f in cSavFiles):      # Optionsfile is the last thing which is stored, so check for this if a measurement is processed or not
        LogLineOK("Yes -> Skip measurement")
        continue
      LogLineOK("No -> Process measurement")


    # Define mean-nPoints
    if type(opt.Image_UseForMeanNPoints) == str:
      LogLine(t0, "Looking for sweepfile (auto-detect nPoints to mean)...", end="\n")
      swpFName = [f for f in files if f.endswith(".swp")]
      if swpFName.__len__() > 0:
        if swpFName.__len__() > 1:
          LogLine(None, "- More sweepfiles found. Using: ", swpFName[0])
        head, swp, dummy = ReadSweepFile(os.path.join(root, swpFName[0]), False)
        swp = DataProvider(head, swp)
        opt.Image_MeanNPoints = int(swp.GetColumn("Rpts")[0])
        del head, swp, dummy
      else:
        LogLine(None, " - No sweepfile found: ", "Using MeanNPoints=1")
        opt.Image_MeanNPoints = 1
    else:
      opt.Image_MeanNPoints = opt.Image_UseForMeanNPoints

    # Build essential paths
    picsPath = os.path.join(root, picDir)

    ##### Do Picture stuff #####
    # Collect shutterspeeds
    LogLine(t0, "Grabbing shutterspeeds: ", wFill=0, end="\n")
    Shutterspeeds, DetectedFiletype = GrabSSFromFilenames(ImgDir=picsPath, Format=ImageFormat, FileTypes=LoadFileTypes, iSSPlaceholder=SS_Index, AllowedDeviationPercent=opt.DetectSS_AllowedPercentDeviation)
    Shutterspeeds.reverse()
    # Shutterspeeds.pop(0)
    for SS in Shutterspeeds:
      LogLine(None, whiteMessage="  - " + str(SS), wFill=18, yFill=0, end="\n")


    print("")
    LogLine(t0, "Collect and prepare images from folder: ", picsPath, end="\n")
    ssData = dict()
    imgContainer = dict()
    cirContainer = dict()
    # ShtrSpds = [100000]
    for SS in Shutterspeeds:
      LogLine(t0, "Current shutterspeed: ", str(SS), end="\n")

      # Prepare dict for image entries
      # ssData[SS] = dict()
      imgContainer[SS] = dict()
      cirContainer[SS] = dict()
      # ssData[SS]["Black"] = dict()
      # ssData[SS]["Images"] = dict()

      # Read float64 pictures and subtract
      LogLine(t0, "Read and crop images...")
      imgs, imgPaths = ReadImages(FolderPath=picsPath, Format=str.format(ImageFormat, "*", "*", SS, "*", DetectedFiletype), CropWindow=opt.Image_CropWin, IgnorePathVector=None, ShowImg=opt.ShowImages_Read)
      # ssData[SS]["Images"]["Cropped"] = imgs
      imgContainer[SS]["AsRead"] = imgs
      LogLineOK()



      LogLine(t0, "Meaning images...")
      # ssData[SS]["Images"]["Mean"] = MeanImages(ImgCollection=ssData[SS]["Images"]["Cropped"], ImgsPerMean=opt.Image_MeanNPicsPerSS, ShowImg=opt.ShowImages_Mean) # Mean nPicsPerSS together
      # ssData[SS]["Images"]["uint16"] = ssData[SS]["Images"]["Mean"][1:]                                                                                           # Remove the "init-datapoint" directly after measurement start
      imgContainer[SS]["Mean"] = MeanImages(ImgCollection=imgContainer[SS]["AsRead"], ImgsPerMean=opt.Image_MeanNPicsPerSS, ShowImg=opt.ShowImages_Mean) # Mean nPicsPerSS together
      imgContainer[SS]["uint16"] = imgContainer[SS]["Mean"][1:]                                                                                           # Remove the "init-datapoint" directly after measurement start
      if opt.Image_MeanNPoints > 1:
        # ssData[SS]["Images"]["Mean"] = MeanImages(ImgCollection=ssData[SS]["Images"]["Mean"], ImgsPerMean=opt.Image_MeanNPoints, ShowImg=opt.ShowImages_Mean)     # Meaning measurement points together
        imgContainer[SS]["Mean"] = MeanImages(ImgCollection=imgContainer[SS]["Mean"], ImgsPerMean=opt.Image_MeanNPoints, ShowImg=opt.ShowImages_Mean)     # Meaning measurement points together
      LogLineOK()
      # Cleanup old ressources
      LogLine(t0, "Cleanup cropped (f64) images...")
      # ssData[SS]["Images"].pop("Cropped")
      # ssData[SS]["Images"].pop("Mean")
      imgContainer[SS].pop("AsRead")
      imgContainer[SS].pop("Mean")
      LogLineOK()
      if (SS == Shutterspeeds[0]) and (opt.PngDump_16bitGrayScale == True):
        LogLine(t0, "Saving uint16-images...")
        # SaveImageCollection(ImgCollection=ssData[SS]["Images"]["uint16"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "uint16", SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("uint16 SS={}", SS)))
        SaveImageCollection(ImgCollection=imgContainer[SS]["uint16"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "16BitRaw", SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("16BitRaw SS={}", SS)))
        LogLineOK()



    LogLine(t0, "Finished image reading", wFill=0, end="\n")
    print("")

    LogLine(t0, "Starting circle detection...", end="\n")
    for SS in Shutterspeeds:
      LogLine(t0, "Current Shutterspeed: ", str(SS), wFill=0, end="\n")


      LogLine(t0, "Creating 8-bit threshold-images...")
      # ssData[SS]["Images"]["Threshold"] = BuildThreshold(ImgCollection=ssData[SS]["Images"]["uint16"], Threshold=opt.Image_bThresh, ThreshType=opt.Image_ThreshType, OtsuDiv=opt.Image_AutoThresDiv, OverexposedValue=opt.Image_OverexposedBrightness)
      threshImgs = BuildThreshold(ImgCollection=imgContainer[SS]["uint16"], Threshold=opt.Image_bThresh, ThreshType=opt.Image_ThreshType, OtsuDiv=opt.Image_AutoThresDiv, OverexposedValue=opt.Image_OverexposedBrightness)
      imgContainer[SS]["8BitThresh"] = ConvertBitsPerPixel(ImgCollection=threshImgs, originBPP=16, targetBPP=8)
      del threshImgs
      LogLineOK()
      print("")

      if (SS == Shutterspeeds[0]) and (opt.PngDump_8bitThreshhold == True):
        LogLine(t0, "Saving (raw) 8bit threshhold-images...")
        # SaveImageCollection(ImgCollection=ssData[SS]["Images"]["uint16"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "uint16", SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("uint16 SS={}", SS)))
        SaveImageCollection(ImgCollection=imgContainer[SS]["uint16"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "8BitRawThresh", SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("8BitRawThresh SS={}", SS)))
        LogLineOK()



      LogLine(t0, "Detecting circles on 8-bit (dilated & eroded) threshhold-images...")
      # _8bitDetectImgs = ConvertBitsPerPixel(ImgCollection=ssData[SS]["Images"]["Threshold"], originBPP=16, targetBPP=8)
      # [detectImgs, circles]= DetectSpots(ImgCollection=_8bitDetectImgs, pxDetectRadiusMin=opt.SpotDetect_pxMinRadius, pxDetectRadiusMax=opt.SpotDetect_pxMaxRadius, Dilate=opt.SpotDetect_Dilate, Erode=opt.SpotDetect_Erode, ShowImg=opt.ShowImages_SpotDetection)
      [detectImgs, circles]= DetectSpots(ImgCollection=imgContainer[SS]["8BitThresh"], pxDetectRadiusMin=opt.SpotDetect_pxMinRadius, pxDetectRadiusMax=opt.SpotDetect_pxMaxRadius, Dilate=opt.SpotDetect_Dilate, Erode=opt.SpotDetect_Erode, ShowImg=opt.ShowImages_SpotDetection)
      LogLineOK()
      LogLine(t0, "Cleanup (raw) threshold (uint8) images...")
      # ssData[SS]["Images"].pop("Threshold")
      imgContainer[SS].pop("8BitThresh")
      LogLineOK()
      # ssData[SS]["Images"]["CircleDetection"] = detectImgs
      # ssData[SS]["Circles"] = dict()
      # ssData[SS]["Circles"]["Raw"] = circles
      imgContainer[SS]["8BitCirDetect"] = detectImgs
      cirContainer[SS] = dict()
      cirContainer[SS]["Raw"] = circles

      if (SS == Shutterspeeds[0]) and (opt.PngDump_8bitCircleDetect == True):
        LogLine(t0, "Saving 8-bit (dilated & eroded) threshhold-images...")
        # SaveImageCollection(ImgCollection=ssData[SS]["Images"]["CircleDetection"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "CircleDetection", SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("CircleDetection SS={}", SS)))
        # SaveImageCollection(ImgCollection=imgContainer[SS]["CircleDetection"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "CircleDetection", SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("CircleDetection SS={}", SS)))
        SaveImageCollection(ImgCollection=imgContainer[SS]["8BitCirDetect"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "8BitCirDetect", SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("8BitCirDetect SS={}", SS)))
        LogLineOK()
      # Cleanup old ressources
      LogLine(t0, "Cleanup 8-bit (dilated & eroded) threshhold-images...")
      # ssData[SS]["Images"].pop("CircleDetection")
      imgContainer[SS].pop("8BitCirDetect")
      LogLineOK()



      if (opt.PngDump_8bitCircleDrawAroundEachDetection == True): # This images are only for optical observation by the user. Therefore the conversion and draw only needs to be done, when the dump was requested!
        LogLine(t0, "Drawing circles around each detected spot on the images...")
        # drawImgs = ConvertBitsPerPixel(ImgCollection=ssData[SS]["Images"]["uint16"], originBPP=16, targetBPP=8)
        # ssData[SS]["Images"]["DrawedCircles"] = CircleDraw(ImgCollection=drawImgs, CircleCollection=circles, pxRadius=opt.CircleDraw_pxRadius, AddPxRadius=opt.CircleDraw_AddPxRadius, ShowImg=opt.ShowImages_Draw)
        drawImgs = ConvertBitsPerPixel(ImgCollection=imgContainer[SS]["uint16"], originBPP=16, targetBPP=8)
        imgContainer[SS]["8BitCirDraw"] = DrawCircleAroundEachSpot(ImgCollection=drawImgs, CircleCollection=circles, pxRadius=opt.CircleDraw_pxRadius, AddPxRadius=opt.CircleDraw_AddPxRadius, ShowImg=opt.ShowImages_Draw)
        del drawImgs

        if (SS == Shutterspeeds[0]):
          # SaveImageCollection(ImgCollection=ssData[SS]["Images"]["DrawedCircles"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "DrawnCircles", SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("DrawnCircles SS={}", SS)))
          SaveImageCollection(ImgCollection=imgContainer[SS]["8BitCirDraw"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "8BitCirDraw", SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("8BitCirDraw SS={}", SS)))
        LogLineOK()
        # Cleanup old ressources
        LogLine(t0, "Cleanup circle-draw images...")
        # ssData[SS]["Images"].pop("8BitCirDraw")
        imgContainer[SS].pop("8BitCirDraw")
        LogLineOK()


      # Sort them into XY-pairs
      LogLine(t0, "Sort circles into XYKey-pairs...")
      # ssData[SS]["Circles"]["XYKeys"] = CollectCirclesAsXYKeys(CircleCollection=circles, pxRadius=opt.XYKeys_pxCollectRadius, AddPxRadius=opt.XYKeys_AddPxCollectRadius, FollowSpots=opt.XYKeys_FollowSpots)
      cirContainer[SS]["XYKeys"] = CollectCirclesAsXYKeys(CircleCollection=circles, pxRadius=opt.XYKeys_pxCollectRadius, AddPxRadius=opt.XYKeys_AddPxCollectRadius, FollowSpots=opt.XYKeys_FollowSpots)
      del circles # From here circles is a part of cirContainer
      LogLineOK()
      print("")

    LogLine(t0, "Finished circle detection and XYKey-pairing", end="\n")


    print("")
    # LogLine(t0, "Correct spot-keys based on SS=", str(next(iter(ssData.keys()))))
    LogLine(t0, "Correct XYKeys based on SS=", str(next(iter(imgContainer.keys()))))
    # CorrectXYSortKeys(ssData=ssData, pxCorrectionRadius=opt.XYKeys_pxCorrectionRadius)
    CorrectXYSortKeys(cirContainer=cirContainer, pxCorrectionRadius=opt.XYKeys_pxCorrectionRadius)
    LogLineOK()

    if opt.XYKeys_CrossCheckKeys:
      print("")
      # LogLine(t0, "Correct spot-keys based on SS=", str(next(iter(ssData.keys()))))
      LogLine(t0, "Crosscheck XYKeys...")
      # CorrectXYSortKeys(ssData=ssData, pxCorrectionRadius=opt.XYKeys_pxCorrectionRadius)
      CrossCheckXYKeys(cirContainer=cirContainer, pxTolerance=opt.XYKeys_pxCorrectionRadius)
      LogLineOK()


    LogLine(t0, "Sorting spot-keys from topleft to bottomright")
    # SortXYFromLUtoRL(cirContainer=ssData, pxRowband=opt.XYKeySort_Rowdistance)
    SortXYFromLUtoRL(cirContainer=cirContainer, pxRowband=opt.XYKeySort_Rowdistance)
    LogLineOK()



    if (opt.PngDump_8bitXYKeyDrawAroundEachXYKey == True): # This images are only for optical observation by the user. Therefore the conversion and draw only needs to be done, when the dump was requested!
      LogLine(t0, "Drawing circles around the detected XYKeys on the images...")
      SS = Shutterspeeds[0] # As we are not in the SS-Loop anymore, SS needs to be set to the correct SS
      drawImgs = ConvertBitsPerPixel(ImgCollection=imgContainer[SS]["uint16"], originBPP=16, targetBPP=8)
      imgContainer[SS]["8BitXYKeyDraw"] = DrawCircleAroundEachXYKey(ImgCollection=drawImgs, CircleContainer=cirContainer, pxRadius=opt.CircleDraw_pxRadius, AddPxRadius=opt.CircleDraw_AddPxRadius, ShowImg=opt.ShowImages_Draw)
      del drawImgs

      
      if (SS == Shutterspeeds[0]):
        SaveImageCollection(ImgCollection=imgContainer[SS]["8BitXYKeyDraw"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "8BitXYKeyDraw", SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("8BitXYKeyDraw SS={}", SS)))
      LogLineOK()
      # Cleanup old ressources
      LogLine(t0, "Cleanup xyKey-draw images...")
      # ssData[SS]["Images"].pop("8BitCirDraw")
      imgContainer[SS].pop("8BitXYKeyDraw")
      LogLineOK()






    # # Saving current progress as data
    # # # print("")
    # # # LogLine(t0, "Saving ssDataImages and ssDataCircle:", end="\n")
    # # # savImgCollection = dict()
    # # # savSpotCollection = dict()
    # # # for SS in Shutterspeeds:
    # # #   savImgCollection[SS] = ssData[SS]["Images"]
    # # #   savSpotCollection[SS] = ssData[SS]["Circles"]

    # # # Raw spot data and images
    # # if opt.PklDump_CirContainer:
    # #   _fName = "PMP_CirContainer.pkl"
    # #   _fPath = os.path.join(cSaveDir, _fName)
    # #   _fHandle = open(_fPath, "wb")
    # #   pickle.dump(savSpotCollection, _fHandle)
    # #   _fHandle.close()
    # #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")

    # # # if opt.SaveSSImagePkl == True:
    # # #   _fName = "PMP_ssDetectionImages.pkl"
    # # #   _fPath = os.path.join(cSaveDir, _fName)
    # # #   _fHandle = open(_fPath, "wb")
    # # #   pickle.dump(savImgCollection, _fHandle)
    # # #   _fHandle.close()
    # # #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    # # if opt.PklDump_ImgContainer == True:
    # #   _fName = "PMP_ImgContainer.pkl"
    # #   _fPath = os.path.join(cSaveDir, _fName)
    # #   _fHandle = open(_fPath, "wb")
    # #   pickle.dump(savImgCollection, _fHandle)
    # #   _fHandle.close()
    # #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")


    # Extract image informations
    LogLine(t0, "Extracting raw brightness data...")
    # sesContainer = SEnsor Signal Container
    sesContainer = SubareaImagesAndSensorsignalInfo(cirContainer=cirContainer, pxSidelen=opt.SesExtraction_pxSideLen, addSidelen=opt.SesExtraction_AddPxSideLen, imgContainer=imgContainer, imgKey="uint16")
    LogLineOK()

    LogLine(t0, "Extracting pixelcounts and overexposureinfo...")
    # PixelCount and Exposureinfo Container
    pcoContainer = PixelcountAndOverexposureInfo(cirContainer=cirContainer, imgContainer=imgContainer, imgKey="uint16", valueOfAreacount=opt.Image_MinBright2CountArea, valueOfOverexposement=opt.Image_OverexposedBrightness)
    LogLineOK()

    LogLine(t0, yellowMsg=f"Merging all sensor signal vectors on based on SS=", whiteMessage=f"{Shutterspeeds[0]}")
    # PixelCount and Exposureinfo Container
    mssContainer = MergeSensorsignalVectors(sesContainer=sesContainer, pcoContainer=pcoContainer)
    LogLineOK()

    # # # ssData,                        \
    # # # imgSets,                       \
    # # # brightSets,                    \
    # # # areaCntSets,                   \
    # # # divFactors,                    \
    # # # scaledAnyBright,               \
    # # # scaledAnyPxImgs,               \
    # # # scaledWhereOverexposedBright,  \
    # # # scaledWhereOverexposedImgs = DataExtractionAndUpscaling(ssData=ssData,
    # # #                                                         ImgKey="uint16",
    # # #                                                         pxSidelen=opt.bDetect_pxSideLen,
    # # #                                                         AddPxSidelen=opt.bDetect_AddPxSideLen,
    # # #                                                         TakeSpotBrightFromAllImgs=opt.bDetect_SpotBrightFromAllImgs,
    # # #                                                         MinBright=opt.Image_MinBright2CountArea,
    # # #                                                         OverexposedValue=opt.Image_OverexposedBrightness,
    # # #                                                         )

    # # # LogLineOK()



    # Dump Image-Container as pickle
    if opt.PklDump_imgContainer == True:
      _fName = "PMP_imgContainer.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(imgContainer, _fHandle)
      _fHandle.close()
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    del imgContainer         # Remove to clear RAM


    # Dump Circle-Container as pickle
    if opt.PklDump_cirContainer == True:
      _fName = "PMP_cirContainer.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(cirContainer, _fHandle)
      _fHandle.close()
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    del cirContainer         # Remove to clear RAM


    # Dump PixelCount- and Overexposureinfo-Container as pickle
    if opt.PklDump_pcoContainer == True:
      _fName = "PMP_pcoContainer.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(pcoContainer, _fHandle)
      _fHandle.close()
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    del pcoContainer         # Remove to clear RAM


    # Dump SEnsorSignal-Container as pickle
    if opt.PklDump_sesContainer == True:
      _fName = "PMP_sesContainer.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(sesContainer, _fHandle)
      _fHandle.close()
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    del sesContainer         # Remove to clear RAM


    # Dump MergedSensorSignal-Container as pickle
    if opt.PklDump_mssContainer == True:
      _fName = "PMP_mssContainer.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(mssContainer, _fHandle)
      _fHandle.close()
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    del mssContainer         # Remove to clear RAM


    # Copy the electrical FEMDAQ-data for data-evalutation
    if opt.Copy_FEMDAQData == True:
      print("")
      LogLine(t0, "Copy FEMDAQ data to result-folder...")
      for file in files:
        if any(file.endswith(ext) for ext in [".png", ".dat", ".swp", ".resistor"]):
          shutil.copy2(os.path.join(root, file), cSaveDir)
      LogLineOK()


    # Save the option-file
    print("")
    _fName = "PMP_Options.opt"
    _fPath = os.path.join(cSaveDir, _fName)
    LogLine(None, f"Saving options as \"{_fPath}\"")
    opt.Save(saveDir=cSaveDir, fName=_fName)
    LogLineOK()



    # # # # Validated and corrected brightness data and -images
    # # # if opt.Save_ImgSets4Brightness == True:
    # # #   _fName = "PMP_ImgSets4Brightness.pkl"
    # # #   _fPath = os.path.join(cSaveDir, _fName)
    # # #   _fHandle = open(_fPath, "wb")
    # # #   pickle.dump(imgSets, _fHandle)
    # # #   _fHandle.close()
    # # #   del imgSets         # Remove to clear RAM
    # # #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    # # # else:
    # # #   del imgSets # When not saving them , just delete them to free the RAM

    # # # if opt.Save_BrightSets4Brightness == True:
    # # #   _fName = "PMP_BrightSets4Brightness.pkl"
    # # #   _fPath = os.path.join(cSaveDir, _fName)
    # # #   _fHandle = open(_fPath, "wb")
    # # #   pickle.dump(brightSets, _fHandle)
    # # #   _fHandle.close()
    # # #   del brightSets      # Remove to clear RAM
    # # #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    # # # else:
    # # #   del brightSets # When not saving them , just delete them to free the RAM


    # # # if opt.Save_PxAreaCnts4Brightness == True:
    # # #   _fName = "PMP_PxAreaCnts4Brightness.pkl"
    # # #   _fPath = os.path.join(cSaveDir, _fName)
    # # #   _fHandle = open(_fPath, "wb")
    # # #   pickle.dump(areaCntSets, _fHandle)
    # # #   _fHandle.close()
    # # #   del areaCntSets      # Remove to clear RAM
    # # #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    # # # else:
    # # #   del areaCntSets # When not saving them , just delete them to free the RAM

    # # # if opt.Save_DivFactors4Brightness == True:
    # # #   _fName = "PMP_DivFactors4Brightness.pkl"
    # # #   _fPath = os.path.join(cSaveDir, _fName)
    # # #   _fHandle = open(_fPath, "wb")
    # # #   pickle.dump(divFactors, _fHandle)
    # # #   _fHandle.close()
    # # #   del divFactors      # Remove to clear RAM
    # # #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    # # # else:
    # # #   del divFactors # When not saving them , just delete them to free the RAM


    # # # if opt.Save_ScaledAnyPxImgs == True:
    # # #   _fName = "PMP_ScaledAnyPxImgs4Brightness.pkl"
    # # #   _fPath = os.path.join(cSaveDir, _fName)
    # # #   _fHandle = open(_fPath, "wb")
    # # #   pickle.dump(scaledAnyPxImgs, _fHandle)
    # # #   _fHandle.close()
    # # #   del scaledAnyPxImgs      # Remove to clear RAM
    # # #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    # # # else:
    # # #   del scaledAnyPxImgs # When not saving them , just delete them to free the RAM

    # # # if opt.Save_ScaledAnyBrightnesses == True:
    # # #   _fName = "PMP_ScaledAnyBrightnesses.pkl"
    # # #   _fPath = os.path.join(cSaveDir, _fName)
    # # #   _fHandle = open(_fPath, "wb")
    # # #   pickle.dump(scaledAnyBright, _fHandle)
    # # #   _fHandle.close()
    # # #   del scaledAnyBright      # Remove to clear RAM
    # # #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    # # # else:
    # # #   del scaledAnyBright # When not saving them , just delete them to free the RAM

    # # # if opt.Save_ScaledWhereOverexposedPxImgs == True:
    # # #   _fName = "PMP_ScaledWhereOverexposedPxImgs.pkl"
    # # #   _fPath = os.path.join(cSaveDir, _fName)
    # # #   _fHandle = open(_fPath, "wb")
    # # #   pickle.dump(scaledWhereOverexposedImgs, _fHandle)
    # # #   _fHandle.close()
    # # #   del scaledWhereOverexposedImgs      # Remove to clear RAM
    # # #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    # # # else:
    # # #   del scaledWhereOverexposedImgs # When not saving them , just delete them to free the RAM


    # # # if opt.Save_ScaledWhereOverexposedBrightnesses == True:
    # # #   _fName = "PMP_ScaledWhereOverexposedBrightnesses.pkl"
    # # #   _fPath = os.path.join(cSaveDir, _fName)
    # # #   _fHandle = open(_fPath, "wb")
    # # #   pickle.dump(scaledWhereOverexposedBright, _fHandle)
    # # #   _fHandle.close()
    # # #   del scaledWhereOverexposedBright      # Remove to clear RAM
    # # #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    # # # else:
    # # #   del scaledWhereOverexposedBright # When not saving them , just delete them to free the RAM


    # # # if opt.Save_FEMDAQCopies == True:
    # # #   print("")
    # # #   LogLine(t0, "Copying FEMDAQ data...")
    # # #   for file in files:
    # # #     if any(file.endswith(ext) for ext in [".png", ".dat", ".swp", ".resistor"]):
    # # #       shutil.copy2(os.path.join(root, file), cSaveDir)
    # # #   LogLineOK()

    # # #   print("")
    # # #   LogLine(t0, "Saving used options...")
    # # #   opt.Save(cSaveDir)                                           # Used options
    # # #   LogLineOK()


    print("\n\n") # Add some space for next iteration



print("\n")
LogLine(t0, "Finished", bcolors.BOLD + "----- PiMagePro -----" + bcolors.ENDC, yFill=15, wFill=0, end="\n")
if "_logger" in locals():
  _logger.flush()
  del _logger


