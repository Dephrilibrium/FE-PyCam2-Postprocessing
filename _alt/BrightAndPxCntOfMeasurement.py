from os.path import join
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

from PMPLib.ImgFileHandling import GrabSSFromFilenames, ReadImages, OTH_BlkFormat, OTH_ImgFormat, OTH_SS_Index, OTH_LoadFileTypes
from PMPLib.ImgManipulation import MeanImages
from PMPLib.ImgAreas import GetCircleArea_XYX2Y2

from misc import GrabPklFile, PlotSupTitleAndLegend



def AppendSubSetToDict(myDict):
  myDict["BGR"] = list()
  myDict["RGB"] = list()
  myDict["GS"]  = list()
  myDict["R"]   = list()
  myDict["G"]   = list()
  myDict["B"]   = list()
  return myDict

def CreateImgVersions(myDict, im):
  myDict["BGR"].append(im)
  myDict["RGB"].append(cv.cvtColor(im, cv.COLOR_BGR2RGB))
  myDict["GS"] .append(cv.cvtColor(im, cv.COLOR_BGR2GRAY))
  myDict["R"]  .append(myDict["RGB"][-1][:,:,0])
  myDict["G"]  .append(myDict["RGB"][-1][:,:,1])
  myDict["B"]  .append(myDict["RGB"][-1][:,:,2])
  return

def CreateBrightnessVersions(myDict, imVersions, iImg):
  myDict["BGR"].append(np.sum(imVersions["BGR"][iImg]))
  myDict["RGB"].append(np.sum(imVersions["RGB"][iImg]))
  myDict["GS"] .append(np.sum(imVersions["GS"] [iImg]))
  myDict["R"]  .append(np.sum(imVersions["R"]  [iImg]))
  myDict["G"]  .append(np.sum(imVersions["G"]  [iImg]))
  myDict["B"]  .append(np.sum(imVersions["B"]  [iImg]))
  return

def CreatePxCntVersions(myDict, imVersions, iImg, bMin):
  myDict["BGR"].append(len(np.where(imVersions["BGR"][iImg] >= bMin)[0]))
  myDict["RGB"].append(len(np.where(imVersions["RGB"][iImg] >= bMin)[0]))
  myDict["GS"] .append(len(np.where(imVersions["GS"] [iImg] >= bMin)[0]))
  myDict["R"]  .append(len(np.where(imVersions["R"]  [iImg] >= bMin)[0]))
  myDict["G"]  .append(len(np.where(imVersions["G"]  [iImg] >= bMin)[0]))
  myDict["B"]  .append(len(np.where(imVersions["B"]  [iImg] >= bMin)[0]))
  return



def PlotVecVersions(axes, vecColl):
  x = list(range(len(vecColl["BGR"])))
  axes[0].plot(x, vecColl["BGR"], "o--", color="#00CCFF", label="BGR")
  axes[0].plot(x, vecColl["RGB"], "*:", color="#FFCC00", label="RGB")
  axes[0].plot(x, vecColl["GS"] , ".-.", color="#808080", label="GS" )
  axes[1].plot(x, vecColl["R"]  , "o--", color="red"    , label="R"  )
  axes[1].plot(x, vecColl["G"]  , "*:", color="green"  , label="G"  )
  axes[1].plot(x, vecColl["B"]  , ".-.", color="blue"   , label="B"  )
  return


bFold = r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Auswertung\01_01 Aktivierungslauf\221213_134454 USwp"
pFold = r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Messung\01_01 Aktivierungslauf\221213_134454 USwp\Pics"
# bFold = r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Auswertung\01_01 Aktivierungslauf\221213_152744 30min"
# pFold = r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Messung\01_01 Aktivierungslauf\221213_152744 30min\Pics"
crcls = GrabPklFile(join(bFold, r"PMP_ssDetectionData.pkl"))


pxWinLen = 50
# pxWinLen = None
iIm2Show = 610
minB2Cnt = 5
figSize  = (10, 5)


yLimBr = [-10, 310000]
xLimBr = [0, 1400]

yLimPC = [-10, 10000]
xLimPC = xLimBr

yLimOE = [-10, 300]
xLimOE = xLimBr


SS = list(crcls.keys())
# SS = [SS[2]]
XY = list(crcls[SS[0]]["XYKeys"].keys())
# XY = [XY[2]] # Select only one XY-Key
# cropWin = [ int(XY[0][1] - pxWinLen/2),
#             int(XY[0][0] - pxWinLen/2),
#             int(XY[0][1] + pxWinLen  ),
#             int(XY[0][0] + pxWinLen  )]
cropWin=None

imags = dict()
print(str.format("Reading images..."))
for ss in SS:
  print(str.format("Reading black images (ss={})", ss))
  bIm, bPa       = ReadImages(fPaths=pFold, Format=str.format(OTH_BlkFormat, "*", ss, "*", "*")     , cvFlags=cv.IMREAD_COLOR, CropWindow=cropWin, IgnorePathVector=None, ShowImg=False)
  print(str.format("Reading images (ss={})", ss))
  rIm, iPa = ReadImages(fPaths=pFold, Format=str.format(OTH_ImgFormat, "*", "*", ss, "*", "*"), cvFlags=cv.IMREAD_COLOR, CropWindow=cropWin, IgnorePathVector=bPa , ShowImg=False)
  print(str.format("Meaning images (ss={})", ss))
  imags[ss] = MeanImages(ImgCollection=rIm, ImgsPerMean=4, ShowImg=False)


print(str.format("Finsihed reading images"))

# OTH_BlkFormat = "{}_HQCam-BlackSubtraction_ss={}_{}.{}"
# OTH_ImgFormat = "{}_HQCam-{}_ss={}_{}.{}"


# imags = GrabPklFile(join(bFold, r"PMP_ssDetectionImages.pkl"  ))


figs = list()
axes = list()

imVersions = AppendSubSetToDict(dict())
brVersions = AppendSubSetToDict(dict())
pcVersions = AppendSubSetToDict(dict())
oeVersions = AppendSubSetToDict(dict())

for ss in SS:
  for xy in XY:
    imCnt = len(imags[ss])
    for _iImg in range(imCnt):
      try:
        _iCrcl = crcls[ss]["XYKeys"][xy]["ImageIndex"].index(_iImg)
        if pxWinLen == None:
          cIm = imags[ss][_iImg]
          x1, y1 , x2, y2 = 0, 0, cIm.shape[1], cIm.shape[0]
        else:
          x1, y1, x2, y2 = GetCircleArea_XYX2Y2(Circle=crcls[ss]["XYKeys"][xy]["ImgCircles"][_iCrcl], pxTolerance=pxWinLen, AddPxTolerance=False)
          cIm = imags[ss][_iImg][y1:y2, x1:x2]
      except:
        if pxWinLen == None:
          cIm = np.zeros(imags[ss][0].shape, dtype=np.uint8) # Empty full image
        else:
          cIm = np.zeros((pxWinLen, pxWinLen, 3), dtype=np.uint8)

      CreateImgVersions(myDict=imVersions, im=cIm)
      CreateBrightnessVersions(myDict=brVersions, imVersions=imVersions, iImg=_iImg)
      CreatePxCntVersions(myDict=pcVersions, imVersions=imVersions, iImg=_iImg, bMin=minB2Cnt)
      CreatePxCntVersions(myDict=oeVersions, imVersions=imVersions, iImg=_iImg, bMin=255)
      continue


    _iCrcl = crcls[ss]["XYKeys"][xy]["ImageIndex"].index(iIm2Show)
    if pxWinLen == None:
      im2Show = imags[ss][iIm2Show]
      x1, y1, x2, y2 = 0, 0, im2Show.shape[1], im2Show.shape[0]
    else:
      x1, y1, x2, y2 = GetCircleArea_XYX2Y2(Circle=crcls[ss]["XYKeys"][xy]["ImgCircles"][_iCrcl], pxTolerance=pxWinLen, AddPxTolerance=False)
      im2Show = imags[ss][iIm2Show][y1:y2, x1:x2]
    figs.append(plt.figure(figsize=figSize))
    axes.append(figs[-1].subplots(nrows=1, ncols=1))
    axes[-1].imshow(im2Show)
    figs[-1].suptitle(str.format("Spot@{} on Image {}", xy, iIm2Show))
    axes[-1].set_ylabel("y")
    axes[-1].set_xlabel("x")




    figs.append(plt.figure(figsize=figSize))
    axes.append(figs[-1].subplots(nrows=1, ncols=2))
    PlotVecVersions(axes[-1], brVersions)
    PlotSupTitleAndLegend(figs[-1], "Brightnesses Colors and RGB-Channels")
    axes[-1][0].set_ylabel("Sum(Bright)")
    axes[-1][0].set_xlabel("Measurement [#]")
    axes[-1][1].set_xlabel("Measurement [#]")

    # axes[-1][0].set_ylim(yLimBr)
    # axes[-1][0].set_xlim(xLimBr)


    figs.append(plt.figure(figsize=figSize))
    axes.append(figs[-1].subplots(nrows=1, ncols=2))
    PlotVecVersions(axes[-1], pcVersions)
    PlotSupTitleAndLegend(figs[-1], "Pixel-Count of Colors and RGB-Channels")
    axes[-1][0].set_ylabel("Sum(Pixels)")
    axes[-1][0].set_xlabel("Measurement [#]")
    axes[-1][1].set_xlabel("Measurement [#]")

    # axes[-1][0].set_ylim(yLimPC)
    # axes[-1][0].set_xlim(xLimPC)


    figs.append(plt.figure(figsize=figSize))
    axes.append(figs[-1].subplots(nrows=1, ncols=2))
    PlotVecVersions(axes[-1], oeVersions)
    PlotSupTitleAndLegend(figs[-1], "Count Overexposed Pixels of Colors and RGB-Channels")
    axes[-1][0].set_ylabel("Sum(OvrExpPixels)")
    axes[-1][0].set_xlabel("Measurement [#]")
    axes[-1][1].set_xlabel("Measurement [#]")

    # axes[-1][0].set_ylim(yLimOE)
    # axes[-1][0].set_xlim(xLimOE)

plt.show()
print("Finished")