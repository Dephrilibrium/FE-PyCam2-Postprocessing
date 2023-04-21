from os.path import join, basename, dirname
from os import makedirs
import pickle
import numpy as np
import FieldEmission as fe


import matplotlib.pyplot as plt


from misc import GrabPklFile
from misc import PlotSupTitleAndLegend
from misc import GetQuadrantOfSpot
from misc import SaveFigList

from _alt.Check_GradeOfOverexposement import __twinx2D___
from _alt.Check_GradeOfOverexposement import __SameXYLimitsOnLRSubplots__
from _alt.Check_GradeOfOverexposement import __SameXYLabelsOnLRSubplots__
from Paper2x2_misc import ColorizeTwinedXWith
from Paper2x2_misc import ReadResistorFile
from Paper2x2_misc import ReadSwpFile
from Paper2x2_misc import ReadCFFile
from Paper2x2_misc import ReadUDFile








# bPath = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\01 Aktivierung IMax1V\230221_115432 Tip Ch1 (aktiviert, 6517)"
# bPath = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\01 Aktivierung IMax1V\230221_124600 Tip Ch2 (aktiviert)"
# bPath = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\01 Aktivierung IMax1V\230222_095249 Tip Ch3 (aktiviert)"
# bPath = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\01 Aktivierung IMax1V\230222_103240 Tip Ch4 (aktiviert)"

# bPath = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\03 Sample-Sweeps\230307_124953 1kV IMax500nA"
bPath = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\02 Alle Zusammen\230306_140339 1kV 250nA #2"
# Read Image-Data
PMP_OE_Bright = GrabPklFile(join(bPath, "PMP_ScaledWhereOverexposedBrightnesses.pkl"))
PMP_PixlAreas = GrabPklFile(join(bPath, "PMP_PxAreaCnts4Brightness.pkl"))
imgWH = [700, 700]

XY = list(PMP_OE_Bright["Spot"].keys())
ssKeys = list(PMP_PixlAreas.keys())
yKeys = list(PMP_OE_Bright["Full"]["SpotBright"].keys())

PMP_PixlAreas = PMP_PixlAreas[ssKeys[0]]










# Read and sort el. data
res = ReadResistorFile(join(bPath, "*.resistor"))

swp = ReadSwpFile(join(bPath, "*.swp"))
swp.AppendColumn("Time", np.linspace(0, swp.Rows * 6, swp.Rows, endpoint=True))

elSpotOrder = [1,2,0,3]

# ig = ReadCFFile(join(bPath, "Dev7_ISum.dat"             ), None)
# i0 = ReadCFFile(join(bPath, "Dev100_FEAR16v2(Ch0CF).dat"), res)
# i1 = ReadCFFile(join(bPath, "Dev100_FEAR16v2(Ch1CF).dat"), res)
# i2 = ReadCFFile(join(bPath, "Dev100_FEAR16v2(Ch2CF).dat"), res)
# i3 = ReadCFFile(join(bPath, "Dev100_FEAR16v2(Ch3CF).dat"), res)

cPaths = [
"Dev100_FEAR16v2(Ch0CF).dat",
"Dev100_FEAR16v2(Ch1CF).dat",
"Dev100_FEAR16v2(Ch2CF).dat",
"Dev100_FEAR16v2(Ch3CF).dat",
]
cf = dict()
cf["Full"] = ReadCFFile(join(bPath, "Dev7_ISum.dat"), None)
for _iXY in range(len(XY)):
    _xy = XY[_iXY]
    y, x = GetQuadrantOfSpot(spotCoord=_xy, imgWH=imgWH)
    _i = x + 2*y
    cf[_xy] = ReadCFFile(fPath=join(bPath, cPaths[elSpotOrder[_i]]), resistor=res)
del cPaths
# cf = {
#     "Full": ig,
#      XY[0]: i1,
#      XY[1]: i2,
#      XY[2]: i0,
#      XY[3]: i3,
# }
# del i0, i1, i2, i3


# UDrop
# u0 = ReadUDFile(join(bPath, "Dev100_FEAR16v2(Ch0UD).dat"), swpProvider=swp)
# u1 = ReadUDFile(join(bPath, "Dev100_FEAR16v2(Ch1UD).dat"), swpProvider=swp)
# u2 = ReadUDFile(join(bPath, "Dev100_FEAR16v2(Ch2UD).dat"), swpProvider=swp)
# u3 = ReadUDFile(join(bPath, "Dev100_FEAR16v2(Ch3UD).dat"), swpProvider=swp)
uPaths = [
"Dev100_FEAR16v2(Ch0UD).dat",
"Dev100_FEAR16v2(Ch1UD).dat",
"Dev100_FEAR16v2(Ch2UD).dat",
"Dev100_FEAR16v2(Ch3UD).dat",
]
ud = dict()
ud["Full"] = swp
for _iXY in range(len(XY)):
    _xy = XY[_iXY]
    y, x = GetQuadrantOfSpot(spotCoord=_xy, imgWH=imgWH)
    _i = x + 2*y
    ud[_xy] = ReadUDFile(fPath=join(bPath, uPaths[elSpotOrder[_i]]), swpProvider=swp)
del uPaths
# ud = {
#     "Full": swp,
#      XY[0]: u1,
#      XY[1]: u2,
#      XY[2]: u0,
#      XY[3]: u3,
# }
# del u0, u1, u2, u3





# Build ImageData (collection of Brightness and ShutterSpeed)
# idDataSet = "PxlBright"
idDataSet = "SpotBright"
idSubSet = yKeys[0]

nanLoVal = 1e-10

id = dict()
id["Full"] = fe.DataProvider("Br",           np.abs(PMP_OE_Bright["Full"][idDataSet][idSubSet])    )    # Just grab theoretical upscale
id["Full"]     .AppendColumn("SS", np.divide(np.abs(PMP_OE_Bright["Full"]["BrightnessFromSS"]), 1000))  # µs / 1000 = ms
# id["Full"]     .AppendColumn("Ar", np.power (np.abs(PMP_PixlAreas["Full"]["Blank"]), 2))                # PxCnt

pxArr = np.abs(PMP_PixlAreas["Full"]["Blank"])
pxArr[pxArr < 1] = 1
id["Full"]     .AppendColumn("Ar", pxArr)                    # PxCnt
# id["Full"]     .DivideColumn("Br", id["Full"].GetColumn("Ar"))

for _xy in XY:
    id[_xy] = fe.DataProvider("Br",          np.abs(          PMP_OE_Bright["Spot"][_xy][idDataSet][idSubSet]    ))     # Just grab theoretical upscale
    id[_xy]     .AppendColumn("SS",          np.abs(np.divide(PMP_OE_Bright["Spot"][_xy]["BrightnessFromSS"], 1000)))   # µs / 1000 = ms
    id[_xy]     .AppendColumn("Ar",          np.abs(PMP_PixlAreas["Spot"][_xy]["Blank"]))                               # PxCnt
    pxArr = np.abs(PMP_PixlAreas["Spot"][_xy]["Blank"])
    pxArr[pxArr < 1] = 1
    # id[_xy]     .AppendColumn("Ar", pxArr)                               # PxCnt
    # id[_xy]     .DivideColumn("Br", id[_xy].GetColumn("Ar"))
    # id[_xy].   OverrideColumn("Br", np.nan_to_num(id[_xy].GetColumn("Br"), nan=nanLoVal, posinf=nanLoVal, neginf=nanLoVal))            # FN-Linearization is also done by I/U^2 -> Try

# Make "Current"-Brightness (remove voltage dependency)
for _xy in XY:
    # uSquared = np.power(ud[_xy]["U"], 1)
    uSquared = ud[_xy]["U"]
    uSquared[uSquared < 1] = 1
    id[_xy]["Br/U"] = np.divide(id[_xy]["Br"], uSquared)            # FN-Linearization is also done by I/U^2 -> Try
    id[_xy]["Br/U"] = np.nan_to_num(id[_xy]["Br/U"], nan=nanLoVal, posinf=nanLoVal, neginf=nanLoVal)            # FN-Linearization is also done by I/U^2 -> Try
    # id[_xy].DivideColumn("Br", ud[_xy].GetColumn("U"))







# Preparation
figs = list()
subL = list()
subR = list()


# Plot Brightness and 
fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
figs.append(fig)
subL.append(lAxis)
subR.append(__twinx2D___(fig, lAxis))



_x = np.array(list(range(len(id[XY[0]].GetColumn("Br")))))
subL[-1][0][0].semilogy(_x, id["Full"].GetColumn("Br"), "d--", markersize=4, linewidth=1  , color="#FF0000", label="Sum(Brightness)")
subR[-1][0][0].plot    (_x, id["Full"].GetColumn("SS"), ".--", markersize=2, linewidth=0.5, color="#666666", label="From Shutterspeed")

for _xy in XY:
    _iY, _iX = GetQuadrantOfSpot(_xy, imgWH)
    _iY += 1 # Add the y-Offset
    subL[-1][_iY][_iX].semilogy(_x, id[_xy].GetColumn("Br"), "d--", markersize=4, linewidth=1  , color="#FF0000", label="Sum(Brightness)")
    subR[-1][_iY][_iX].plot    (_x, id[_xy].GetColumn("SS"), ".--", markersize=2, linewidth=0.5, color="#666666", label="From Shutterspeed")

    subL[-1][0][0].plot(_x, id[_xy].GetColumn("Br"), "1--", markersize=4, linewidth=0.5, label=f"Spot@{_xy}")

PlotSupTitleAndLegend(figs[-1], "F01 - Brightness & Shutterspeed")
__SameXYLimitsOnLRSubplots__(subL[-1], [1e0, 1e9], subR[-1], [0, 35], None)
ColorizeTwinedXWith(subR[-1], "#666666")
subL[-1][0][0].set_ylabel("Brightness")
subL[-1][1][0].set_ylabel("Brightness")
subL[-1][2][0].set_ylabel("Brightness")
subR[-1][0][1].set_ylabel("Shutterspeed")
subR[-1][1][1].set_ylabel("Shutterspeed")
subR[-1][2][1].set_ylabel("Shutterspeed")





# Plot El-Data
fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
figs.append(fig)
subL.append(lAxis)
subR.append(__twinx2D___(fig, lAxis))



_x = np.array(list(range(len(cf["Full"].GetColumn("I")))))
subL[-1][0][0].semilogy(_x, cf["Full"].GetColumn( "I"), "d--", markersize=4, linewidth=1  , color="#FF0000", label="El. Current")
subR[-1][0][0].plot    (_x, swp       .GetColumn("U7"), "1--", markersize=2, linewidth=0.5, color="#666666", label="Voltage")

for _xy in XY:
    _iY, _iX = GetQuadrantOfSpot(_xy, imgWH)
    _iY += 1 # Add the y-Offset
    subL[-1][_iY][_iX].semilogy(_x, cf[_xy].GetColumn("I"), "d--", markersize=4, linewidth=1  , color="#FF0000", label="El. Current")
    subR[-1][_iY][_iX].plot    (_x, ud[_xy].GetColumn("U"), "1--", markersize=2, linewidth=0.5, color="#666666", label="Voltage")

    subL[-1][0][0].plot(_x, cf[_xy].GetColumn("I"), "1--", markersize=4, linewidth=0.5, label=f"Current@{_xy}")

PlotSupTitleAndLegend(figs[-1], "F02 - Current & Voltage")
__SameXYLimitsOnLRSubplots__(subL[-1], [1e-10, 1e-5], subR[-1], [-50, 1050], None)
ColorizeTwinedXWith(subR[-1], "#666666")
subL[-1][0][0].set_ylabel("Current")
subL[-1][1][0].set_ylabel("Current")
subL[-1][2][0].set_ylabel("Current")
subR[-1][0][1].set_ylabel("Supply-Voltage")
subR[-1][1][1].set_ylabel("Tip-Voltage")
subR[-1][2][1].set_ylabel("Tip-Voltage")









### Brightness Contribution
# Build Brightness-Contribution
bc = dict()
for _iXY in range(len(XY)): # Add up all ucrrents to a sum (for comparison of measured sum of 6517B)
    _xy = XY[_iXY]
    if _iXY == 0:
        bc["SumB"] = np.array(id[_xy]["Br/U"].copy())
    else:
        bc["SumB"] = np.add(bc["SumB"], id[_xy]["Br/U"])

for _iXY in range(len(XY)): # Build CurrentContributions
    _xy = XY[_iXY]
    percDiv = np.nan_to_num(np.divide(id[_xy]["Br/U"], bc["SumB"]), nan=0, posinf=0, neginf=0, copy=True)

    if _iXY == 0:
        bc["Sum%"] =  np.array(percDiv.copy())
    else:
        bc["Sum%"] = np.add(bc["Sum%"], percDiv)
    
    bc[_xy] = percDiv


# Plot Brightness contribution
fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
figs.append(fig)
subL.append(lAxis)
subR.append(__twinx2D___(fig, lAxis))



_x = np.array(list(range(len(cf["Full"].GetColumn("I")))))
subL[-1][0][0].semilogy(_x, bc["SumB"], "d--", markersize=4, linewidth=1  , color="#FF0000", label="Bright")
subR[-1][0][0].plot    (_x, bc["Sum%"], "1--", markersize=2, linewidth=0.5, color="#666666", label="Contrib.")

for _xy in XY:
    _iY, _iX = GetQuadrantOfSpot(_xy, imgWH)
    _iY += 1 # Add the y-Offset
    subL[-1][_iY][_iX].semilogy(_x, id[_xy]["Br"]  , "d--", markersize=4, linewidth=1  , color="#FF0000", label="Bright")
    subL[-1][_iY][_iX].semilogy(_x, id[_xy]["Br/U"], "d--", markersize=4, linewidth=1  , color="#00CC00", label="Bright/U")
    subR[-1][_iY][_iX].plot    (_x, bc[_xy]        , "1--", markersize=2, linewidth=0.5, color="#666666", label="Contrib.")

    subL[-1][0][0].plot(_x, id[_xy]["Br"], "1--", markersize=4, linewidth=0.5, label=f"Bright@{_xy}")
    subR[-1][0][0].plot(_x, bc[_xy]      , "1--", markersize=4, linewidth=0.5, label=f"Contrib.@{_xy}")

PlotSupTitleAndLegend(figs[-1], "F03 - Brightness & Ratio")
__SameXYLimitsOnLRSubplots__(subL[-1], [1e0, 1e9], subR[-1], [-0.1, 1.1], None)
ColorizeTwinedXWith(subR[-1], "#666666")
subL[-1][0][0].set_ylabel("Brightness")
subL[-1][1][0].set_ylabel("Brightness")
subL[-1][2][0].set_ylabel("Brightness")
subR[-1][0][1].set_ylabel("Ratio")
subR[-1][1][1].set_ylabel("Ratio")
subR[-1][2][1].set_ylabel("Ratio")











# Build Current Sum and brightnes-dependend current contribution
# Build I-Contribution
ic = dict()
for _iXY in range(len(XY)): # Add up all ucrrents to a sum (for comparison of measured sum of 6517B)
    _xy = XY[_iXY]
    if _iXY == 0:
        ic["SumI"] = np.array(cf[_xy].GetColumn("I").copy())
    else:
        ic["SumI"] = np.add(ic["SumI"], cf[_xy].GetColumn("I"))

iDev = dict()
for _iXY in range(len(XY)): # Build CurrentContributions
    _xy = XY[_iXY]
    # brightCurr = np.multiply(cf["Full"].GetColumn("I"), bc[_xy])
    # iDev[_xy] = np.divide(brightCurr, cf[_xy].GetColumn("I"))
    brightCurr = np.multiply(ic["SumI"], bc[_xy])
    iDev[_xy] = np.divide(brightCurr, ic["SumI"])
    # iDev[_xy] = np.divide(brightCurr, cf[_xy]["I"])

    if _iXY == 0:
        iDev["SumDev"] = iDev[_xy].copy()
        ic["SumBrI"] = brightCurr.copy()
    else:
        iDev["SumDev"] = np.add(iDev["SumDev"], iDev[_xy])
        ic["SumBrI"] = np.add(ic["SumBrI"], brightCurr)

    ic[_xy] = brightCurr

# Plot
fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
figs.append(fig)
subL.append(lAxis)
subR.append(__twinx2D___(fig, lAxis))



_x = np.array(list(range(len(cf["Full"].GetColumn("I")))))
subL[-1][0][0].semilogy(_x, cf["Full"].GetColumn("I"), "d--", markersize=4, linewidth=1  , color="#FF0000", label="El. Current")
subL[-1][0][0].semilogy(_x, cf["Full"].GetColumn("I"), "d--", markersize=4, linewidth=1  , color="#FF0000", label="Br. Current")
subL[-1][0][0].semilogy(_x, ic["SumI"]               , "x--", markersize=4, linewidth=1  , color="#0000FF", label="Sum(TipCurrent)")
subL[-1][0][0].semilogy(_x, ic["SumBrI"]             , "3--", markersize=4, linewidth=1  , color="#000000", label="Sum(BrCurrent)")
subR[-1][0][0].plot    (_x, bc["Sum%"]               , "1--", markersize=2, linewidth=0.5, color="#666666", label="Sum(Ratio)")
subR[-1][_iY][_iX].plot([_x[0], _x[-1]], [1, 1]      ,  "-.", markersize=2, linewidth=1  , color="#000000", label="\"1\"")

for _xy in XY:
    _iY, _iX = GetQuadrantOfSpot(_xy, imgWH)
    _iY += 1 # Add the y-Offset
    subL[-1][_iY][_iX].semilogy(_x             , cf[_xy].GetColumn("I"), "d--", markersize=4, linewidth=1  , color="#FF0000", label="El. Current")
    subL[-1][_iY][_iX].semilogy(_x             , ic[_xy]               , "x--", markersize=4, linewidth=1  , color="#000000", label="Br. Current")
    subR[-1][_iY][_iX].plot    (_x             , bc[_xy]               , "1--", markersize=2, linewidth=0.5, color="#666666", label="Ratio of 100%")
    subR[-1][_iY][_iX].plot    (_x             , iDev[_xy]             , "3--", markersize=2, linewidth=0.5, color="#0000FF", label="BrCurrent/TipCurrent")
    subR[-1][_iY][_iX].plot    ([_x[0], _x[-1]], [1, 1]                ,  "-.", markersize=2, linewidth=1  , color="#000000", label="\"1\"")

    subL[-1][0][0].plot(_x, ic[_xy], "1--", markersize=8, linewidth=0.5, label=f"TipCurr.@{_xy}")
    subR[-1][0][0].plot(_x, bc[_xy], "2--", markersize=4, linewidth=0.5, label=f"Ratio@{_xy}")

PlotSupTitleAndLegend(figs[-1], "F04 - El. Current, BrightCurrent & Ratio", loc="upper right", ncol=2)
__SameXYLimitsOnLRSubplots__(subL[-1], [1e-10, 1e-5], subR[-1], [-0.1, 3.1], None)
ColorizeTwinedXWith(subR[-1], "#666666")
subL[-1][0][0].set_ylabel("Current")
subL[-1][1][0].set_ylabel("Current")
subL[-1][2][0].set_ylabel("Current")
subR[-1][0][1].set_ylabel("Ratio")
subR[-1][1][1].set_ylabel("Ratio")
subR[-1][2][1].set_ylabel("Ratio")










# Plot BrightCurrent and area
fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
figs.append(fig)
subL.append(lAxis)
subR.append(__twinx2D___(fig, lAxis))



_x = np.array(list(range(len(cf["Full"].GetColumn("I")))))
subL[-1][0][0].semilogy(_x, id["Full"].GetColumn("Br"), "d--", markersize=4, linewidth=1  , color="#FF0000", label="Brightness")
subR[-1][0][0].plot    (_x, id["Full"].GetColumn("Ar"), "1--", markersize=4, linewidth=1  , color="#008000", label="Area (Pxls > 1)")

for _xy in XY:
    _iY, _iX = GetQuadrantOfSpot(_xy, imgWH)
    _iY += 1 # Add the y-Offset
    subL[-1][_iY][_iX].semilogy(_x, id[_xy].GetColumn("Br"), "d--", markersize=4, linewidth=1  , color="#FF0000", label="Brightness")
    subR[-1][_iY][_iX].plot    (_x, id[_xy].GetColumn("Ar"), "1--", markersize=4, linewidth=1  , color="#008000", label="Area (Pxls > 1)")

PlotSupTitleAndLegend(figs[-1], "F05 - Brightness & Area")
__SameXYLimitsOnLRSubplots__(subL[-1], [1e-7, 1e8], subR[-1], [-100, 6650], None)
ColorizeTwinedXWith(subR[-1], "#666666")
subL[-1][0][0].set_ylabel("Brightness")
subL[-1][1][0].set_ylabel("Brightness")
subL[-1][2][0].set_ylabel("Brightness")
subR[-1][0][1].set_ylabel("PxlCnts")
subR[-1][1][1].set_ylabel("PxlCnts")
subR[-1][2][1].set_ylabel("PxlCnts")











# Plot el. Current, brightCurrent and area
fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
figs.append(fig)
subL.append(lAxis)
subR.append(__twinx2D___(fig, lAxis))



_x = np.array(list(range(len(cf["Full"].GetColumn("I")))))
subL[-1][0][0].semilogy(_x, cf["Full"].GetColumn("I") , "d--", markersize=4, linewidth=1  , color="#FF0000", label="OverallCurrent")
subL[-1][0][0].semilogy(_x, ic["SumI"]                , "3--", markersize=4, linewidth=1  , color="#0000FF", label="Sum(TipCurrent)")
subL[-1][0][0].semilogy(_x, ic["SumBrI"]              , "x--", markersize=4, linewidth=1  , color="#000000", label="Sum(BrightCurrent)")
# subR[-1][0][0].plot    (_x, id["Full"].GetColumn("Ar"), "1--", markersize=4, linewidth=1  , color="#008000", label="Area (Pxls > 5)")
subR[-1][0][0].plot    (_x, iDev["SumDev"]            , "1--", markersize=4, linewidth=1  , color="#008000", label="Sum(BrCurr/Curr)")


for _xy in XY:
    _iY, _iX = GetQuadrantOfSpot(_xy, imgWH)
    _iY += 1 # Add the y-Offset
    subL[-1][_iY][_iX].semilogy(_x, cf[_xy].GetColumn("I") , "d--", markersize=4, linewidth=1  , color="#FF0000", label="TipCurrent")
    subL[-1][_iY][_iX].semilogy(_x, ic[_xy]                , "x--", markersize=4, linewidth=1  , color="#000000", label="BrightnessCurrent")
    # subR[-1][_iY][_iX].plot    (_x, id[_xy].GetColumn("Ar"), "1--", markersize=4, linewidth=1  , color="#008000", label="Area (Pxls > 5)")
    subR[-1][_iY][_iX].plot    (_x, iDev[_xy]              , "1--", markersize=4, linewidth=1  , color="#008000", label="BrCurr/TipCurr")

    subR[-1][_iY][_iX].plot    ([_x[0], _x[-1]],     [1, 1],  "-.", markersize=4, linewidth=1  , color="#000000", label="1")

PlotSupTitleAndLegend(figs[-1], "F06 - El. Current, Br. Current, Ratio and Deviation")
__SameXYLimitsOnLRSubplots__(subL[-1], [1e-10, 1e-3], subR[-1], [-0.2, 3.2], None)
ColorizeTwinedXWith(subR[-1], "#666666")
subL[-1][0][0].set_ylabel("Current")
subL[-1][1][0].set_ylabel("Current")
subL[-1][2][0].set_ylabel("Current")
subR[-1][0][1].set_ylabel("Factor")
subR[-1][1][1].set_ylabel("Factor")
subR[-1][2][1].set_ylabel("Factor")













sPath = join(bPath, "Plots")
makedirs(sPath, exist_ok=True)
SaveFigList(figList=figs, saveFolder=sPath, figSize=(15,12), dpi=300)




print("Finished")