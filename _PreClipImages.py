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
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\01 Aktivierung IMax1V\230221_115432 Tip Ch1 (aktiviert, 6517)",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\01 Aktivierung IMax1V\230221_124600 Tip Ch2 (aktiviert)",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\01 Aktivierung IMax1V\230222_095249 Tip Ch3 (aktiviert)",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\01 Aktivierung IMax1V\230222_103240 Tip Ch4 (aktiviert)",

# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\02 Alle Zusammen\230222_160417 1kV 100nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\02 Alle Zusammen\230223_084426 1kV 250nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\02 Alle Zusammen\230306_124505 1kV 250nA #1",
r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\02 Alle Zusammen\230306_140339 1kV 250nA #2",

# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\03 Sample-Sweeps\230307_124953 1kV IMax500nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\03 Sample-Sweeps\230308_085027 1kV IMax 250nA",

# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\04 USwp für bessere Charakteristik\230308_133039",

# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_143559 USwp 1kV, IMax250nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_151018 ZickZack 1by1 linStps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_154416 ZickZack 1by1 linStps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_164837 USwp 1kV, IMax250nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_172255 ZickZack 1by1 log10Stps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_175658 ZickZack 1by1 log10Stps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_190251 USwp 1kV, IMax250nA",

# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_200641 USwp 1kV, IMax250nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_202958 ZickZack 1while1 linStps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_205330 ZickZack 1while1 linStps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_215722 USwp 1kV, IMax250nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_222134 ZickZack 1by1 log10Stps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_224524 ZickZack 1by1 log10Stps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_234915 USwp 1kV, IMax250nA",
]
picDir = "Pics"
skipBadSubDir = True

# imgWin = [x, y, w, h] -     x, y = Left upper cornder; w(idth), h(eight)
# imgWin = [1730, 1237, 550, 550]  # r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\_alte Cam (KS-Test + Aktivierung ok)_XX"
imgWin = [415,573,700,700]  # r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen"





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