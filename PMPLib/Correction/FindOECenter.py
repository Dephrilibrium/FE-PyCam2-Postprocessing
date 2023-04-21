# import os.path as p
import matplotlib.pyplot as plt
# import pickle
import cv2 as cv
import os
import numpy as np
# from scipy.optimize import curve_fit

# import FieldEmission as fe

from misc import GrabPklFile
from PMPLib.ImgAreas import GetCircleArea_XYX2Y2
from PMPLib.CircleDetectAndXYSort import DetectSpots

def CenterAndCoordOfBrightMin(Image, BMin, Dilate=None, Erode=None, ShowImg=False):

  if BMin == 0:
    return (0,0), 0, np.empty([2,0])

  BMin -= 1
  thVal, thImg = cv.threshold(Image, thresh=BMin, maxval=255, type=cv.THRESH_BINARY) # + cv.THRESH_OTSU) # Do not use otsu!
  oeCoord = np.where(thImg >= 255)

  if Dilate != None:
    thImg = cv.dilate(thImg, kernel=None, iterations=Dilate) # Auto-creates a copy
  if Erode != None:
    thImg = cv.erode(thImg, kernel=None, iterations=Erode) # Auto-creates a copy -> Override first copy so save RAM

  _contours, _h1 = cv.findContours(thImg, mode=cv.RETR_LIST, method=cv.CHAIN_APPROX_SIMPLE)
  if _contours != ():
    # for _cont in _contours:
    (x,y), r = cv.minEnclosingCircle(_contours[0])
    # Build nearest integer (drawable) values
    (x,y) = tuple(int(round(f)) for f in (x,y))
    r = int(round(r))

    dImg = cv.circle(Image.copy(), (x,y), r, color=(255,255,255), thickness=1)

  if ShowImg:
    figImg = plt.figure()
    plt.imshow(Image)
    figThrsh = plt.figure()
    plt.imshow(thImg)

    if np.size(oeCoord) > 0:
      tmp = Image.copy()
      for coord in zip(oeCoord[0], oeCoord[1]):
        tmp[coord] = 0
      figTmp = plt.figure()
      plt.imshow(tmp)

    if "dImg" in locals():
      figDImg = plt.figure()
      plt.imshow(dImg)

  return (x,y), r, oeCoord


# def SplitAndGrad(vFull, Dict2Store):

#   vecHalf = int(len(vFull)/2)

#   Dict2Store["bVec"] = dict()
#   Dict2Store["bVec"]["Full"] = vFull
#   LeftHalfVector = vFull[:vecHalf + 1]
#   Dict2Store["bVec"]["Left"] = LeftHalfVector
#   RightVector = vFull[vecHalf - 1:] #np.flip(vFull[vecHalf:])
#   Dict2Store["bVec"]["Right"] = RightVector

#   # vFull = np.insert(vFull, 0, 0)
#   # vFull = np.append(vFull, 0)
#   # fullDiff = np.diff(vFull) #np.gradient(vFull) #np.subtract(vFull[:-1], vFull[1:])
#   # fullDiff = np.gradient(vFull) #np.subtract(vFull[:-1], vFull[1:])
#   fullDiff = np.subtract(vFull[:-1], vFull[1:])
#   Dict2Store["dVec"] = dict()
#   Dict2Store["dVec"]["Full"] = fullDiff
#   leftDiff = fullDiff[:vecHalf] # np.subtract(LeftHalfVector[:-1], LeftHalfVector[1:])
#   Dict2Store["dVec"]["Left"] = leftDiff
#   rightDiff = fullDiff[vecHalf:]  # np.subtract(RightVector[:-1], RightVector[1:])
#   Dict2Store["dVec"]["Right"] = rightDiff
#   # gHalf1 = gFull[:vecHalf + 1]
#   # gHalf2 = gFull[vecHalf-2:]

#   # return LeftHalfVector, RightVector, fullDiff, leftDiff, rightDiff
#   return

# def CreateVectors(SpotImage):
#   sX = SpotImage.shape[0]
#   sY = SpotImage.shape[1]

#   dataType = np.int16

#   v0 = SpotImage[int(sX/2), :].astype(dataType).copy()
#   v90 = SpotImage[:, int(sY/2)].astype(dataType).copy()

#   if(sX > sY):
#     dBase = sX
#   else:
#     dBase = sY

#   dX = sX/dBase
#   dY = sY/dBase

#   v45 = list()
#   v135 = list()
#   for d in range(dBase):
#     x = int(dX * d)
#     y = int(dY * d)

#     v45.append(SpotImage[y, x])
#     v135.append(SpotImage[(sY-1) - y, x])
#   v45 = np.array(v45, dtype=dataType)
#   v135 = np.array(v135, dtype=dataType)

#   bVecDict = dict()
#   bVecDict["-45°"] = dict()
#   bVecDict["+0°"] = dict()
#   bVecDict["+45°"] = dict()
#   bVecDict["+90°"] = dict()

#   SplitAndGrad(v135, bVecDict["-45°"])
#   SplitAndGrad(v0  , bVecDict["+0°"])
#   SplitAndGrad(v45 , bVecDict["+45°"])
#   SplitAndGrad(v90 , bVecDict["+90°"])


#   bVecDict["-45°"]["OvrX"] = np.where(bVecDict["-45°"]["bVec"]["Full"] >= 255)[0]
#   bVecDict["+0°"] ["OvrX"] = np.where(bVecDict["+0°" ]["bVec"]["Full"] >= 255)[0]
#   bVecDict["+45°"]["OvrX"] = np.where(bVecDict["+45°"]["bVec"]["Full"] >= 255)[0]
#   bVecDict["+90°"]["OvrX"] = np.where(bVecDict["+90°"]["bVec"]["Full"] >= 255)[0]

#   bVecDict["-45°"]["OvrB"] = bVecDict["-45°"]["bVec"]["Full"][bVecDict["-45°"]["OvrX"]]
#   bVecDict["+0°"] ["OvrB"] = bVecDict["+0°" ]["bVec"]["Full"][bVecDict["+0°"] ["OvrX"]]
#   bVecDict["+45°"]["OvrB"] = bVecDict["+45°"]["bVec"]["Full"][bVecDict["+45°"]["OvrX"]]
#   bVecDict["+90°"]["OvrB"] = bVecDict["+90°"]["bVec"]["Full"][bVecDict["+90°"]["OvrX"]]

#   bVecDict["-45°"]["OvrD"] =bVecDict["-45°"]["dVec"]["Full"][bVecDict["-45°"]["OvrX"]]
#   bVecDict["+0°"] ["OvrD"] =bVecDict["+0°" ]["dVec"]["Full"][bVecDict["+0°"] ["OvrX"]]
#   bVecDict["+45°"]["OvrD"] =bVecDict["+45°"]["dVec"]["Full"][bVecDict["+45°"]["OvrX"]]
#   bVecDict["+90°"]["OvrD"] =bVecDict["+90°"]["dVec"]["Full"][bVecDict["+90°"]["OvrX"]]

#   return bVecDict


# def FindFirstSlope(bVec, dVec): 

#   for _iVec in range(len(dVec)):
#     bVecVal = bVec[_iVec]
#     dVecVal = dVec[_iVec]
#     # if bVecVal < 255 and dVecVal != 0:
#     if dVecVal != 0:
#       return abs(dVecVal)

#   return np.nan


# def BuildMeanOfFirstSlopes(vec):
#   slopes = list()
#   _dKeys = list(vec.keys())
#   for _iDeg in range(len(_dKeys)):
#     _dKey = _dKeys[_iDeg]

#     slopes.append(FindFirstSlope(np.flip(vec[_dKey]["bVec"]["Left"]), np.flip(vec[_dKey]["dVec"]["Left"])))
#     slopes.append(FindFirstSlope(vec[_dKey]["bVec"]["Right"], vec[_dKey]["dVec"]["Right"]))
  
#   return np.nanmean(slopes)



# def pltStd(ax, coll, xOff, OvrX, OvrY, PreLabel):
#   ax.plot(                      OvrX + xOff                                          , OvrY         , "o"  , label="Overexposed", color="purple", markersize=10, fillstyle="none")
#   ax.plot(np.add(list(range(len(coll["Full"]))), xOff)                               , coll["Full"] , "o--", label=PreLabel + "Full")
#   ax.plot(np.add(list(range(len(coll["Left"]))), xOff)                               , coll["Left"] , "x-.", label=PreLabel + "Left")
#   ax.plot(np.add(list(range(len(coll["Right"] ))), int(len(coll["Full"]) / 2) + xOff), coll["Right"], "^-.", label=PreLabel + "Right")
#   # ax.set_title("Bright +0°")













# circles = GrabPklFile(r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Auswertung\01_01 Aktivierungslauf\221213_134454 USwp\PMP_ssDetectionData.pkl")
# images = GrabPklFile( r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Auswertung\01_01 Aktivierungslauf\221213_134454 USwp\PMP_ssDetectionImages.pkl")
# _ssKeys = list(circles.keys())
# _ssKey = _ssKeys[0]

# _xyKeys = list(circles[_ssKey]["XYKeys"].keys())
# _xyKey = _xyKeys[2]

# _iImg = 610
# sideLen = 50


# _cIndex = circles[_ssKey]["XYKeys"][_xyKey]["ImageIndex"].index(_iImg)
# Circle = circles[_ssKey]["XYKeys"][_xyKey]["ImgCircles"][_cIndex]
# Image = images[_ssKey]["uint8"][_iImg]

# x1, y1, x2, y2 = GetCircleArea_XYX2Y2(Circle=Circle, pxTolerance=sideLen, AddPxTolerance=False)
# circImg = Image[y1:y2, x1:x2]

# imFig = plt.imshow(circImg)
# vecDict = CreateVectors(circImg)

# deriFig = plt.figure()
# deriAx = deriFig.subplots(nrows=1, ncols=4)

# pltStd(deriAx[0], vecDict["+0°"]["bVec"], 0, vecDict["+0°"]["OvrX"], vecDict["+0°"]["OvrB"], "bVec ")
# # deriAx[0].set_title("Bright +0°")
# pltStd(deriAx[0], vecDict["+0°"]["dVec"], 0.5, vecDict["+0°"]["OvrX"], vecDict["+0°"]["OvrD"], "dVec ")
# # deriAx[0].set_title("Diff +0°")
# deriAx[0].set_title("Vector +0°")



# pltStd(deriAx[1], vecDict["+90°"]["bVec"], 0, vecDict["+90°"]["OvrX"], vecDict["+90°"]["OvrB"], "bVec ")
# # deriAx[1].set_title("Bright +90°")
# pltStd(deriAx[1], vecDict["+90°"]["dVec"], 0.5, vecDict["+90°"]["OvrX"], vecDict["+90°"]["OvrD"], "dVec ")
# # deriAx[1].set_title("Diff +90°")
# deriAx[1].set_title("Vector +90°")



# pltStd(deriAx[2], vecDict["+45°"]["bVec"], 0, vecDict["+45°"]["OvrX"], vecDict["+45°"]["OvrB"], "bVec ")
# # deriAx[2].set_title("Bright +45°")
# pltStd(deriAx[2], vecDict["+45°"]["dVec"], 0.5, vecDict["+45°"]["OvrX"], vecDict["+45°"]["OvrD"], "dVec ")
# # deriAx[2].set_title("Diff +45°")
# deriAx[2].set_title("Vector +45°")



# pltStd(deriAx[3], vecDict["-45°"]["bVec"], 0, vecDict["-45°"]["OvrX"], vecDict["-45°"]["OvrB"], "bVec ")
# # deriAx[3].set_title("Bright -45°")
# pltStd(deriAx[3], vecDict["-45°"]["dVec"], 0.5, vecDict["-45°"]["OvrX"], vecDict["-45°"]["OvrD"], "dVec ")
# # deriAx[3].set_title("Diff -45°")
# deriAx[3].set_title("Vector -45°")



# def bVecMean(vecDict):
#   fullList = list()
#   leftList = list()
#   rightList = list()
#   lrList = list()

#   for dKey in list(vecDict.keys()):
#     fullList .append(vecDict[dKey]["bVec"]["Full"])
#     leftList .append(vecDict[dKey]["bVec"]["Left"])
#     rightList.append(vecDict[dKey]["bVec"]["Right"])
#     lrList   .append(leftList[-1])
#     lrList   .append(np.flip(rightList[-1]))
  
#   meanVec = dict()
#   meanVec["bVec"] = dict()
#   meanVec["bVec"]["Full"]  = np.mean(fullList , dtype=np.int16, axis=0)
#   meanVec["bVec"]["Left"]  = np.mean(leftList , dtype=np.int16, axis=0)
#   meanVec["bVec"]["Right"] = np.mean(rightList, dtype=np.int16, axis=0)
#   meanVec["bVec"]["L&R"]   = np.mean(lrList   , dtype=np.int16, axis=0)


#   return meanVec


# def fCap(pxlX, A):
#   y = (255 * 1.1) * (1 - np.exp(-pxlX/A))
#   return y

# def GetFitForVec(bVec, Thres, flip):
#   # nonzero = np.where((vecDict["+0°"]["bVec"]["Left"] < 255) & (vecDict["+0°"]["bVec"]["Left"] > 0))[0]
#   # nonzero = np.where((vecDict["+0°"]["bVec"]["Left"] > 3))[0]

#   if flip:
#     bVec = np.flip(bVec)

#   nonzero = np.where((bVec >= Thres[0]) & (bVec <= Thres[1]))[0]
#   # x = np.array(list(range(len(vecDict["+0°"]["bVec"]["Left"]))))
#   x = np.array(list(range(len(bVec))))
#   x = x[nonzero[0]:nonzero[-1]+1]
#   x0 = x[0]
#   x = x - x0
#   # y = vecDict["+0°"]["bVec"]["Left"][nonzero[0]:nonzero[-1]+1]
#   y = bVec[nonzero[0]:nonzero[-1]+1]
#   popt, pcov = curve_fit(f=fCap, xdata=x, ydata=y, p0=[1])
#   pmean = np.mean([popt[0], pcov[0]])

#   xFine = np.linspace(start=x[0] - 3, stop=x[-1] + 3, num=150, endpoint=True)
#   yFine = list()
#   for xF in xFine:
#     yFine.append(fCap(xF, popt[0]))
#     # yFine.append(fCap(xF, pcov[0]))
#     # yFine.append(fCap(xF, pmean))

#   if flip:
#     xFine = xFine + len(bVec)
#     # xFine = np.flip(xFine)
#     yFine = np.flip(yFine)
#   else:
#      xFine = xFine + x0

#   return xFine, yFine


# iThresh = [20, 250]
# xI, yI = GetFitForVec(vecDict["+0°"]["bVec"]["Left"], iThresh, False)
# deriAx[0].plot(xI, yI, "r.", label=r"$Interpol_{Left}$")
# xI, yI = GetFitForVec(vecDict["+0°"]["bVec"]["Right"], iThresh, True)
# deriAx[0].plot(xI, yI, "r.", label=r"$Interpol_{Right}$")

# xI, yI = GetFitForVec(vecDict["+90°"]["bVec"]["Left"], iThresh, False)
# deriAx[1].plot(xI, yI, "r.", label=r"$Interpol_{Left}$")
# xI, yI = GetFitForVec(vecDict["+90°"]["bVec"]["Right"], iThresh, True)
# deriAx[1].plot(xI, yI, "r.", label=r"$Interpol_{Right}$")

# xI, yI = GetFitForVec(vecDict["+45°"]["bVec"]["Left"], iThresh, False)
# deriAx[2].plot(xI, yI, "r.", label=r"$Interpol_{Left}$")
# xI, yI = GetFitForVec(vecDict["+45°"]["bVec"]["Right"], iThresh, True)
# deriAx[2].plot(xI, yI, "r.", label=r"$Interpol_{Right}$")

# xI, yI = GetFitForVec(vecDict["-45°"]["bVec"]["Left"], iThresh, False)
# deriAx[3].plot(xI, yI, "r.", label=r"$Interpol_{Left}$")
# xI, yI = GetFitForVec(vecDict["-45°"]["bVec"]["Right"], iThresh, True)
# deriAx[3].plot(xI, yI, "r.", label=r"$Interpol_{Right}$")
# slope = BuildMeanOfFirstSlopes(vecDict)










# def PlotSupLegend(fig, suptitle):
#   lines = []
#   labels = []
#   for axis in fig.axes:
#     Line, Label = axis.get_legend_handles_labels()
#     # print(Label)
#     for _iLab in range(len(Label)):
#       if labels.__contains__(Label[_iLab]):
#         continue
#       lines.append(Line[_iLab])
#       labels.append(Label[_iLab])
#   fig.legend(lines, labels, loc="upper right")
#   fig.suptitle(suptitle)
#   # deriFig.suptitle("Brightness-factors of each pixels (mean)")

# PlotSupLegend(deriFig, "Brightness Derivation @Tip " + str(_xyKey))




# interFig = plt.figure()
# interAx = interFig.subplots(nrows=1, ncols=4)

# xFull = np.array(list(range(len(vecDict["+0°"]["bVec"]["Full"]))))
# interAx[0].plot(xFull, vecDict["+0°"] ["bVec"]["Full"], label=r"$Full$")
# interAx[1].plot(xFull, vecDict["+90°"]["bVec"]["Full"], label=r"$Full$")
# interAx[2].plot(xFull, vecDict["+45°"]["bVec"]["Full"], label=r"$Full$")
# interAx[3].plot(xFull, vecDict["-45°"]["bVec"]["Full"], label=r"$Full$")
# interAx[0].set_title("Vector +0°")
# interAx[1].set_title("Vector +90°")
# interAx[2].set_title("Vector +45°")
# interAx[3].set_title("Vector -45°")


# meanVec = bVecMean(vecDict=vecDict)

# # Plot Left half mean
# xI, yI = GetFitForVec(meanVec["bVec"]["Left"], iThresh, False)
# interAx[0].plot(xI, yI, "r.", label=r"$Interpol_{MeanL}$")
# interAx[1].plot(xI, yI, "r.", label=r"$Interpol_{MeanL}$")
# interAx[2].plot(xI, yI, "r.", label=r"$Interpol_{MeanL}$")
# interAx[3].plot(xI, yI, "r.", label=r"$Interpol_{MeanL}$")

# # Plot right half mean
# xI, yI = GetFitForVec(meanVec["bVec"]["Right"], iThresh, True)
# interAx[0].plot(xI, yI, "rx", label=r"$Interpol_{MeanR}$")
# interAx[1].plot(xI, yI, "rx", label=r"$Interpol_{MeanR}$")
# interAx[2].plot(xI, yI, "rx", label=r"$Interpol_{MeanR}$")
# interAx[3].plot(xI, yI, "rx", label=r"$Interpol_{MeanR}$")

# # Plot left & right mean
# xI, yI = GetFitForVec(meanVec["bVec"]["L&R"], iThresh, False)
# interAx[0].plot(xI, yI, "k.", label=r"$Interpol_{MeanLR}$")
# interAx[1].plot(xI, yI, "k.", label=r"$Interpol_{MeanLR}$")
# interAx[2].plot(xI, yI, "k.", label=r"$Interpol_{MeanLR}$")
# interAx[3].plot(xI, yI, "k.", label=r"$Interpol_{MeanLR}$")
# # mirror and plot left & right mean
# xI = xI - xI[0] + len(meanVec["bVec"]["L&R"]) - 3
# yI = np.flip(yI)
# interAx[0].plot(xI, yI, "k.", label=r"$Interpol_{MeanLR}$")
# interAx[1].plot(xI, yI, "k.", label=r"$Interpol_{MeanLR}$")
# interAx[2].plot(xI, yI, "k.", label=r"$Interpol_{MeanLR}$")
# interAx[3].plot(xI, yI, "k.", label=r"$Interpol_{MeanLR}$")
# slope = BuildMeanOfFirstSlopes(vecDict)


# PlotSupLegend(interFig, "Brightness Interpolation @Tip " + str(_xyKey))





# for ax in deriAx:
#   ax.set_xlim([-1, 16])
#   ax.set_ylim([-310, 310])

# for ax in interAx:
#   ax.set_xlim([-1, 16])
#   ax.set_ylim([-310, 310])



# plt.show()
# print("Finished")



# # def SplitAndGrad(vFull):
# #   vecHalf = int(len(vFull)/2)

# #   # vFull = im[:, vecHalf]
# #   vHalf1 = vFull[:vecHalf + 1]
# #   vHalf2 = np.flip(vFull[vecHalf - 1:])
# #   gFull = np.subtract(vFull[:-1], vFull[1:])
# #   gHalf1 = np.subtract(vHalf1[:-1], vHalf1[1:])
# #   gHalf2 = np.subtract(vHalf2[:-1], vHalf2[1:])
# #   # gHalf1 = gFull[:vecHalf + 1]
# #   # gHalf2 = gFull[vecHalf-2:]

# #   return vHalf1, vHalf2, gFull, gHalf1, gHalf2



# # im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\Dev101_rPiHQCam-0464_ss=100000_0001.jpg")
# # x, y, w, h = 278, 314, 16, 16

# # # im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\Dev101_rPiHQCam-0112_ss=100000_0003.png")
# # # x, y, w, h = 35, 96, 13, 13
# # im = im[y:y+h, x:x+w]


# # # im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\TestCircle.png")


# # plt_image = cv.cvtColor(im, cv.COLOR_BGR2RGB)
# # imgplot = plt.imshow(plt_image)
# # im = cv.cvtColor(im, cv.COLOR_BGR2GRAY).astype(np.float64)
# # # im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\TestImage.png", cv.IMREAD_GRAYSCALE).astype(np.float64)
# # # im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\TestCircle.png", cv.IMREAD_GRAYSCALE).astype(np.float64)
# # nX = int(im.shape[0]/2)
# # nY = int(im.shape[1]/2)

# # v0 = im[nY, :]
# # v01, v02, g0, g01, g02 = SplitAndGrad(v0)

# # v90 = im[:, nX]
# # v901, v902, g90, g901, g902 = SplitAndGrad(v90)


# # v45 = list()
# # v135 = list()
# # for _iDiag in range(im.shape[0]):
# #   v45.append(im[_iDiag, _iDiag]) # Get all 45 Diagonal
# #   v135.append(im[-1 - _iDiag, _iDiag]) # Get all -45 Diagonal
# # v45 = np.array(v45)
# # v135 = np.array(v135)

# # v451, v452, g45, g451, g452 = SplitAndGrad(v45)
# # v1351, v1352, g135, g1351, g1352 = SplitAndGrad(v135)


# # mv = np.mean([v0, v90, v45, v135], axis=0)
# # mv1, mv2, g, g1, g2 = SplitAndGrad(mv)

# # fig = plt.figure()
# # axe = fig.subplots(nrows=2, ncols=5)


# # axe[0, 0].plot(v0 , "o--", label="V0°")
# # axe[0, 0].plot(v01, ".-.", label="V0° LH")
# # axe[0, 0].plot(v02, ".-.", label="V0° RH")
# # axe[0, 0].set_title("Helligkeit 0° >")
# # axe[0, 0].legend()

# # axe[1, 0].plot(g0 , "o--", label="G0°")
# # axe[1, 0].plot(g01, ".-.", label="G0° LH")
# # axe[1, 0].plot(g02, ".-.", label="G0° RH")
# # axe[1, 0].set_title("Gradienten 0° >")
# # axe[1, 0].legend()

# # axe[0, 1].plot(v90 , "o--", label="V90°")
# # axe[0, 1].plot(v901, ".-.", label="V90° LH")
# # axe[0, 1].plot(v902, ".-.", label="V90° RH")
# # axe[0, 1].set_title("Helligkeit 90° v")
# # axe[0, 1].legend()

# # axe[1, 1].plot(g90 , "o--", label="G90°")
# # axe[1, 1].plot(g901, ".-.", label="G90° LH")
# # axe[1, 1].plot(g902, ".-.", label="G90° RH")
# # axe[1, 1].set_title("Gradienten 90° v")
# # axe[1, 1].legend()

# # axe[0, 2].plot(v45 , "o--", label="V45°")
# # axe[0, 2].plot(v451, ".-.", label="V45° LH")
# # axe[0, 2].plot(v452, ".-.", label="V45° RH")
# # axe[0, 2].set_title("Helligkeit 45° >v")
# # axe[0, 2].legend()

# # axe[1, 2].plot(g45 , "o--", label="G45°")
# # axe[1, 2].plot(g451, ".-.", label="G45° LH")
# # axe[1, 2].plot(g452, ".-.", label="G45° RH")
# # axe[1, 2].set_title("Gradienten 45° >v")
# # axe[1, 2].legend()

# # axe[0, 3].plot(v135 , "o--", label="V-45°")
# # axe[0, 3].plot(v1351, ".-.", label="V-45° LH")
# # axe[0, 3].plot(v1352, ".-.", label="V-45° RH")
# # axe[0, 3].set_title("Helligkeit -45° >^")
# # axe[0, 3].legend()

# # axe[1, 3].plot(g135 , "o--", label="G-45°")
# # axe[1, 3].plot(g1351, ".-.", label="G-45° LH")
# # axe[1, 3].plot(g1352, ".-.", label="G-45° RH")
# # axe[1, 3].set_title("Gradienten -45° >^")
# # axe[1, 3].legend()

# # axe[0, 4].plot(mv , "o--", label="mv")
# # axe[0, 4].plot(mv1, ".-.", label="mv LH")
# # axe[0, 4].plot(mv2, ".-.", label="mv RH")
# # axe[0, 4].set_title("Helligkeit Alle")
# # axe[0, 4].legend()

# # axe[1, 4].plot(g , "o--", label="g")
# # axe[1, 4].plot(g1, ".-.", label="g LH")
# # axe[1, 4].plot(g2, ".-.", label="g RH")
# # axe[1, 4].set_title("Gradienten Alle")
# # axe[1, 4].legend()


# # gradX = cv.Sobel(src=im, ddepth=cv.CV_64F, dx=1, dy=0, ksize=3)
# # gradY = cv.Sobel(src=im, ddepth=cv.CV_64F, dx=0, dy=1, ksize=3)
# # # And get combined gradient
# # grad  = np.sqrt(gradX**2 + gradY**2)
# # cv.imshow("Raw", im)
# # cv.imshow("GradX" , gradX)
# # cv.imshow("GradY" , gradY)
# # cv.imshow("GradXY", grad)







# # print("Finished")
