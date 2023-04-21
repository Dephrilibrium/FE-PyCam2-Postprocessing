import os.path as p
import matplotlib.pyplot as plt
import pickle
import cv2 as cv
import numpy as np

import FieldEmission as fe

from misc import GrabPklFile



def SplitAndGrad(vFull):
  vecHalf = int(len(vFull)/2)

  # vFull = im[:, vecHalf]
  vHalf1 = vFull[:vecHalf + 1]
  vHalf2 = np.flip(vFull[vecHalf - 1:])
  gFull = np.subtract(vFull[:-1], vFull[1:])
  gHalf1 = np.subtract(vHalf1[:-1], vHalf1[1:])
  gHalf2 = np.subtract(vHalf2[:-1], vHalf2[1:])
  # gHalf1 = gFull[:vecHalf + 1]
  # gHalf2 = gFull[vecHalf-2:]

  return vHalf1, vHalf2, gFull, gHalf1, gHalf2






im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\Dev101_rPiHQCam-0464_ss=100000_0001.jpg")
x, y, w, h = 278, 314, 16, 16

# im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\Dev101_rPiHQCam-0112_ss=100000_0003.png")
# x, y, w, h = 35, 96, 13, 13
im = im[y:y+h, x:x+w]


# im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\TestCircle.png")


plt_image = cv.cvtColor(im, cv.COLOR_BGR2RGB)
imgplot = plt.imshow(plt_image)
im = cv.cvtColor(im, cv.COLOR_BGR2GRAY).astype(np.float64)
# im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\TestImage.png", cv.IMREAD_GRAYSCALE).astype(np.float64)
# im = cv.imread(r"C:\Users\ham38517\Downloads\PiCam\_Auswertungs-Scripte\TestCircle.png", cv.IMREAD_GRAYSCALE).astype(np.float64)
nX = int(im.shape[0]/2)
nY = int(im.shape[1]/2)

v0 = im[nY, :]
v01, v02, g0, g01, g02 = SplitAndGrad(v0)

v90 = im[:, nX]
v901, v902, g90, g901, g902 = SplitAndGrad(v90)


v45 = list()
v135 = list()
for _iDiag in range(im.shape[0]):
  v45.append(im[_iDiag, _iDiag]) # Get all 45 Diagonal
  v135.append(im[-1 - _iDiag, _iDiag]) # Get all -45 Diagonal
v45 = np.array(v45)
v135 = np.array(v135)

v451, v452, g45, g451, g452 = SplitAndGrad(v45)
v1351, v1352, g135, g1351, g1352 = SplitAndGrad(v135)


mv = np.mean([v0, v90, v45, v135], axis=0)
mv1, mv2, g, g1, g2 = SplitAndGrad(mv)

fig = plt.figure()
axe = fig.subplots(nrows=2, ncols=5)


axe[0, 0].plot(v0 , "o--", label="V0°")
axe[0, 0].plot(v01, ".-.", label="V0° LH")
axe[0, 0].plot(v02, ".-.", label="V0° RH")
axe[0, 0].set_title("Helligkeit 0° >")
axe[0, 0].legend()

axe[1, 0].plot(g0 , "o--", label="G0°")
axe[1, 0].plot(g01, ".-.", label="G0° LH")
axe[1, 0].plot(g02, ".-.", label="G0° RH")
axe[1, 0].set_title("Gradienten 0° >")
axe[1, 0].legend()

axe[0, 1].plot(v90 , "o--", label="V90°")
axe[0, 1].plot(v901, ".-.", label="V90° LH")
axe[0, 1].plot(v902, ".-.", label="V90° RH")
axe[0, 1].set_title("Helligkeit 90° v")
axe[0, 1].legend()

axe[1, 1].plot(g90 , "o--", label="G90°")
axe[1, 1].plot(g901, ".-.", label="G90° LH")
axe[1, 1].plot(g902, ".-.", label="G90° RH")
axe[1, 1].set_title("Gradienten 90° v")
axe[1, 1].legend()

axe[0, 2].plot(v45 , "o--", label="V45°")
axe[0, 2].plot(v451, ".-.", label="V45° LH")
axe[0, 2].plot(v452, ".-.", label="V45° RH")
axe[0, 2].set_title("Helligkeit 45° >v")
axe[0, 2].legend()

axe[1, 2].plot(g45 , "o--", label="G45°")
axe[1, 2].plot(g451, ".-.", label="G45° LH")
axe[1, 2].plot(g452, ".-.", label="G45° RH")
axe[1, 2].set_title("Gradienten 45° >v")
axe[1, 2].legend()

axe[0, 3].plot(v135 , "o--", label="V-45°")
axe[0, 3].plot(v1351, ".-.", label="V-45° LH")
axe[0, 3].plot(v1352, ".-.", label="V-45° RH")
axe[0, 3].set_title("Helligkeit -45° >^")
axe[0, 3].legend()

axe[1, 3].plot(g135 , "o--", label="G-45°")
axe[1, 3].plot(g1351, ".-.", label="G-45° LH")
axe[1, 3].plot(g1352, ".-.", label="G-45° RH")
axe[1, 3].set_title("Gradienten -45° >^")
axe[1, 3].legend()

axe[0, 4].plot(mv , "o--", label="mv")
axe[0, 4].plot(mv1, ".-.", label="mv LH")
axe[0, 4].plot(mv2, ".-.", label="mv RH")
axe[0, 4].set_title("Helligkeit Alle")
axe[0, 4].legend()

axe[1, 4].plot(g , "o--", label="g")
axe[1, 4].plot(g1, ".-.", label="g LH")
axe[1, 4].plot(g2, ".-.", label="g RH")
axe[1, 4].set_title("Gradienten Alle")
axe[1, 4].legend()


gradX = cv.Sobel(src=im, ddepth=cv.CV_64F, dx=1, dy=0, ksize=3)
gradY = cv.Sobel(src=im, ddepth=cv.CV_64F, dx=0, dy=1, ksize=3)
# And get combined gradient
grad  = np.sqrt(gradX**2 + gradY**2)
cv.imshow("Raw", im)
cv.imshow("GradX" , gradX)
cv.imshow("GradY" , gradY)
cv.imshow("GradXY", grad)



def ReadElDataAsDP(fPath, RemoveRows, DivVecOrVal=None, SubVecOrVal=None):
  H, D = fe.ReadDataFile(fPath)
  dp = fe.DataProvider(H, D)
  dp.RemoveRows(RemoveRows)
  if type(DivVecOrVal) != None:
    dp.DivideColumn("Y", DivVecOrVal)
  if type(SubVecOrVal) != None:
    dp.SubtractColumnFrom("Y", SubVecOrVal)

  return dp

def CreateBrightAsDP(Header, Data, DivideVec=None):
  dp = fe.DataProvider(Header, Data)
  if type(DivideVec) != None:
    dp.AppendColumn("DivByU", dp.GetColumn(0))
    dp.DivideColumn("DivByU", DivideVec)
  return dp



# Common
tarFold = r"C:\Users\ham38517\Downloads\PiCam\220725 PiCam Einzelemitter\Ausw\01 USweep Activation with IMax 100nA (ab hier 10Meg)\220804_143127"
pltFold = "PyPlot"





# Read Electrical data
RemoveRowIndicies = 0

f = open(p.join(tarFold, "value.resistor"))
resistor = f.readline();
f.close()
del f
resistor = int(float(resistor))

h, l, o = fe.ReadSweepFile(p.join(tarFold, r"Act 0_1400V_2VS Imax1V.swp"))
swp = fe.DataProvider(h, l)
# swp.RemoveRows(RemoveRowIndicies)

i1 = ReadElDataAsDP(fPath=p.join(tarFold, r"Dev100_FEAR16v2(Ch0CF).dat"), RemoveRows=RemoveRowIndicies, DivVecOrVal=resistor, SubVecOrVal=None)
i2 = ReadElDataAsDP(fPath=p.join(tarFold, r"Dev100_FEAR16v2(Ch1CF).dat"), RemoveRows=RemoveRowIndicies, DivVecOrVal=resistor, SubVecOrVal=None)
i3 = ReadElDataAsDP(fPath=p.join(tarFold, r"Dev100_FEAR16v2(Ch2CF).dat"), RemoveRows=RemoveRowIndicies, DivVecOrVal=resistor, SubVecOrVal=None)
i4 = ReadElDataAsDP(fPath=p.join(tarFold, r"Dev100_FEAR16v2(Ch3CF).dat"), RemoveRows=RemoveRowIndicies, DivVecOrVal=resistor, SubVecOrVal=None)

u1 = ReadElDataAsDP(p.join(tarFold, r"Dev100_FEAR16v2(Ch0UD).dat"), RemoveRows=RemoveRowIndicies, DivVecOrVal=None, SubVecOrVal=swp.GetColumn("U7"))
u2 = ReadElDataAsDP(p.join(tarFold, r"Dev100_FEAR16v2(Ch1UD).dat"), RemoveRows=RemoveRowIndicies, DivVecOrVal=None, SubVecOrVal=swp.GetColumn("U7"))
u3 = ReadElDataAsDP(p.join(tarFold, r"Dev100_FEAR16v2(Ch2UD).dat"), RemoveRows=RemoveRowIndicies, DivVecOrVal=None, SubVecOrVal=swp.GetColumn("U7"))
u4 = ReadElDataAsDP(p.join(tarFold, r"Dev100_FEAR16v2(Ch3UD).dat"), RemoveRows=RemoveRowIndicies, DivVecOrVal=None, SubVecOrVal=swp.GetColumn("U7"))

eleIList = [i2, i3, i1, i4] # List where the electrical data is sorted in same order like the image-spots are soreted! (LeftUpper to RightLower)
eleUList = [u2, u3, u1, u4] # List where the electrical data is sorted in same order like the image-spots are soreted! (LeftUpper to RightLower)

eleXDat = range(i1.Rows)




# Read Image-Data
rawBright = GrabPklFile(p.join(tarFold, "PMP_BrightSets4Brightness.pkl"))
ovrBright = GrabPklFile(p.join(tarFold, "PMP_ScaledWhereOverexposedBrightnesses.pkl"))
imageSets = GrabPklFile(p.join(tarFold, "PMP_ImgSets4Brightness.pkl"))


# Find unoverexposed data
ovrSS = list()
for brightSS in ovrBright["Full"]["BrightnessFromSS"]:
  if ovrSS.__contains__(brightSS):
    continue
  ovrSS.append(brightSS)
ovrSS.sort()
SS = ovrSS[0] # Grab the fastest SS
SS = ovrSS[-1]

imgYData = rawBright[SS]
imgXData = range(len(imgYData["Full"]["Blank"]))
imgYData = imgYData["Spot"]

_xyKeys = list(imgYData.keys())
imgYDict = dict()
for _iXY in range(len(_xyKeys)):
  _xyKey = _xyKeys[_iXY]
  xyDP = CreateBrightAsDP("Blank", imgYData[_xyKey]["Blank"], eleUList[_iXY].GetColumn("Y"))
  imgYDict[_xyKey] = xyDP





figs = list()
axisL = list()
axisR = list()

# Plot 1
fig = plt.figure()
nrows = 2
ncols = 2
axL = fig.subplots(nrows=nrows, ncols=ncols)
axR = list()

axisL.append(axL)
axisR.append(axR)
for _iXY in range(len(_xyKeys)):
  _xyKey = _xyKeys[_iXY]

  pRow = int(_iXY/ncols)
  pCol = int(_iXY % nrows)

  axR.append(axL[pRow, pCol].twinx())
  axL[pRow, pCol].semilogy(eleXDat , eleIList[_iXY].GetColumn("Y")       , "r.--", label=r"$Current$"   )
  axR[-1]        .semilogy(imgXData, imgYDict[_xyKey].GetColumn("Blank") , "g.--", label=r"$Brightness$")
  axR[-1]        .semilogy(imgXData, imgYDict[_xyKey].GetColumn("DivByU"), "b.--", label=r"$Brightness/U_{Tip}$")
  axL[pRow, pCol].set_ylim([1e-11, 1e-6])
  axR[-1]        .set_ylim([0, 10e3])
  axL[pRow, pCol].set_xlim([0, eleXDat [-1]])
  axR[-1]        .set_xlim([0, imgXData[-1]])

  axL[pRow, pCol].set_title(r"Spot @" + str(_iXY))
  # axR[-1]        .set_title("Spot @" str(_xyKey))

  h1, l1 = axL[pRow, pCol].get_legend_handles_labels()
  h2, l2 = axR[-1]        .get_legend_handles_labels()
  axL[pRow, pCol].legend(h1+h2, l1+l2, loc=2)
  # axL[pRow, pCol].legend()
  # axR[-1]        .legend()






figs.append(fig)



