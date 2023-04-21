from os.path import join, basename, dirname
import pickle
import numpy as np


import matplotlib.pyplot as plt


from misc import GrabPklFile
from misc import PlotSupTitleAndLegend
from misc import GetQuadrantOfSpot
from _alt.Check_GradeOfOverexposement import __twinx2D___
from _alt.Check_GradeOfOverexposement import __SameXYLimitsOnLRSubplots__
from _alt.Check_GradeOfOverexposement import __SameXYLabelsOnLRSubplots__



def ColorizeTwinedXWith(twinXList, color):
    twinXList[0][0].spines["right"].set_color(color)
    twinXList[1][0].spines["right"].set_color(color)
    twinXList[1][1].spines["right"].set_color(color)
    twinXList[2][0].spines["right"].set_color(color)
    twinXList[2][1].spines["right"].set_color(color)

    twinXList[0][0].tick_params(colors=color)
    twinXList[1][0].tick_params(colors=color)
    twinXList[1][1].tick_params(colors=color)
    twinXList[2][0].tick_params(colors=color)
    twinXList[2][1].tick_params(colors=color)

    twinXList[0][0].yaxis.label.set_color(color)
    twinXList[1][0].yaxis.label.set_color(color)
    twinXList[1][1].yaxis.label.set_color(color)
    twinXList[2][0].yaxis.label.set_color(color)
    twinXList[2][1].yaxis.label.set_color(color)

    return









PMP_OE_Bright = GrabPklFile(r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\03 Sample-Sweeps\230307_124953 1kV IMax500nA\PMP_ScaledWhereOverexposedBrightnesses.pkl")
imgWH = [700, 700]

XY = list(PMP_OE_Bright["Spot"].keys())


figs = list()
subL = list()
subR = list()


yKeys = list(PMP_OE_Bright["Full"]["SpotBright"].keys())

for _yKey in yKeys:
    fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
    figs.append(fig)
    subL.append(lAxis)
    subR.append(__twinx2D___(fig, lAxis))

    _ySpot = np.abs(PMP_OE_Bright["Full"]["SpotBright"][_yKey])
    _yPixl = np.abs(PMP_OE_Bright["Full"]["PxlBright"][_yKey])
    _xSSpd = np.abs(PMP_OE_Bright["Full"]["BrightnessFromSS"]) / 1000
    _x = np.array(list(range(len(_ySpot))))

    subL[-1][0][0].plot(_x, _ySpot, "d--", markersize=8, linewidth=1, color="#FF0000", label=_yKey + " (Spot)")
    subL[-1][0][0].plot(_x, _yPixl, "x--", markersize=4, linewidth=1, color="#00CC00", label=_yKey + " (Pixl)")
    subR[-1][0][0].plot(_x, _xSSpd,   "-", markersize=4, linewidth=1, color="#0000CC", label=_yKey + " (FromSS)")

    for _xy in XY:
        _ySpot = np.abs(np.array(PMP_OE_Bright["Spot"][_xy]["SpotBright"][_yKey]))
        _yPixl = np.abs(np.array(PMP_OE_Bright["Spot"][_xy]["PxlBright"][_yKey]))

        _iY, _iX = GetQuadrantOfSpot(_xy, imgWH)
        _iY += 1 # Add the y-Offset
        subL[-1][_iY][_iX].plot(_x, _ySpot, "d--", markersize=8, linewidth=1, color="#FF0000", label=_yKey + " (Spot)")
        subL[-1][_iY][_iX].plot(_x, _yPixl, "x--", markersize=4, linewidth=1, color="#00CC00", label=_yKey + " (Pixl)")
        subR[-1][_iY][_iX].plot(_x, _xSSpd,   "-", markersize=4, linewidth=1, color="#0000CC", label=_yKey + " (FromSS)")

        subL[-1][0][0].plot(_x, _ySpot, "1--", markersize=4, linewidth=0.5, label=_yKey + f" (Spot@{_xy})")
        subL[-1][0][0].plot(_x, _yPixl, "2--", markersize=4, linewidth=0.5, label=_yKey + f" (Pixl@{_xy})")

    PlotSupTitleAndLegend(figs[-1], "ySpot")
    __SameXYLimitsOnLRSubplots__(subL[-1], [0, 1e8], subR[-1], [0, 35], None)
    ColorizeTwinedXWith(subR[-1], "#0000CC")
    subL[-1][0][0].set_ylabel("Brightness")
    subL[-1][1][0].set_ylabel("Brightness")
    subL[-1][2][0].set_ylabel("Brightness")
    subR[-1][0][1].set_ylabel("Shutterspeed")
    subR[-1][1][1].set_ylabel("Shutterspeed")
    subR[-1][2][1].set_ylabel("Shutterspeed")
    

print("Finished")