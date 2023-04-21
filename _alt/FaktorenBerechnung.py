import os
from math import atan2, pi, inf, nan, isnan
from typing import Dict
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import pickle

from misc import bcolors





from _ImageSpotProcessing import __BrightnessFactors_GetBrightSets__
from _ImageSpotProcessing import __BrightnessFactors_GetPxAreaCnt__
from _ImageSpotProcessing import __BrightnessFactors_BuildDivFactors__
from _ImageSpotProcessing import __BrightnessFactors_BuildCombinedFactors__
from _ImageSpotProcessing import __BrightUpscale_Any__
from _ImageSpotProcessing import __BrightUpscale_WhereOverexposed__


# # Test for boolean matrix-combination
a = np.array([True] * 9)
a = a.reshape((3,3))
a[1,2] = False
b = np.array([False] * 9)
b = b.reshape((3,3))
b[1,2] = True
b[2,2] = True

c = a & b



## Test how pickles behave!
# x1 = 218
# y1 = 190
# x2 = x1 + 200
# y2 = y1 + 200

# img = dict()
# img["raw"] = list()
# img["prt"] = list()

# img["raw"].append(cv.imread(r"C:\Users\ham38517\Downloads\PiCam\220725 PiCam Einzelemitter\Messungen\05 1h I2uA U1400V (ab hier 1Meg)\220805_174743 (#1)\Pics\Dev101_rPiHQCam-0121_ss=100000_0000.jpg", cv.IMREAD_GRAYSCALE))
# img["prt"].append(img["raw"][-1][x1:x2, y1:y2])
# img["raw"].append(cv.imread(r"C:\Users\ham38517\Downloads\PiCam\220725 PiCam Einzelemitter\Messungen\05 1h I2uA U1400V (ab hier 1Meg)\220805_174743 (#1)\Pics\Dev101_rPiHQCam-0121_ss=100000_0001.jpg", cv.IMREAD_GRAYSCALE))
# img["prt"].append(img["raw"][-1][x1:x2, y1:y2])


# f = open(r"C:\Users\ham38517\Downloads\test.pkl", "wb")
# pickle.dump(img, f)
# f.close()

# f = open(r"C:\Users\ham38517\Downloads\test.pkl", "rb")
# img2 = pickle.load(f)
# f.close()

# img ["raw"][1][img["raw"][1] > 50] = 0
# img2["raw"][1][img["raw"][1] > 50] = 0




_folder = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Ausw\220725 PiCam Einzelemitter\03 1h I500nA U1400V\220804_161157 (#1)_+10.0%AO"

_fPath = r"PMP_ImgSets4Brightness.pkl"
_fHandle = open(os.path.join(_folder, _fPath), "rb")
imgSets = pickle.load(_fHandle)
_fHandle.close()

# _fPath = r"PMP_BrightSets4Brightness.pkl"
# _fHandle = open(os.path.join(_folder, _fPath), "rb")
# brightSets = pickle.load(_fHandle)
# _fHandle.close()

# _fPath = r"PMP_PxAreaCnts4Brightness.pkl"
# _fHandle = open(os.path.join(_folder, _fPath), "rb")
# areaCntSets = pickle.load(_fHandle)
# _fHandle.close()

# _fPath = r"PMP_DivFactors4Brightness.pkl"
# _fHandle = open(os.path.join(_folder, _fPath), "rb")
# divFactors = pickle.load(_fHandle)
# _fHandle.close()

# _fPath = r"PMP_CombinedFactors4Brightness.pkl"
# _fHandle = open(os.path.join(_folder, _fPath), "rb")
# combinedFactors = pickle.load(_fHandle)
# _fHandle.close()


# _bKey = 100000
# _dKey = 10000
# fImgs = imgSets[_bKey]["FullImgs"]
# for _iImg in range(len(fImgs["Blank"])):
#   cv.imshow("Blank", fImgs["Blank"][_iImg])
#   cv.imshow("Clean", fImgs["Clean"][_iImg])


brightSets = __BrightnessFactors_GetBrightSets__(imgSets)
areaCntSets = __BrightnessFactors_GetPxAreaCnt__(imgSets)
divFactors = __BrightnessFactors_BuildDivFactors__(imgSets=imgSets, brightSets=brightSets, pxAreaCntSets=areaCntSets, PxDivTrustband=[1, 254], PxDivMinBright=1)
combinedFactors = __BrightnessFactors_BuildCombinedFactors__(divFactors)
upscaledAnyBright, upscaledAnyPxImgs = __BrightUpscale_Any__(imgSets, brightSets, divFactors, combinedFactors)
upscaledOvrBright, upscaledOvrPxImgs = __BrightUpscale_WhereOverexposed__(imgSets, brightSets, upscaledAnyBright, upscaledAnyPxImgs)


print("Finished")