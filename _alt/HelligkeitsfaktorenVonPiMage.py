from cProfile import label
import os
import pickle
import glob
import random
from tkinter.messagebox import NO
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
from misc import GrabPklFile
from misc import CollectEachValueOnceFromVector





# OTH-Folder
parentDir = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\02 Alle Zusammen\230223_084426 1kV 250nA"
# parentDir = r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Auswertung"

# Ketek-Folder

fNameBrightSet = "PMP_BrightSets4Brightness.pkl"
fNameDivFactor = "PMP_DivFactors4Brightness.pkl"
fNamePxAreaCnt = "PMP_PxAreaCnts4Brightness.pkl"
fNameCombiFact = "PMP_CombinedFactors4Brightness.pkl"
fNameScaledAny = "PMP_ScaledAnyBrightnesses.pkl"
fNameImgOvrExp = "PMP_ScaledWhereOverexposedPxImgs.pkl"
fNameWhrOvrBri = "PMP_ScaledWhereOverexposedBrightnesses.pkl"

for pklFolder, dirs, files in os.walk(parentDir):
  LogLine(None, "Entering: ", pklFolder, yFill=15, wFill=0, end="\n")

  # wDir = r"C:\Users\ham38517\Downloads\PiCam\220725 PiCam Einzelemitter\Ausw\03 1h I500nA U1400V\220804_175655 (#1)"
  rawBright = GrabPklFile(os.path.join(pklFolder, fNameBrightSet))
  divFactor = GrabPklFile(os.path.join(pklFolder, fNameDivFactor))
  areaCnts  = GrabPklFile(os.path.join(pklFolder, fNamePxAreaCnt))
  combiFac  = GrabPklFile(os.path.join(pklFolder, fNameCombiFact))
  sclBright = GrabPklFile(os.path.join(pklFolder, fNameScaledAny))
  ovrExpImg = GrabPklFile(os.path.join(pklFolder, fNameImgOvrExp))
  ovrExpBri = GrabPklFile(os.path.join(pklFolder, fNameWhrOvrBri))


  if rawBright == None or divFactor == None or areaCnts == None or combiFac == None or sclBright == None:
    LogLine(None, " - Skipping: ", pklFolder, yFill=15, wFill=0, end="\n\n")
    continue
  LogLine(None, "Reading pickles: ")
  LogLineOK()


  figWidth_cm = 60
  figHeight_cm = figWidth_cm / (16/9)
  figDPI = 300

  LogLine(None, "Plotting figures", end="\n")
  nRows = 3
  nCols = 3
  doOnly_nXY = 8 # Stop after plotting n Points; -1 -> Do all points!
    
  # Define your result-keys
  _bKeys = list(rawBright.keys())
  _bKeys = [_bKeys[0]]
  for _iBase in range(len(_bKeys)):
    _bKey = _bKeys[_iBase]
    
    _dKeys = list(rawBright[_bKey]["Div"].keys())
    _dKeys = [_dKeys[0]]
    for _iDiv in range(0, len(_dKeys)):
      _dKey = _dKeys[_iDiv]

      # bDatSel = bDat[bSS]
      # # bImgSel = bImg[bSS][dSS]
      # dDatSel = bDat[bSS]["Div"][dSS]

      figNames = list()
      figs = list()
      axes = list()

      _xyKeys = list(rawBright[_bKey]["Div"][_dKey]["Spot"].keys())
      nCnt = 0
      for _iXY in range(len(_xyKeys)):
        _xyKey = _xyKeys[_iXY]
        if doOnly_nXY >= 0 and nCnt >= doOnly_nXY: # Stop if there are too much points!
          LogLine(None, "Stopped: ", "\"doOnly_nXY\" = " + str(doOnly_nXY))
          break
        nCnt += 1

        try:
          # bCheck = bDatSel["Spots"][_xyKey]
          # dCheck = dDatSel["Spots"][_xyKey]
          xArr = np.where(np.not_equal(rawBright[_bKey]["Spot"][_xyKey]["Blank"], rawBright[_bKey]["Spot"][_xyKey]["Clean"]))[0]

          figs.append(plt.figure())
          figNames.append("Base " + str.format("{:03d}", int(_bKey / 1000)) + "ms, Div " + str.format("{:03d}", int(_dKey / 1000)) + "ms; " + str.format("{:03d}", len(figs)) + " Spot@" + str(_xyKey))
          axes.append(figs[-1].subplots(nrows=nRows, ncols=nCols))

          _nPnts = len(rawBright[_bKey]["Full"]["Blank"])
          xVal = list(range(_nPnts))

          figs[-1].suptitle("Brightnesscorrection of " + figNames[-1])
          axes[-1][0,0].set_title("Brightness")
          axes[-1][0,0].set_xlabel("Image")
          axes[-1][0,0].set_ylabel("Brightness")
          axes[-1][0,0].plot(xVal, rawBright[_bKey]              ["Spot"][_xyKey]["Blank"], ".--", label=r"$Blank_{" + str(int(_bKey / 1000)) + "}$")
          axes[-1][0,0].plot(xVal, rawBright[_bKey]              ["Spot"][_xyKey]["Clean"], ".--", label=r"$Clean_{" + str(int(_bKey / 1000)) + "}$")
          axes[-1][0,0].plot(xVal, rawBright[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Blank"], ".--", label=r"$Blank_{" + str(int(_dKey / 1000)) + "}$")
          axes[-1][0,0].plot(xVal, rawBright[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Clean"], ".--", label=r"$Clean_{" + str(int(_dKey / 1000)) + "}$")
          # # Overexposed marker
          # axes[-1][0,0].plot(xArr,[rawBright[_bKey]              ["Spot"][_xyKey]["Blank"][xA] for xA in xArr], "o", markersize=8, fillstyle="none", color="purple")
          # axes[-1][0,0].plot(xArr,[rawBright[_bKey]              ["Spot"][_xyKey]["Clean"][xA] for xA in xArr], "o", markersize=8, fillstyle="none", color="purple")
          # axes[-1][0,0].plot(xArr,[rawBright[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Blank"][xA] for xA in xArr], "o", markersize=8, fillstyle="none", color="purple")
          # axes[-1][0,0].plot(xArr,[rawBright[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Clean"][xA] for xA in xArr], "o", markersize=8, fillstyle="none", color="purple")
          axes[-1][0,0].legend()

          axes[-1][1,0].set_title("Brightness-Factors")
          axes[-1][1,0].set_xlabel("Image")
          axes[-1][1,0].set_ylabel("Factor")
          axes[-1][1,0].plot(xVal, divFactor[_bKey][_dKey]["Theory"]                                          , "k--", label="Ref.")                             # (" + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          axes[-1][1,0].plot(xVal, divFactor[_bKey][_dKey]["Spot"][_xyKey]["SpotDiv"]  ["Blank"]              , ".--", label=r"$SpotBlank$")                          # + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)))
          axes[-1][1,0].plot(xVal, divFactor[_bKey][_dKey]["Spot"][_xyKey]["SpotDiv"]  ["Clean"]              , ".--", label=r"$SpotClean$")                       # + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)))
          axes[-1][1,0].plot(xVal, divFactor[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Blank"]              , ".--", label=r"$PxwiseBlank$")              # (" + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          axes[-1][1,0].plot(xVal, divFactor[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Clean"]              , ".--", label=r"$PxwiseClean$")           # (" + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          # axes[-1][1,0].plot(xVal, combiFac [_bKey][_dKey]["Spot"][_xyKey]["Theory"]   ["/BlankArea"]         , ".--", label=r"$TraceBlank$")                   # + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          # axes[-1][1,0].plot(xVal, combiFac [_bKey][_dKey]["Spot"][_xyKey]["Theory"]   ["/CleanArea"]         , ".--", label=r"$TraceClean$")                # + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          # axes[-1][1,0].plot(xVal, combiFac [_bKey][_dKey]["Spot"][_xyKey]["SpotDiv"]  ["Blank&Clean"]["Mean"], ".--", label=r"$Mean(Blank, Clean)$")                # + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          # axes[-1][1,0].plot(xVal, combiFac [_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Blank&Clean"]["Mean"], ".--", label=r"$Mean(Blank, Clean)$")                # + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          # # Overexposed marker
          # axes[-1][1,0].plot(xArr,[divFactor[_bKey][_dKey]["Theory"]                                 [xA] for xA in xArr], "o", markersize=8, fillstyle="none", color="purple")
          # axes[-1][1,0].plot(xArr,[divFactor[_bKey][_dKey]["Spot"][_xyKey]["SpotDiv"]  ["Blank"]     [xA] for xA in xArr], "o", markersize=8, fillstyle="none", color="purple")
          # axes[-1][1,0].plot(xArr,[divFactor[_bKey][_dKey]["Spot"][_xyKey]["SpotDiv"]  ["Clean"]     [xA] for xA in xArr], "o", markersize=8, fillstyle="none", color="purple")
          # axes[-1][1,0].plot(xArr,[divFactor[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Blank"]     [xA] for xA in xArr], "o", markersize=8, fillstyle="none", color="purple")
          # axes[-1][1,0].plot(xArr,[divFactor[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Clean"]     [xA] for xA in xArr], "o", markersize=8, fillstyle="none", color="purple")
          # axes[-1][1,0].plot(xArr,[combiFac [_bKey][_dKey]["Spot"][_xyKey]["Theory"]   ["/BlankArea"][xA] for xA in xArr], "o", markersize=8, fillstyle="none", color="purple")
          # axes[-1][1,0].plot(xArr,[combiFac [_bKey][_dKey]["Spot"][_xyKey]["Theory"]   ["/CleanArea"][xA] for xA in xArr], "o", markersize=8, fillstyle="none", color="purple")
          axes[-1][1,0].legend()


          axes[-1][0,1].set_title("Area (count of active pixels)")
          axes[-1][0,1].set_xlabel("Image")
          axes[-1][0,1].set_ylabel("Area (active pixels)")
          axes[-1][0,1].plot(xVal, areaCnts[_bKey]              ["Spot"][_xyKey]["Blank"], ".--", label=r"$Blank_{" + str(int(_bKey / 1000)) + "}$")     # + str(int(bSS / 1000)))
          axes[-1][0,1].plot(xVal, areaCnts[_bKey]              ["Spot"][_xyKey]["Clean"], ".--", label=r"$Clean_{" + str(int(_bKey / 1000)) + "}$")  # + str(int(bSS / 1000)))
          axes[-1][0,1].plot(xVal, areaCnts[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Blank"], ".--", label=r"$Blank_{" + str(int(_dKey / 1000)) + "}$")      # + str(int(dSS / 1000)))
          axes[-1][0,1].plot(xVal, areaCnts[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Clean"], ".--", label=r"$Clean_{" + str(int(_dKey / 1000)) + "}$")   # + str(int(dSS / 1000)))
          axes[-1][0,1].legend()


          axes[-1][1,1].set_title("Area-Factor")
          axes[-1][1,1].set_xlabel("Image")
          axes[-1][1,1].set_ylabel("Factor")
          # axes[-1][1,1].plot(iX, targetFacY, "k--", label="BaseSS/DivSS (Reference)")
          axes[-1][1,1].plot(xVal, divFactor[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"]["Blank"], ".--", label="Blank")    # + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)))
          axes[-1][1,1].plot(xVal, divFactor[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"]["Clean"], ".--", label="Clean")    # + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)))
          axes[-1][1,1].legend()


          axes[-1][2,1].set_title("Multiplied Factor")
          axes[-1][2,1].set_xlabel("Image")
          axes[-1][2,1].set_ylabel("Factor")
          # axes[-1][2,1].plot(iX, npFacMulRawDiv, ".--", label="RawBrightFac * RawAreaFac")
          axes[-1][2,1].plot(xVal, divFactor[_bKey][_dKey]["Theory"]                                         , "k--", label=r"$Ref. (" + str(int(_bKey / 1000)) + "/" + str(int(_dKey / 1000)) + ")$")
          axes[-1][2,1].plot(xVal, combiFac[_bKey][_dKey]["Spot"][_xyKey]["SpotDiv"]  ["Clean"]      ["xAreaBlank"], ".--", label=r"$SpotDiv*AreaBlank$")        # (" + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          axes[-1][2,1].plot(xVal, combiFac[_bKey][_dKey]["Spot"][_xyKey]["SpotDiv"]  ["Clean"]      ["xAreaClean"], ".--", label=r"$SpotDiv*AreaClean$")          # (" + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          axes[-1][2,1].plot(xVal, combiFac[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Clean"]      ["xAreaBlank"], ".--", label=r"$MeanPxDiv*AreaBlank$")        # (" + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          axes[-1][2,1].plot(xVal, combiFac[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Clean"]      ["xAreaClean"], ".--", label=r"$MeanPxDiv*AreaClean$")          # (" + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          axes[-1][2,1].plot(xVal, combiFac[_bKey][_dKey]["Spot"][_xyKey]["SpotDiv"]  ["Blank&Clean"]["xAreaBlank"], ".--", label=r"$SpotDivBl&Cl*AreaBlank$")        # (" + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          axes[-1][2,1].plot(xVal, combiFac[_bKey][_dKey]["Spot"][_xyKey]["SpotDiv"]  ["Blank&Clean"]["xAreaClean"], ".--", label=r"$SpotDivBl&Cl*AreaBlank$")        # (" + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          axes[-1][2,1].plot(xVal, combiFac[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Blank&Clean"]["xAreaBlank"], ".--", label=r"$MeanPxDivBl&Cl*AreaClean$")          # (" + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          axes[-1][2,1].plot(xVal, combiFac[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Blank&Clean"]["xAreaClean"], ".--", label=r"$MeanPxDivBl&Cl*AreaClean$")          # (" + str(int(bSS / 1000)) + "/" + str(int(dSS / 1000)) + ")")
          # axes[-1][2,1].plot(iX, npFacMulPurPDi, ".--", label="PurBrightFac * PurAreaFac")
          axes[-1][2,1].legend()


          axes[-1][0,2].set_title("Brightnesscorrection (any spot)")
          axes[-1][0,2].set_xlabel("Image")
          axes[-1][0,2].set_ylabel("Brightness")
          axes[-1][0,2].plot(xVal, rawBright[_bKey]       ["Spot"][_xyKey]["Blank"]                                   , "o"  , label="Base")
          axes[-1][0,2].plot(xVal, rawBright[_bKey]       ["Spot"][_xyKey]["Clean"]                                   , "D"  , label="BasePur")
          axes[-1][0,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xTheory"]          , ".--", label=r"$Spot*Ref.$")
          axes[-1][0,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xSpotDivBlank"]    , ".--", label=r"$Spot*SpotDiv_{Blank}$")
          axes[-1][0,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xSpotDivClean"]    , ".--", label=r"$Spot*SpotDiv_{Clean}$")
          axes[-1][0,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xMeanPxDivBlank"]  , ".--", label=r"$Spot*PixelDiv_{Blank}$")
          axes[-1][0,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xMeanPxDivClean"]  , ".--", label=r"$Spot*PixelDiv_{Clean}$")
          axes[-1][0,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xTheory/BlankArea"], ".--", label=r"$Spot*Traceback_{Blank}$")
          axes[-1][0,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xTheory/CleanArea"], ".--", label=r"$Spot*Traceback_{Clean}$")

    #         axes[-1][0,2].plot(xVal, bDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["Theoretical"]              , ".--", label="Pixels * Theoretical")
    #         axes[-1][0,2].plot(xVal, bDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["ImgSpotDiv"]["Raw"]        , ".--", label="Pixels * SpotDivRaw")
    #         axes[-1][0,2].plot(xVal, bDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["ImgSpotDiv"]["Purged"]     , ".--", label="Pixels * SpotDivPurged")
    #         axes[-1][0,2].plot(xVal, bDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["ImgPixelDiv"]["RawMean"]   , ".--", label="Pixels * PixelDivRaw")
    #         axes[-1][0,2].plot(xVal, bDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["ImgPixelDiv"]["PurgedMean"], ".--", label="Pixels * PixelDivPurged")
    #         axes[-1][0,2].plot(xVal, bDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["Traceback"]["Raw"]         , ".--", label="Spot * TracebackRaw")
    #         axes[-1][0,2].plot(xVal, bDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["Traceback"]["Purged"]      , ".--", label="Spot * TracebackPurged")
          axes[-1][0,2].legend()


          axes[-1][1,2].set_title("Brightnesscorrection (overexposed pixels)")
          axes[-1][1,2].set_xlabel("Image")
          axes[-1][1,2].set_ylabel("Brightness")
          axes[-1][1,2].plot(xVal, rawBright[_bKey]       ["Spot"][_xyKey]["Blank"]                         , "o"  , label="Base")
          axes[-1][1,2].plot(xVal, rawBright[_bKey]       ["Spot"][_xyKey]["Clean"]                         , "D"  , label="BasePur")
          axes[-1][1,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xTheory"]          , ".--", label=r"$Pxl*Ref.$")
          axes[-1][1,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xSpotDivBlank"]    , ".--", label=r"$Pxl*SpotDiv_{Blank}$")
          axes[-1][1,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xSpotDivClean"]    , ".--", label=r"$Pxl*SpotDiv_{Clean}$")
          axes[-1][1,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xMeanPxDivBlank"]  , ".--", label=r"$Pxl*PixelDiv_{Blank}$")
          axes[-1][1,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xMeanPxDivClean"]  , ".--", label=r"$Pxl*PixelDiv_{Clean}$")
          axes[-1][1,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xTheory/BlankArea"], ".--", label=r"$Pxl*Traceback_{Blank}$")
          axes[-1][1,2].plot(xVal, sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xTheory/CleanArea"], ".--", label=r"$Pxl*Traceback_{Clean}$")

    #         axes[-1][1,2].plot(xVal, dDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["Theoretical"]              , ".--", label="Pixels * Theoretical")
    #         axes[-1][1,2].plot(xVal, dDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["ImgSpotDiv"]["Raw"]        , ".--", label="Pixels * SpotDivRaw")
    #         axes[-1][1,2].plot(xVal, dDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["ImgSpotDiv"]["Purged"]     , ".--", label="Pixels * SpotDivPurged")
    #         axes[-1][1,2].plot(xVal, dDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["ImgPixelDiv"]["RawMean"]   , ".--", label="Pixels * PixelDivRaw")
    #         axes[-1][1,2].plot(xVal, dDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["ImgPixelDiv"]["PurgedMean"], ".--", label="Pixels * PixelDivPurged")
    #         axes[-1][1,2].plot(xVal, dDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["Traceback"]["Raw"]         , ".--", label="Pixels * TracebackRaw")
    #         axes[-1][1,2].plot(xVal, dDatSel["Spots"][_xyKey]["Brightnesses"]["UpscaledPixels"]["Traceback"]["Purged"]      , ".--", label="Pixels * TracebackPurged")
          axes[-1][1,2].legend()


          axes[-1][2,2].set_title(r"$Scaled: Any Bright_{Spot, scaled}/Bright_{Blank}$")
          axes[-1][2,2].set_xlabel("Image")
          axes[-1][2,2].set_ylabel("Norm. Brightness")
          # xVal, rawBright[_bKey]       ["Spot"][_xyKey]["Blank"]                                   , "o"  , label="Base")
          # xVal, rawBright[_bKey]       ["Spot"][_xyKey]["Clean"]                                   , "D"  , label="BasePur")
          axes[-1][2,2].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xTheory"]          , rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$Ref.$")
          axes[-1][2,2].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xSpotDivBlank"]    , rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$SpotDiv_{Blank}$")
          axes[-1][2,2].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xSpotDivClean"]    , rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$SpotDiv_{Clean}$")
          axes[-1][2,2].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xMeanPxDivBlank"]  , rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$PixelDiv_{Blank}$")
          axes[-1][2,2].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xMeanPxDivClean"]  , rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$PixelDiv_{Clean}$")
          axes[-1][2,2].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xTheory/BlankArea"], rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$Traceback_{Blank}$")
          axes[-1][2,2].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]["xTheory/CleanArea"], rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$Traceback_{Clean}$")
          # axes[-1][2,2].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledSpots"]["Theoretical"]              , ".--", label="Theoretical")
          # axes[-1][2,2].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledSpots"]["ImgSpotDiv"]["Raw"]        , ".--", label="SpotDivRaw")
          # axes[-1][2,2].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledSpots"]["ImgSpotDiv"]["Purged"]     , ".--", label="SpotDivPurged")
          # axes[-1][2,2].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledSpots"]["ImgPixelDiv"]["RawMean"]   , ".--", label="PixelDivRaw")
          # axes[-1][2,2].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledSpots"]["ImgPixelDiv"]["PurgedMean"], ".--", label="PixelDivPurged")
          # axes[-1][2,2].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledSpots"]["Traceback"]["Raw"]         , ".--", label="TracebackRaw")
          # axes[-1][2,2].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledSpots"]["Traceback"]["Purged"]      , ".--", label="TracebackPurged")
          axes[-1][2,2].legend()


          axes[-1][2,0].set_title(r"$Scaled: Any Bright_{Pxls, scaled}/Bright_{Blank}$")
          axes[-1][2,0].set_xlabel("Image")
          axes[-1][2,0].set_ylabel("Norm. Brightness")
          axes[-1][2,0].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xTheory"]          , rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$Ref./Spot_{Blank}$")
          axes[-1][2,0].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xSpotDivBlank"]    , rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$SpotDiv_{Blank}/Spot_{Blank}$")
          axes[-1][2,0].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xSpotDivClean"]    , rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$SpotDiv_{Clean}/Spot_{Blank}$")
          axes[-1][2,0].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xMeanPxDivBlank"]  , rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$PixelDiv_{Blank}/Spot_{Blank}$")
          axes[-1][2,0].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xMeanPxDivClean"]  , rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$PixelDiv_{Clean}/Spot_{Blank}$")
          axes[-1][2,0].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xTheory/BlankArea"], rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$Traceback_{Blank}/Spot_{Blank}$")
          axes[-1][2,0].plot(xVal, np.nan_to_num(np.divide(sclBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]["xTheory/CleanArea"], rawBright[_bKey]["Spot"][_xyKey]["Blank"])), ".--", label=r"$Traceback_{Clean}/Spot_{Blank}$")
    #         axes[-1][2,0].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledPixels"]["Theoretical"]              , ".--", label="Theoretical")
    #         axes[-1][2,0].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledPixels"]["ImgSpotDiv"]["Raw"]        , ".--", label="SpotDivRaw")
    #         axes[-1][2,0].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledPixels"]["ImgSpotDiv"]["Purged"]     , ".--", label="SpotDivPurged")
    #         axes[-1][2,0].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledPixels"]["ImgPixelDiv"]["RawMean"]   , ".--", label="PixelDivRaw")
    #         axes[-1][2,0].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledPixels"]["ImgPixelDiv"]["PurgedMean"], ".--", label="PixelDivPurged")
    #         axes[-1][2,0].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledPixels"]["Traceback"]["Raw"]         , ".--", label="TracebackRaw")
    #         axes[-1][2,0].plot(xVal, dDatSel["Spots"][_xyKey]["Normalizations"]["UpscaledPixels"]["Traceback"]["Purged"]      , ".--", label="TracebackPurged")
          axes[-1][2,0].legend()

    #         # LogLineOK()
        except Exception as e:
          pass


  LogLine(None, "Saving figures:", end="\n")
  cmPerInch = 2.54
  # dirName = os.path.join(os.path.dirname(pklFolder), "PyPlots")
  dirName = os.path.join(pklFolder, "PyPlots")
  if not os.path.exists(dirName):
    os.makedirs(dirName)
  for _iFig in range(len(figs)):
    figFilename = os.path.join(dirName, figNames[_iFig] + ".png")
    LogLine(None, "Saving: ", os.path.basename(figFilename))
    figs[_iFig].set_size_inches(figWidth_cm / cmPerInch, figHeight_cm / cmPerInch)
    figs[_iFig].savefig(figFilename, dpi=figDPI)
    figs[_iFig].clf()
    LogLineOK()
  plt.close('all')

print("Finished: " + os.path.basename(__file__))