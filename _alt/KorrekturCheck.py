import os
import pickle
import glob
import random
import parse
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import axes3d

from misc import Logger
from misc import LogLine
from misc import LogLineOK
from misc import GrabPklFile


def __CheckDictStructure__(brightDict, keys):

  for key in keys:
    try:
      brightDict[key]
    except:
      return False
  
  return True



# a = [0, 1, 0]
# fac = 1.1
# g1 = int(0.299*a[0]) + int(0.587*a[1]) + int(0.114*a[2])
# a2 = np.multiply(a, fac)
# g2 = int(0.299*a2[0]) + int(0.587*a2[1]) + int(0.114*a2[2])
# g3 = g1 * fac







figWidth_cm = 60
figHeight_cm = figWidth_cm / (16/9)
figDPI = 300

# factor = 1.1 # Value used in "ArtificialOverexposing.py"          # !!! Automatically calculated now from AOEnding !!!
_iBase = 0
_iDiv = 0
# _iXY = 3







walkFolder = r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Auswertung\01_01 Aktivierungslauf\221213_134454 USwp"
# walkFolder = r"C:\Users\ham38517\Downloads\PiCam\221117 PiCam Korrekturverifikation\Ausw\220725 PiCam Einzelemitter\03 1h I500nA U1400V\220804_175655 (#1)"
# overexpFolder = r"_+10.0%AO"
overexpFolders = [
  r"_+10.0%AO",
  r"_+30.0%AO",
  # r"_+50.0%AO",
  # r"_+80.0%AO",
  # r"_+100.0%AO",
]


# plt.style.use("Solarize_Light2")
for root, dirs, files in os.walk(walkFolder):

  for overexpFolder in overexpFolders:

    upsclPerc = parse.parse("_{}%AO", overexpFolder)[0]
    upsclPerc = float(upsclPerc)
    factor = 1 + (upsclPerc / 100)
    
    figNames = list()
    figs = list()
    axes = list()
    
    # Grab pickles
    # Normalization-divider-brightness from unmanipulated pictures
    fPathOriBright = root + r"\PMP_BrightSets4Brightness.pkl"

    fPathScldAnyBright = root + overexpFolder + r"\PMP_ScaledAnyBrightnesses.pkl"
    # fPathScldPxls = root + overexpFolder + r"\PMP_ScaledAnyBrightnesses.pkl.pkl"

    fPathScldOvrBright = root + overexpFolder + r"\PMP_ScaledWhereOverexposedBrightnesses.pkl"
    
    try:
      OriginalBright = GrabPklFile(fPathOriBright)
      # Normalization-nominator-brightness from upscaled manipulated pictures
      ScaledSpotsAny = GrabPklFile(fPathScldAnyBright)
      # ScaledPixls = GrabPklFile(fPathScldPxls)

      ScaledSpotsOvr = GrabPklFile(fPathScldOvrBright)
      # ScaledPixls = GrabPklFile(fPathScldPxls)

      if OriginalBright == None or ScaledSpotsAny == None or ScaledSpotsOvr == None: # or ScaledPixls == None:
        raise Exception("Wasn't able to grab at least one Pickle-file")
    except Exception as e:
      LogLine(None, "Missing Pickle. Skipping " + root, "", yFill=0, wFill=0, end="\n")
      continue

    # Grab all keys for necessary plot-data
    _bKeys = list(OriginalBright.keys())
    _bKey = _bKeys[_iBase]
    _dKeys = list(OriginalBright[_bKey]["Div"].keys())
    _dKey = _dKeys[_iDiv]
    _xyKeys = list(OriginalBright[_bKey]["Spot"].keys())
    # _xyKey = _xyKeys[_iXY]


    for _iXY in range(len(_xyKeys)):
    # for _iXY in [_iXY]:
      _xyKey = _xyKeys[_iXY]

      # Grab data-vectors
      oriBright = np.multiply(OriginalBright[_bKey]["Spot"][_xyKey]["Blank"], factor)

      dataLen = len(oriBright)
      xVals = range(dataLen)

      try:
        anySptDatSet = ScaledSpotsAny[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"]["Blank"]
        anyPxlDatSet = ScaledSpotsAny[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"]
        ovrSptDatSet = ScaledSpotsOvr["Spot"][_xyKey]["SpotBright"]
        ovrPxlDatSet = ScaledSpotsOvr["Spot"][_xyKey]["PxlBright"]

        # Try to access the data if all dictionaries were created correctly
        dictKeys = ["xTheory",
                    "xSpotDivBlank",
                    "xSpotDivClean",
                    "xMeanPxDivBlank",
                    "xMeanPxDivClean",
                    "xTheory/BlankArea",
                    "xTheory/CleanArea"]
        if (   not __CheckDictStructure__(anySptDatSet, dictKeys)
            or not __CheckDictStructure__(anyPxlDatSet, dictKeys)
            or not __CheckDictStructure__(ovrSptDatSet, dictKeys)
            or not __CheckDictStructure__(ovrPxlDatSet, dictKeys)):
          raise Exception("Failed DictStruct-check")

      except Exception as e:
        LogLine(None, str.format("Missing spot {} or mismatching dictionaries in one dataset", str(_xyKey)), end="\n")
        continue

      figs.append(plt.figure())
      axes.append(figs[-1].subplots(nrows=3, ncols=2))
      # figNames.append(os.path.basename(os.path.dirname(fPathScldSpots)))
      # figNames.append(r"Brightness-Normalization for $\frac{" + str(int(_bKey/1000)) + "}{"+ str(int(_dKey/1000)) +"}$,  ")
      figNames.append("Normalization of AO" + str.format("{:+03.1f}%", upsclPerc) + ", Base " + str.format("{:03d}", int(_bKey / 1000)) + "ms, Div " + str.format("{:03d}", int(_dKey / 1000)) + "ms; " + str.format("{:03d}", len(figs)) + " Spot@" + str(_xyKey))


      figs[-1].suptitle(figNames[-1]) 

      # Brightnessvalues
      # gs = axes[-1][0, 0].get_gridspec()
      # axes[-1][0, 0].remove()
      # axes[-1][0, 1].remove()
      # axes[-1][0, 0] = figs[-1].add_subplot(gs[0, :])
      # axes[-1][0, 1] = axes[-1][0, 0]
      # zipBright = list(zip(OriginalBright[_bKey]["Spot"][_xyKey]["Blank"], oriBright))
      # p1 = list(zip(xVals, OriginalBright[_bKey]["Spot"][_xyKey]["Blank"]))
      # p2 = list(zip(xVals, oriBright))
      # p3 = list(zip(xVals, OriginalBright[_bKey]["Spot"][_xyKey]["Blank"], oriBright))

      # axes[-1][0, 0].plot(xVals, OriginalBright[_bKey]["Spot"][_xyKey]["Blank"]                        , "o", label=r"$Unoverexposed Ref.$")
      axes[-1][0, 0].plot(xVals, oriBright                                , "k--", label=r"$Unoverexposed Ref.$")
      axes[-1][0, 0].plot(xVals, anySptDatSet["xTheory"]                  , ".--", label=r"$xTheory$")
      axes[-1][0, 0].plot(xVals, anySptDatSet["xSpotDivBlank"]            , ".--", label=r"$xSpotDivBlank$")
      axes[-1][0, 0].plot(xVals, anySptDatSet["xSpotDivClean"]            , ".--", label=r"$xSpotDivClean$")
      axes[-1][0, 0].plot(xVals, anySptDatSet["xMeanPxDivBlank"]          , ".--", label=r"$xMeanPxDivBlank$")
      axes[-1][0, 0].plot(xVals, anySptDatSet["xMeanPxDivClean"]          , ".--", label=r"$xMeanPxDivClean$")
      axes[-1][0, 0].plot(xVals, anySptDatSet["xTheory/BlankArea"]        , ".--", label=r"$xTheory/BlankArea$")
      axes[-1][0, 0].plot(xVals, anySptDatSet["xTheory/CleanArea"]        , ".--", label=r"$xTheory/CleanArea$")
      axes[-1][0, 0].plot(xVals, anySptDatSet["xSpot_Mean(Blank,Clean)"]  , ".--", label=r"$xSptMean(Bl,Cl)$")
      axes[-1][0, 0].plot(xVals, anySptDatSet["xMeanPx_Mean(Blank,Clean)"], ".--", label=r"$xPxMean(Bl,Cl)$")
      axes[-1][0, 0].legend()
      axes[-1][0, 0].set_title(r"$Any: \sum(Brightness_{Pixel})$")

      axes[-1][0, 1].plot(xVals, oriBright                                , "k--", label=r"$Unoverexposed Ref.$")
      axes[-1][0, 1].plot(xVals, ovrSptDatSet["xTheory"]                  , ".--", label=r"$xTheory$")
      axes[-1][0, 1].plot(xVals, ovrSptDatSet["xSpotDivBlank"]            , ".--", label=r"$xSpotDivBlank$")
      axes[-1][0, 1].plot(xVals, ovrSptDatSet["xSpotDivClean"]            , ".--", label=r"$xSpotDivClean$")
      axes[-1][0, 1].plot(xVals, ovrSptDatSet["xMeanPxDivBlank"]          , ".--", label=r"$xMeanPxDivBlank$")
      axes[-1][0, 1].plot(xVals, ovrSptDatSet["xMeanPxDivClean"]          , ".--", label=r"$xMeanPxDivClean$")
      axes[-1][0, 1].plot(xVals, ovrSptDatSet["xTheory/BlankArea"]        , ".--", label=r"$xTheory/BlankArea$")
      axes[-1][0, 1].plot(xVals, ovrSptDatSet["xTheory/CleanArea"]        , ".--", label=r"$xTheory/CleanArea$")
      axes[-1][0, 1].plot(xVals, ovrSptDatSet["xSpot_Mean(Blank,Clean)"]  , ".--", label=r"$xSptMean(Bl,Cl)$")
      axes[-1][0, 1].plot(xVals, ovrSptDatSet["xMeanPx_Mean(Blank,Clean)"], ".--", label=r"$xPxMean(Bl,Cl)$")
      axes[-1][0, 1].legend()
      axes[-1][0, 1].set_title(r"$Overexposed: \sum(Brightness_{Pixel})$")


      # Normalization
      axes[-1][1, 0].plot(xVals, [1] * dataLen                                                    , "k--", label=r"$Unoverexposed Ref.$")
      axes[-1][1, 0].plot(xVals, np.nan_to_num(np.divide(anySptDatSet["xTheory"]                  , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory$")
      axes[-1][1, 0].plot(xVals, np.nan_to_num(np.divide(anySptDatSet["xSpotDivBlank"]            , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSpotDivBlank$")
      axes[-1][1, 0].plot(xVals, np.nan_to_num(np.divide(anySptDatSet["xSpotDivClean"]            , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSpotDivClean$")
      axes[-1][1, 0].plot(xVals, np.nan_to_num(np.divide(anySptDatSet["xMeanPxDivBlank"]          , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xMeanPxDivBlank$")
      axes[-1][1, 0].plot(xVals, np.nan_to_num(np.divide(anySptDatSet["xMeanPxDivClean"]          , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xMeanPxDivClean$")
      axes[-1][1, 0].plot(xVals, np.nan_to_num(np.divide(anySptDatSet["xTheory/BlankArea"]        , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory/BlankArea$")
      axes[-1][1, 0].plot(xVals, np.nan_to_num(np.divide(anySptDatSet["xTheory/CleanArea"]        , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory/CleanArea$")
      axes[-1][1, 0].plot(xVals, np.nan_to_num(np.divide(anySptDatSet["xSpot_Mean(Blank,Clean)"]  , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSptMean(Bl,Cl)$")
      axes[-1][1, 0].plot(xVals, np.nan_to_num(np.divide(anySptDatSet["xMeanPx_Mean(Blank,Clean)"], oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xPxMean(Bl,Cl)$")
      axes[-1][1, 0].legend()
      axes[-1][1, 0].set_title(r"Spotwise normalization (any): $\frac{Brightness_{Upscaled}}{Brightness_{Unoverexposed}}$")
      axes[-1][1, 0].set_xlim([15, 65])
      axes[-1][1, 0].set_ylim([0.7, 1.3])


      # Normalization
      axes[-1][2, 0].plot(xVals, [1] * dataLen                                                    , "k--", label=r"$Unoverexposed Ref.$")
      axes[-1][2, 0].plot(xVals, np.nan_to_num(np.divide(anyPxlDatSet["xTheory"]                  , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory$")
      axes[-1][2, 0].plot(xVals, np.nan_to_num(np.divide(anyPxlDatSet["xSpotDivBlank"]            , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSpotDivBlank$")
      axes[-1][2, 0].plot(xVals, np.nan_to_num(np.divide(anyPxlDatSet["xSpotDivClean"]            , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSpotDivClean$")
      axes[-1][2, 0].plot(xVals, np.nan_to_num(np.divide(anyPxlDatSet["xMeanPxDivBlank"]          , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xMeanPxDivBlank$")
      axes[-1][2, 0].plot(xVals, np.nan_to_num(np.divide(anyPxlDatSet["xMeanPxDivClean"]          , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xMeanPxDivClean$")
      axes[-1][2, 0].plot(xVals, np.nan_to_num(np.divide(anyPxlDatSet["xTheory/BlankArea"]        , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory/BlankArea$")
      axes[-1][2, 0].plot(xVals, np.nan_to_num(np.divide(anyPxlDatSet["xTheory/CleanArea"]        , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory/CleanArea$")
      axes[-1][2, 0].plot(xVals, np.nan_to_num(np.divide(anySptDatSet["xSpot_Mean(Blank,Clean)"]  , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSptMean(Bl,Cl)$")
      axes[-1][2, 0].plot(xVals, np.nan_to_num(np.divide(anySptDatSet["xMeanPx_Mean(Blank,Clean)"], oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xPxMean(Bl,Cl)$")
      axes[-1][2, 0].legend()
      axes[-1][2, 0].set_title(r"Pixelwise normalization (any): $\frac{Brightness_{Upscaled}}{Brightness_{Unoverexposed}}$")
      axes[-1][2, 0].set_xlim([15, 65])
      axes[-1][2, 0].set_ylim([0.7, 1.3])



          # Normalization
      axes[-1][1, 1].plot(xVals, [1] * dataLen                                                    , "k--", label=r"$Unoverexposed Ref.$")
      axes[-1][1, 1].plot(xVals, np.nan_to_num(np.divide(ovrSptDatSet["xTheory"]                  , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory$")
      axes[-1][1, 1].plot(xVals, np.nan_to_num(np.divide(ovrSptDatSet["xSpotDivBlank"]            , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSpotDivBlank$")
      axes[-1][1, 1].plot(xVals, np.nan_to_num(np.divide(ovrSptDatSet["xSpotDivClean"]            , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSpotDivClean$")
      axes[-1][1, 1].plot(xVals, np.nan_to_num(np.divide(ovrSptDatSet["xMeanPxDivBlank"]          , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xMeanPxDivBlank$")
      axes[-1][1, 1].plot(xVals, np.nan_to_num(np.divide(ovrSptDatSet["xMeanPxDivClean"]          , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xMeanPxDivClean$")
      axes[-1][1, 1].plot(xVals, np.nan_to_num(np.divide(ovrSptDatSet["xTheory/BlankArea"]        , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory/BlankArea$")
      axes[-1][1, 1].plot(xVals, np.nan_to_num(np.divide(ovrSptDatSet["xTheory/CleanArea"]        , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory/CleanArea$")
      axes[-1][1, 1].plot(xVals, np.nan_to_num(np.divide(ovrSptDatSet["xSpot_Mean(Blank,Clean)"]  , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSptMean(Bl,Cl)$")
      axes[-1][1, 1].plot(xVals, np.nan_to_num(np.divide(ovrSptDatSet["xMeanPx_Mean(Blank,Clean)"], oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xPxMean(Bl,Cl)$")
      axes[-1][1, 1].legend()
      axes[-1][1, 1].set_title(r"Spotwise normalization (overexposed): $\frac{Brightness_{Upscaled}}{Brightness_{Unoverexposed}}$")
      axes[-1][1, 1].set_xlim([15, 65])
      axes[-1][1, 1].set_ylim([0.7, 1.3])


      # Normalization
      axes[-1][2, 1].plot(xVals, [1] * dataLen                                                    , "k--", label=r"$Unoverexposed Ref.$")
      axes[-1][2, 1].plot(xVals, np.nan_to_num(np.divide(ovrPxlDatSet["xTheory"]                  , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory$")
      axes[-1][2, 1].plot(xVals, np.nan_to_num(np.divide(ovrPxlDatSet["xSpotDivBlank"]            , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSpotDivBlank$")
      axes[-1][2, 1].plot(xVals, np.nan_to_num(np.divide(ovrPxlDatSet["xSpotDivClean"]            , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSpotDivClean$")
      axes[-1][2, 1].plot(xVals, np.nan_to_num(np.divide(ovrPxlDatSet["xMeanPxDivBlank"]          , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xMeanPxDivBlank$")
      axes[-1][2, 1].plot(xVals, np.nan_to_num(np.divide(ovrPxlDatSet["xMeanPxDivClean"]          , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xMeanPxDivClean$")
      axes[-1][2, 1].plot(xVals, np.nan_to_num(np.divide(ovrPxlDatSet["xTheory/BlankArea"]        , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory/BlankArea$")
      axes[-1][2, 1].plot(xVals, np.nan_to_num(np.divide(ovrPxlDatSet["xTheory/CleanArea"]        , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xTheory/CleanArea$")
      axes[-1][2, 1].plot(xVals, np.nan_to_num(np.divide(ovrPxlDatSet["xSpot_Mean(Blank,Clean)"]  , oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xSptMean(Bl,Cl)$")
      axes[-1][2, 1].plot(xVals, np.nan_to_num(np.divide(ovrPxlDatSet["xMeanPx_Mean(Blank,Clean)"], oriBright), copy=False, nan=0, posinf=0, neginf=0), ".--", label=r"$xPxMean(Bl,Cl)$")
      axes[-1][2, 1].legend()
      axes[-1][2, 1].set_title(r"Pixelwise normalization (overexposed): $\frac{Brightness_{Upscaled}}{Brightness_{Unoverexposed}}$")
      axes[-1][2, 1].set_xlim([15, 65])
      axes[-1][2, 1].set_ylim([0.7, 1.3])


    LogLine(None, "Saving figures:", end="\n")
    cmPerInch = 2.54
    dirName = os.path.join(os.path.dirname(fPathScldAnyBright), "PyPlots")
    # dirName = os.path.join(ScaledSpots, "PyPlots")
    if not os.path.exists(dirName):
      os.makedirs(dirName)
    for _iFig in range(len(figs)):
      figFilename = os.path.join(dirName, figNames[_iFig] + ".png")
      LogLine(None, "Saving: ", os.path.basename(figFilename), wFill=90)
      figs[_iFig].set_size_inches(figWidth_cm / cmPerInch, figHeight_cm / cmPerInch)
      figs[_iFig].savefig(figFilename, dpi=figDPI)
      figs[_iFig].clf()
      LogLineOK()
    plt.close('all')


print("Finished: " + os.path.basename(__file__))