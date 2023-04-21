
from os.path import join

import matplotlib.pyplot as plt



from misc import GrabPklFile, PlotSupTitleAndLegend





def __findColRow__(xy, width):
  '''Accepts an xy-tuple. Returns nRow and nCol'''
  x = xy[0]
  y = xy[1]

  wHalf = width/2
  nrow = 0
  ncol = 0

  if x > wHalf and y < wHalf:
    nrow = 0
    ncol = 1
  elif x < wHalf and y > wHalf:
    nrow = 1
    ncol = 0
  elif x > wHalf and y > wHalf:
    nrow = 1
    ncol = 1
  
  return nrow, ncol


bFold = r"D:\05 PiCam\221222 HQCam SOI2x2_0005 (Paper)\Auswertung\03_01 Sweep mit neuen SS, 30FPS\230124_172732"

circles = GrabPklFile(join(bFold, "PMP_ssDetectionData.pkl"))
images  = GrabPklFile(join(bFold, "PMP_ssDetectionImages.pkl"))

cBright = GrabPklFile(join(bFold, "PMP_ScaledWhereOverexposedBrightnesses.pkl"))
cImages = GrabPklFile(join(bFold, "PMP_ScaledWhereOverexposedPxImgs.pkl"))

SS = list(circles.keys())
XY = list(circles[SS[0]]["XYKeys"].keys())
SSCnt = len(SS)
XYCnt = len(XY)

nRows = 2
nCols = 2


figs = list()
fAxL = list()

figs.append(plt.figure())
fAxL.append(figs[-1].subplots())
oeSS  = cBright["Full"]["BrightnessFromSS"]
oeOvr = cBright["Full"]["Overexposed"]

fAxL[0].plot(list(range(len(oeSS))), oeSS)


figs.append(plt.figure())
fAxL.append(figs[-1].subplots(ncols=nCols, nrows=nRows))
fAxR = list()
for _iXY in range(XYCnt):
  fAxR.append(list())
  xy = XY[_iXY]
  bSet = cBright["Spot"][xy]["PxlBright"]["xSpotDivBlank"]
  ssSet = cBright["Spot"][xy]["BrightnessFromSS"]
  r, c = __findColRow__(xy, 195)
  bX = list(range(len(bSet)))
  fAxL[-1][r, c].plot(bX, bSet, label="Brightness")
  fAxR[-1].append(fAxL[-1][r, c].twinx())
  fAxR[-1][-1].plot(bX, ssSet, ".", color="orange", markersize=3, label="FromSS")

  fAxL[-1][r, c].set_title(xy)

fAxL[-1][1,0].set_xlabel("Measurementpoint [#]")
fAxL[-1][1,1].set_xlabel("Measurementpoint [#]")
fAxL[-1][0,0].set_ylabel("Brightness")
fAxL[-1][1,0].set_ylabel("Brightness")
PlotSupTitleAndLegend(figs[-1], "Tipbrightness and Currents vs Measurement-Point")
figs[-1].tight_layout()



print("Finished")