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


picFiles = [
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0100_0000.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0100_0001.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0100_0002.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0100_0003.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0333_0000.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0333_0001.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0333_0002.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0333_0003.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0666_0000.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0666_0001.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0666_0002.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=0666_0003.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=1000_0000.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=1000_0001.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=1000_0002.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=1000_0003.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=3333_0000.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=3333_0001.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=3333_0002.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=3333_0003.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=6666_0000.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=6666_0001.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=6666_0002.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=6666_0003.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=10000_0000.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=10000_0001.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=10000_0002.png",
r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Messungen\02_01 Finding SS without CamDamage\230124_120049\Pics\Dev101_HQCam-BlackSubtraction_ss=10000_0003.png",
]





for pFile in picFiles:
  if not pFile.endswith(".png"):
    continue

  LogLine(None, yellowMsg=pFile, whiteMessage="Processing Image    ", yFill=50, wFill=0, end="")
  # LogLine(None, yellowMsg=pFile, whiteMessage="Load RGB-Image", yFill=50, wFill=0, end="")
  # img = cv.imread(lPath)
  img = cv.imread(pFile, cv.IMREAD_GRAYSCALE)

  # LogLine(-1, whiteMessage="-> Clipping image", yFill=0, wFill=0, end="")
  img[:] = 0

  # Override the image!
  # LogLine(-1, whiteMessage="-> Saving RGB.png", yFill=0, wFill=0, end="")
  cv.imwrite(pFile, img)

  LogLineOK()


print("\n")
print("Finished")