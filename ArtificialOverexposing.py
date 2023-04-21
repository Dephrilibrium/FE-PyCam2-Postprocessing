import os
import time

import cv2 as cv
import numpy as np
from matplotlib import pyplot
import natsort
import shutil

from FieldEmission import ReadSweepFile
from FieldEmission import DataProvider

from PMPLib.ImgFileHandling import OTH_BlkFormat, OTH_ImgFormat, OTH_SS_Index
from PMPLib.ImgFileHandling import ExtractShutterspeedsAndFiletypeFromFilenames
from PMPLib.ImgFileHandling import ReadImages
from PMPLib.ImgFileHandling import SaveImageCollection

from misc import bcolors
from misc import DiffTime
from misc import DiffToNow
from misc import Time2Human
from misc import Logger
from misc import LogLine
from misc import LogLineOK


from _PiMageOptions import PiMageOptions



# # Test imread and imwrite
# fJpg     = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Messungen\03 1h I500nA U1400V\220804_161157 (#1)\Pics\Dev101_rPiHQCam-0000_ss=1000_0000.jpg"
# fPath50  = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Messungen\03 1h I500nA U1400V\test50.raw"
# fPath75  = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Messungen\03 1h I500nA U1400V\test75.raw"
# fPath95  = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Messungen\03 1h I500nA U1400V\test95.raw"
# fPath100 = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Messungen\03 1h I500nA U1400V\test100.raw"
# pic = np.zeros((5, 5, 3)).astype(np.uint8)
# # pic = img = np.random.randint(255, size=(5, 5, 3))
# pic[2, 0:4, 0] = 0      # B
# pic[2, 0:4, 1] = 255    # G
# pic[2, 0:4, 2] = 0      # R
# # cv.imwrite(fPath50 , pic, [cv.IMWRITE_JPEG_QUALITY, 50 ])
# # cv.imwrite(fPath75 , pic, [cv.IMWRITE_JPEG_QUALITY, 75 ])
# # cv.imwrite(fPath95 , pic, [cv.IMWRITE_JPEG_QUALITY, 95 ])
# # cv.imwrite(fPath100, pic, [cv.IMWRITE_JPEG_QUALITY, 100])
# cv.imwrite(fPath50 , pic)
# cv.imwrite(fPath75 , pic)
# cv.imwrite(fPath95 , pic)
# cv.imwrite(fPath100, pic)

# rJpg    = cv.imread(fJpg)
# read50  = cv.imread(fPath50 )
# read75  = cv.imread(fPath75 )
# read95  = cv.imread(fPath95 )
# read100 = cv.imread(fPath100)




parentDir = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Messungen"
# parentDir = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Messungen\220725 PiCam Einzelemitter"
# parentDir = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Messungen\221025 CCD mit WCam"
picDir = "Pics"
allowedImgTypes = ["jpg", "png"]
skipBadSubDir = True
# factors = [1.1, 1.25, 1.5, 1.75, 2]
factors = [1.3, 1.5, 1.8, 2]
# factor = 2      # Multiply all pixels 
ovrExpValue = 255

AOMarker = "AO"


# # Test of artificial overexposing -> Working
# intMat = [
#   [ 64, 128,  64],
#   [128, 254, 128],
#   [ 64, 128,  64],
#   ]
# intMat = np.multiply(intMat, factor)
# intMat[intMat > ovrExpValue] = ovrExpValue
# intMat = intMat.astype(np.uint8)

t0 = time.time()
LogLine(t0, "Starting", bcolors.BOLD + "----- Artificial Overexpose -----" + bcolors.ENDC, yFill=15, wFill=0, end="\n")
LogLine(t0, "Toolname:", "Subtool of Raspberry " + bcolors.OKBLUE + "Pi" + bcolors.ENDC + "-i" + bcolors.OKBLUE + "Mage Pro"+ bcolors.ENDC + "cessor", yFill=15, wFill=30, end="\n")
LogLine(t0, "Programmer:", "haum", yFill=15, wFill=30, end="\n")
LogLine(t0, "Affiliation:", "OTH-Regensburg", yFill=15, wFill=30, end="\n")
LogLine(t0, "Year:", "2022", yFill=15, wFill=30, end="\n")

_XXBadDirs = list()
for root, dirs, files in os.walk(parentDir):
  # Firstly check if path contains one of the already marked bad measurement-folders
  if any(root.__contains__(_bDir) for _bDir in _XXBadDirs):
    LogLine(None, "Bad parent - skipped: ", root, wFill=0, end="\n")
    continue
  # Folder marked as bad measurement -> Skip
  if root.endswith("_XX"):
    if skipBadSubDir == True:
      _XXBadDirs.append(root)
    LogLine(None, "Marked as bad - skipped: ", root, wFill=0, end="\n")
    continue

  if root.endswith(AOMarker):
    if skipBadSubDir == True:
      _XXBadDirs.append(root)
    LogLine(None, "Skipping AO-Folder: ", root, wFill=0, end="\n")
    continue

  print("")
  LogLine(None, "Entering: ", root, wFill=0, end="\n")

  #Check if current directory contains measurement-files
  #  Directory found when it contains a Pics directory and *.dat files
  if not dirs.__contains__(picDir) or not any(f.endswith(".dat") for f in files):
    LogLine(None, "Nothing interesting here...", wFill=0, end="\n")
    continue
  else:
    LogLine(t0, "Possible directory found: ", root, end="\n")

  for factor in factors:
    AOEnding = "_" + str.format("{:+03.1f}%", (factor-1) * 100) + AOMarker
    loadPicDir = os.path.join(root, picDir)
    saveDir = root + AOEnding
    savePicDir = os.path.join(saveDir, picDir)

    if not os.path.exists(savePicDir):
      LogLine(t0, "Created Savedirectory: ", savePicDir, wFill=0, end="\n")
      os.makedirs(savePicDir)

    LogLine(t0, "Copying FEMDAQ data...")
    for file in files:
      if any(file.endswith(ext) for ext in [".png", ".dat", ".swp", ".resistor"]):
        shutil.copy2(os.path.join(root, file), saveDir)
    LogLineOK()

    picFiles = os.listdir(loadPicDir)
    picFiles = natsort.natsorted(picFiles, alg=natsort.ns.IGNORECASE) # Be sure that all pictures sorted correctly!
    scaleFac = str.format("{:+03.1f}%", (factor-1) * 100)
    for pFile in picFiles:
      if not any(pFile.endswith(ext) for ext in allowedImgTypes):
        continue

      lPath = os.path.join(loadPicDir, pFile)
      sPath = os.path.join(savePicDir, pFile)
      sPath = sPath.replace(".jpg", ".png")
      
      LogLine(None, yellowMsg=pFile, whiteMessage="Load RGB-Image", yFill=50, wFill=0, end="")
      img = cv.imread(lPath, cv.IMREAD_GRAYSCALE)
      # img = cv.imread(lPath)
      LogLine(-1, whiteMessage="-> Scale RGB by " + scaleFac, yFill=0, wFill=0, end="")
      # img[img <= 1] = 0
      img = np.multiply(img, factor)
      LogLine(-1, whiteMessage="-> Clip RGB @255", yFill=0, wFill=0, end="")
      img[img > ovrExpValue] = ovrExpValue
      img = img.astype(np.uint8)
      # Override the image!
      LogLine(-1, whiteMessage="-> Saving RGB-Image", yFill=0, wFill=25, end="")

      cv.imwrite(sPath, img)
      LogLineOK()


print("\n")
LogLine(t0, "Finished", bcolors.BOLD + "----- Artificial Overexpose -----" + bcolors.ENDC, yFill=15, wFill=0, end="\n")