import sys
import os
from os.path import join, dirname, basename, abspath, splitext
# sys.path.append(dirname(dirname(abspath(__file__)))) # If the data evaluation script is stored in a subfolder of the libs, this line may be neccessary and depend on your folderstructure

from lib import SplitAndMean, ReadElAsDP, ReadSwpAsDP, ReadSwpAsDPFromFolder, ReadPkl, ReadResistor, ReadResistorFromFolder
from lib import GetQuadrantOfSpot, CombinePlots, Twinx2D_2x2, Twinx2D_3x2, SameXYLimitsOnAxisColl, SameXYLimitsOnLRSubplots, SaveFigList
from lib import PlotSupTitleAndLegend, PlotLegend, ShowMajorMinorY

from CombiCommon import Build_CF_UD_DP, Build_IC_DP, AbsAllDPColumns
from CombiCommon import DataPreparation, DataPlot, FNDataPreparation, FNDataPlot
from CombiCommon import DataBuildPotentials, DataPlotPotentials, DataPlotPotentials
from CombiCommon import FN_And_CurrDeviation, FNDeviDataPlot

from CalcCrossCurrInfo import CalcCrossEmissionInfo

import glob
import FieldEmission as fe
import numpy as np
import matplotlib.pyplot as plt
import parse
import json

os.chdir(dirname(__file__))



folderFromFilename = splitext(basename(__file__))[0]
folders = [
join(os.getcwd(), folderFromFilename),
]


plotCol = {
    "el": [
        "#FF0000",
        "#00FF00",
        "#0000FF",
        "#FF8000",
    ],
    "brEl": [
        "#800000",
        "#008000",
        "#000080",
        "#804000",
    ],
    "contrib": [
        "#FF00FF",
        "#FF00FF",
        "#FF00FF",
        "#FF00FF",
    ],
}


font = {
    #'family' : 'normal',
    #'weight' : 'bold',
    'size'   : 13}

imgWH = [650, 650]
brPaths = [
r"PMP_ScaledWhereOverexposedBrightnesses.pkl",
r"PMP_ScaledWhereOverexposedBrightnesses.pkl",
r"PMP_ScaledWhereOverexposedBrightnesses.pkl",
r"PMP_ScaledWhereOverexposedBrightnesses.pkl",
]

icPaths = [
r"Dev7_ISum.dat",
r"Dev7_ISum.dat",
r"Dev7_ISum.dat",
r"Dev7_ISum.dat",
]

tipNum_2_XYiPos = [
1, # There should only be 1 Spot -> Due to (too high) threshhold there was detected to much spots!
2, # There should only be 1 Spot -> Due to (too high) threshhold there was detected to much spots!
0, # There should only be 1 Spot -> Due to (too high) threshhold there was detected to much spots!
3, # There should only be 1 Spot -> Due to (too high) threshhold there was detected to much spots!
]

XY_Popout = sorted([
], reverse=True) # Highest index first!

cfPaths = [
r"Dev100_FEAR16v2(Ch0CF).dat",
r"Dev100_FEAR16v2(Ch1CF).dat",
r"Dev100_FEAR16v2(Ch2CF).dat",
r"Dev100_FEAR16v2(Ch3CF).dat",
]

udPaths = [
r"Dev100_FEAR16v2(Ch0UD).dat",
r"Dev100_FEAR16v2(Ch1UD).dat",
r"Dev100_FEAR16v2(Ch2UD).dat",
r"Dev100_FEAR16v2(Ch3UD).dat",
]

cfGNDPaths = [
r"Dev99_grounded(Ch0CF).dat",
r"Dev99_grounded(Ch1CF).dat",
r"Dev99_grounded(Ch2CF).dat",
r"Dev99_grounded(Ch3CF).dat",
]

udGNDPaths = [
r"Dev99_grounded(Ch0UD).dat",
r"Dev99_grounded(Ch1UD).dat",
r"Dev99_grounded(Ch2UD).dat",
r"Dev99_grounded(Ch3UD).dat",
]

# Setup plot
tipSep = dict()
tipSep["el"]    = dict()
# tipSep["br"]    = dict()
tipSum = dict()
tipSum["el"]    = dict()
# tipSum["br"]    = dict()

contrib = dict() # Brightness: Sum / Sum; + XY / Sum

brCurr = dict()

curDiv = dict()



plt.rc('font', **font)
figs = []
axLs = []
axRs = []
for _i in range(len(folders)):
    # CombiCommon.DataPreparation(globals())
    # Get current folder
    folder = folders[_i]

    fig, axL = plt.subplots(nrows=3, ncols=2)
    fig.set_size_inches(w=14, h=10)
    CombinePlots(fig, axL[0, 0:])

    axR = Twinx2D_3x2(fig, axL)
    figs.append(fig)
    axLs.append(axL)
    axRs.append(axR)

    # Grab brightness
    brPath = abspath(join(folder, brPaths[_i]))
    brDat = ReadPkl(brPath)
    keys = list(brDat["Spot"].keys())
    # Rearange keys, so that TipOfInterest (ToI) is first!
    keys.insert(0, keys.pop(3)) # Put ToI on first position
    # keys.append((500, 100)) # Add "missing" spot for el. Data

    # Grab el data and collect XY wise in dictionaries
    elDat = dict()
    elGNDDat = dict()
    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        x, y = GetQuadrantOfSpot(spotCoord=_xy, imgWH=imgWH)
        _iEl = 2*y + x

        if _iXY == 0:
            cfPath    = abspath(join(folder, cfPaths   [tipNum_2_XYiPos[_iEl]]))
            udPath    = abspath(join(folder, udPaths   [tipNum_2_XYiPos[_iEl]]))
        else:
            cfPath = abspath(join(folder, cfGNDPaths[tipNum_2_XYiPos[_iEl]]))
            udPath = abspath(join(folder, udGNDPaths[tipNum_2_XYiPos[_iEl]]))
        icPath    = abspath(join(folder, icPaths   [tipNum_2_XYiPos[_iEl]]))

        # Read and manage el. data
        cfDat    = ReadElAsDP(cfPath)
        udDat    = ReadElAsDP(udPath)
        icDat    = ReadElAsDP(icPath)
        swDat    = ReadSwpAsDPFromFolder(folder)
        reVal    = ReadResistorFromFolder(folder)

        cfDat   .RemoveRows(-1)
        udDat   .RemoveRows(-1)
        icDat   .RemoveRows(-1)
        elDat    = Build_CF_UD_DP(cf=cfDat   , ud=udDat   , uVec=swDat["U7"], resistor=reVal, dTime=6)
        elDat    = AbsAllDPColumns(elDat)
        icDat    = Build_IC_DP(icDat, swDat["U7"], dTime=6)
        icDat    = AbsAllDPColumns(icDat)

        # Collect separately
        tipSep["el"][_xy]    = elDat

        if _iXY == 0:
            tipSum["el"] = np.array(tipSep["el"][_xy]["ITip"].copy())
        else:
            tipSum["el"] = np.subtract(tipSum["el"], tipSep["el"][_xy]["ITip"])
    tipSum["el"] = np.abs(tipSum["el"])



    g, l = CalcCrossEmissionInfo(globals(), locals())
    globals().update(l)
    globals().update(g)
    locals().update(g)
    locals().update(l)



    # Plot
    axL[0,0].semilogy(elDat["Time"], icDat["ISum"] , "o", markersize=7, linewidth=0.2, color="#000000", label="Integral current")
    axL[0,0].semilogy(elDat["Time"], tipSum["el"]  , "x", markersize=7, linewidth=0.2, color="#000000", label="Tip current")
    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        x, y = GetQuadrantOfSpot(spotCoord=_xy, imgWH=imgWH)
        _iEl = 2*y + x
        y += 1
        elTip = tipSep["el"][_xy]

        axL[0, 0].semilogy(elDat["Time"] , elTip["ITip"], "x", markersize=7, linewidth=0.2, color=plotCol["el"]  [_iEl], label="Tip current")
        axL[y, x].semilogy(elDat["USply"], elTip["ITip"], "x", markersize=7, linewidth=0.2, color=plotCol["el"]  [_iEl], label="Tip current")

    fName = splitext(basename(__file__))[0]
    # fig.suptitle(fName + "\nElectrical and brightness currents")
    fig.suptitle("Crossemission between the emitters\nusing defined potentials")
    axL[0, 0].set_ylabel("Current [A]")
    axL[1, 0].set_ylabel("Current [A]")
    axL[2, 0].set_ylabel("Current [A]")

    axL[0, 0].set_xlabel("Time [s]")
    axL[2, 0].set_xlabel("Supply voltage [V]")
    axL[2, 1].set_xlabel("Supply voltage [V]")

    SameXYLimitsOnAxisColl(axL, [1e-11, 1e-6], [0, 650])
    SameXYLimitsOnAxisColl(axR, [-0.5, 4.5]  , [0, 650])
    axL[0, 0].set_xlim([0, 1284])

    PlotLegend(fig, axes=[axL[0, 0]], loc="upper right", ncol=1, LabelColor="#000000")


    ShowMajorMinorY(axLs[-1].flatten())    

    axL[0, 0].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=True , labelleft=True , labelright=False)
    axR[0, 0].tick_params(which="both", bottom=True , left=False, right=False, labelbottom=True , labelleft=False, labelright=False)

    axL[1, 0].tick_params(which="both", bottom=False, left=True , right=False, labelbottom=True , labelleft=True , labelright=False)
    axR[1, 0].tick_params(which="both", bottom=False, left=False, right=False, labelbottom=True , labelleft=False, labelright=False)

    axL[1, 1].tick_params(which="both", bottom=False, left=True , right=False, labelbottom=True , labelleft=False, labelright=False)
    axR[1, 1].tick_params(which="both", bottom=False, left=False, right=False, labelbottom=True , labelleft=False, labelright=False)

    axL[2, 0].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=True , labelleft=True , labelright=False)
    axR[2, 0].tick_params(which="both", bottom=True , left=False, right=False, labelbottom=True , labelleft=False, labelright=False)

    axL[2, 1].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=True , labelleft=False, labelright=False)
    axR[2, 1].tick_params(which="both", bottom=True , left=False, right=False, labelbottom=True , labelleft=False, labelright=False)


SaveFigList(figs, dirname(__file__), (14, 10), 300)


print("Finished")