from base64 import encode
from cmath import nan
from multiprocessing import connection
import os
from posixpath import basename
import time
import pickle
import glob
from tkinter import Y
from turtle import color, pos
import natsort
import parse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import axes3d
import FieldEmission as fe


from misc import Logger
from misc import LogLine
from misc import LogLineOK




def MeanRows(dp:fe.DataProvider, datPnts):
  # datPnts = 2
  colLen = dp.GetColumn(0).__len__()
  iterCnt =  colLen / datPnts
  iterCnt = int(iterCnt)

  for i in range(iterCnt):
    fRow = i * datPnts      # First row for mean
    lRow = fRow + datPnts   # Last row for mean
    rows = dp.GetRow(range(fRow, lRow))
    nRow = np.mean(rows, axis=0) # Along y-axis!
    dp.OverrideRow(i, nRow)
  
  dp.RemoveRows(range(iterCnt, colLen))

  return dp


def eFileKeys(fNames):
  keys = list()
  for name in fNames:
    parsed = parse.parse("Dev100_FEAR16v2({}).dat", os.path.basename(name))
    keys.append(parsed[0])
  return keys


def ManageFEAReCFData(dp:fe.DataProvider, resistorValue, meanDatPnts):
  dp.AppendColumn("CF", dp.GetColumn("Y"))
  dp.RemoveColumns(["Time", "Y", "Dev7"])
  dp.RemoveRows(0) # First line is black-line -> Remove from dataset
  MeanRows(dp, meanDatPnts)
  dp.DivideColumn("CF", resistorValue) # 10Meg resistor
  return dp

def ManageFEAReUDData(dp:fe.DataProvider, UVec, meanDatPnts):
  dp.AppendColumn("UD", dp.GetColumn("Y"))
  dp.RemoveColumns(["Time", "Y", "Dev7"])
  dp.RemoveRows(0) # First line is black-line -> Remove from dataset
  MeanRows(dp, meanDatPnts)
  dp.SubtractColumnFrom("UD", UVec)
  return dp

def RotateFEARKeys(KeyList):

  # bak = KeyList[0]
  # KeyList[0] = KeyList[1]
  # KeyList[1] = KeyList[2]
  # KeyList[2] = bak
  # KeyList[3] = KeyList[3] # Key 3 doesn't change

  return KeyList


def CollectImagePlotXY(imData):
  imKeys = list()
  for key in imData["ValidXYKeys"]: # Collect all keys for xy-sorting
    imKeys.append(key)
  imKeys = sorted(imKeys , key=lambda k: [k[1], k[0]]) # Sort by x then by y!
  # collect brightnesses in vectors!
  imData["Plot"] = dict()
  for key in imKeys:
    imData["Plot"][key] = dict()
    imData["Plot"][key]["xSpot"] = list()
    imData["Plot"][key]["bSpot"] = list()
    imData["Plot"][key]["bImage"] = list()
    for iPnt in range(mPnts):
      if not imData["ValidXYKeys"][key]["ImgIndex"].__contains__(iPnt):
        imData["Plot"][key]["xSpot"].append(0)
        imData["Plot"][key]["bSpot"].append(0.0)
        imData["Plot"][key]["bImage"].append(0.0)
        continue

      xSpot = iPnt
      iSpot = imData["ValidXYKeys"][key]["ImgIndex"].index(iPnt)
      bSpot = imData["ValidXYKeys"][key]["ExposedCombination"][iSpot]["ScaledBrightness"]
      bImg = imData["ValidXYKeys"][key]["ExposedCombination"][iSpot]["RefCircle"]["ImgBrightness"]
      imData["Plot"][key]["xSpot"].append(xSpot)
      imData["Plot"][key]["bSpot"].append(bSpot)
      imData["Plot"][key]["bImage"].append(bImg)
  return imKeys, imData




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














#testwise
pxMeanRaw = list()
pxMeanPurged = list()



# root = r"C:\Users\ham38517\Downloads\220725 PiCam Einzelemitter\Ausw\01 USweep Activation with IMax 100nA (ab hier 10Meg)\220804_143127\"

plotCol = {100000: {10000: "tab:blue", 5000: "tab:orange", 1000: "tab:green" },   # 100ms: 10ms, 5ms, 1ms
           10000 : {                   5000: "tab:red"   , 1000: "tab:purple"},   # 10ms:        5ms, 1ms
           5000  : {                                       1000: "tab:cyan"  },   # 5ms:              1ms
 }

baseDir = r"C:\Users\ham38517\Downloads\220725 PiCam Einzelemitter\Ausw"
dpi = 150
pxWidth = 1920
aspectRatio = 16/9
pxHeight = pxWidth / aspectRatio
meanNPoints = 2

SkipBadSubdirs = True



logger = Logger(os.path.join(baseDir, "Auswertung.log"))
t0 = time.time()
_XXBadDirs = list()
for root, dirs, files in os.walk(baseDir):
  # Firstly check if path contains one of the already marked bad measurement-folders
  if any(root.__contains__(_bDir) for _bDir in _XXBadDirs):
    LogLine(t0, "Bad parent - skipped: ", root, wFill=0, end="\n")
    continue
  # Folder marked as bad measurement -> Skip
  if root.endswith("_XX"):
    if SkipBadSubdirs == True:
      _XXBadDirs.append(root)
    LogLine(t0, "Marked as bad - skipped: ", root, wFill=0, end="\n")
    continue


  LogLine(t0, "Entering: ", root, end="\n")
  print("")
  LogLine(t0, "Checking for *.dat and *.pkl files", "", end="\n")
  if not any(file.endswith(".dat") for file in files) and not any(file.endswith(".pkl") for file in files):
    print("Nothing interesting found. Skipping directory...".rjust(18) + "\n")
    continue

  LogLine(None, "Found files. Grabbing *.pkl filenames", wFill=0, end="\n")
  pklFile = "PMP*brightFactors*.pkl"
  bFac = GrabPklFile(os.path.join(root, pklFile))
  LogLine(t0, "Reconstructed pickle-structure")
  LogLineOK()


  # Plot
  lFac = r"$Factors$"
  lMean = r"$Mean + Error$"

  pltCol = [[]]

  nRows = 2
  nCols = 2
  figRaw = plt.figure()
  figPur = plt.figure()
  fig3dRaw = plt.figure()
  fig3dPur = plt.figure()
  axRaw = figRaw.subplots(nrows=nRows, ncols=nCols)
  axPur = figPur.subplots(nrows=nRows, ncols=nCols)
  ax3dRaw = fig3dRaw.subplots(nrows=nRows, ncols=nCols, subplot_kw=dict(projection='3d'))
  ax3dPur = fig3dPur.subplots(nrows=nRows, ncols=nCols, subplot_kw=dict(projection='3d'))
  # fig3d.axes(projection="3d")


  # vX = np.linspace(0, 20, 20)#.reshape([3,3])
  # vY = np.linspace(0, 20, 20)#.reshape([3,3])
  # vZ = np.linspace(11, 99, 20*20).reshape([20,20])
  # xp, yp = np.meshgrid(vX, vY)
  # xp = xp.flatten()
  # yp = yp.flatten()
  # zp = np.zeros(20*20)
  # dx = np.zeros(20*20) + 0.5
  # dy = np.zeros(20*20) + 0.5
  # dz = vZ.ravel()

  # cmap = cm.get_cmap("plasma")
  # norm = Normalize(vmin=min(dz), vmax=max(dz))
  # cols = cmap(norm(dz))
  # ax3d[0,0].bar3d(xp, yp, zp, dx, dy, dz, color=cols)
  # sc = cm.ScalarMappable(cmap=cmap,norm=norm)
  # sc.set_array([])
  # fig3d.colorbar(sc, ax=ax3d[0,0])

  # bx = [[0 for i in range(nCols)] for j in range(nRows)]
  for _iR in range(nRows):
    for _iC in range(nCols):
      # bx[_iR][_iC] = ax[_iR, _iC].twinx()
      pass
  

  ssKeys = list(bFac.keys())
  # # for Spots
  # for _iBKey in range(len(ssKeys)):
  #   _bKey = ssKeys[_iBKey]

  #   dKeys = list(bFac[_bKey].keys())
  #   for _iDKey in range(len(dKeys)):
  #     _dKey = dKeys[_iDKey]

  #     xyKeys = list(bFac[_bKey][_dKey].keys())

  #     for _iR in range(nRows):
  #       for _iC in range(nCols):
  #         _i = _iR * nRows +_iC
  #         try:
  #           _xyKey = xyKeys[_i]
  #         except:
  #           continue
          
  #         # Spotwise raw
  #         cSpot = bFac[_bKey][_dKey][_xyKey]
  #         cFac = cSpot["SpotFactor"]["Raw"]
  #         sptMean = np.mean(cFac)
  #         sptStd = np.std(cFac)

  #         vecLen = len(cFac)
  #         theoretical = cSpot["MathScale"]
  #         axRaw[_iR, _iC].plot([theoretical] * vecLen, cFac, "x", label=str(_bKey/1000) + "ms/" + str(_dKey/1000) + "ms", color=plotCol[_bKey][_dKey])
  #         axRaw[_iR][_iC].errorbar(theoretical, sptMean, yerr=sptStd, fmt = 'o',color = 'black', ecolor = 'red', capsize=5)


  #         # Spotwise purged
  #         # cSpot = bFac[_bKey][_dKey][_xyKey]
  #         cFac = cSpot["SpotFactor"]["Purged"]
  #         sptMean = np.mean(cFac)
  #         sptStd = np.std(cFac)

  #         vecLen = len(cFac)
  #         # theoretical = cSpot["MathScale"]
  #         axPur[_iR, _iC].plot([theoretical] * vecLen, cFac, "x", label=str(_bKey/1000) + "ms/" + str(_dKey/1000) + "ms", color=plotCol[_bKey][_dKey])
  #         axPur[_iR][_iC].errorbar(theoretical, sptMean, yerr=sptStd, fmt = 'o',color = 'black', ecolor = 'red', capsize=5)

  


  # Pixelwise (only 100/10ms)
  _bKey = ssKeys[0]
  _dKey = ssKeys[1]
  xyKeys = list(bFac[_bKey][_dKey].keys())

  for _iR in range(nRows):
    for _iC in range(nCols):
      _i = _iR * nRows +_iC
      try:
        _xyKey = xyKeys[_i]
      except:
        continue
      
      # Spotwise raw
      cSpot = bFac[_bKey][_dKey][_xyKey]
      cFac = cSpot["SpotFactor"]["Raw"]
      sptMean = np.mean(cFac)
      sptStd = np.std(cFac)

      vecLen = len(cFac)
      theoretical = cSpot["MathScale"]
      axRaw[_iR, _iC].plot([theoretical] * vecLen, cFac, "x", label=str(_bKey/1000) + "ms/" + str(_dKey/1000) + "ms", color=plotCol[_bKey][_dKey])
      axRaw[_iR][_iC].errorbar(theoretical, sptMean, yerr=sptStd, fmt = 'o',color = 'black', ecolor = 'red', capsize=5)


      # Spotwise purged
      # cSpot = bFac[_bKey][_dKey][_xyKey]
      cFac = cSpot["SpotFactor"]["Purged"]
      sptMean = np.mean(cFac)
      sptStd = np.std(cFac)

      vecLen = len(cFac)
      # theoretical = cSpot["MathScale"]
      axPur[_iR, _iC].plot([theoretical] * vecLen, cFac, "x", label=str(_bKey/1000) + "ms/" + str(_dKey/1000) + "ms", color=plotCol[_bKey][_dKey])
      axPur[_iR][_iC].errorbar(theoretical, sptMean, yerr=sptStd, fmt = 'o',color = 'black', ecolor = 'red', capsize=5)



      # PxWise Raw
      try:
        cAr = cSpot["PxFactor"]["AreaWindow"][0]
        xCntPx = cSpot["PxFactor"]["Raw"][0].shape[1]
        yCntPx = cSpot["PxFactor"]["Raw"][0].shape[0]
        x = np.linspace(0, xCntPx, xCntPx, endpoint=True)
        y = np.linspace(0, xCntPx, xCntPx, endpoint=True)
        # Load z and convert all nan, inf and 0 to nan! (because of nanmean!)
        z = np.nan_to_num(cSpot["PxFactor"]["Raw"], copy=True, nan=nan, posinf=nan, neginf=nan)
        z[z == 0] = nan
        z = np.nanmean(z, axis=0)
        pxMeanRaw.append(np.nanmean(z)) # testwise
        # z = np.mean(cSpot["PxFactor"]["Raw"], axis=0)
        z = np.nan_to_num(z, copy=True, nan=0, posinf=0, neginf=0) # Convert back nans to 0 for plot!

        xx, yy = np.meshgrid(x, y)
        xx = xx.flatten()
        yy = yy.flatten()
        zz = np.zeros(xCntPx * yCntPx)

        dx = np.zeros(xCntPx * yCntPx) + 0.6
        dy = np.zeros(xCntPx * yCntPx) + 0.6
        dz = z.ravel()
        # np.nan_to_num(dz, copy=False, nan=0, posinf=0, neginf=0)

        cmap = cm.get_cmap("plasma")
        norm = Normalize(vmin=min(dz), vmax=max(dz))
        cols = cmap(norm(dz))
        ax3dRaw[_iR, _iC].bar3d(xx, yy, zz, dx, dy, dz, color=cols)
        sc = cm.ScalarMappable(cmap=cmap,norm=norm)
        sc.set_array([])
        fig3dRaw.colorbar(sc, ax=ax3dRaw[_iR,_iC])
      except:
        pass




      # PxWise Purged
      try:
        # cAr = cSpot["PxFactor"]["AreaWindow"][0]
        xCntPx = cSpot["PxFactor"]["Purged"][0].shape[1]
        yCntPx = cSpot["PxFactor"]["Purged"][0].shape[0]
        x = np.linspace(0, xCntPx, xCntPx, endpoint=True)
        y = np.linspace(0, xCntPx, xCntPx, endpoint=True)
        # Load z and convert all nan, inf and 0 to nan! (because of nanmean!)
        z = np.nan_to_num(cSpot["PxFactor"]["Purged"], copy=True, nan=nan, posinf=nan, neginf=nan)
        z[z == 0] = nan
        z = np.nanmean(z, axis=0)
        pxMeanPurged.append(np.nanmean(z)) # testwise
        # z = np.mean(cSpot["PxFactor"]["Raw"], axis=0)
        z = np.nan_to_num(z, copy=True, nan=0, posinf=0, neginf=0) # Convert back nans to 0 for plot!

        xx, yy = np.meshgrid(x, y)
        xx = xx.flatten()
        yy = yy.flatten()
        zz = np.zeros(xCntPx * yCntPx)

        dx = np.zeros(xCntPx * yCntPx) + 0.6
        dy = np.zeros(xCntPx * yCntPx) + 0.6
        dz = z.ravel()
        np.nan_to_num(dz, copy=False, nan=0, posinf=0, neginf=0)

        cmap = cm.get_cmap("plasma")
        norm = Normalize(vmin=min(dz), vmax=max(dz))
        cols = cmap(norm(dz))
        ax3dPur[_iR, _iC].bar3d(xx, yy, zz, dx, dy, dz, color=cols)
        sc = cm.ScalarMappable(cmap=cmap,norm=norm)
        sc.set_array([])
        fig3dPur.colorbar(sc, ax=ax3dPur[_iR,_iC])
      except:
        pass


  lines = []
  labels = []
  for axis in figRaw.axes:
    Line, Label = axis.get_legend_handles_labels()
    # print(Label)
    for _iLab in range(len(Label)):
      if labels.__contains__(Label[_iLab]):
        continue
      lines.append(Line[_iLab])
      labels.append(Label[_iLab])
  figRaw.legend(lines, labels, loc="upper right")
  figRaw.suptitle("Brightness-factors of entire spots")
  fig3dRaw.suptitle("Brightness-factors of each pixels (mean)")


  xyKeys = xyKeys = list(bFac[ssKeys[0]][ssKeys[1]].keys())
  for _iR in range(nRows):
    for _iC in range(nCols):
      _i = _iR * nRows +_iC
      axRaw[_iR, _iC].set_title(str.format("Spot @{}", xyKeys[_i]))
      # axRaw[_iR, _iC].set_xticks(range(-10,110, 10))
      # axRaw[_iR, _iC].set_yticks(range(-10,110, 10))
      # axRaw[_iR, _iC].set_xlim([-10, 110])
      # axRaw[_iR, _iC].set_ylim([-10, 110])

plt.show()
print("Finished")