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
# ### Before Cam-Change!
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_185118 Tip Ch1",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_193753 Tip Ch2",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_202712 Tip Ch3",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230408_114847 Tip Ch4",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_131817 Tip1-4 1kV 250nA (Reg. for Tip-Quality)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_143425 Tip1, 3 700V (Sat)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_150043 Tip1, 3 600V (UnSat)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_152323 Tip2, 4 400V (Sat)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_154730 Tip1, 4 400V (UnSat)",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_112532 800V T1-4=2.5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_120802 800V T1-4=0",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_124826 800V T1,4=2.5, T2,3=0",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_133017 800V T1,3=2.5, T2,4=0",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_152121 300V T1-4=5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_153855 500V T1-4=5",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230411_161431 850V T1=2.5, T2-4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230411_170007 600V T1=5, T2-4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230411_173651 850V T2=2.5, T1,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_095047 300V T2=2.5, T1,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_104129 850V T3=2.5, T1,2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_112600 550V T3=2.5, T1,2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_120205 850V T4=2.5, T1,2,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_121044 275V T4=2.5, T1,2,3=f",

# ### After Cam-Change
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230414_142228 850V T1=2.5, T2,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230414_162436 850V T2=2.5, T1,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230414_171309 1kV T3=2.5, T1,2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230416_113420 1kV T4=2.5, T1,2,3=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_124224 850V T1-4=2.5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_130710 650V T1-4=2.5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_132804 600V T1-4=2.5",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_140248 850V T2,3,4=2.5, T1=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_143702 650V T2,3,4=5, T1=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_151519 850V T2,4=2.5, T1,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_153805 650V T2,4=5, T1,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_155756 575V T2,4=5, T1,3=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_164211 850V T2,3=2.5, T1,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_091311 650V T2,3=5, T1,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_093726 650V T2,3=5, T1,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_100014 650V T2,3=5, T1,4=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_103529 850V T3,4=2.5, T1,2=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_111937 600V T3,4=5, T1,2=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_120247 850V T1,2=2.5, T3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_124704 650V T1,2=5, T3,4=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_132015 850V T1,3=2.5, T2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_140546 550V T1,3=5, T2,4=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_154117 550V T1,4=2.5, T2,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_163540 550V T1,4=2.5, T2,3=f",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230417_171941 850V T1-4=2.5",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230417_174418 700V T1-4=1",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230418_085317 850V T1-4=2.5",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_094854 450V T1=2.5, T2,3,4=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_101154 450V T1=5, T2,3,4=gnd",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_104503 850V T2=2.5, T1,3,4=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_112114 950V T2=5, T1,3,4=gnd",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_115301 750V T3=2.5, T1,2,4=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_121938 750V T3=5, T1,2,4=gnd",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_124726 650V T4=2.5, T1,2,3=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_131423 650V T4=5, T1,2,3=gnd",
]
picDir = "Pics"
skipBadSubDir = True

# imgWin = [x, y, w, h] -     x, y = Left upper cornder; w(idth), h(eight)
# imgWin = [1730, 1237, 550, 550]  # r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\_alte Cam (KS-Test + Aktivierung ok)_XX"
# imgWin = [415, 573, 700, 700]  # r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen"

# PyCam2 Paper measurements!
# imgWin = [299, 713, 650, 650]   # r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen" !!!! Before Cam-Change !!!!
imgWin = [399, 690, 650, 650]      # r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen" !!!! After Cam-Chane !!!!





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