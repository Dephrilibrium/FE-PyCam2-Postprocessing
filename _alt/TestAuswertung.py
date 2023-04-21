from base64 import encode
import os
from posixpath import basename
import time
import pickle
import glob
from tkinter import Y
import natsort
import parse
import numpy as np
import matplotlib.pyplot as plt
import FieldEmission as fe
import cv2 as cv

from _ImageFileHandling import ReadImages
from _ImageProcessing import MeanImages

from misc import Logger
from misc import LogLine
from misc import LogLineOK


# foldPath = r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\221130 HQCam Paper SOI2x2_0004\01_01 Aktivierungsversuch mit MCP\221201_112053 USweep1400V IMax300nA\Pics"
# imNum = 610

foldPath = r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\221130 HQCam Paper SOI2x2_0004\01_01 Aktivierungsversuch mit MCP\221201_121903 30min 140V IMax 300nA\Pics"
imNum = 175
fileForm = str.format("Dev101_HQCam-{:04d}_ss={}_{}.png", imNum, "*", "*")

# ClipWin = [42, 240, 20, 20]
ClipWin = None


rImgs, fPaths = ReadImages(foldPath, fileForm, CropWindow=ClipWin)
mImgs = MeanImages(rImgs, 4)
# cv.imshow("3150"  , mImgs[0])
# cv.imshow("10000" , mImgs[1])
# cv.imshow("31500" , mImgs[2])
# cv.imshow("100000", mImgs[3])
fig = plt.figure()
ax = fig.subplots(nrows=2, ncols=2)
ax[0, 0].imshow(mImgs[0])
ax[0, 1].imshow(mImgs[1])
ax[1, 0].imshow(mImgs[2])
ax[1, 1].imshow(mImgs[3])

ax[0, 0].set_title("SS=3150"  )
ax[0, 1].set_title("SS=10000" )
ax[1, 0].set_title("SS=31500" )
ax[1, 1].set_title("SS=100000")

fig.suptitle("Meaned SS-Images (Image #" + str(imNum) + ")")




print("Finished")