##################################################################################
# 
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

from PMPLib.ImgFileHandling import BlackFormat, ImageFormat, OTH_LoadFileTypes, OTH_SaveFileType, SS_Index
from PMPLib.ImgFileHandling import GrabSSFromFilenames
from PMPLib.ImgFileHandling import ReadImages
from PMPLib.ImgFileHandling import SaveImageCollection

from PMPLib.ImgManipulation import MeanImages
from PMPLib.ImgManipulation import SubtractFromImgCollection
from PMPLib.ImgManipulation import ConvertBitsPerPixel
from PMPLib.ImgManipulation import ConvertImgCollectionDataType
from PMPLib.ImgManipulation import BuildThreshold
from PMPLib.ImgManipulation import CircleDraw

from PMPLib.CircleDetectAndXYSort import DetectSpots
from PMPLib.CircleDetectAndXYSort import CollectCirclesAsXYKeys
from PMPLib.CircleDetectAndXYSort import CorrectXYSortKeys
from PMPLib.CircleDetectAndXYSort import SortXYFromLUtoRL

from PMPLib.DataProcessing import DataExtractionAndUpscaling


from PMPLib.PiMageOptions import PiMageOptions


# Paths
# parentDir = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\01 Aktivierung IMax1V\230222_095249 Tip Ch3 (aktiviert)"
# parentDir = r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen"

# parentDir = r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)"
# parentDir = r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)"
# parentDir = r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Weitere Kombis"
# parentDir = r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Tips einzeln, Rest floatend"
# parentDir = r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche"
# parentDir = r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis"
# parentDir = r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check"
parentDir = r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded"

picDir = "Pics"

saveDir = str.replace(parentDir, "Messungen", "Auswertung")
if not os.path.exists(saveDir):
  os.makedirs(saveDir)


### Options/Parameters ###
opt = PiMageOptions()

# LogFile
LogFilePath = os.path.join(saveDir, "PiMage.log")
_logger = Logger(LogFilePath) # Keep instance for closing logger
LogLen = 70


# PiMage-sequence
opt.PiMage_SkipBadSubdirs = True                                        # If a parent folder is marked as bad (postfix: _XX) measurement, the subdirectories also skipped!y
opt.PiMage_ForceOverride = True                                         # False = Checks for already processed and skips in case; True = Won't check if a measurement is already processed!


# Visualization
opt.ShowImages_Read = False                                             # True = show each image (during debugging); False = Silent process
opt.ShowImages_Mean = False                                             # True = show each image (during debugging); False = Silent process
opt.ShowImages_SpotDetection = False                                    # True = show each image (during debugging); False = Silent process
opt.ShowImages_Draw = False                                             # True = show each image (during debugging); False = Silent process


# Image processing
opt.Image_CropWin = None                                                # None/False: Images not cropped; [x, y, w, h]   -   x, y: left upper corner   -   w, h: size of window
opt.Image_bThresh = 35                                                  # 8bit brightness Threshold value. It's only used, when the threshold of autodetect-algorithm (Image_ThreshType) is smaller than this one!
opt.Image_ThreshType = cv.THRESH_OTSU                                   # cv.THRESH_OTSU:                     Tries otsu
                                                                        # cv.ADAPTIVE_THRESH_GAUSSIAN_C:      Adaptive won't work with 16bit
                                                                        # cv.ADAPTIVE_THRESH_MEAN_C:          Adaptive won't work with 16bit
                                                                        # Other else:                         Uses fixed bThres-Value
opt.Image_AutoThresDiv = 8                                              # When ThrehType is used for auto-thresh, the returend threshold is divided by AutoThreshDiv and used to build the actual threshold (used for fine-tuning of threshhold)
opt.Image_UseForMeanNPoints = ".swp"                                    # <int>: Means together n measurement-points; ".swp": Tryies to find a sweep-file where it can extract the number of n measurement points
opt.Image_MeanNPicsPerSS = 1                                            # Means n pics (in row) together
opt.Image_OverexposedBrightness = 0xFFF0                                # Defines at which 16bit value a pixel counts as overexposed
opt.Image_MinBright2CountArea = 1* 0xFF                                 # Defines at which 16bit value a pixel counts as brightness-contributing pixel


# Spot-detection
opt.SpotDetect_Dilate = 10                                              # Detected image-contours (on thresh-images) are extended by n pixel-rows (entire circumfence) to close small gaps between a splitted spot
opt.SpotDetect_Erode = opt.SpotDetect_Dilate                            # The dilated image-contours are reduced by n pixel-rows (entire circumfence) (if erode=dilate the resulting spot should be the same as initially but whitout missing pixels within)
opt.CircleDetect_pxMinRadius = 5                                        # Minimum radius for a valid spot: pxMinRadius <= r <= pxMaxRadius; Used to avoid artifacts detected as spots
opt.CircleDetect_pxMaxRadius = 50                                       # Maximum radius for a valid spot: pxMinRadius <= r <= pxMaxRadius; Used to avoid the detection of spots bigger than being estimated


# Spot-Draw on Images
opt.CircleDraw_pxRadius = opt.CircleDetect_pxMaxRadius                  # Draws a circle using pxRadius to visualize the detected spots on the "circle-draw-images"
opt.CircleDraw_AddPxRadius = False                                      # When enabled, the circles detected spot-radius is added to pxRadius


# Brightness-Detection
opt.bDetect_SpotBrightFromAllImgs = True                                # When enabled, the brightness is extracted from ALL images based on the xy-key position! (NOTE: This ensures, that all vectors have the same)
opt.bDetect_pxSideLen = 2 * opt.CircleDetect_pxMaxRadius                # Sidelength of a square around the circle center from which the circle-brightness is extracted
opt.bDetect_AddPxSideLen = False                                        # When enabled, the circles radius is added to bDetect_pxSideLen


# XY-Keys
opt.XYKeys_pxCollectRadius = opt.CircleDetect_pxMaxRadius               # Valid radius around a xy-coordinate a detected image-spot is collected under, when located within this area.
opt.XYKeys_AddPxCollectRadius = False                                   # When enabled, the image-spots radius is added to CircleDetect_pxMaxRadius
opt.XYKeys_FollowSpots = True                                           # When enabled, the xy-key follows the related circle-centers by meaning them
opt.XYKeys_pxCorrectionRadius = opt.XYKeys_pxCollectRadius              # For each SS a set of XY-Key-Pairs can be found. To assign them together, this radius is used as a tolerance and is then re-attached to ssData.


# XY-Key Sorting
opt.XYKeySort_Rowdistance = opt.CircleDetect_pxMaxRadius                # Each leftmost spot of a row does a horizontal raycast to the right. XYKeySort_Rowdistance (in [px]) defines the vertical distance to that ray, in which a spot needs to be located to count as part of the row.


# Saving
opt.SaveSSImagePkl                          = False                     # Save internal raw ssData structure
opt.Save_ImgSets4Brightness                 = False                     # Save "Imageset"                                             for Brightnesses and it's correction as pickle
opt.Save_BrightSets4Brightness              = True                      # Save "Brightnesses"                                         from Imageset as pickle
opt.Save_PxAreaCnts4Brightness              = True                      # Save "PixelArea-Counts & -Factors"                          from Imageset as pickle
opt.Save_DivFactors4Brightness              = True                      # Save "Division-Correction-Factors"                          from BrightSets as pickle
opt.Save_ScaledAnyPxImgs                    = False                     # Save "Any upscaled pixelcorrected images"                   as pickle (huge!)
opt.Save_ScaledAnyBrightnesses              = True                      # Save "Any upscaled spotbrightness"                          as pickle
opt.Save_ScaledWhereOverexposedPxImgs       = False                     # Save "Any upscaled spotbrightness images"                   as pickle
opt.Save_ScaledWhereOverexposedBrightnesses = True                      # Save "Upscaled spotbrightness where overexposure occured"   as pickle
opt.Save_FEMDAQCopies                       = True                      # Creates copies of the relevant FEMDAQ-data (if FEMDAQ was used as measurement-tool!)









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
    Shutterspeeds, DetectedFiletype = GrabSSFromFilenames(picsPath, ImageFormat, OTH_LoadFileTypes, SS_Index)
    Shutterspeeds.reverse()
    # Shutterspeeds.pop(0)
    for SS in Shutterspeeds:
      LogLine(None, whiteMessage="  - " + str(SS), wFill=18, yFill=0, end="\n")


    print("")
    LogLine(t0, "Collect and prepare images from folder: ", picsPath, end="\n")
    ssData = dict()
    # ShtrSpds = [100000]
    for SS in Shutterspeeds:
      LogLine(t0, "Current shutterspeed: ", str(SS), end="\n")

      # Prepare dict for image entries
      ssData[SS] = dict()
      # ssData[SS]["Black"] = dict()
      ssData[SS]["Images"] = dict()

      # Read float64 pictures and subtract
      LogLine(t0, "Read and crop images...")
      imgs, imgPaths = ReadImages(fPaths=picsPath, Format=str.format(ImageFormat, "*", "*", SS, "*", DetectedFiletype), CropWindow=opt.Image_CropWin, IgnorePathVector=None, ShowImg=opt.ShowImages_Read)
      ssData[SS]["Images"]["Cropped"] = imgs
      LogLineOK()



      LogLine(t0, "Meaning images...")
      ssData[SS]["Images"]["Mean"] = MeanImages(ImgCollection=ssData[SS]["Images"]["Cropped"], ImgsPerMean=opt.Image_MeanNPicsPerSS, ShowImg=opt.ShowImages_Mean) # Mean nPicsPerSS together
      ssData[SS]["Images"]["uint16"] = ssData[SS]["Images"]["Mean"][1:]                                                                                           # Remove the "init-datapoint" directly after measurement start
      if opt.Image_MeanNPoints > 1:
        ssData[SS]["Images"]["Mean"] = MeanImages(ImgCollection=ssData[SS]["Images"]["Mean"], ImgsPerMean=opt.Image_MeanNPoints, ShowImg=opt.ShowImages_Mean)     # Meaning measurement points together
      LogLineOK()
      # Cleanup old ressources
      LogLine(t0, "Cleanup cropped (f64) images...")
      ssData[SS]["Images"].pop("Cropped")
      ssData[SS]["Images"].pop("Mean")
      LogLineOK()


      if SS == Shutterspeeds[0]:
        LogLine(t0, "Saving uint16-images...")
        SaveImageCollection(ImgCollection=ssData[SS]["Images"]["uint16"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "uint16", OTH_SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("uint16 SS={}", SS)))
        LogLineOK()






      LogLine(t0, "Creating threshold-images...")
      ssData[SS]["Images"]["Threshold"] = BuildThreshold(ImgCollection=ssData[SS]["Images"]["uint16"], Threshold=opt.Image_bThresh, ThreshType=opt.Image_ThreshType, OtsuDiv=opt.Image_AutoThresDiv, OverexposedValue=opt.Image_OverexposedBrightness)
      LogLineOK()
      print("")


    LogLine(t0, "Finished image processing", wFill=0, end="\n")
    print("")

    LogLine(t0, "Starting circle detection...", end="\n")
    for SS in Shutterspeeds:
      LogLine(t0, "Current Shutterspeed: ", str(SS), wFill=0, end="\n")



      LogLine(t0, "Detecting circles on images...")
      _8bitDetectImgs = ConvertBitsPerPixel(ImgCollection=ssData[SS]["Images"]["Threshold"], originBPP=16, targetBPP=8)
      [detectImgs, circles]= DetectSpots(ImgCollection=_8bitDetectImgs, pxDetectRadiusMin=opt.CircleDetect_pxMinRadius, pxDetectRadiusMax=opt.CircleDetect_pxMaxRadius, Dilate=opt.SpotDetect_Dilate, Erode=opt.SpotDetect_Erode, ShowImg=opt.ShowImages_SpotDetection)
      del _8bitDetectImgs
      ssData[SS]["Images"]["CircleDetection"] = detectImgs
      ssData[SS]["Circles"] = dict()
      ssData[SS]["Circles"]["Raw"] = circles
      if SS == Shutterspeeds[0]:
        SaveImageCollection(ImgCollection=ssData[SS]["Images"]["CircleDetection"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "CircleDetection", OTH_SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("CircleDetection SS={}", SS)))
      LogLineOK()
      # Cleanup old ressources
      LogLine(t0, "Cleanup threshold (uint8) images...")
      ssData[SS]["Images"].pop("Threshold")
      LogLineOK()
      LogLine(t0, "Cleanup CircleDetection (uint8) images...")
      ssData[SS]["Images"].pop("CircleDetection")
      LogLineOK()




      LogLine(t0, "Drawing detected circles on images...")
      drawImgs = ConvertBitsPerPixel(ImgCollection=ssData[SS]["Images"]["uint16"], originBPP=16, targetBPP=8)
      ssData[SS]["Images"]["DrawedCircles"] = CircleDraw(ImgCollection=drawImgs, CircleCollection=circles, pxRadius=opt.CircleDraw_pxRadius, AddPxRadius=opt.CircleDraw_AddPxRadius, ShowImg=opt.ShowImages_Draw)
      del drawImgs
      if SS == Shutterspeeds[0]:
        SaveImageCollection(ImgCollection=ssData[SS]["Images"]["DrawedCircles"], FileFormat=str.format(ImageFormat, "Dev101", "{:05d}", SS, "DrawnCircles", OTH_SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("DrawnCircles SS={}", SS)))
      LogLineOK()
      # Cleanup old ressources
      LogLine(t0, "Cleanup circle-draw images...")
      ssData[SS]["Images"].pop("DrawedCircles")
      LogLineOK()


      # Sort them into XY-pairs
      LogLine(t0, "Sort circles into XYKey-pairs...")
      ssData[SS]["Circles"]["XYKeys"] = CollectCirclesAsXYKeys(CircleCollection=circles, pxRadius=opt.XYKeys_pxCollectRadius, AddPxRadius=opt.XYKeys_AddPxCollectRadius, FollowSpots=opt.XYKeys_FollowSpots)
      LogLineOK()
      print("")



    LogLine(t0, "Finished circle detection and XYKey-pairing", end="\n")


    print("")
    LogLine(t0, "Correct spot-keys based on SS=", str(next(iter(ssData.keys()))))
    CorrectXYSortKeys(ssData=ssData, pxCorrectionRadius=opt.XYKeys_pxCorrectionRadius)
    LogLineOK()



    LogLine(t0, "Sorting spot-keys from topleft to bottomright")
    SortXYFromLUtoRL(ssData=ssData, pxRowband=opt.XYKeySort_Rowdistance)
    LogLineOK()






    # Saving current progress as data
    print("")
    LogLine(t0, "Saving ssDataImages and ssDataCircle:", end="\n")
    savImgCollection = dict()
    savSpotCollection = dict()
    for SS in Shutterspeeds:
      savImgCollection[SS] = ssData[SS]["Images"]
      savSpotCollection[SS] = ssData[SS]["Circles"]

    # Raw spot data and images
    _fName = "PMP_ssDetectionData.pkl"
    _fPath = os.path.join(cSaveDir, _fName)
    _fHandle = open(_fPath, "wb")
    pickle.dump(savSpotCollection, _fHandle)
    _fHandle.close()
    LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")

    if opt.SaveSSImagePkl == True:
      _fName = "PMP_ssDetectionImages.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(savImgCollection, _fHandle)
      _fHandle.close()
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")


    # Extract img brightness of detection
    LogLine(t0, "Extracting brightness data...")

    ssData,                        \
    imgSets,                       \
    brightSets,                    \
    areaCntSets,                   \
    divFactors,                    \
    scaledAnyBright,               \
    scaledAnyPxImgs,               \
    scaledWhereOverexposedBright,  \
    scaledWhereOverexposedImgs = DataExtractionAndUpscaling(ssData=ssData,
                                                            ImgKey="uint16",
                                                            pxSidelen=opt.bDetect_pxSideLen,
                                                            AddPxSidelen=opt.bDetect_AddPxSideLen,
                                                            TakeSpotBrightFromAllImgs=opt.bDetect_SpotBrightFromAllImgs,
                                                            MinBright=Image_MinBright2CountArea,
                                                            OverexposedValue=Image_OverexposedBrightness,
                                                            )

    LogLineOK()


    # Validated and corrected brightness data and -images
    if opt.Save_ImgSets4Brightness == True:
      _fName = "PMP_ImgSets4Brightness.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(imgSets, _fHandle)
      _fHandle.close()
      del imgSets         # Remove to clear RAM
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    else:
      del imgSets # When not saving them , just delete them to free the RAM

    if opt.Save_BrightSets4Brightness == True:
      _fName = "PMP_BrightSets4Brightness.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(brightSets, _fHandle)
      _fHandle.close()
      del brightSets      # Remove to clear RAM
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    else:
      del brightSets # When not saving them , just delete them to free the RAM


    if opt.Save_PxAreaCnts4Brightness == True:
      _fName = "PMP_PxAreaCnts4Brightness.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(areaCntSets, _fHandle)
      _fHandle.close()
      del areaCntSets      # Remove to clear RAM
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    else:
      del areaCntSets # When not saving them , just delete them to free the RAM

    if opt.Save_DivFactors4Brightness == True:
      _fName = "PMP_DivFactors4Brightness.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(divFactors, _fHandle)
      _fHandle.close()
      del divFactors      # Remove to clear RAM
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    else:
      del divFactors # When not saving them , just delete them to free the RAM


    if opt.Save_ScaledAnyPxImgs == True:
      _fName = "PMP_ScaledAnyPxImgs4Brightness.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(scaledAnyPxImgs, _fHandle)
      _fHandle.close()
      del scaledAnyPxImgs      # Remove to clear RAM
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    else:
      del scaledAnyPxImgs # When not saving them , just delete them to free the RAM

    if opt.Save_ScaledAnyBrightnesses == True:
      _fName = "PMP_ScaledAnyBrightnesses.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(scaledAnyBright, _fHandle)
      _fHandle.close()
      del scaledAnyBright      # Remove to clear RAM
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    else:
      del scaledAnyBright # When not saving them , just delete them to free the RAM

    if opt.Save_ScaledWhereOverexposedPxImgs == True:
      _fName = "PMP_ScaledWhereOverexposedPxImgs.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(scaledWhereOverexposedImgs, _fHandle)
      _fHandle.close()
      del scaledWhereOverexposedImgs      # Remove to clear RAM
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    else:
      del scaledWhereOverexposedImgs # When not saving them , just delete them to free the RAM


    if opt.Save_ScaledWhereOverexposedBrightnesses == True:
      _fName = "PMP_ScaledWhereOverexposedBrightnesses.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(scaledWhereOverexposedBright, _fHandle)
      _fHandle.close()
      del scaledWhereOverexposedBright      # Remove to clear RAM
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    else:
      del scaledWhereOverexposedBright # When not saving them , just delete them to free the RAM


    if opt.Save_FEMDAQCopies == True:
      print("")
      LogLine(t0, "Copying FEMDAQ data...")
      for file in files:
        if any(file.endswith(ext) for ext in [".png", ".dat", ".swp", ".resistor"]):
          shutil.copy2(os.path.join(root, file), cSaveDir)
      LogLineOK()

      print("")
      LogLine(t0, "Saving used options...")
      opt.Save(cSaveDir)                                           # Used options
      LogLineOK()


    print("\n\n") # Add some space for next iteration



print("\n")
LogLine(t0, "Finished", bcolors.BOLD + "----- PiMagePro -----" + bcolors.ENDC, yFill=15, wFill=0, end="\n")
if "_logger" in locals():
  _logger.flush()
  del _logger


