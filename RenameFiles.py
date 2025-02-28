##################################################################################
# This script can be used, to rename files from ReadFormat into ConvertFormat.   #
# It scans the given input-folder for the type given by ReadFormat and converts  #
# the filename into ConvertFormat into the OutDir-folder.
#                                                                                #
# How to use (variable explanation):                                             #
# wds:              contains a list of paths which is scanned for files with the #
#                    srcExtension                                                #
# srcExtension:     wds are searched for ending with this string                 #
# dstExtension:     The files srcExtension gets replaced with this string        #
# SkipBadSubdirs:   If this is enabled, the subfolders of any _XX marked parent  #
#                    are skipped in addition.                                    #
#                                                                                #
# Version: 1.0.0.0                                                               #
# 2025 © haum (OTH-Regensburg)                                                   #
##################################################################################

import os
import parse
import shutil



ReadFormat = "{}_rPiHQCam-{}_ss={}_{}.jpg"
ConvertFormat = "LT{:08d}_ss={:09d}_{:03d}"


ImgDir = r"<Drive>\<Input Pics folderpath here>"
OutDir = r"<Drive>\<Output Pics folderpath here>",
if not os.path.exists(OutDir):
  os.makedirs(OutDir)

fList = os.listdir(ImgDir)
outFNames = list()


for file in fList:
    if not file.endswith(os.path.splitext(ReadFormat)[1]): # Be sure only scanning filetype of interest! Sometimes a 0kb tar.gz can be within the pictures
      print("Non-matching filetype detected: " + file)
      fList.remove(file)
    else:
      _parsed = parse.parse(ReadFormat, file)
      _nums = list()
      for _iPrsd in range(1, len(_parsed.fixed)):
        _nums.append(int(_parsed[_iPrsd]))
      outFNames.append(str.format(ConvertFormat + ".jpg", _nums[0], _nums[1], _nums[2]))

for _iFile in range(len(fList)):
  src = os.path.join(ImgDir, fList[_iFile])
  dst = os.path.join(OutDir, outFNames[_iFile])
  shutil.copy(src, dst)