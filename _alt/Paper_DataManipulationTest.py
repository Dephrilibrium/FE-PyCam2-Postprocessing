

from os.path import join, dirname, basename, split
from os import listdir

import FieldEmission as fe
import matplotlib.pyplot as plt
import numpy as np

from picamraw import PiRawBayer, PiCameraVersion

PiCameraVersion.


pCamRaw = PiRawBayer()



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
  dp.RemoveColumns(["Time", "Dev7"])
  dp.DivideColumn("Y", resistor)
  return

def __ElPrepareU__(dp, remRows, UE):
  dp.RemoveRows(remRows)
  dp.RemoveColumns(["Time", "Dev7"])
  dp.SubtractColumnFrom("Y", UE)
  dp.AppendColumn("USqu", dp.GetColumn("Y"))
  dp.MultiplyColumn("USqu", dp.GetColumn("Y"))
  sqrt = np.sqrt(np.abs(dp.GetColumn("Y")))
  dp.AppendColumn("USqrt", sqrt)
  return

pFolder = r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Auswertung\01_11 3x Swp nach Aktivierung 1.4kV@IMax 100nA\230117_130410"
# pFolder = r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Auswertung\01_11 3x Swp nach Aktivierung 1.4kV@IMax 100nA\230117_140132"

bSetTakeSpot = True
bSetKey = "xSpotDivBlank"
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


figs = list()
fAxL1 = list()
fAxR1 = list()
fAxR2 = list()

figs.append(plt.figure())
fAxL1.append(figs[-1].subplots())
oeSS  = cBright["Full"]["BrightnessFromSS"]#[19:-1]
oeOvr = cBright["Full"]["Overexposed"]

fAxL1[0].plot(list(range(len(oeSS))), oeSS, "-", label="Shutterspeeds")
PlotSupTitleAndLegend(figs[-1], "Shutterspeeds which were used for upscale")
figs[-1].tight_layout()


bDivUAndPxCnt        = dict()
bDivUSquAndPxCnt     = dict()
bDivUSqrtAndPxCnt     = dict()
bDivUAndPxCntMulI    = dict()
bDivUAndPxCntMulB    = dict()
bDivUSquAndPxCntMulI = dict()
bDivUSquAndPxCntMulB = dict()
sum4BrightNorm       = np.zeros(len(cBright["Spot"][XY[0]]["SpotBright"]["xSpotDivBlank"]))
brightNorm           = dict()

# figs.append(plt.figure())
# fAxL.append(figs[-1].subplots(ncols=nCols, nrows=nRows))

for _iXY in range(XYCnt):
  figs.append(plt.figure(figsize=fSize))
  fAxL1.append(figs[-1].subplots(ncols=nCols, nrows=nRows))
  fAxR1.append(list())
  fAxR2.append(list())

  fAxR1[-1].append(fAxL1[-1][0].twinx())
  fAxR1[-1].append(fAxL1[-1][1].twinx())
  fAxR1[-1].append(fAxL1[-1][2].twinx())
  fAxR1[-1].append(fAxL1[-1][3].twinx())

  fAxR2[-1].append(fAxL1[-1][0].twinx())
  fAxR2[-1].append(fAxL1[-1][1].twinx())
  fAxR2[-1].append(fAxL1[-1][2].twinx())
  fAxR2[-1].append(fAxL1[-1][3].twinx())

  _xy = XY[_iXY]
  if bSetTakeSpot:
    bSet = cBright["Spot"][_xy]["SpotBright"][bSetKey]#[19:-1]
  else:
    bSet = cBright["Spot"][_xy]["PxlBright"][bSetKey]#[19:-1]
  bSet = np.array(bSet)
  bSet = np.nan_to_num(np.divide(bSet, resistor), nan=0, posinf=0, neginf=0)
  ssSet = cBright["Spot"][_xy]["BrightnessFromSS"]#[19:-1]
  pxSet = dict()
  pxSet[SS[0]] = np.array(pxCount[SS[0]]["Spot"][_xy]["Blank"])#[19:-1])
  pxSet[SS[1]] = np.array(pxCount[SS[0]]["Div"][SS[1]]["Spot"][_xy]["Blank"])#[19:-1])
  pxSet[SS[2]] = np.array(pxCount[SS[0]]["Div"][SS[2]]["Spot"][_xy]["Blank"])#[19:-1])
  pxSet[SS[3]] = np.array(pxCount[SS[0]]["Div"][SS[3]]["Spot"][_xy]["Blank"])#[19:-1])
  oePxSet = list()
  for _i in range(len(pxSet[oeSS[0]])):
    _ss = oeSS[_i]
    if(oeSS[_i] < 0):
      _val = 0
    else:
      _val = pxSet[oeSS[_i]][_i]
    oePxSet.append(_val)
  # pxSet100  = pxCount[SS[0]]["Spot"][xy]["Blank"][19:-1]
  # pxSet31_5 = pxCount[SS[0]]["Div"][SS[1]]["Spot"][xy]["Blank"][19:-1]
  # pxSet10   = pxCount[SS[0]]["Div"][SS[2]]["Spot"][xy]["Blank"][19:-1]
  # pxSet3_15 = pxCount[SS[0]]["Div"][SS[3]]["Spot"][xy]["Blank"][19:-1]
  oePxSet = np.array(oePxSet)
  oePxSet[oePxSet < 1] = 1
  r, c, i = __findColRow__(_xy, 500)
  iSet = current[i]
  # iSet.RemoveRows([range(19)])
  uSet = voltage[i]
  # uSet.RemoveRows([range(19)])
  

  bLen = len(bSet)
  xLo = 0
  xHi = bLen
  xVal = range(xLo, xHi)

  fAxL1[-1][0].semilogy(xVal, bSet[xLo:xHi]                     , "-"  , markersize=3, color="#AA0000", label="RawB")
  fAxR1[-1][0].semilogy(xVal, iSet.GetColumn("Y")[xLo:xHi]      , "."  , markersize=3, color="#00AA00", label="Current")

  fAxL1[-1][0].legend(loc="upper left")
  fAxR1[-1][0].legend(loc="upper right")


  fAxL1[-1][1].plot(xVal, bSet[xLo:xHi]                  , "-"  , markersize=3, color="#AA0000", label="RawB")
  fAxR1[-1][1].plot(xVal, uSet.GetColumn("Y")[xLo:xHi]   , "."  , markersize=3, color="#0000AA", label="UE")
  # fAxR1[-1][1].plot(xVal, uSet.GetColumn("USqu")[xLo:xHi], "."  , markersize=3, color="#000055", label="UE^2")
  bDivU     = np.nan_to_num(np.divide(bSet[xLo:xHi], uSet.GetColumn("Y")    [xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  bDivUSqu  = np.nan_to_num(np.divide(bSet[xLo:xHi], uSet.GetColumn("USqu") [xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  bDivUSqrt = np.nan_to_num(np.divide(bSet[xLo:xHi], uSet.GetColumn("USqrt")[xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  fAxR2[-1][1].plot(xVal, bDivUSqu                        , "*"  , markersize=3, color="#00CC00", label="RawB/UE^2")
  fAxR2[-1][1].plot(xVal, bDivU                           , "*"  , markersize=3, color="#008000", label="RawB/UE")
  fAxR2[-1][1].plot(xVal, bDivUSqrt                       , "*"  , markersize=3, color="#000080", label="RawB/sqrt(UE)")

  fAxL1[-1][1].legend(loc="upper left")
  fAxR1[-1][1].legend(loc="upper right")
  fAxR2[-1][1].legend(loc="lower right")


  fAxL1[-1][2].plot(xVal, pxSet[SS[0]][xLo:xHi]        , ".-", markersize=5, linewidth=0.5, color="#000080", label="PxCnt100")
  # fAxL1[-1][2].plot(xVal, pxSet[SS[1]][xLo:xHi]        , ".-", markersize=5, linewidth=0.5, color="#808000", label="PxCnt31.5")
  # fAxL1[-1][2].plot(xVal, pxSet[SS[2]][xLo:xHi]        , ".-", markersize=5, linewidth=0.5, color="#008080", label="PxCnt10")
  # fAxL1[-1][2].plot(xVal, pxSet[SS[3]][xLo:xHi]        , ".-", markersize=5, linewidth=0.5, color="#808080", label="PxCnt3.15")
  bDivPx = dict()
  bDivPx[SS[0]] = np.nan_to_num(np.divide(bSet[xLo:xHi], pxSet[SS[0]][xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  # bDivPx[SS[1]] = np.nan_to_num(np.divide(bSet[xLo:xHi], pxSet[SS[1]][xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  # bDivPx[SS[2]] = np.nan_to_num(np.divide(bSet[xLo:xHi], pxSet[SS[2]][xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  # bDivPx[SS[3]] = np.nan_to_num(np.divide(bSet[xLo:xHi], pxSet[SS[3]][xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  fAxR1[-1][2].plot(xVal, bDivPx[SS[0]]                , ".--", markersize=5, linewidth=0.5, color="#008080", label="RawB/PxCnt100")
  # fAxR1[-1][2].plot(xVal, bDivPx[SS[1]]                , ".--", markersize=5, linewidth=0.5, color="#808000", label="RawB/PxCnt31.5")
  # fAxR1[-1][2].plot(xVal, bDivPx[SS[2]]                , ".--", markersize=5, linewidth=0.5, color="#008080", label="RawB/PxCnt10")
  # fAxR1[-1][2].plot(xVal, bDivPx[SS[3]]                , ".--", markersize=5, linewidth=0.5, color="#808080", label="RawB/PxCnt3.15")

  fAxL1[-1][2].legend(loc="upper left")
  fAxR1[-1][2].legend(loc="upper right")



  pxDivName = f'{pxSet[oeSS[0]]=}'.split('=')[0]
  pxDivSet = pxSet[SS[0]]
  # pxDivSet = oePxSet
  fAxL1[-1][3].semilogy(xVal, bSet[xLo:xHi]                   , "-"  , markersize=3, color="#AA0000", label="RawB")
  fAxR1[-1][3].semilogy(xVal, iSet.GetColumn("Y")[xLo:xHi]    , "."  , markersize=3, color="#00AA00", label="Current")
  # bDivUAndPxCnt       [_xy] = bDivU[xLo:xHi]
  bDivUAndPxCnt       [_xy] = np.nan_to_num(np.multiply(bDivU             , pxDivSet           [xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  bDivUSqrtAndPxCnt   [_xy] = np.nan_to_num(np.multiply(bDivUSqrt         , pxDivSet           [xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  bDivUSquAndPxCnt    [_xy] = np.nan_to_num(np.multiply(bDivUSqu          , pxDivSet           [xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  bDivUAndPxCntMulI   [_xy] = np.nan_to_num(np.multiply(bDivUAndPxCnt   [_xy], iSet.GetColumn("Y")[xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  bDivUAndPxCntMulB   [_xy] = np.nan_to_num(np.multiply(bDivUAndPxCnt   [_xy], bSet               [xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  bDivUSquAndPxCntMulI[_xy] = np.nan_to_num(np.multiply(bDivUSquAndPxCnt[_xy], iSet.GetColumn("Y")[xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  bDivUSquAndPxCntMulB[_xy] = np.nan_to_num(np.multiply(bDivUSquAndPxCnt[_xy], bSet               [xLo:xHi]), copy=False, nan=0, posinf=0, neginf=0)
  fAxR2[-1][3].semilogy(xVal, bDivUAndPxCntMulI   [_xy], "*--", markersize=1, linewidth=0.5, color="#00FF00", label="RawB * Current /(UE * "+ pxDivName + "))")
  fAxR2[-1][3].semilogy(xVal, bDivUAndPxCntMulB   [_xy], "*--", markersize=1, linewidth=0.5, color="#0000FF", label="RawB^2 /(UE * "+ pxDivName + "))")
  fAxR2[-1][3].semilogy(xVal, bDivUSquAndPxCntMulI[_xy], "*--", markersize=1, linewidth=0.5, color="#00FF00", label="RawB * Current/(UE^2 * "+ pxDivName + "))")
  fAxR2[-1][3].semilogy(xVal, bDivUSquAndPxCntMulB[_xy], "*--", markersize=1, linewidth=0.5, color="#000080", label="RawB^2/(UE^2 * "+ pxDivName + ")")
  fAxR2[-1][3].semilogy(xVal, bDivUSquAndPxCnt    [_xy], "*--", markersize=1, linewidth=0.5, color="#FF0000", label="RawB/(UE^2 * "+ pxDivName + "))")
  fAxR2[-1][3].semilogy(xVal, bDivUAndPxCnt       [_xy], "*--", markersize=1, linewidth=0.5, color="#800080", label="RawB/(UE * "+ pxDivName + "))")
  fAxR2[-1][3].semilogy(xVal, bDivUSqrtAndPxCnt   [_xy], "*--", markersize=1, linewidth=0.5, color="#FF00FF", label="RawB/(sqrt(UE) * "+ pxDivName + "))")

  fAxL1[-1][3].legend(loc="upper left")
  fAxR1[-1][3].legend(loc="upper right")
  fAxR2[-1][3].legend(loc="lower right")

  figs[-1].suptitle("Testplots for tip " + str(_xy))
  figs[-1].tight_layout()



selSet = bDivUAndPxCnt
for _xy in XY:
  sum4BrightNorm = np.add(sum4BrightNorm, np.abs(selSet[_xy]))
  # bDivUAndPxCnt       [_xy][:100]  = 0
  # bDivUAndPxCnt       [_xy][-100:] = 0
  # bDivUSquAndPxCnt    [_xy][:100]  = 0
  # bDivUSquAndPxCnt    [_xy][-100:] = 0
  # bDivUAndPxCntMulI   [_xy][:100]  = 0
  # bDivUAndPxCntMulI   [_xy][-100:] = 0
  # bDivUAndPxCntMulB   [_xy][:100]  = 0
  # bDivUAndPxCntMulB   [_xy][-100:] = 0
  # bDivUSquAndPxCntMulI[_xy][:100]  = 0
  # bDivUSquAndPxCntMulI[_xy][-100:] = 0
  # bDivUSquAndPxCntMulB[_xy][:100]  = 0
  # bDivUSquAndPxCntMulB[_xy][-100:] = 0
sum4BrightNorm[:100] = 0
sum4BrightNorm[-100:] = 0

sumFromNorm = np.zeros(len(sum4BrightNorm))
for _xy in XY:
  brightNorm[_xy] = np.nan_to_num(np.divide(np.abs(selSet[_xy]), sum4BrightNorm), copy=False, nan=0, posinf=0, neginf=0)
  sumFromNorm = np.add(sumFromNorm, brightNorm[_xy])



iSum = np.zeros(len(current[0].GetColumn("Y")))
for _iXY in range(len(XY)):
  iSum = np.add(iSum, current[_iXY].GetColumn("Y"))
# iSum = sCF.GetColumn("Y") # Override the sum if you want to use common measured integer current


cFromBright = dict()
Abw = dict()
AbwB2Curr = dict()
for _iXY in range(len(XY)):
  _xy = XY[_iXY]
  iSet = current[_iXY]
  cFromBright[_xy] = np.nan_to_num(np.multiply(np.abs(iSum), brightNorm[_xy]), copy=False, nan=0, posinf=0, neginf=0)
  # cFromBright[_xy] = np.multiply(cFromBright[_xy], 3)
  Abw[_xy] = np.nan_to_num(np.divide(iSet.GetColumn("Y"), np.abs(cFromBright[_xy])), copy=False, nan=0, posinf=0, neginf=0)
  AbwB2Curr[_xy] = np.nan_to_num(np.divide(iSet.GetColumn("Y"), np.abs(selSet[_xy])), copy=False, nan=0, posinf=0, neginf=0)


figs.append(plt.figure(figsize=fSize))
fAxL1.append(figs[-1].subplots(ncols=2, nrows=3))
fAxR1.append(__twinx2D___(figs[-1], fAxL1[-1]))
fAxR2.append(fAxR1[-1])

fAxL1[-1][0,0].semilogy(xVal, sum4BrightNorm    , ".", markersize=3, linewidth=1, color="#808080", label="Sum(Bright)")
fAxR1[-1][0,0].semilogy(xVal, sCF.GetColumn("Y"), ".", markersize=3, linewidth=1, color="#008000", label="Sum(TipCurrent)")
fAxR1[-1][0,0].semilogy(xVal, iSum, ".", markersize=3, linewidth=1, color="#00FF00", label="Integer Current")

# fAxR1[-1][0,0].semilogy(xVal, sumFromNorm      , ".-", markersize=3, linewidth=0.5, color="#000000", label="Tip 1")
# if DrawXYOn[0] != None:      fAxR1[-1][0,0].semilogy(xVal, brightNorm[XY[0]], ".-", markersize=3, linewidth=0.5, color="#FF0000", label="Tip 1")
# if DrawXYOn[1] != None:      fAxR1[-1][0,0].semilogy(xVal, brightNorm[XY[1]], ".-", markersize=3, linewidth=0.5, color="#008000", label="Tip 2")
# if DrawXYOn[2] != None:      fAxR1[-1][0,0].semilogy(xVal, brightNorm[XY[2]], ".-", markersize=3, linewidth=0.5, color="#0000FF", label="Tip 3")
# if DrawXYOn[3] != None:      fAxR1[-1][0,0].semilogy(xVal, brightNorm[XY[3]], ".-", markersize=3, linewidth=0.5, color="#808000", label="Tip 4")



if DrawXYOn[0] != None:      fAxL1[-1][1,0].semilogy(xVal, Abw[XY[0]], "*--", markersize=1, linewidth=0.5, color="#0000FF", label="Abw")
if DrawXYOn[1] != None:      fAxL1[-1][1,1].semilogy(xVal, Abw[XY[1]], "*--", markersize=1, linewidth=0.5, color="#0000FF", label="Abw")
if DrawXYOn[2] != None:      fAxL1[-1][2,0].semilogy(xVal, Abw[XY[2]], "*--", markersize=1, linewidth=0.5, color="#0000FF", label="Abw")
if DrawXYOn[3] != None:      fAxL1[-1][2,1].semilogy(xVal, Abw[XY[3]], "*--", markersize=1, linewidth=0.5, color="#0000FF", label="Abw")

# if DrawXYOn[0] != None:      fAxL1[-1][1,0].semilogy(xVal, brightNorm[XY[0]], ".-", markersize=3, linewidth=1, color="#FF0000", label="%-Contribution")
# if DrawXYOn[1] != None:      fAxL1[-1][1,1].semilogy(xVal, brightNorm[XY[1]], ".-", markersize=3, linewidth=1, color="#008000", label="%-Contribution")
# if DrawXYOn[2] != None:      fAxL1[-1][2,0].semilogy(xVal, brightNorm[XY[2]], ".-", markersize=3, linewidth=1, color="#0000FF", label="%-Contribution")
# if DrawXYOn[3] != None:      fAxL1[-1][2,1].semilogy(xVal, brightNorm[XY[3]], ".-", markersize=3, linewidth=1, color="#808000", label="%-Contribution")

if DrawXYOn[0] != None:      fAxR1[-1][1,0].semilogy(xVal, cFromBright[XY[0]], "x--", markersize=3, linewidth=0.5, color="#800000", label="Brightcurrent")
if DrawXYOn[1] != None:      fAxR1[-1][1,1].semilogy(xVal, cFromBright[XY[1]], "x--", markersize=3, linewidth=0.5, color="#800000", label="Brightcurrent")
if DrawXYOn[2] != None:      fAxR1[-1][2,0].semilogy(xVal, cFromBright[XY[2]], "x--", markersize=3, linewidth=0.5, color="#800000", label="Brightcurrent")
if DrawXYOn[3] != None:      fAxR1[-1][2,1].semilogy(xVal, cFromBright[XY[3]], "x--", markersize=3, linewidth=0.5, color="#800000", label="Brightcurrent")

# fAxR1[-1][1,0].semilogy(xVal, sCF.GetColumn("Y"), "o--", markersize=3, linewidth=0.5, color="#00FF00", label="Tipcurrent")
# fAxR1[-1][1,1].semilogy(xVal, sCF.GetColumn("Y"), "o--", markersize=3, linewidth=0.5, color="#00FF00", label="Tipcurrent")
# fAxR1[-1][2,0].semilogy(xVal, sCF.GetColumn("Y"), "o--", markersize=3, linewidth=0.5, color="#00FF00", label="Tipcurrent")
# fAxR1[-1][2,1].semilogy(xVal, sCF.GetColumn("Y"), "o--", markersize=3, linewidth=0.5, color="#00FF00", label="Tipcurrent")
if DrawXYOn[0] != None:      fAxR1[-1][1,0].semilogy(xVal, current[0].GetColumn("Y"), "o--", markersize=3, linewidth=0.5, color="#00C000", label="Tipcurrent")
if DrawXYOn[1] != None:      fAxR1[-1][1,1].semilogy(xVal, current[1].GetColumn("Y"), "o--", markersize=3, linewidth=0.5, color="#00C000", label="Tipcurrent")
if DrawXYOn[2] != None:      fAxR1[-1][2,0].semilogy(xVal, current[2].GetColumn("Y"), "o--", markersize=3, linewidth=0.5, color="#00C000", label="Tipcurrent")
if DrawXYOn[3] != None:      fAxR1[-1][2,1].semilogy(xVal, current[3].GetColumn("Y"), "o--", markersize=3, linewidth=0.5, color="#00C000", label="Tipcurrent")



PlotSupTitleAndLegend(figs[-1], "Brightnesscurrent vs measured current")
__SameXYLimitsOnLRSubplots__(lAxis=fAxL1[-1], lYLim=[0.01, 10.]        , rAxis=fAxR1[-1], rYLim=[1e-10, 1e-5], xLim=None)
__SameXYLabelsOnLRSubplots__(lAxis=fAxL1[-1], lText="Brightness/Factor", rAxis=fAxR1[-1], rText="%/Current", xText="Time [s]")


# SaveFigList(figs, saveFolder=r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Testplots howto Datenmanipulation", figSize=[(5,5), fSize, fSize, fSize], dpi=300)

# fAxL1[-1][1,0].set_xlabel("Measurementpoint [#]")
# fAxL1[-1][1,1].set_xlabel("Measurementpoint [#]")
# fAxL1[-1][0,0].set_ylabel("Brightness")
# fAxL1[-1][1,0].set_ylabel("Brightness")
# PlotSupTitleAndLegend(figs[-1], "Tipbrightness and Currents vs Measurement-Point")
# figs[-1].tight_layout()



print("Finished")