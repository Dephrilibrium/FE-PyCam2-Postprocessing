##################################################################################
# This script is used to clip the reconverted 16bit grayscale PNGs to the area   #
# of interest. This can greatly reduce the consumed time for the data-extraction #
# of the images.                                                                 #
#                                                                                #
# How to use (variable explanation):                                             #
# parentDir:        This folder is scanned recursevly for possible candidates of #
#                    a possible measurement-folder.                              #
# picDir:           Name of the subfolder where the PyCam2 pictures are stored   #
#                    in.                                                         #
# clipInBayerSpace: Support was added for preclipping not only images, but also  #
#                    the ".raw" pickle files in bayer-space.                     #
# SkipBadSubdirs:   If this is enabled, the subfolders of any _XX marked parent  #
#                    are skipped in addition.                                    #
# imgWin:           Is used to define the area of interest:                      #
#                    1.) [w, h]:       Defines width and height of the image     #
#                                      around the image center                   #
#                    1.) [x, y, w, h]: Defines the left upper corner (x, y) and  #
#                                      the image size (width, height).           #
#                    Note: The imgWin is ALWAYS the direct indicies at which the #
#                          images/raw are clipped!
#                                                                                #
# 2023 © haum (OTH-Regensburg)                                                   #
##################################################################################

import os
import time

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import natsort
import shutil
import pickle


from misc import bcolors
from misc import DiffTime
from misc import DiffToNow
from misc import Time2Human
from misc import Logger
from misc import LogLine
from misc import LogLineOK


parentDirs = [
# 21x21
r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\05_01 10k, AutoSS",
]
picDir = "Pics"
skipBadSubDir = True


### Clip-Window
## Note:
#  When clipping in bayer-space, only the x-direction is encoded in Bayer-Pattern.
#  x and w therefore, needs to be multiplied by 1.5 (= 12bit / 8bit)
#  Thereby, only even values are allowed !!! EXCEPT !!!, when you need to re-align the RAW-pickles
#
#  When clipping an already demosaicked image, there are no such limitations, as there is no index-scaling necessary
#
## Coordinates of the left upper corner (startpoint)
x = int(2)
y = int(0)

## Size of the image in pixels
w = int(2798 * 1.5)     # Image Width (use -*1.5 for bayer-space)
h = int(2798)           # Image Height





t0 = time.time()
LogLine(t0, "Starting", bcolors.BOLD + "----- PreClipImages -----" + bcolors.ENDC, yFill=15, wFill=0, end="\n")
LogLine(t0, "Toolname:", "Subtool of Raspberry " + bcolors.OKBLUE + "Pi" + bcolors.ENDC + "-i" + bcolors.OKBLUE + "Mage Pro"+ bcolors.ENDC + "cessor", yFill=15, wFill=30, end="\n")
LogLine(t0, "Programmer:", "haum", yFill=15, wFill=30, end="\n")
LogLine(t0, "Affiliation:", "OTH-Regensburg", yFill=15, wFill=30, end="\n")
LogLine(t0, "Year:", "2022", yFill=15, wFill=30, end="\n")


_XXBadDirs = list()
for parentDir in parentDirs: # Iterate through parentDirs
  for root, dirs, files in os.walk(parentDir): # Iterate recursively through the parentDirs
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

    picFiles = os.listdir(loadPicDir)
    picFiles = natsort.natsorted(picFiles, alg=natsort.ns.IGNORECASE) # Be sure that all pictures sorted correctly!
    fileIsType = ".png" # by default, png ist assumed
    for _iFile in range(len(picFiles)):
      pFile = picFiles[_iFile]
      if pFile.endswith(".jpg"):
        fileIsType = ".jpg"
      elif pFile.endswith(".raw"):
        fileIsType = ".raw"
      else:
        continue

      lPath = os.path.join(loadPicDir, pFile)
      sPath = lPath
      if fileIsType == ".jpg": # JPGs are converted into PNGs
        sPath = sPath.replace(".jpg", ".png")
      # else: # It's a raw or png (sPath = sPath)
      #   sPath = sPath.replace(".raw", ".raw")

      LogLine(None, yellowMsg=pFile, whiteMessage="Processing Image    ", yFill=50, wFill=0, end="\r")
      if fileIsType == ".jpg" or fileIsType == ".png":
        img = cv.imread(lPath, cv.IMREAD_ANYDEPTH | cv.IMREAD_GRAYSCALE)  # Load image
        img = img[y:y+h, x:x+w]                                           # Clip image
        # Override the image!
        cv.imwrite(sPath, img)
      else: # It's a .raw --> Clip in bayer-space
        # Load in RAW-pickle
        fImg = open(lPath, "rb")
        img = pickle.load(fImg)
        fImg.close()

        img = img[y:y+h, x:x+w] # Actual clip

        # Store back
        fImg = open(lPath, "wb")
        pickle.dump(img, fImg)
        fImg.close()


      if fileIsType == ".jpg":
        os.remove(lPath) # Do not remove. PNG and RAW overwrites itself
    LogLineOK()

  print("\n")

LogLine(t0, "Finished", bcolors.BOLD + "----- PreClipImages -----" + bcolors.ENDC, yFill=15, wFill=0, end="\n")