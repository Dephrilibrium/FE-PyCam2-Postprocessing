from copyreg import pickle
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

from PMPLib.ImgFileHandling import OTH_BlkFormat, OTH_ImgFormat, OTH_LoadFileTypes, OTH_SaveFileType, OTH_SS_Index
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
# parentDir = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\03 Sample-Sweeps\230307_124953 1kV IMax500nA"
# parentDir = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\02 Alle Zusammen\230306_140339 1kV 250nA #2"
parentDir = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\01 Aktivierung IMax1V\230222_095249 Tip Ch3 (aktiviert)"
# parentDir = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen"
picDir = "Pics"

# saveDir = r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Auswertung\01_11 3x Swp nach Aktivierung 1.4kV@IMax 100nA\230117_112848"
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
opt.PiMage_SkipBadSubdirs = True                                        # If a parent folder is marked as bad measurement, the subdirectories also skipped!y
opt.PiMage_ForceOverride = True                                        # True = Won't check if a measurement is already processed!; False = Checks for already processed and skips in case

# Visualization
opt.ShowImages_Read = False                                             # True = show each image; False = Silent process
opt.ShowImages_Mean = False                                             # True = show each image; False = Silent process
opt.ShowImages_Subtract = False                                         # True = show each image; False = Silent process
opt.ShowImages_SpotDetection = False                                    # True = show each image; False = Silent process
opt.ShowImages_Draw = False                                             # True = show each image; False = Silent process
opt.ShowImages_BrightnessExtraction = False                             # True = show each image; False = Silent process

# Image processing
opt.Image_CropWin = None                                                # None/False or [x, y, w, h]   -   x, y: left upper corner   -   w, h: size of window
opt.Image_bThresh = 50                                                  # Brightness Threshold value (only used, when threshold of autodetect-algorithm is smaller than this one!)
opt.Image_ThreshType = cv.THRESH_OTSU                                   # cv.THRESH_OTSU:                     Tries otsu
                                                                        # cv.ADAPTIVE_THRESH_GAUSSIAN_C:      Adaptive won't work with 16bit
                                                                        # cv.ADAPTIVE_THRESH_MEAN_C:          Adaptive won't work with 16bit
                                                                        # Other else:                         Uses fixed bThres-Value
opt.Image_OtsuDiv = 10                                                  # When TryOtsu is used, a Otsu-Threshhold is build. The returend found threshhold-value is then divided by this number and reused again if its > than Image_bThres!
opt.Image_UseForMeanNPoints = ".swp"                                    # Amount of measurements per swp-line or use ".swp" for auto-find from sweep-file
# opt.Image_MeanNPoints = 2                                               # This was the old value set here. Now its set during the code, but left as comment here (avoid confuses)
opt.Image_MeanNPicsPerSS = 1                                            # Amount of images per Shutterspeed
opt.Image_OverexposedBrightness = 0xFFF0                                # Value at which a pixel is marked as overexposed. See also option "bDetect_Trustband"

# Spot-detection
opt.SpotDetect_Dilate = 10                                              # Dilates bright threshold-image-contours by <uint> pixels to avoid multiple spots due to very small gaps!
opt.SpotDetect_Erode = opt.SpotDetect_Dilate                            # Re-Erodes bright threshold-image-contours by <uint> pixels to avoid multiple spots due to very small gaps!
opt.CircleDetect_pxMinRadius = 5
opt.CircleDetect_pxMaxRadius = 50                                       # Maximum radius for a valid circle:  1 <= r <= pxMaxRadius
opt.CircleDetect_AddPxRadius = False                                    # The maximum radius for a valid circle is False: pxMaxRadius OR True: circle-radius + pxMaxRadius
opt.XYKeys_FollowSpots = True                                           # Follows the related circle-centers (means circle-centroids)

# Spot-Draw on Images
#  Images with drawed circles are saved for use in papers or for gif-creation
opt.CircleDraw_pxRadius = opt.CircleDetect_pxMaxRadius                  # Draw radius for visualization-circle after detection
opt.CircleDraw_AddPxRadius = False                                      # The drawn circle-radius is False: pxRadius OR True: circle-radius + pxRadius

# Brightness-Detection
opt.bDetect_SpotBrightFromAllImgs = True                                # True: The brightness is extracted from ALL images based on the xy-key position!; False: Brightness is only extracted from Images where a circle was detected!
opt.bDetect_pxSideLen = 2 * opt.CircleDetect_pxMaxRadius                # Sidelength of a square around the circle center from which the circle-brightness gets extracted
opt.bDetect_AddPxSideLen = False                                        # The maximum brightness-square is False: pxSidelen OR True: circle-radius + pxSidelen
opt.bDetect_Trustband = [180 *256, 250 *256]                             # Brightness-Trustband of the overexposed image for brightness-factor-calculation (replacement of overexposed pixels) [LoTrust, HiTrust]. See also option "Image_OverexposedBrightness"
opt.bDetect_MinTrust = 50 *256                                           # If: Pixelbrightness < MinTrust -> skips pixels on the replacement-pictures to avoid to high errors and save computation time
# opt.bDetect_SaveImages = True                                           # Attaches the images to each circle! (May need a lot of disk space!)

# XY-Keys
opt.XYKeys_pxCollectRadius = opt.CircleDetect_pxMaxRadius               # Valid radius around a xy-coordinate to collect all related circles (of the different images)
opt.XYKeys_AddPxCollectRadius = True                                    # The collect radius is False: pxCollectRadius OR True: circle-radius + pxCollectRadius
opt.XYKeys_pxCorrectionRadius = opt.XYKeys_pxCollectRadius              # Valid radius tolerance for xy-keys to be assigned to match together

# XY-Key Sorting
opt.XYKeySort_Rowdistance = opt.CircleDetect_pxMaxRadius                # Maximum perpendicular XYKey-distance [px] to be part of a row

# Saving
opt.SaveSSImagePkl = True                                              # Save internal shutterspeed data images
#opt.SaveValidImagePkl = False                                           # Save internal valid brightness images                                    !!!MAYBE OBSOLET!!!
#opt.SaveBrightnessFactors = True                                        # Calculate and save brightness-factors of spots and corresponding pixels  !!!MAYBE OBSOLET!!!
opt.Save_ImgSets4Brightness                 = False                     # Save "Imageset"                             for Brightnesses and it's correction as pickle
opt.Save_BrightSets4Brightness              = True                      # Save "Brightnesses"                         from Imageset as pickle
opt.Save_PxAreaCnts4Brightness              = True                      # Save "PixelArea-Counts & -Factors"          from Imageset as pickle
opt.Save_DivFactors4Brightness              = True                      # Save "Division-Correction-Factors"          from BrightSets as pickle
opt.Save_CombinedFactors4Brightness         = True                      # Save "Combined Factors"                     from DivFactors & PixelAreaCounts as pickle
opt.Save_ScaledAnyPxImgs                    = False                     # Save "Any upscaled pixelcorrected images"   as pickle (huge!)
opt.Save_ScaledAnyBrightnesses              = True                      # Save "Any upscaled spotbrightness"          as pickle
opt.Save_ScaledWhereOverexposedPxImgs       = True                      # Save "Any upscaled spotbrightness images"   as pickle
opt.Save_ScaledWhereOverexposedBrightnesses = True                      # Save "Any upscaled spotbrightness"          as pickle


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
    Shutterspeeds, DetectedFiletype = GrabSSFromFilenames(picsPath, OTH_ImgFormat, OTH_LoadFileTypes, OTH_SS_Index)
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
      # imgs, imgPaths = ReadImages(fPaths=picsPath, Format=str.format(OTH_BlkFormat, "*", SS, "*", DetectedFiletype), CropWindow=opt.Image_CropWin, IgnorePathVector=None, ShowImg=opt.ShowImages_Read)
      # ssData[SS]["Black"]["Cropped"] = imgs
      imgs, imgPaths = ReadImages(fPaths=picsPath, Format=str.format(OTH_ImgFormat, "*", "*", SS, "*", DetectedFiletype), CropWindow=opt.Image_CropWin, IgnorePathVector=None, ShowImg=opt.ShowImages_Read)
      # imgs, imgPaths = ReadImages(fPaths=picsPath, Format=str.format(OTH_ImgFormat, "*", "*", SS, "*", DetectedFiletype), CropWindow=opt.Image_CropWin, IgnorePathVector=imgPaths, ShowImg=opt.ShowImages_Read)
      ssData[SS]["Images"]["Cropped"] = imgs
      LogLineOK()




      LogLine(t0, "Meaning images...")
      # ssData[SS]["Black"]["Mean"] = MeanImages(ImgCollection=ssData[SS]["Black"]["Cropped"], ImgsPerMean=opt.Image_MeanNPicsPerSS, ShowImg=opt.ShowImages_Mean)   # Mean nPicsPerSS together
      ssData[SS]["Images"]["Mean"] = MeanImages(ImgCollection=ssData[SS]["Images"]["Cropped"], ImgsPerMean=opt.Image_MeanNPicsPerSS, ShowImg=opt.ShowImages_Mean) # Mean nPicsPerSS together
      ssData[SS]["Images"]["uint16"] = ssData[SS]["Images"]["Mean"][1:]                                                                                             # Remove the "init-datapoint" directly after measurement start
      if opt.Image_MeanNPoints > 1:
        ssData[SS]["Images"]["Mean"] = MeanImages(ImgCollection=ssData[SS]["Images"]["Mean"], ImgsPerMean=opt.Image_MeanNPoints, ShowImg=opt.ShowImages_Mean)     # Meaning measurement points together
      LogLineOK()
      # Cleanup old ressources
      LogLine(t0, "Cleanup cropped (f64) images...")
      # ssData[SS]["Black"] .pop("Cropped")
      ssData[SS]["Images"].pop("Cropped")
      ssData[SS]["Images"].pop("Mean")
      LogLineOK()




      # LogLine(t0, "Subtract darkfield image...")
      # ssData[SS]["Images"]["uint16"] = SubtractDarkfield(ImgCollection=ssData[SS]["Images"]["Mean"], DarkfieldImage=ssData[SS]["Black"]["Mean"][0], ShowImg=opt.ShowImages_Subtract)
      # LogLineOK()
      # # Cleanup old ressources
      # LogLine(t0, "Cleanup darkfield (f64) & mean (f64) images...")
      # ssData[SS].pop("Black") # Black image not used anymore
      # ssData[SS]["Images"].pop("Mean")
      # LogLineOK()


      if SS == Shutterspeeds[0]:
        LogLine(t0, "Saving uint16-images...")
        SaveImageCollection(ImgCollection=ssData[SS]["Images"]["uint16"], FileFormat=str.format(OTH_ImgFormat, "Dev101", "{:05d}", SS, "uint16", OTH_SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("uint16 SS={}", SS)))
        LogLineOK()


      # LogLine(t0, "Convert images to uint8...")
      # # ssData[SS]["Images"]["uint8"] = ConvertImgCollectionDataType(ImgCollection=ssData[SS]["Images"]["uint16"], DataType=np.uint8)
      # ssData[SS]["Images"]["uint8"] = ConvertBitsPerPixel(OriImgCollection=ssData[SS]["Images"]["uint16"], originBPP=16, targetBPP=8)
      # LogLineOK()
      # LogLine(t0, "Saving uint8-images...")
      # SaveImageCollection(ImgCollection=ssData[SS]["Images"]["uint8"], FileFormat=str.format(OTH_ImgFormat, "Dev101", "{:05d}", SS, "uint8", OTH_SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("uint8 SS={}", SS)))
      # LogLineOK()

      # Cleanup old ressources
      # LogLine(t0, "Cleanup uint8 save-collection...")
      # ssData[SS]["Images"].pop("uint8")
      # LogLineOK()





      LogLine(t0, "Creating threshold-images...")
      ssData[SS]["Images"]["Threshold"] = BuildThreshold(ImgCollection=ssData[SS]["Images"]["uint16"], Threshold=opt.Image_bThresh, ThreshType=opt.Image_ThreshType, OtsuDiv=opt.Image_OtsuDiv, OverexposedValue=opt.Image_OverexposedBrightness)
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
        SaveImageCollection(ImgCollection=ssData[SS]["Images"]["CircleDetection"], FileFormat=str.format(OTH_ImgFormat, "Dev101", "{:05d}", SS, "CircleDetection", OTH_SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("CircleDetection SS={}", SS)))
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
      ssData[SS]["Images"]["DrawedCircles"] = CircleDraw(ImgCollection=drawImgs, CircleCollection=circles, pxRadius=opt.CircleDraw_pxRadius, AddPxRadius=opt.CircleDetect_AddPxRadius, ShowImg=opt.ShowImages_Draw)
      del drawImgs
      if SS == Shutterspeeds[0]:
        SaveImageCollection(ImgCollection=ssData[SS]["Images"]["DrawedCircles"], FileFormat=str.format(OTH_ImgFormat, "Dev101", "{:05d}", SS, "DrawnCircles", OTH_SaveFileType), SaveDir=os.path.join(cSaveDir, str.format("DrawnCircles SS={}", SS)))
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
    # ssData, bData, bImages = ExtractBrightnessData(ssData=ssData, ImgKey="uint8", pxSidelen=opt.bDetect_pxSideLen, AddPxSidelen=opt.bDetect_AddPxSideLen, TrustbandBrightness=opt.bDetect_Trustband, TrustBrightnessMin=opt.bDetect_MinTrust, ShowImg=opt.ShowImages_BrightnessExtraction)

    # !!! CURRENTLY FOR TEST PURPOSES A VERY UNCLEAN WAY TO CONVERT THE 8BIT-SETTINGS INTO 16BIT SETTINGS !!!
    # Image_OverexposedBrightness_16Bit = (opt.Image_OverexposedBrightness) * 256
    # bDetect_Trustband_16Bit = [(trustVal + 1) * 256 - 1 for trustVal in opt.bDetect_Trustband]
    # bDetect_MinTrust_16Bit = (opt.bDetect_MinTrust) * 256
    Image_OverexposedBrightness_16Bit = opt.Image_OverexposedBrightness # Rewrote code that it handles 16bit already
    bDetect_Trustband_16Bit = opt.bDetect_Trustband                     # Rewrote code that it handles 16bit already
    bDetect_MinTrust_16Bit = opt.bDetect_MinTrust                       # Rewrote code that it handles 16bit already
    Image_MinBright2CountArea = 1* 0xFF

    ssData,                        \
    imgSets,                       \
    brightSets,                    \
    areaCntSets,                   \
    divFactors,                    \
    combinedFactors,               \
    scaledAnyBright,               \
    scaledAnyPxImgs,               \
    scaledWhereOverexposedBright,  \
    scaledWhereOverexposedImgs = DataExtractionAndUpscaling(ssData=ssData,
                                                            ImgKey="uint16",
                                                            pxSidelen=opt.bDetect_pxSideLen,
                                                            AddPxSidelen=opt.bDetect_AddPxSideLen,
                                                            TakeSpotBrightFromAllImgs=opt.bDetect_SpotBrightFromAllImgs,
                                                            PxDivTrustband=bDetect_Trustband_16Bit,
                                                            PxDivMinBright=bDetect_MinTrust_16Bit,
                                                            MinBright=Image_MinBright2CountArea,
                                                            OverexposedValue=Image_OverexposedBrightness_16Bit,
                                                            # PxDivTrustband=opt.bDetect_Trustband,             # Old 8-bit calls -> Clean re-implementation when it works
                                                            # PxDivMinBright=opt.bDetect_MinTrust,              # Old 8-bit calls -> Clean re-implementation when it works
                                                            # OverexposedValue=opt.Image_OverexposedBrightness, # Old 8-bit calls -> Clean re-implementation when it works
                                                            ShowImg=opt.ShowImages_BrightnessExtraction)

    LogLineOK()


    # print("")
    # LogLine(t0, "Create xy-plot data from valid exposed xy-keys...")
    # bData = CreateImagePlotXY(ValidData=bData)
    # LogLineOK()



    # if opt.SaveBrightnessFactors == True: # Calculate brighntess-factors of spots/pixels
    #   print("")
    #   LogLine(t0, "Generating brightness-factors...")
    #   brightFactorData = CalculateAllSpotpixelFactors(ssData=ssData, imgKey="uint8", pxSidelen=opt.bDetect_pxSideLen, AddPxSidelen=opt.bDetect_AddPxSideLen)
    #   LogLineOK()



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


    if opt.Save_CombinedFactors4Brightness == True:
      _fName = "PMP_CombinedFactors4Brightness.pkl"
      _fPath = os.path.join(cSaveDir, _fName)
      _fHandle = open(_fPath, "wb")
      pickle.dump(combinedFactors, _fHandle)
      _fHandle.close()
      del combinedFactors      # Remove to clear RAM
      LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")
    else:
      del combinedFactors # When not saving them , just delete them to free the RAM

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


    # if opt.bDetect_SaveImages == True:
    #   _fName = "PMP_correctedImages.pkl"
    #   _fPath = os.path.join(cSaveDir, _fName)
    #   _fHandle = open(_fPath, "wb")
    #   pickle.dump(bImages, _fHandle)
    #   _fHandle.close()
    #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")

    # if opt.SaveValidImagePkl == True:
    #   _fName = "PMP_validImgData.pkl"
    #   _fPath = os.path.join(cSaveDir, _fName)
    #   _fHandle = open(_fPath, "wb")
    #   pickle.dump(bData["Images"], _fHandle)
    #   _fHandle.close()
    #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")


    # if opt.SaveBrightnessFactors == True: # Save brightness-factors of spots/pixels
    #   _fName = "PMP_brightFactors.pkl"
    #   _fPath = os.path.join(cSaveDir, _fName)
    #   _fHandle = open(_fPath, "wb")
    #   pickle.dump(brightFactorData, _fHandle)
    #   _fHandle.close()
    #   LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")


    # bData.pop("Images")                                           # Remove images from valid data! If wanted, they are saved from the block above!
    # _fName = "PMP_validSpotData.pkl"
    # _fPath = os.path.join(cSaveDir, _fName)
    # _fHandle = open(_fPath, "wb")
    # pickle.dump(bData, _fHandle)
    # _fHandle.close()
    # LogLine(None, whiteMessage=str.format(" - Saved: {}", _fName), end="\n")


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


