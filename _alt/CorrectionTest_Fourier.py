import os.path as p
import matplotlib.pyplot as plt
import pickle
import cv2 as cv
import numpy as np

import FieldEmission as fe

from misc import GrabPklFile

import cv2 as cv

from PMPLib.ImgAreas import GetXYArea_XYX2Y2
from PMPLib.Correction.FindOECenter import CenterAndCoordOfBrightMin
from PMPLib.Correction.Vectors import GrabLuminosityVector4Coord
from PMPLib.Correction.Fourier import FourierOnLuminosityVector


# crcls = GrabPklFile(r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Auswertung\01_01 Aktivierungslauf\221213_134454 USwp\PMP_ssDetectionData.pkl")
# imags = GrabPklFile(r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Auswertung\01_01 Aktivierungslauf\221213_134454 USwp\PMP_ssDetectionImages.pkl")
# SS = list(crcls.keys())
# XY = list(crcls[SS[0]]["XYKeys"].keys())
# XY = [XY[2]]


imags = dict()
imags[100000] = dict()
imags[100000]["uint8"] = [cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\_TestImages\Dev101_HQCam-0937_ss=100000_0003.jpg", cv.IMREAD_GRAYSCALE)]   # UHD
# imags[100000]["uint8"] = [cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\_TestImages\Dev101_rPiHQCam-0100_ss=100000_0003.png", cv.IMREAD_GRAYSCALE)]    # FHD
SS = [100000]
XY = [(2065, 1878)]





imNum = 0
sideLen = 60
x1, y1, x2, y2 = GetXYArea_XYX2Y2(XY[0], sideLen)
# x1, y1, x2, y2 = [[0][0] - sideLen, XY[0][1] - sideLen, XY[0][0] + sideLen, XY[0][1] + sideLen,]


bRepl = 254

tImg = imags[SS[0]]["uint8"][imNum][y1:y2, x1:x2]
center, r, oeCoord = CenterAndCoordOfBrightMin(tImg, BMin=bRepl, Dilate=5, Erode=2, ShowImg=True)


divVecPx = list()
divVecSum = list()

rImg = tImg.copy().astype(np.uint16)
estOE = 1 + (np.where(tImg > bRepl)[0].__len__() / np.where(tImg > 1)[0].__len__())
_iter = 0
print("Divs are in: BrightCorrected / BrightOriginal")
for coord in zip(oeCoord[0], oeCoord[1]):
  _iter += 1
  bVec, iCoord = GrabLuminosityVector4Coord(tImg=tImg, center=center, coord=coord, overlap=int(r), flip=True)
  ipVec = FourierOnLuminosityVector(bVec)
  rImg[coord] = ipVec["y"][iCoord]
  divVecPx.append(ipVec["y"][iCoord] / bVec["y"][iCoord])
  divVecSum.append(np.sum(ipVec["y"]) / np.sum(bVec["y"]))
  print(str.format("Pixel-Replace [{:3d}] @ {}:".ljust(30) + "{} -> {}".ljust(15) + "DivPx: {:.5f}".ljust(20) + "DivSum: {:.5f}", _iter, coord, tImg[coord], ipVec["y"][iCoord], divVecPx[-1], divVecSum[-1]))

print("")
print(str.format("Mean of Pixel-Replacement:"              .ljust(45 + 6) + "DivPx: {:.5f}".ljust(20) + "DivSum: {:.5f}", np.mean(divVecPx), np.mean(divVecSum)))
print(str.format("Standard-Deviation of Pixel-Replacement:".ljust(45 + 6) + "DivPx: {:.5f}".ljust(20) + "DivSum: {:.5f}", np.std (divVecPx), np.std(divVecSum)))

dImg = np.divide(rImg, tImg, dtype=np.float32)
dImg = np.nan_to_num(dImg, copy=False, nan=0, posinf=0, neginf=0)
plt.close()
plt.imshow(dImg, cmap="seismic")
plt.colorbar()
plt.xlabel("x")
plt.ylabel("y")
plt.title("Pixel-Factor (Correction/Original)")


# Pixelwise replacement dividers as graph
plt.close()
plt.plot(list(range(len(divVecPx))), divVecPx, ".--", label="DivPx")
mean = np.mean(divVecPx)
std = np.std(divVecPx)
plt.plot([0, len(divVecPx)-1], [mean, mean]        , "k-", label="Mean"   )
plt.plot([0, len(divVecPx)-1], [mean+std, mean+std], "r-", label="StdBand")
plt.plot([0, len(divVecPx)-1], [mean-std, mean-std], "r-"                 )
plt.xlabel("Pixelcoordinate-Iterator [#]")
plt.ylabel("Factor")
plt.title("Division InterpolatedBright / OriginalBright")
plt.legend()


# Pixelwise replacement dividers of the sum-brightness as graph
plt.close()
plt.plot(list(range(len(divVecSum))), divVecSum, ".--", label="DivPx")
mean = np.mean(divVecSum)
std = np.std(divVecSum)
plt.plot([0, len(divVecSum)-1], [mean, mean]        , "k-", label="Mean"   )
plt.plot([0, len(divVecSum)-1], [mean+std, mean+std], "r-", label="StdBand")
plt.plot([0, len(divVecSum)-1], [mean-std, mean-std], "r-"                 )
plt.xlabel("Pixelcoordinate-Iterator [#]")
plt.ylabel("Factor")
plt.title("Division sum(InterpolatedBright) / sum(OriginalBright)")
plt.legend()


print("Finished Correction")

# def SplitAndGrad(vFull):
#   vecHalf = int(len(vFull)/2)

#   # vFull = im[:, vecHalf]
#   vHalf1 = vFull[:vecHalf + 1]
#   vHalf2 = np.flip(vFull[vecHalf - 1:])
#   gFull = np.subtract(vFull[:-1], vFull[1:])
#   gHalf1 = np.subtract(vHalf1[:-1], vHalf1[1:])
#   gHalf2 = np.subtract(vHalf2[:-1], vHalf2[1:])
#   # gHalf1 = gFull[:vecHalf + 1]
#   # gHalf2 = gFull[vecHalf-2:]

#   return vHalf1, vHalf2, gFull, gHalf1, gHalf2



# im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\Dev101_rPiHQCam-0464_ss=100000_0001.jpg")
# x, y, w, h = 278, 314, 16, 16

# # im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\Dev101_rPiHQCam-0112_ss=100000_0003.png")
# # x, y, w, h = 35, 96, 13, 13
# im = im[y:y+h, x:x+w]


# # im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\TestCircle.png")


# plt_image = cv.cvtColor(im, cv.COLOR_BGR2RGB)
# imgplot = plt.imshow(plt_image)
# im = cv.cvtColor(im, cv.COLOR_BGR2GRAY).astype(np.float64)
# # im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\TestImage.png", cv.IMREAD_GRAYSCALE).astype(np.float64)
# # im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\TestCircle.png", cv.IMREAD_GRAYSCALE).astype(np.float64)
# nX = int(im.shape[0]/2)
# nY = int(im.shape[1]/2)

# v0 = im[nY, :]
# v01, v02, g0, g01, g02 = SplitAndGrad(v0)

# v90 = im[:, nX]
# v901, v902, g90, g901, g902 = SplitAndGrad(v90)


# v45 = list()
# v135 = list()
# for _iDiag in range(im.shape[0]):
#   v45.append(im[_iDiag, _iDiag]) # Get all 45 Diagonal
#   v135.append(im[-1 - _iDiag, _iDiag]) # Get all -45 Diagonal
# v45 = np.array(v45)
# v135 = np.array(v135)

# v451, v452, g45, g451, g452 = SplitAndGrad(v45)
# v1351, v1352, g135, g1351, g1352 = SplitAndGrad(v135)


# mv = np.mean([v0, v90, v45, v135], axis=0)
# mv1, mv2, g, g1, g2 = SplitAndGrad(mv)

# fig = plt.figure()
# axe = fig.subplots(nrows=2, ncols=5)


# axe[0, 0].plot(v0 , "o--", label="V0°")
# axe[0, 0].plot(v01, ".-.", label="V0° LH")
# axe[0, 0].plot(v02, ".-.", label="V0° RH")
# axe[0, 0].set_title("Helligkeit 0° >")
# axe[0, 0].legend()

# axe[1, 0].plot(g0 , "o--", label="G0°")
# axe[1, 0].plot(g01, ".-.", label="G0° LH")
# axe[1, 0].plot(g02, ".-.", label="G0° RH")
# axe[1, 0].set_title("Gradienten 0° >")
# axe[1, 0].legend()

# axe[0, 1].plot(v90 , "o--", label="V90°")
# axe[0, 1].plot(v901, ".-.", label="V90° LH")
# axe[0, 1].plot(v902, ".-.", label="V90° RH")
# axe[0, 1].set_title("Helligkeit 90° v")
# axe[0, 1].legend()

# axe[1, 1].plot(g90 , "o--", label="G90°")
# axe[1, 1].plot(g901, ".-.", label="G90° LH")
# axe[1, 1].plot(g902, ".-.", label="G90° RH")
# axe[1, 1].set_title("Gradienten 90° v")
# axe[1, 1].legend()

# axe[0, 2].plot(v45 , "o--", label="V45°")
# axe[0, 2].plot(v451, ".-.", label="V45° LH")
# axe[0, 2].plot(v452, ".-.", label="V45° RH")
# axe[0, 2].set_title("Helligkeit 45° >v")
# axe[0, 2].legend()

# axe[1, 2].plot(g45 , "o--", label="G45°")
# axe[1, 2].plot(g451, ".-.", label="G45° LH")
# axe[1, 2].plot(g452, ".-.", label="G45° RH")
# axe[1, 2].set_title("Gradienten 45° >v")
# axe[1, 2].legend()

# axe[0, 3].plot(v135 , "o--", label="V-45°")
# axe[0, 3].plot(v1351, ".-.", label="V-45° LH")
# axe[0, 3].plot(v1352, ".-.", label="V-45° RH")
# axe[0, 3].set_title("Helligkeit -45° >^")
# axe[0, 3].legend()

# axe[1, 3].plot(g135 , "o--", label="G-45°")
# axe[1, 3].plot(g1351, ".-.", label="G-45° LH")
# axe[1, 3].plot(g1352, ".-.", label="G-45° RH")
# axe[1, 3].set_title("Gradienten -45° >^")
# axe[1, 3].legend()

# axe[0, 4].plot(mv , "o--", label="mv")
# axe[0, 4].plot(mv1, ".-.", label="mv LH")
# axe[0, 4].plot(mv2, ".-.", label="mv RH")
# axe[0, 4].set_title("Helligkeit Alle")
# axe[0, 4].legend()

# axe[1, 4].plot(g , "o--", label="g")
# axe[1, 4].plot(g1, ".-.", label="g LH")
# axe[1, 4].plot(g2, ".-.", label="g RH")
# axe[1, 4].set_title("Gradienten Alle")
# axe[1, 4].legend()


# gradX = cv.Sobel(src=im, ddepth=cv.CV_64F, dx=1, dy=0, ksize=3)
# gradY = cv.Sobel(src=im, ddepth=cv.CV_64F, dx=0, dy=1, ksize=3)
# # And get combined gradient
# grad  = np.sqrt(gradX**2 + gradY**2)
# cv.imshow("Raw", im)
# cv.imshow("GradX" , gradX)
# cv.imshow("GradY" , gradY)
# cv.imshow("GradXY", grad)







# print("Finished")
