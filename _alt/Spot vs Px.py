import os
import pickle
import glob
import random
from tokenize import endpats
import cv2 as cv
from cv2 import THRESH_BINARY_INV
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import axes3d

from misc import Logger
from misc import LogLine
from misc import LogLineOK


def GrabPklFile(PklPath):

  _pklPath = glob.glob(PklPath)
  if _pklPath.__len__() == 1:
    LogLine(None, " - Found: ", os.path.basename(_pklPath[0]), yFill=15, wFill=0, end="\n")
    f = open(_pklPath[0], "rb")
    pkl = pickle.load(f)
    f.close()
    return pkl

  LogLine(None, " - Missing: ", "Wasn't able to find any " + os.path.basename(PklPath), yFill=15, wFill=0, end="\n")
  return




figWidth_cm = 50
figHeight_cm = figWidth_cm / (16/9)


pklPath = r"C:\Users\ham38517\Downloads\220725 PiCam Einzelemitter\Ausw\03 1h I500nA U1400V\220804_175655 (#1)\PMP_correctedImages.pkl"
bDat = GrabPklFile(pklPath)

figNames = list()
figs = list()
axes = list()

bSS = 100000
dSS = 10000

bSel = bDat[bSS][dSS]
_xyKeys = list(bSel.keys())
for _iKey in range(len(_xyKeys)):
  _xyKey = _xyKeys[_iKey]
  cSpot = bSel[_xyKey]
  cPx = cSpot["OriginalImages"]

  nIm = cSpot["nImages"]
  imgsRaw = cPx["uint8_BaseAreaRaw"]
  imgsPur = cPx["uint8_BaseAreaPurged"]
  imgsDiv = cPx["uint8_DivAreaRaw"]
  imgsPDi = cPx["uint8_DivAreaPurged"]


  nonZeroRaw = list()
  nonZeroPur = list()
  nonZeroDiv = list()
  nonZeroPDi = list()

  nonZeroRawDiv = list()
  nonZeroPurPDi = list()
  nonZeroDivPDi = list()

  npSumSpotRaw = list()
  npSumSpotPur = list()
  npSumSpotDiv = list()
  npSumSpotPDi = list()

  npMeanSpotRaw = list()
  npMeanSpotPur = list()
  npMeanSpotDiv = list()
  npMeanSpotPDi = list()

  npSpotDivRaw = list()
  npSpotDivPur = list()
  npSpotPDiPur = list()

  npMeanSpotDivRaw = list()
  npMeanSpotDivPur = list()
  npMeanSpotPDiPur = list()

  npFacMulRawDiv = list()
  npFacMulPurDiv = list()
  npFacMulPurPDi = list()




  npPxDivRaw = list()
  npPxDivPur = list()
  npPxMeanRaw = list()
  npPxMeanPur = list()


  cvPxDivRaw = list()
  cvPxDivPur = list()
  cvPxMeanRaw = list()
  cvPxMeanPur = list()


  npMeanRaw = list()
  npMeanPur = list()
  npMeanDiv = list()

  npDivRaw = list()
  npDivPur = list()



  
  for _iIm in range(nIm):
    imRaw = imgsRaw[_iIm]
    imPur = imgsPur[_iIm]
    imDiv = imgsDiv[_iIm]
    imPDi = imDiv.copy()
    imPDi[imPur == 0] = 0

    nonZeroRaw.append(np.nonzero(imRaw)[0].size)
    nonZeroPur.append(np.nonzero(imPur)[0].size)
    nonZeroDiv.append(np.nonzero(imDiv)[0].size)
    nonZeroPDi.append(np.nonzero(imPDi)[0].size)

    nonZeroRawDiv.append(np.divide(nonZeroRaw[-1], nonZeroDiv[-1]))
    nonZeroPurPDi.append(np.divide(nonZeroPur[-1], nonZeroPDi[-1]))
    nonZeroDivPDi.append(np.divide(nonZeroDiv[-1], nonZeroPDi[-1]))

    # Spotwise
    npSumSpotRaw.append(np.sum(imRaw))
    npSumSpotPur.append(np.sum(imPur))
    npSumSpotDiv.append(np.sum(imDiv))
    npSumSpotPDi.append(np.sum(imPDi))

    npMeanSpotRaw.append(np.divide(npSumSpotRaw[-1], nonZeroRaw[-1]))
    npMeanSpotPur.append(np.divide(npSumSpotPur[-1], nonZeroPur[-1]))
    npMeanSpotDiv.append(np.divide(npSumSpotDiv[-1], nonZeroDiv[-1]))
    npMeanSpotPDi.append(np.divide(npSumSpotPDi[-1], nonZeroPDi[-1]))

    npSpotDivRaw.append(np.divide(npSumSpotRaw[-1], npSumSpotDiv[-1]))
    npSpotDivPur.append(np.divide(npSumSpotPur[-1], npSumSpotDiv[-1]))
    npSpotPDiPur.append(np.divide(npSumSpotPur[-1], npSumSpotPDi[-1]))

    npMeanSpotDivRaw.append(np.divide(npMeanSpotRaw[-1], npMeanSpotDiv[-1]))
    npMeanSpotDivPur.append(np.divide(npMeanSpotPur[-1], npMeanSpotDiv[-1]))
    npMeanSpotPDiPur.append(np.divide(npMeanSpotPur[-1], npMeanSpotPDi[-1]))

    npFacMulRawDiv.append(np.multiply(npSpotDivRaw[-1], nonZeroRawDiv[-1]))
    npFacMulPurDiv.append(np.multiply(npSpotDivPur[-1], nonZeroRawDiv[-1]))
    npFacMulPurPDi.append(np.multiply(npSpotDivPur[-1], nonZeroPurPDi[-1]))



    # # Pixelwise
    # tmp = np.nan_to_num(np.divide(imRaw, imDiv), nan=np.nan, posinf=np.nan, neginf=np.nan);
    # npPxDivRaw.append(tmp)
    # tmp = np.nan_to_num(np.divide(imPur, imDiv), nan=np.nan, posinf=np.nan, neginf=np.nan);
    # npPxDivPur.append(tmp)
    # npPxMeanRaw.append(np.nanmean(npPxDivRaw[-1]))
    # npPxMeanPur.append(np.nanmean(npPxDivPur[-1]))

    # cvPxDivRaw.append(cv.divide(imRaw, imDiv))
    # cvPxDivPur.append(cv.divide(imPur, imDiv))
    # ret, thres = cv.threshold(cvPxDivRaw[-1].copy(), 0, 255, cv.THRESH_BINARY)
    # if ret == 0:
    #   cvPxMeanRaw.append(0)
    #   cvPxMeanPur.append(0)
    # else:
    #   cvPxMeanRaw.append(cv.mean(cvPxDivRaw[-1], thres)[0])
    #   cvPxMeanPur.append(cv.mean(cvPxDivPur[-1], thres)[0])


    # npMeanRaw.append(np.mean(imRaw))
    # npMeanPur.append(np.mean(imPur))
    # npMeanDiv.append(np.mean(imDiv))

    # npDivRaw.append(np.divide(npMeanRaw[-1], npMeanDiv[-1]))
    # npDivPur.append(np.divide(npMeanPur[-1], npMeanDiv[-1]))







  # Spotwise with np/cv: Sum() & Divide()
  nRows = 2
  nCols = 3
  iX = range(nIm)
  targetFacY = [int(bSS/dSS)] * nIm

  
  figNames.append(str(_xyKey) + " Spotwise")
  figs.append(plt.figure())
  axes.append(figs[-1].subplots(nrows=nRows, ncols=nCols))

  figs[-1].suptitle("Spotwise: Spot @" + str(_xyKey))
  axes[-1][0,0].set_title("Brightness")
  axes[-1][0,0].set_xlabel("Image")
  axes[-1][0,0].set_ylabel("Brightness")
  axes[-1][0,0].plot(iX, npSumSpotRaw, ".--", label="Base")
  axes[-1][0,0].plot(iX, npSumSpotPur, ".--", label="BasePur")
  axes[-1][0,0].plot(iX, npSumSpotDiv, ".--", label="Div")
  axes[-1][0,0].plot(iX, npSumSpotPDi, ".--", label="DivPur")
  axes[-1][0,0].legend()

  axes[-1][1,0].set_title("Brightness-Factors")
  axes[-1][1,0].set_xlabel("Image")
  axes[-1][1,0].set_ylabel("Factor")
  axes[-1][1,0].plot(iX, targetFacY, "k--", label="BaseSS/DivSS (Reference)")
  axes[-1][1,0].plot(iX, npSpotDivRaw, ".--", label="Base/Div")
  axes[-1][1,0].plot(iX, npSpotPDiPur, ".--", label="BasePur/DivPur")
  axes[-1][1,0].legend()

  axes[-1][0,1].set_title("Area (count of active pixels)")
  axes[-1][0,1].set_xlabel("Image")
  axes[-1][0,1].set_ylabel("Area (active pixels)")
  axes[-1][0,1].plot(iX, nonZeroRaw, ".--", label="Base")
  axes[-1][0,1].plot(iX, nonZeroDiv, ".--", label="Div")
  axes[-1][0,1].legend()

  axes[-1][1,1].set_title("Area-Factor")
  axes[-1][1,1].set_xlabel("Image")
  axes[-1][1,1].set_ylabel("Factor")
  # axes[-1][1,1].plot(iX, targetFacY, "k--", label="BaseSS/DivSS (Reference)")
  axes[-1][1,1].plot(iX, nonZeroRawDiv, ".--", label="Base/Div")
  axes[-1][1,1].legend()

  axes[-1][1,2].set_title("Multiplied Factor")
  axes[-1][1,2].set_xlabel("Image")
  axes[-1][1,2].set_ylabel("Factor")
  # axes[-1][1,2].plot(iX, npFacMulRawDiv, ".--", label="RawBrightFac * RawAreaFac")
  axes[-1][1,2].plot(iX, targetFacY, "k--", label="BaseSS/DivSS (Reference)")
  axes[-1][1,2].plot(iX, npFacMulPurDiv, ".--", label="PurBrightFac * RawAreaFac")
  # axes[-1][1,2].plot(iX, npFacMulPurPDi, ".--", label="PurBrightFac * PurAreaFac")
  axes[-1][1,2].legend()

  axes[-1][0,2].set_title("Corrected Brightness")
  axes[-1][0,2].set_xlabel("Image")
  axes[-1][0,2].set_ylabel("Brightness")
  # axes[-1][0,2].plot(iX, npSumSpotRaw, "o", label="Raw Bright (Reference)")
  # axes[-1][0,2].plot(iX, npSumSpotPur, ".--", label="Purged Bright (Reference)")
  # axes[-1][0,2].plot(iX, npFacMulPurPDi, ".--", label="Corrected Bright")
  axes[-1][0,2].legend()


  # # Pixelwise with np/cv: divide() & mean
  # nRows = 2
  # nCols = 2

  # figNames.append(str(_xyKey) + " Pixelwise")
  # figs.append(plt.figure())
  # axes.append(figs[-1].subplots(nrows=nRows, ncols=nCols))

  # iX = range(nIm)
  # ZRaw = np.mean(cvPxDivRaw, axis=0)
  # ZPur = np.mean(cvPxDivPur, axis=0)
  # X, Y = np.meshgrid(range(ZRaw.shape[0]), range(ZRaw.shape[1]))
  # sc = axes[-1][0,0].scatter(X, Y, s=40**2, c=ZRaw, marker='s', cmap="gist_heat", label="Raw/Div")
  # # axes[-1][0,0].scatter(X, Y, s=3**2, c='k')
  # axes[-1][0,0].axis('equal')
  # figs[-1].colorbar(sc, ax=axes[-1][0,0])
   
  # axes[-1][0,1].plot(iX, npPxMeanRaw, "r.--", label="Raw/Div")
  # axes[-1][0,1].plot(iX, npPxMeanPur, "g.--", label="Pur/Div")

  # sc = axes[-1][1,0].scatter(X, Y, s=40**2, c=ZRaw, marker='s', cmap="gist_heat", label="Raw/Div")
  # # axes[-1][0,0].scatter(X, Y, s=7**2, c='k')
  # axes[-1][1,0].axis('equal')
  # figs[-1].colorbar(sc, ax=axes[-1][1,0])

  # axes[-1][1,1].plot(iX, npPxMeanRaw, "r.--", label="Raw/Div")
  # axes[-1][1,1].plot(iX, npPxMeanPur, "g.--", label="Pur/Div")

  

  # figs[-1].suptitle("Pixelwise: divide() & mean() @" + str(_xyKey))
  # axes[-1][0,1].set_ylabel("Numpy")
  # axes[-1][1,1].set_ylabel("OpenCV")
  # axes[-1][0,0].set_title("Px-Map (cv)")
  # axes[-1][0,1].set_title("Scalar Mean")

  # axes[-1][0,0].set_xticks(np.linspace(0, ZRaw.shape[0], 5, endpoint=True))
  # axes[-1][0,0].set_yticks(np.linspace(0, ZRaw.shape[1], 5, endpoint=True))
  # axes[-1][1,0].set_xticks(np.linspace(0, ZPur.shape[0], 5, endpoint=True))
  # axes[-1][1,0].set_yticks(np.linspace(0, ZPur.shape[1], 5, endpoint=True))




  # lines = []
  # labels = []
  # # for axis in figs[-1].axes:
  #   # Line, Label = axis.get_legend_handles_labels()
  # Line, Label = axes[-1][0,1].get_legend_handles_labels()
  # # print(Label)
  # for _iLab in range(len(Label)):
  #   if labels.__contains__(Label[_iLab]):
  #     continue
  #   lines.append(Line[_iLab])
  #   labels.append(Label[_iLab])
  # figs[-1].legend(lines, labels, loc="upper right")



# cmPerInch = 2.54
# dirName = os.path.dirname(pklPath)
# for _iFig in range(len(figs)):
#   figs[_iFig].set_size_inches(figWidth_cm / cmPerInch, figHeight_cm / cmPerInch)
#   figs[_iFig].savefig(os.path.join(dirName, figNames[_iFig] + ".png"), dpi=300)

print("Hallo")