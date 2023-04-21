from os.path import join
from os import listdir

import numpy as np
import matplotlib.pyplot as plt

from PMPLib.ImgFileHandling import ReadImages, OTH_ImgFormat
from PMPLib.ImgAreas import GetXYArea_XYX2Y2

from misc import GrabPklFile
from misc import PlotSupTitleAndLegend

from Check_GradeOfOverexposement import __twinx2D___
from Check_GradeOfOverexposement import __SameXYLabelsOnLRSubplots__
from Check_GradeOfOverexposement import __SameXYLimitsOnLRSubplots__
from Check_GradeOfOverexposement import __CollectSubImages__
from Check_GradeOfOverexposement import __AppendValues__







bFold = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\01 Aktivierung IMax1V\230221_115432 Tip Ch1 (aktiviert, 6517)"
uintFold = r"uint16 SS={}"
XYSideLen = 50



circles = GrabPklFile(join(bFold, "PMP_ssDetectionData.pkl"))
SS = list(circles.keys())
SS = SS[:1]
XY = list(circles[SS[0]]["XYKeys"].keys())

xyPlotOn = [(1,0), (1,1), (2,0), (2,1)]
# xyPlotOn = [(1,0),  None,  None,  None]
# xyPlotOn = [(1,1),  None,  None,  None]
# xyPlotOn = [(2,0),  None,  None,  None]
# xyPlotOn = [(2,1),  None,  None,  None]


imgs = dict()
imgs["Full"] = dict()
imgs["XY"] = dict() # SubImage-Collection

bVec = dict()
bVec["Full"] = dict()
bVec["XY"] = dict() # SubImage-Collection

pxCntAll = dict()
pxCntAll["Full"] = dict()
pxCntAll["XY"] = dict() # SubImage-Collection

pxCntOE = dict()
pxCntOE["Full"] = dict()
pxCntOE["XY"] = dict() # SubImage-Collection

pxOEDivAll = dict()
pxOEDivAll["Full"] = dict()
pxOEDivAll["XY"] = dict() # SubImage-Collection

pxBMax = dict()
pxBMax["Full"] = dict()
pxBMax["XY"] = dict() # SubImage-Collection

for _ss in SS:
    rFold = join(bFold, str.format(uintFold, _ss))
    imgFormat = str.format(OTH_ImgFormat, "Dev101", "*", _ss, "uint16", "png")
    _imgs, _pths = ReadImages(rFold, imgFormat)
    imgs["Full"][_ss] = _imgs
    imgs["XY"][_ss] = dict()

    bVec      ["Full"][_ss] = []
    pxCntAll  ["Full"][_ss] = []
    pxCntOE   ["Full"][_ss] = []
    pxOEDivAll["Full"][_ss] = []

    pxBMax["Full"][_ss] = np.array([im.max() for im in imgs["Full"][_ss]])

    bVec      ["XY"][_ss] = dict()
    pxCntAll  ["XY"][_ss] = dict()
    pxCntOE   ["XY"][_ss] = dict()
    pxOEDivAll["XY"][_ss] = dict()

    pxBMax["XY"][_ss] = dict()


    __AppendValues__(ImgArr=imgs["Full"][_ss], bArr=bVec["Full"][_ss], allPxlsArr=pxCntAll["Full"][_ss], oePxlsArr=pxCntOE["Full"][_ss], oePxDivArr=pxOEDivAll["Full"][_ss])

    for _xy in XY:
        [x, y, x2, y2] = GetXYArea_XYX2Y2(XYTuple=_xy, pxWidth=XYSideLen, pxHeight=XYSideLen)
        imgs["XY"][_ss][_xy] = __CollectSubImages__(imgs["Full"][_ss], [x, y, x2, y2])

        bVec      ["XY"][_ss][_xy] = []
        pxCntAll  ["XY"][_ss][_xy] = []
        pxCntOE   ["XY"][_ss][_xy] = []
        pxOEDivAll["XY"][_ss][_xy] = []

        __AppendValues__(ImgArr=imgs["XY"][_ss][_xy], bArr=bVec["XY"][_ss][_xy], allPxlsArr=pxCntAll["XY"][_ss][_xy], oePxlsArr=pxCntOE["XY"][_ss][_xy], oePxDivArr=pxOEDivAll["XY"][_ss][_xy])
        
        pxBMax["XY"][_ss][_xy] = np.array([im.max() for im in imgs["XY"][_ss][_xy]])

bDivPxl = dict()
bDivPxl["Full"] = dict()
bDivPxl["XY"] = dict()
bDivSpt = dict()
bDivSpt["Full"] = dict()
bDivSpt["XY"] = dict()
bDivKeys = []

bSS = [SS[0]]   # bSS = SS[:-1]
dSS = [SS[0]]    # dSS = SS[1:]
imCnt = len(imgs["Full"][bSS[0]])
for _bSS in bSS:
    for _dSS in dSS:
        # bDivKeys.append(f"{_bSS}/{_dSS}")
        _key = _bSS

        bDivSpt["Full"][_key] = []
        bDivSpt["Full"][_key] = np.nan_to_num(np.divide(bVec["Full"][_bSS], bVec["Full"][_dSS]), copy=False, nan=0, posinf=0, neginf=0)

        bDivPxl["Full"][_key] = []
        for _iImg in range(imCnt):
            _tmpDiv = np.nan_to_num(np.divide(imgs["Full"][_bSS][_iImg], imgs["Full"][_dSS][_iImg]), copy=False, nan=np.nan, posinf=np.nan, neginf=np.nan)
            bDivPxl["Full"][_key].append(np.nanmean(_tmpDiv))
        bDivPxl["Full"][_key] = np.array(bDivPxl["Full"][_key])


        bDivSpt["XY"][_key] = dict()
        bDivPxl["XY"][_key] = dict()
        for _xy in XY:
            bDivSpt["XY"][_key][_xy] = np.nan_to_num(np.divide(bVec["XY"][_bSS][_xy], bVec["XY"][_dSS][_xy]), copy=False, nan=0, posinf=0, neginf=0)

            bDivPxl["XY"][_key][_xy] = []
            for _iImg in range(imCnt):
                _tmpDiv = np.nan_to_num(np.divide(imgs["XY"][_bSS][_xy][_iImg], imgs["XY"][_dSS][_xy][_iImg]), copy=False, nan=np.nan, posinf=np.nan, neginf=np.nan)
                bDivPxl["XY"][_key][_xy].append(np.nanmean(_tmpDiv))
            bDivPxl["XY"][_key][_xy] = np.array(bDivPxl["XY"][_key][_xy])

figs = list()
subL = list()
subR = list()


for _ss in SS:
    fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
    figs.append(fig)
    subL.append(lAxis)
    subR.append(__twinx2D___(fig, lAxis))

    xVals = range(0, len(imgs["Full"][_ss]))
    subL[-1][0,0].plot(xVals, bVec  ["Full"][_ss], ".--", markersize=3, linewidth=0.5, color="#FF0000", label="Brightness")
    subR[-1][0,0].plot(xVals, pxBMax["Full"][_ss], ".--", markersize=3, linewidth=0.5, color="#008000", label="Max. Px-Bright")

    if xyPlotOn[0] != None: subL[-1][xyPlotOn[0]].plot(xVals, bVec["XY"][_ss][XY[0]], ".", markersize=1, linewidth=0.5, color="#FF0000", label="Brightness")
    if xyPlotOn[1] != None: subL[-1][xyPlotOn[1]].plot(xVals, bVec["XY"][_ss][XY[1]], ".", markersize=1, linewidth=0.5, color="#FF0000", label="Brightness")
    if xyPlotOn[2] != None: subL[-1][xyPlotOn[2]].plot(xVals, bVec["XY"][_ss][XY[2]], ".", markersize=1, linewidth=0.5, color="#FF0000", label="Brightness")
    if xyPlotOn[3] != None: subL[-1][xyPlotOn[3]].plot(xVals, bVec["XY"][_ss][XY[3]], ".", markersize=1, linewidth=0.5, color="#FF0000", label="Brightness")

    if xyPlotOn[0] != None: subR[-1][xyPlotOn[0]].plot(xVals, pxBMax["XY"][_ss][XY[0]], ".", markersize=1, linewidth=0.5, color="#008000", label="Max. Px-Bright")
    if xyPlotOn[1] != None: subR[-1][xyPlotOn[1]].plot(xVals, pxBMax["XY"][_ss][XY[1]], ".", markersize=1, linewidth=0.5, color="#008000", label="Max. Px-Bright")
    if xyPlotOn[2] != None: subR[-1][xyPlotOn[2]].plot(xVals, pxBMax["XY"][_ss][XY[2]], ".", markersize=1, linewidth=0.5, color="#008000", label="Max. Px-Bright")
    if xyPlotOn[3] != None: subR[-1][xyPlotOn[3]].plot(xVals, pxBMax["XY"][_ss][XY[3]], ".", markersize=1, linewidth=0.5, color="#008000", label="Max. Px-Bright")

    PlotSupTitleAndLegend(figs[-1], "Sum(Brightness) & max. Px-Brightness on SS=" + str(_ss))

for _iSS in range(len(bSS)):
    _bSS = bSS[_iSS]
    _dSS = dSS[_iSS]
    _ss = _bSS

    fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
    figs.append(fig)
    subL.append(lAxis)
    subR.append(__twinx2D___(fig, lAxis))

    subL[-1][0,0].plot(xVals, bVec   ["Full"][_bSS], ".-", markersize=1, linewidth=0.5, color="#FF0000", label=f"Full Brightness {_bSS}")
    subL[-1][0,0].plot(xVals, bVec   ["Full"][_dSS], ".-", markersize=1, linewidth=0.5, color="#00A000", label=f"Full Brightness {_dSS}")
    subR[-1][0,0].plot(xVals, bDivPxl["Full"] [_ss], ".--", markersize=1, linewidth=0.5, color="#0000A0", label=f"Full {_bSS}/{_dSS}")
    subR[-1][0,0].plot(xVals, bDivSpt["Full"] [_ss], ".--", markersize=1, linewidth=0.5, color="#A000A0", label=f"Full {_bSS}/{_dSS}")

    if xyPlotOn[0] != None: subL[-1][xyPlotOn[0]].plot(xVals, bVec["XY"][_bSS][XY[0]], ".-", markersize=1, linewidth=0.5, color="#FF0000", label=f"SpotBright {_bSS}")
    if xyPlotOn[1] != None: subL[-1][xyPlotOn[1]].plot(xVals, bVec["XY"][_bSS][XY[1]], ".-", markersize=1, linewidth=0.5, color="#FF0000", label=f"SpotBright {_bSS}")
    if xyPlotOn[2] != None: subL[-1][xyPlotOn[2]].plot(xVals, bVec["XY"][_bSS][XY[2]], ".-", markersize=1, linewidth=0.5, color="#FF0000", label=f"SpotBright {_bSS}")
    if xyPlotOn[3] != None: subL[-1][xyPlotOn[3]].plot(xVals, bVec["XY"][_bSS][XY[3]], ".-", markersize=1, linewidth=0.5, color="#FF0000", label=f"SpotBright {_bSS}")

    if xyPlotOn[0] != None: subL[-1][xyPlotOn[0]].plot(xVals, bVec["XY"][_dSS][XY[0]], ".-", markersize=1, linewidth=0.5, color="#00A000", label=f"SpotBright {_dSS}")
    if xyPlotOn[1] != None: subL[-1][xyPlotOn[1]].plot(xVals, bVec["XY"][_dSS][XY[1]], ".-", markersize=1, linewidth=0.5, color="#00A000", label=f"SpotBright {_dSS}")
    if xyPlotOn[2] != None: subL[-1][xyPlotOn[2]].plot(xVals, bVec["XY"][_dSS][XY[2]], ".-", markersize=1, linewidth=0.5, color="#00A000", label=f"SpotBright {_dSS}")
    if xyPlotOn[3] != None: subL[-1][xyPlotOn[3]].plot(xVals, bVec["XY"][_dSS][XY[3]], ".-", markersize=1, linewidth=0.5, color="#00A000", label=f"SpotBright {_dSS}")

    if xyPlotOn[0] != None: subR[-1][xyPlotOn[0]].plot(xVals, bDivPxl["XY"][_ss][XY[0]], ".--", markersize=1, linewidth=0.5, color="#0000A0", label=f"Mean({_bSS}/{_dSS} PxlWise)")
    if xyPlotOn[1] != None: subR[-1][xyPlotOn[1]].plot(xVals, bDivPxl["XY"][_ss][XY[1]], ".--", markersize=1, linewidth=0.5, color="#0000A0", label=f"Mean({_bSS}/{_dSS} PxlWise)")
    if xyPlotOn[2] != None: subR[-1][xyPlotOn[2]].plot(xVals, bDivPxl["XY"][_ss][XY[2]], ".--", markersize=1, linewidth=0.5, color="#0000A0", label=f"Mean({_bSS}/{_dSS} PxlWise)")
    if xyPlotOn[3] != None: subR[-1][xyPlotOn[3]].plot(xVals, bDivPxl["XY"][_ss][XY[3]], ".--", markersize=1, linewidth=0.5, color="#0000A0", label=f"Mean({_bSS}/{_dSS} PxlWise)")

    if xyPlotOn[0] != None: subR[-1][xyPlotOn[0]].plot(xVals, bDivSpt["XY"][_ss][XY[0]], ".--", markersize=1, linewidth=0.5, color="#A000A0", label=f"Mean({_bSS}/{_dSS} SptWise)")
    if xyPlotOn[1] != None: subR[-1][xyPlotOn[1]].plot(xVals, bDivSpt["XY"][_ss][XY[1]], ".--", markersize=1, linewidth=0.5, color="#A000A0", label=f"Mean({_bSS}/{_dSS} SptWise)")
    if xyPlotOn[2] != None: subR[-1][xyPlotOn[2]].plot(xVals, bDivSpt["XY"][_ss][XY[2]], ".--", markersize=1, linewidth=0.5, color="#A000A0", label=f"Mean({_bSS}/{_dSS} SptWise)")
    if xyPlotOn[3] != None: subR[-1][xyPlotOn[3]].plot(xVals, bDivSpt["XY"][_ss][XY[3]], ".--", markersize=1, linewidth=0.5, color="#A000A0", label=f"Mean({_bSS}/{_dSS} SptWise)")

    # __SameXYLimitsOnLRSubplots__(subL[-1], None, subR[-1], [-2, 10], None)
    PlotSupTitleAndLegend(figs[-1], "Mean(BrightnessDivision) SS=" + str(_ss))




print("Finished")