

from os.path import join, dirname, basename, split
from os import listdir

import FieldEmission as fe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd



from misc import GrabPklFile, PlotSupTitleAndLegend, SaveFigList
from Check_GradeOfOverexposement import __twinx2D___, __SameXYLabelsOnLRSubplots__, __SameXYLimitsOnLRSubplots__





def __findColRow__(xy, width):
  '''Accepts an xy-tuple. Returns nRow and nCol'''
  x = xy[0]
  y = xy[1]

  wHalf = width/2
  nRow = 0
  nCol = 0
  nLin = 0

  if x > wHalf and y < wHalf:
    nRow = 0
    nCol = 1
    nLin = 1
  elif x < wHalf and y > wHalf:
    nRow = 1
    nCol = 0
    nLin = 2
  elif x > wHalf and y > wHalf:
    nRow = 1
    nCol = 1
    nLin = 3
  
  return nRow, nCol, nLin



def __ReadElData__(fName):
  if fName.endswith(".resistor"):
    f = open(fName, "r")
    value = f.readlines()[0]
    f.close()
    return float(value)
  elif fName.endswith(".dat"):
    h, d = fe.ReadDataFile(fName)
  else:
    h, d, dummy = fe.ReadSweepFile(fName)
  
  dp = fe.DataProvider(h, d)
  return dp


def __ElPrepareI__(dp, remRows, resistor):
  dp.RemoveRows(remRows)
  dp.AppendColumn("I", dp.GetColumn("Y"))                    # Copy U
  dp.RemoveColumns(["Time", "Dev7", "Y"])
  dp.DivideColumn("I", resistor)
  return

def __ElPrepareU__(dp, remRows, UE):
  dp.RemoveRows(remRows)
  dp.AppendColumn("U", dp.GetColumn("Y")) # Rename
  dp.RemoveColumns(["Time", "Dev7", "Y"]) # Remove

  dp.SubtractColumnFrom("U", UE)                                # U
  dp.AppendColumn("U**2", dp.GetColumn("U"))                    # Copy U
  dp.MultiplyColumn("U**2", dp.GetColumn("U"))                  # U**2
  dp.AppendColumn("sqrt(U)", np.sqrt(np.abs(dp.GetColumn("U"))))  # sqrt(U)
  return

pFolder = r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Auswertung\01_11 3x Swp nach Aktivierung 1.4kV@IMax 100nA\230117_130410"
# pFolder = r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Auswertung\01_11 3x Swp nach Aktivierung 1.4kV@IMax 100nA\230117_140132"

SptOrPxlBright = "SpotBright" # "SpotBright" or "PxlBright"
bSubKey = "xSpotDivBlank" # One of the belows!
# "xTheory"
# "xSpotDivBlank"
# "xSpotDivClean"
# "xMeanPxDivBlank"
# "xMeanPxDivClean"
# "xTheory/BlankArea"
# "xTheory/CleanArea"
# "xSpot_Mean(Blank,Clean)"
# "xMeanPx_Mean(Blank,Clean)"


swpFName = listdir(pFolder)
for fname in swpFName:
  if fname.endswith(".swp"):
   swpFName = fname
   del fname
   break
SWP = __ReadElData__(join(pFolder, swpFName))
# SWP = __ReadElData__(join(pFolder, "swp U - U0..1400V 5VS I5V - 1Rpts.swp"))
resistor = __ReadElData__(join(pFolder, "value.resistor"))

sCF = __ReadElData__(join(pFolder, "Dev27_ISum.dat"))
sCF.RemoveRows(0)
sCF.RemoveColumns(["Time", "Dev7"])

i0 = __ReadElData__(join(pFolder, "Dev100_FEAR16v2(Ch0CF).dat"))
i1 = __ReadElData__(join(pFolder, "Dev100_FEAR16v2(Ch1CF).dat"))
i2 = __ReadElData__(join(pFolder, "Dev100_FEAR16v2(Ch2CF).dat"))
i3 = __ReadElData__(join(pFolder, "Dev100_FEAR16v2(Ch3CF).dat"))
__ElPrepareI__(i0, 0, resistor)
__ElPrepareI__(i1, 0, resistor)
__ElPrepareI__(i2, 0, resistor)
__ElPrepareI__(i3, 0, resistor)

u0 = __ReadElData__(join(pFolder, "Dev100_FEAR16v2(Ch0UD).dat"))
u1 = __ReadElData__(join(pFolder, "Dev100_FEAR16v2(Ch1UD).dat"))
u2 = __ReadElData__(join(pFolder, "Dev100_FEAR16v2(Ch2UD).dat"))
u3 = __ReadElData__(join(pFolder, "Dev100_FEAR16v2(Ch3UD).dat"))
__ElPrepareU__(u0, 0, SWP.GetColumn("U7"))
__ElPrepareU__(u1, 0, SWP.GetColumn("U7"))
__ElPrepareU__(u2, 0, SWP.GetColumn("U7"))
__ElPrepareU__(u3, 0, SWP.GetColumn("U7"))

drawCol = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]
current = [i1, i2, i0, i3] # Sort el. data in order of spots incomming
voltage = [u3, u2, u0, u3] # Sort el. data in order of spots incomming
DrawXYOn = [0, 0, 0, 0]




removeXY = []
circles = GrabPklFile(join(pFolder, "PMP_ssDetectionData.pkl"))
images  = GrabPklFile(join(pFolder, "PMP_ssDetectionImages.pkl"))
pxCount = GrabPklFile(join(pFolder, "PMP_PxAreaCnts4Brightness.pkl"))
cBright = GrabPklFile(join(pFolder, "PMP_ScaledWhereOverexposedBrightnesses.pkl"))
cImages = GrabPklFile(join(pFolder, "PMP_ScaledWhereOverexposedPxImgs.pkl"))

SS = list(circles.keys())
for _xy in removeXY:
  circles[SS[0]]["XYKeys"].pop(_xy) # Remove keys before creating the Key-List
XY = list(circles[SS[0]]["XYKeys"].keys())
SSCnt = len(SS)
XYCnt = len(XY)

nRows = 4
nCols = 1
fSize = (14, 16)


ovrSS = cBright["Full"]["BrightnessFromSS"]#[19:-1]
isOvr = cBright["Full"]["Overexposed"]


bright = dict()
_pxCnt = pxCount[SS[0]] # Take px-count of max SS
for _iXY in range(len(XY)):
  # Grab coordinate
  _xy = XY[_iXY]

  # Helpers
  _b = np.array(cBright["Spot"][_xy][SptOrPxlBright][bSubKey])
  _v = voltage[_iXY]
  _i = current[_iXY]
  _p = _pxCnt["Spot"][_xy]["Blank"]

  ### Make vectors
  bright[_xy] = dict()
  bright[_xy]["B*1"]      = _b
  bright[_xy]["B**2"]     = np.nan_to_num(np.multiply(_b, _b)            , nan=0, posinf=0, neginf=0)
  bright[_xy]["B/R"]      = np.nan_to_num(np.divide(_b, resistor)        , nan=0, posinf=0, neginf=0)
  bright[_xy]["(B/R)**2"] = np.nan_to_num(np.power(bright[_xy]["B/R"], 2), nan=0, posinf=0, neginf=0)


    # Grab necessary vectors
  _sqrtU = _v.GetColumn("sqrt(U)")
  _U     = _v.GetColumn("U")
  _U2    = _v.GetColumn("U**2")
  # _p     = _p

  # Caluclate with B
  _B    = bright[_xy]["B*1"]
  _B2   = bright[_xy]["B**2"]
  bright[_xy]["B / (sqrt(UE) * PxCnt)"]    = np.nan_to_num(np.divide(_B , np.multiply(_sqrtU, _p)), nan=0, posinf=0, neginf=0)
  bright[_xy]["B / (UE * PxCnt)"]          = np.nan_to_num(np.divide(_B , np.multiply(_U    , _p)), nan=0, posinf=0, neginf=0)
  bright[_xy]["B / (UE**2 * PxCnt)"]       = np.nan_to_num(np.divide(_B , np.multiply(_U2   , _p)), nan=0, posinf=0, neginf=0)
  bright[_xy]["B**2 / (sqrt(UE) * PxCnt)"] = np.nan_to_num(np.divide(_B2, np.multiply(_sqrtU, _p)), nan=0, posinf=0, neginf=0)
  bright[_xy]["B**2 / (UE * PxCnt)"]       = np.nan_to_num(np.divide(_B2, np.multiply(_U    , _p)), nan=0, posinf=0, neginf=0)
  bright[_xy]["B**2 / (UE**2 * PxCnt)"]    = np.nan_to_num(np.divide(_B2, np.multiply(_U2   , _p)), nan=0, posinf=0, neginf=0)

  # Caluclate with B/R
  _BR    = bright[_xy]["B/R"]
  _BR2   = bright[_xy]["(B/R)**2"]
  bright[_xy]["(B/R) / (sqrt(UE) * PxCnt)"]    = np.nan_to_num(np.divide(_BR , np.multiply(_sqrtU, _p)), nan=0, posinf=0, neginf=0)
  bright[_xy]["(B/R) / (UE * PxCnt)"]          = np.nan_to_num(np.divide(_BR , np.multiply(_U    , _p)), nan=0, posinf=0, neginf=0)
  bright[_xy]["(B/R) / (UE**2 * PxCnt)"]       = np.nan_to_num(np.divide(_BR , np.multiply(_U2   , _p)), nan=0, posinf=0, neginf=0)
  bright[_xy]["(B/R)**2 / (sqrt(UE) * PxCnt)"] = np.nan_to_num(np.divide(_BR2, np.multiply(_sqrtU, _p)), nan=0, posinf=0, neginf=0)
  bright[_xy]["(B/R)**2 / (UE * PxCnt)"]       = np.nan_to_num(np.divide(_BR2, np.multiply(_U    , _p)), nan=0, posinf=0, neginf=0)
  bright[_xy]["(B/R)**2 / (UE**2 * PxCnt)"]    = np.nan_to_num(np.divide(_BR2, np.multiply(_U2   , _p)), nan=0, posinf=0, neginf=0)



figs = list()
fAxL1 = list()
fAxR1 = list()

for _iXY in range(len(XY)):
  _xy = XY[_iXY]




print("Finished")