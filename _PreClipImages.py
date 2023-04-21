import os
import time

import cv2 as cv
import numpy as np
from matplotlib import pyplot
import natsort
import shutil


from misc import bcolors
from misc import DiffTime
from misc import DiffToNow
from misc import Time2Human
from misc import Logger
from misc import LogLine
from misc import LogLineOK


parentDirs = [
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_185118 Tip Ch1",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_193753 Tip Ch2",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_202712 Tip Ch3",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230408_114847 Tip Ch4",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_131817 Tip1-4 1kV 250nA (Reg. for Tip-Quality)",
]
picDir = "Pics"
skipBadSubDir = True

# imgWin = [x, y, w, h] -     x, y = Left upper cornder; w(idth), h(eight)
# imgWin = [1730, 1237, 550, 550]  # r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\_alte Cam (KS-Test + Aktivierung ok)_XX"
# imgWin = [415, 573, 700, 700]  # r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen"
imgWin = [286, 693, 700, 700]  # r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen"





t0 = time.time()
LogLine(t0, "Starting", bcolors.BOLD + "----- PreClipImages -----" + bcolors.ENDC, yFill=15, wFill=0, end="\n")
LogLine(t0, "Toolname:", "Subtool of Raspberry " + bcolors.OKBLUE + "Pi" + bcolors.ENDC + "-i" + bcolors.OKBLUE + "Mage Pro"+ bcolors.ENDC + "cessor", yFill=15, wFill=30, end="\n")
LogLine(t0, "Programmer:", "haum", yFill=15, wFill=30, end="\n")
LogLine(t0, "Affiliation:", "OTH-Regensburg", yFill=15, wFill=30, end="\n")
LogLine(t0, "Year:", "2022", yFill=15, wFill=30, end="\n")


x = imgWin[0]
y = imgWin[1]
w = imgWin[2]
h = imgWin[3]



_XXBadDirs = list()
for parentDir in parentDirs:
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

    if root.endswith("AO"):
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

    loadPicDir = os.path.join(root, picDir)
    savePicDir = loadPicDir

    # if not os.path.exists(savePicDir):
    #   LogLine(t0, "Created Savedirectory: ", savePicDir, wFill=0, end="\n")
    #   os.makedirs(savePicDir)

    # LogLine(t0, "Copying FEMDAQ data...")
    # for file in files:
    #   if any(file.endswith(ext) for ext in [".png", ".dat", ".swp", ".resistor"]):
    #     shutil.copy2(os.path.join(root, file), saveDir)
    # LogLineOK()

    picFiles = os.listdir(loadPicDir)
    picFiles = natsort.natsorted(picFiles, alg=natsort.ns.IGNORECASE) # Be sure that all pictures sorted correctly!
    # scaleFac = str.format("{:+03.1f}%", (factor-1) * 100)
    fileIsJPG = False
    for pFile in picFiles:
      if pFile.endswith(".jpg"):
        fileIsJPG = True
      elif pFile.endswith(".png"):
        fileIsJPG = False
      else:
        continue

      lPath = os.path.join(loadPicDir, pFile)
      sPath = lPath
      if fileIsJPG:
        sPath = sPath.replace(".jpg", ".png")

      LogLine(None, yellowMsg=pFile, whiteMessage="Processing Image    ", yFill=50, wFill=0, end="\r")
      # LogLine(None, yellowMsg=pFile, whiteMessage="Load RGB-Image", yFill=50, wFill=0, end="")
      # img = cv.imread(lPath)
      img = cv.imread(lPath, cv.IMREAD_ANYDEPTH | cv.IMREAD_GRAYSCALE)

      # LogLine(-1, whiteMessage="-> Clipping image", yFill=0, wFill=0, end="")
      img = img[y:y+h, x:x+w]

      # Override the image!
      # LogLine(-1, whiteMessage="-> Saving RGB.png", yFill=0, wFill=0, end="")
      cv.imwrite(sPath, img)

      # LogLine(-1, whiteMessage="-> Delete old RGB.jpg", yFill=0, wFill=25, end="")
      if fileIsJPG:
        os.remove(lPath) # Do not remove. PNG already overwrites PNG
    LogLineOK()

  print("\n")

LogLine(t0, "Finished", bcolors.BOLD + "----- PreClipImages -----" + bcolors.ENDC, yFill=15, wFill=0, end="\n")