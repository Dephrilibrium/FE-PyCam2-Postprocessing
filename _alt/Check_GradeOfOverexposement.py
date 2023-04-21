from os.path import join
from os import listdir

import numpy as np
import matplotlib.pyplot as plt

from PMPLib.ImgFileHandling import ReadImages, OTH_ImgFormat
from PMPLib.ImgAreas import GetXYArea_XYX2Y2

from misc import GrabPklFile
from misc import PlotSupTitleAndLegend



def __twinx2D___(fig, lAxis):

    gs = lAxis[0,0].get_gridspec()
    lAxis[0,0].remove()
    lAxis[0,1].remove()
    sF = fig.add_subplot(gs[0, 0:])
    lAxis[0,0] = sF
    lAxis[0,1] = sF

    rAxis = list()
    rAxis.append(sF.twinx())
    rAxis.append(rAxis[-1])
    for axY in lAxis[1:]:
        for axX in axY:
            rAxis.append(axX.twinx())
    rAxis = np.array(rAxis).reshape((3,2))
    return rAxis



def __SameXYLabelsOnLRSubplots__(lAxis, lText, rAxis, rText, xText):
    for lRow, rRow in zip(lAxis, rAxis):
        for lAx, rAx in zip(lRow, rRow):
            lAx.set_ylabel(lText)
            rAx.set_ylabel(rText)
            lAx.set_xlabel(xText)



def __SameXYLimitsOnLRSubplots__(lAxis, lYLim, rAxis, rYLim, xLim):
    for lRow, rRow in zip(lAxis, rAxis):
        for lAx, rAx in zip(lRow, rRow):
            lAx.set_ylim(lYLim)
            rAx.set_ylim(rYLim)
            lAx.set_xlim(xLim)



def __CollectSubImages__(FullImgArr, XYX2Y2):
    subImgs = list()

    for _img in FullImgArr:
        subImgs.append(_img[XYX2Y2[1]:XYX2Y2[3], XYX2Y2[0]:XYX2Y2[2]])
    return subImgs




def __AppendValues__(ImgArr, bArr, allPxlsArr, oePxlsArr, oePxDivArr):
    for _iImg in range(len(ImgArr)):
    
        _img = ImgArr[_iImg]

        bArr.append(np.sum(_img))
        allPxlsArr.append(np.count_nonzero(_img >= b2Count))
        oePxlsArr .append(np.count_nonzero(_img >= b2CountAsOE))
        oePxDivArr.append(np.divide(allPxlsArr[-1], oePxlsArr[-1]))
    
    bArr = np.array(bArr)
    allPxlsArr = np.array(allPxlsArr)
    oePxlsArr = np.array(oePxlsArr)
    oePxDivArr = np.nan_to_num(oePxDivArr, copy=False, nan=0, posinf=0, neginf=0)

    return







bFold = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\02 Alle Zusammen\230223_084426 1kV 250nA"
uintFold = r"uint16 SS={}"
XYSideLen = 50

usePickles = False
iMin = 0
iMax = 1400

printXYOn = [0, 1, 2, 3]

b2Count     = 0x0300 # Equal to 3 in 8-bit
b2CountAsOE = 0xFFFF # Maximum 16bit-value!


# circles = GrabPklFile(join(bFold, "PMP_ssDetectionData.pkl"))
# SS = list(circles.keys())
# bData = GrabPklFile(join(bFold, "PMP_BrightSets4Brightness.pkl"))

# corrSpots = GrabPklFile(join(bFold, "PMP_ScaledWhereOverexposedBrightnesses.pkl"))
# if usePickles:
#     # corrPxWise = GrabPklFile(join(bFold, "PMP_ScaledWhereOverexposedPxImgs.pkl"))
#     pxCounts = GrabPklFile(join(bFold, "PMP_PxAreaCnts4Brightness.pkl"))
#     divFactors = GrabPklFile(join(bFold, "PMP_DivFactors4Brightness.pkl"))

# XY = [_xy for _xy in circles[SS[0]]["XYKeys"]]


# # "Dev101_HQCam-00000_ss=100000_uint8.png"
# # "    {}_HQCam-   {}_ss=    {}_   {}.{}"
# imgs = dict()
# imgs["Full"] = dict()
# imgs["XY"] = dict() # SubImage-Collection
# for _ss in SS:
#     rFold = join(bFold, str.format(uintFold, _ss))
#     imgFormat = str.format(OTH_ImgFormat, "Dev101", "*", _ss, "uint16", "png")
#     _imgs, _pths = ReadImages(rFold, imgFormat)
#     imgs["Full"][_ss] = _imgs

# # Get Brightness
# bright    = dict()
# relBright = dict()
# allPxls   = dict()
# oePxls    = dict()
# oePxDiv   = dict()

# bright   ["Full"] = dict()
# relBright["Full"] = dict() # Sum of the XY-relBrights!
# allPxls  ["Full"] = dict()
# oePxls   ["Full"] = dict()
# oePxDiv  ["Full"] = dict()


# bright   ["XY"] = dict()
# relBright["XY"] = dict()
# allPxls  ["XY"] = dict()
# oePxls   ["XY"] = dict()
# oePxDiv  ["XY"] = dict()

# for _ss in SS:
#     bright   ["Full"][_ss] = list()
#     relBright["Full"][_ss] = np.array([0] * len(imgs["Full"][_ss]))
#     allPxls  ["Full"][_ss] = list()
#     oePxls   ["Full"][_ss] = list()
#     oePxDiv  ["Full"][_ss] = list()

#     bright   ["XY"][_ss] = dict()
#     relBright["XY"][_ss] = dict()
#     allPxls  ["XY"][_ss] = dict()
#     oePxls   ["XY"][_ss] = dict()
#     oePxDiv  ["XY"][_ss] = dict()

#     # Readout from images
#     if not usePickles:
#         __AppendValues__(ImgArr=imgs["Full"][_ss], bArr=bright["Full"][_ss], allPxlsArr=allPxls["Full"][_ss], oePxlsArr=oePxls["Full"][_ss], oePxDivArr=oePxDiv["Full"][_ss])
#         bright   ["Full"][_ss] = bright   ["Full"][_ss][iMin:iMax]
#         relBright["Full"][_ss] = relBright["Full"][_ss][iMin:iMax]
#         allPxls  ["Full"][_ss] = allPxls  ["Full"][_ss][iMin:iMax]
#         oePxls   ["Full"][_ss] = oePxls   ["Full"][_ss][iMin:iMax]
#         oePxDiv  ["Full"][_ss] = oePxDiv  ["Full"][_ss][iMin:iMax]


#     # Grab vom Pickles
#     else:
#         bright["Full"][_ss]  = corrSpots    ["Full"]["SpotBright"]["xSpotDivBlank"][iMin:iMax]
#         try:
#             allPxls["Full"][_ss] = pxCounts[_ss]["Full"]              ["Blank"]        [iMin:iMax]
#         except:
#             allPxls["Full"][_ss] = np.array(([0] * len(imgs["Full"][_ss]))[iMin:iMax])
#         try:
#             oePxls["Full"][_ss]  = pxCounts[_ss]["Full"]              ["Blank-Clean"]  [iMin:iMax]
#         except:
#             oePxls["Full"][_ss] = np.array(([0] * len(imgs["Full"][_ss]))[iMin:iMax])
#         try:
#             oePxDiv["Full"][_ss] = np.nan_to_num(np.divide(oePxls["Full"][_ss], allPxls["Full"][_ss]), copy=False, nan=0, posinf=0, neginf=0)
#         except:
#             oePxDiv["Full"][_ss] = np.array(([0] * len(imgs["Full"][_ss]))[iMin:iMax])
#         relBright["Full"][_ss] = relBright["Full"][_ss][iMin:iMax]

#     imgs["XY"][_ss] = dict()
#     for _xy in XY:

#         # Readout from images
#         if not usePickles:
#             _imWin = [x, y, x2, y2] = GetXYArea_XYX2Y2(XYTuple=_xy, pxWidth=XYSideLen, pxHeight=XYSideLen)
#             imgs["XY"][_ss][_xy] = __CollectSubImages__(imgs["Full"][_ss], _imWin)

#             bright ["XY"][_ss][_xy] = list()
#             allPxls["XY"][_ss][_xy] = list()
#             oePxls ["XY"][_ss][_xy] = list()
#             oePxDiv["XY"][_ss][_xy] = list()
#             __AppendValues__(ImgArr=imgs["XY"][_ss][_xy], bArr=bright["XY"][_ss][_xy], allPxlsArr=allPxls["XY"][_ss][_xy], oePxlsArr=oePxls["XY"][_ss][_xy], oePxDivArr=oePxDiv["XY"][_ss][_xy])
#             bright ["XY"][_ss][_xy] = bright ["XY"][_ss][_xy][iMin:iMax]
#             allPxls["XY"][_ss][_xy] = allPxls["XY"][_ss][_xy][iMin:iMax]
#             oePxls ["XY"][_ss][_xy] = oePxls ["XY"][_ss][_xy][iMin:iMax]
#             oePxDiv["XY"][_ss][_xy] = oePxDiv["XY"][_ss][_xy][iMin:iMax]

#         # Grab from Pickles
#         else:
#             try:
#                 bright ["XY"][_ss][_xy] = corrSpots    ["Spot"][_xy]["SpotBright"]["xSpotDivBlank"][iMin:iMax]
#             except:
#                 bright ["XY"][_ss][_xy] = np.array(([0] * len(imgs["Full"][_ss]))[iMin:iMax])
#             try:
#                 allPxls["XY"][_ss][_xy] = pxCounts[_ss]["Spot"][_xy]              ["Blank"]        [iMin:iMax]
#             except:
#                 allPxls["XY"][_ss][_xy] = np.array(([0] * len(imgs["Full"][_ss]))[iMin:iMax])
#             try:
#                 oePxls ["XY"][_ss][_xy] = pxCounts[_ss]["Spot"][_xy]              ["Blank-Clean"]  [iMin:iMax]
#             except:
#                 oePxls ["XY"][_ss][_xy] = np.array(([0] * len(imgs["Full"][_ss]))[iMin:iMax])

#             oePxDiv["XY"][_ss][_xy] = np.nan_to_num(np.divide(oePxls["XY"][_ss][_xy], allPxls["XY"][_ss][_xy]), copy=False, nan=0, posinf=0, neginf=0)


#         relBright["XY"][_ss][_xy] = np.nan_to_num(np.multiply(np.divide(bright ["XY"][_ss][_xy], bright ["Full"][_ss]), 100), copy=False, nan=0, posinf=0, neginf=0) # (SpotBright / ImBright) * 100%
#         relBright["Full"][_ss] = np.add(relBright["Full"][_ss], relBright["XY"][_ss][_xy])




# figs = list()
# subL = list()
# subR = list()


# if usePickles:
#     # Plot SS of used brightness and replacements
#     fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
#     figs.append(fig)
#     subL.append(lAxis)
#     subR.append(__twinx2D___(fig, lAxis))

#     subL[-1][0,0].plot(range(len(corrSpots["Full"]       ["BrightnessFromSS"])), corrSpots["Full"]       ["BrightnessFromSS"], ".--", markersize=10, color="#000000", label="Shutterspeed")
#     if printXYOn[0] != None:    subL[-1][1,0].plot(range(len(corrSpots["Spot"][XY[printXYOn[0]]]["BrightnessFromSS"])), corrSpots["Spot"][XY[printXYOn[0]]]["BrightnessFromSS"], ".", markersize=5,  color="#FF0000", label="Shutterspeed")
#     if printXYOn[1] != None:    subL[-1][1,1].plot(range(len(corrSpots["Spot"][XY[printXYOn[1]]]["BrightnessFromSS"])), corrSpots["Spot"][XY[printXYOn[1]]]["BrightnessFromSS"], ".", markersize=5,  color="#008000", label="Shutterspeed")
#     if printXYOn[2] != None:    subL[-1][2,0].plot(range(len(corrSpots["Spot"][XY[printXYOn[2]]]["BrightnessFromSS"])), corrSpots["Spot"][XY[printXYOn[2]]]["BrightnessFromSS"], ".", markersize=5,  color="#0000FF", label="Shutterspeed")
#     if printXYOn[3] != None:    subL[-1][2,1].plot(range(len(corrSpots["Spot"][XY[printXYOn[3]]]["BrightnessFromSS"])), corrSpots["Spot"][XY[printXYOn[3]]]["BrightnessFromSS"], ".", markersize=5,  color="#FF8000", label="Shutterspeed")

#     __SameXYLabelsOnLRSubplots__(lAxis=subL[-1], lText="SS [µs]", rAxis=subR[-1], rText="", xText="Time [s]")
#     __SameXYLimitsOnLRSubplots__(lAxis=subL[-1], lYLim=[-1000, 11000], rAxis=subR[-1], rYLim=None, xLim=None)
#     figs[-1].legend(loc="upper right")
#     figs[-1].suptitle("Shutterspeeds from where brightness were reconstructed")
#     figs[-1].tight_layout()


#     fig, lAxis = plt.subplots(nrows=1, ncols=1)#, sharex=True, sharey=True)
#     figs.append(fig)
#     subL.append(lAxis)
#     subR.append(lAxis)

#     subL[-1].plot(range(len(corrSpots["Full"]       ["BrightnessFromSS"])), corrSpots["Full"]       ["BrightnessFromSS"], ".--", markersize=10, color="#000000", label="Shutterspeed")
#     if printXYOn[0] != None:    subL[-1].plot(range(len(corrSpots["Spot"][XY[printXYOn[0]]]["BrightnessFromSS"])), corrSpots["Spot"][XY[printXYOn[0]]]["BrightnessFromSS"], ".", markersize=5,  color="#FF0000", label="Shutterspeed")
#     if printXYOn[1] != None:    subL[-1].plot(range(len(corrSpots["Spot"][XY[printXYOn[1]]]["BrightnessFromSS"])), corrSpots["Spot"][XY[printXYOn[1]]]["BrightnessFromSS"], ".", markersize=5,  color="#008000", label="Shutterspeed")
#     if printXYOn[2] != None:    subL[-1].plot(range(len(corrSpots["Spot"][XY[printXYOn[2]]]["BrightnessFromSS"])), corrSpots["Spot"][XY[printXYOn[2]]]["BrightnessFromSS"], ".", markersize=5,  color="#0000FF", label="Shutterspeed")
#     if printXYOn[3] != None:    subL[-1].plot(range(len(corrSpots["Spot"][XY[printXYOn[2]]]["BrightnessFromSS"])), corrSpots["Spot"][XY[printXYOn[3]]]["BrightnessFromSS"], ".", markersize=5,  color="#FF8000", label="Shutterspeed")

#     # PlotSupTitleAndLegend(figs[-1], "Shutterspeeds from where brightness were reconstructed")
#     subL[-1].set_ylabel("SS [µs]")
#     subL[-1].set_xlabel("Time [s]")
#     subL[-1].set_ylim([-int(SS[0]*0.1), int(SS[0]*1.1)])
#     figs[-1].suptitle("Shutterspeeds from where brightness were reconstructed")
#     figs[-1].tight_layout()
#     figs[-1].legend()


# for _ss in SS:
#     xVal = np.array(list(range(len(imgs["Full"][_ss])))[iMin:iMax])

#     fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
#     figs.append(fig)
#     subL.append(lAxis)
#     subR.append(__twinx2D___(fig, lAxis))

#     subL[-1][0,0].plot(xVal, bright["Full"][_ss]       , ".", color="#808080", label="Brightness")
#     if printXYOn[0] != None:        subL[-1][1,0].plot(xVal, bright["XY"][_ss][XY[printXYOn[0]]], ".", color="#808080", label="Brightness")
#     if printXYOn[1] != None:        subL[-1][1,1].plot(xVal, bright["XY"][_ss][XY[printXYOn[1]]], ".", color="#808080", label="Brightness")
#     if printXYOn[2] != None:        subL[-1][2,0].plot(xVal, bright["XY"][_ss][XY[printXYOn[2]]], ".", color="#808080", label="Brightness")
#     if printXYOn[3] != None:        subL[-1][2,1].plot(xVal, bright["XY"][_ss][XY[printXYOn[3]]], ".", color="#808080", label="Brightness")

#     # subR[-1][0,0].plot(xVal, oePxDiv["Full"][_ss]       , ".", color="#008000", label="Overexpose-Rate")
#     # subR[-1][1,0].plot(xVal, oePxDiv["XY"]  [_ss][XY[0]], ".", color="#008000", label="Overexpose-Rate")
#     # subR[-1][1,1].plot(xVal, oePxDiv["XY"]  [_ss][XY[1]], ".", color="#008000", label="Overexpose-Rate")
#     # # subR[-1][2,0].plot(xVal, oePxDiv["XY"]  [_ss][XY[2]], ".", color="#008000", label="Overexpose-Rate")
#     # subR[-1][2,1].plot(xVal, oePxDiv["XY"]  [_ss][XY[2]], ".", color="#008000", label="Overexpose-Rate")

#     subR[-1][0,0].plot(xVal, relBright["Full"][_ss]       , ".", color="#800080", label="Contribution")
#     if printXYOn[0] != None:        subR[-1][1,0].plot(xVal, relBright["XY"][_ss][XY[printXYOn[0]]], ".", color="#800080", label="Contribution")
#     if printXYOn[1] != None:        subR[-1][1,1].plot(xVal, relBright["XY"][_ss][XY[printXYOn[1]]], ".", color="#800080", label="Contribution")
#     if printXYOn[2] != None:        subR[-1][2,0].plot(xVal, relBright["XY"][_ss][XY[printXYOn[2]]], ".", color="#800080", label="Contribution")
#     if printXYOn[3] != None:        subR[-1][2,1].plot(xVal, relBright["XY"][_ss][XY[printXYOn[3]]], ".", color="#800080", label="Contribution")

#     PlotSupTitleAndLegend(figs[-1], str.format("Brightness & Tipcontribution for SS={:.2f}ms", _ss/1000))
#     __SameXYLabelsOnLRSubplots__(lAxis=subL[-1], lText="Brightness", rAxis=subR[-1], rText="[%]", xText="Time [s]")
#     __SameXYLimitsOnLRSubplots__(lAxis=subL[-1], lYLim=None, rAxis=subR[-1], rYLim=[-20, 120], xLim=None)

#     fig, lAxis = plt.subplots(nrows=3, ncols=2) #, sharex=True, sharey=True)
#     figs.append(fig)
#     subL.append(lAxis)
#     subR.append(__twinx2D___(fig, lAxis))

#     subL[-1][0,0].plot(xVal, allPxls["Full"][_ss]       , ".", color="#404040", label="Contributing Pxls (>=" + str(b2Count) + ")")
#     if printXYOn[0] != None:        subL[-1][1,0].plot(xVal, allPxls["XY"][_ss][XY[printXYOn[0]]], ".", color="#404040", label="Contributing Pxls (>=" + str(b2Count) + ")")
#     if printXYOn[1] != None:        subL[-1][1,1].plot(xVal, allPxls["XY"][_ss][XY[printXYOn[1]]], ".", color="#404040", label="Contributing Pxls (>=" + str(b2Count) + ")")
#     if printXYOn[2] != None:        subL[-1][2,0].plot(xVal, allPxls["XY"][_ss][XY[printXYOn[2]]], ".", color="#404040", label="Contributing Pxls (>=" + str(b2Count) + ")")
#     if printXYOn[3] != None:        subL[-1][2,1].plot(xVal, allPxls["XY"][_ss][XY[printXYOn[3]]], ".", color="#404040", label="Contributing Pxls (>=" + str(b2Count) + ")")

#     subL[-1][0,0].plot(xVal, oePxls["Full"][_ss]       , "*", color="#C00000", label="Overexposed Pxls (>=" + str(b2CountAsOE) + ")")
#     if printXYOn[0] != None:        subL[-1][1,0].plot(xVal, oePxls["XY"][_ss][XY[printXYOn[0]]], "*", color="#C00000", label="Overexposed Pxls (>=" + str(b2CountAsOE) + ")")
#     if printXYOn[1] != None:        subL[-1][1,1].plot(xVal, oePxls["XY"][_ss][XY[printXYOn[1]]], "*", color="#C00000", label="Overexposed Pxls (>=" + str(b2CountAsOE) + ")")
#     if printXYOn[2] != None:        subL[-1][2,0].plot(xVal, oePxls["XY"][_ss][XY[printXYOn[2]]], "*", color="#C00000", label="Overexposed Pxls (>=" + str(b2CountAsOE) + ")")
#     if printXYOn[3] != None:        subL[-1][2,1].plot(xVal, oePxls["XY"][_ss][XY[printXYOn[3]]], "*", color="#C00000", label="Overexposed Pxls (>=" + str(b2CountAsOE) + ")")


#     subR[-1][0,0].plot(xVal, oePxDiv["Full"][_ss]       , ".", color="#00C000", label="OvrExp / Contribute * 100%")
#     if printXYOn[0] != None:        subR[-1][1,0].plot(xVal, oePxDiv["XY"][_ss][XY[printXYOn[0]]], ".", color="#00C000", label="OvrExp / Contribute * 100%")
#     if printXYOn[1] != None:        subR[-1][1,1].plot(xVal, oePxDiv["XY"][_ss][XY[printXYOn[1]]], ".", color="#00C000", label="OvrExp / Contribute * 100%")
#     if printXYOn[2] != None:        subR[-1][2,0].plot(xVal, oePxDiv["XY"][_ss][XY[printXYOn[2]]], ".", color="#00C000", label="OvrExp / Contribute * 100%")
#     if printXYOn[3] != None:        subR[-1][2,1].plot(xVal, oePxDiv["XY"][_ss][XY[printXYOn[3]]], ".", color="#00C000", label="OvrExp / Contribute * 100%")

#     PlotSupTitleAndLegend(figs[-1], str.format("Amount of Contributing and Overexposed Pixels for SS={:.2f}ms", _ss/1000))
#     __SameXYLabelsOnLRSubplots__(lAxis=subL[-1], lText="Px-Count", rAxis=subR[-1], rText="[%]", xText="Time [s]")
#     if not usePickles:
#         __SameXYLimitsOnLRSubplots__(lAxis=subL[-1], lYLim=None, rAxis=subR[-1], rYLim=[-2, 20], xLim=None)
#     else:
#         __SameXYLimitsOnLRSubplots__(lAxis=subL[-1], lYLim=None, rAxis=subR[-1], rYLim=[-2, 20], xLim=None)
#         # __SameXYLimitsOnLRSubplots__(lAxis=subL[-1], lYLim=None, rAxis=subR[-1], rYLim=[-0.05, 0.2], xLim=None)



# # for _ss in SS:
# print("Finished")