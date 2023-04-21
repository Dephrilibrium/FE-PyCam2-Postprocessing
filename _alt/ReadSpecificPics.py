import cv2 as cv
import numpy as np
import os
import pickle
import matplotlib.pyplot as plt

imgOriPath = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Ausw\220725 PiCam Einzelemitter\03 1h I500nA U1400V\220804_161157 (#1)\PMP_ImgSets4Brightness.pkl"
bAnyOriPath = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Ausw\220725 PiCam Einzelemitter\03 1h I500nA U1400V\220804_161157 (#1)\PMP_ScaledAnyBrightnesses.pkl"
bWheOriPath = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Ausw\220725 PiCam Einzelemitter\03 1h I500nA U1400V\220804_161157 (#1)\PMP_ScaledWhereOverexposedBrightnesses.pkl"


imgOvrPath = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Ausw\220725 PiCam Einzelemitter\03 1h I500nA U1400V\220804_161157 (#1)_+10.0%AO\PMP_ImgSets4Brightness.pkl"

bAnyOvrPath = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Ausw\220725 PiCam Einzelemitter\03 1h I500nA U1400V\220804_161157 (#1)_+10.0%AO\PMP_ScaledAnyBrightnesses.pkl"
bWheOvrPath = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Ausw\220725 PiCam Einzelemitter\03 1h I500nA U1400V\220804_161157 (#1)_+10.0%AO\PMP_ScaledWhereOverexposedBrightnesses.pkl"

f = open(imgOriPath, "rb")
imgSetOri = pickle.load(f)
f.close()
f = open(bAnyOriPath, "rb")
bAnySetOri = pickle.load(f)
f.close()
f = open(bWheOriPath, "rb")
bWheSetOri = pickle.load(f)
f.close()

f = open(imgOvrPath, "rb")
imgSetOvr = pickle.load(f)
f.close()
f = open(bAnyOvrPath, "rb")
bAnySetOvr = pickle.load(f)
f.close()
f = open(bWheOvrPath, "rb")
bWheSetOvr = pickle.load(f)
f.close()

_bKey = 100000
_dKey = 10000
_sptXY = (71, 69)


sumSetOri = np.array(imgSetOri[_bKey]["Spot"][_sptXY]["Blank"])
sumSetOri10 = np.multiply(sumSetOri, 1.1) # Add 10% to match ovr-brightness
bSetAnyOri = bAnySetOri[_bKey][_dKey]["Spot"][_sptXY]["SpotBright"]["Blank"]["xSpotDivBlank"]

sumSetOvr = np.array(imgSetOri[_bKey]["Spot"][_sptXY]["Blank"])
sumSetOvrUp = np.array(imgSetOri[_bKey]["Div"][_dKey]["Spot"][_sptXY]["Blank"])
bSetAnyOvr = bAnySetOvr[_bKey][_dKey]["Spot"][_sptXY]["SpotBright"]["Blank"]["xSpotDivBlank"]

sumOri   = list()
sumOri10 = list()
sumOvr   = list()
sumOvrUp = list()
imLen = len(sumSetOri)
xAxis = range(imLen)
for iImg in range(imLen):
  sumOri  .append(np.sum(sumSetOri  [iImg]))
  sumOri10.append(np.sum(sumSetOri10[iImg]))
  sumOvr  .append(np.sum(sumSetOvr  [iImg]))
  sumOvrUp.append(np.sum(sumSetOvrUp[iImg]))

sumOri   = np.array(sumOri  )
sumOri10 = np.array(sumOri10)
sumOvr   = np.array(sumOvr  )
sumOvrUp = np.array(sumOvrUp)

plt.plot(xAxis, bSetAnyOri  , "x", label=r"$Ovr Ori$")
plt.plot(xAxis, bSetAnyOri  , ".", label=r"$Any Ori$")
plt.plot(xAxis, sumOri10  , "o", label=r"$OriUp$")
plt.plot(xAxis, sumOri  , "k--", label=r"$Ori$")

plt.legend()
plt.title("Spot " + str(_sptXY))
plt.xlabel("Image [#]")
plt.ylabel("Brightness [#]")


print("Finished")