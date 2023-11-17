# # Use to import from lib.py when its in the next higher parent-dir
# import sys
# from os.path import join, dirname, basename, abspath, splitext
# sys.path.append(dirname(dirname(abspath(__file__))))
# from lib import SplitAndMean




from os.path import join, dirname, basename, abspath, splitext

import numpy as np
import FieldEmission as fe
import pickle
import glob
from matplotlib import pyplot as plt, ticker as mticker
from matplotlib.legend_handler import HandlerTuple



def SplitAndMean(dp:fe.DataProvider):
    up, down = dp.SplitDataAtRow(dp.Rows//2, fe.SplitFlags.OverlapInHiRows)
    mean = np.abs(np.mean([up, down], axis=0))
    mnDat = fe.DataProvider(dp.ColumnHeader, mean)
    return mnDat


def CombinePlots(fig, axis):
    axLen = len(axis)
    ax0 = axis[0]

    gs = ax0.get_gridspec()
    for ax in axis:
        ax.remove()
        
    sF = fig.add_subplot(gs[0, 0:])
    for _i in range(axLen):
        axis[_i] = sF

def Twinx2D_2x2(fig, lAxis):
    rAxis = []
    for axY in lAxis:
        for axX in axY:
            rAxis.append(axX.twinx())
    rAxis = np.array(rAxis).reshape((2,2))
    return rAxis


def Twinx2D_3x2(fig, lAxis):

    # CombinePlots(fig, lAxis[0,0:])

    sF = lAxis[0,0]

    rAxis = []
    rAxis.append(sF.twinx())
    rAxis.append(rAxis[-1])
    for axY in lAxis[1:]:
        for axX in axY:
            rAxis.append(axX.twinx())
    rAxis = np.array(rAxis).reshape((3,2))
    return rAxis


def SameXYLimitsOnAxisColl(axis, yLim, xLim):
    for axRow in axis:
        for ax in axRow:
            ax.set_ylim(yLim)
            ax.set_xlim(xLim)

def SameXYLimitsOnLRSubplots(lAxis, lYLim, rAxis, rYLim, xLim):
    for lRow, rRow in zip(lAxis, rAxis):
        for lAx, rAx in zip(lRow, rRow):
            lAx.set_ylim(lYLim)
            rAx.set_ylim(rYLim)
            lAx.set_xlim(xLim)


def PlotLegend(fig, lHandles=None, lLabels=None, axes=None, loc="upper right", ncol=1, LabelColor="linecolor"):
    if lHandles == None and lLabels == None: # Auto-scan for labels
        lines = []
        labels = []
        if axes==None:
            axes = fig.axes
            
        for axis in axes:
            Line, Label = axis.get_legend_handles_labels()
            # print(Label)
            for _iLab in range(len(Label)):
                _label = Label[_iLab]
                if labels.__contains__(_label):
                    continue
                _line = Line[_iLab]

                # _line._markeredgecolor = LabelColor
                # _line._markerfacecolor = LabelColor

                lines.append(_line)
                labels.append(_label)
        if (LabelColor=="linecolor"):
            fig.legend(lines, labels, loc=loc, ncol=ncol, labelcolor="linecolor")
        else:
            leg = fig.legend(lines, labels, loc=loc, ncol=ncol)
            for _l in leg.legendHandles:
                _l.set_color(LabelColor)

    else: # use specific given handles and labels
        if len(lHandles) != len(lLabels):
            raise  ValueError(f"Length of handle-lists ({len(lHandles)}) not matching with length of labels ({len(lLabels)})!")
        
        leg = fig.legend(lHandles, lLabels, handler_map={tuple: HandlerTuple(ndivide=None)}, loc=loc, ncol=ncol, labelcolor=LabelColor)
        # for _l in leg.legendHandles:  # Noticed, not necessary, when fig.legend uses legendcolor already
        #     _l.set_color("linecolor") # Noticed, not necessary, when fig.legend uses legendcolor already
    return

def PlotSupTitleAndLegend(fig, axes, suptitle, loc="upper right", ncol=1):
  PlotLegend(fig=fig, axes=axes, loc=loc, ncol=ncol)
#   lines = []
#   labels = []
#   for axis in fig.axes:
#     Line, Label = axis.get_legend_handles_labels()
#     # print(Label)
#     for _iLab in range(len(Label)):
#       if labels.__contains__(Label[_iLab]):
#         continue
#       lines.append(Line[_iLab])
#       labels.append(Label[_iLab])
#   fig.legend(lines, labels, loc=loc, ncol=ncol)
  fig.suptitle(suptitle)
  # deriFig.suptitle("Brightness-factors of each pixels (mean)")
  return



def ShowMajorMinorY(axis, useLogLocator=True, which="both"):
    for ax in axis:
        ax.grid(visible=True, which=which, axis="both", color="#CCCCCC", linestyle="-", linewidth=0.5)
        
        ax.minorticks_on()
        
        if useLogLocator:
            ax.yaxis.set_major_locator(mticker.LogLocator(numticks=999))
            ax.yaxis.set_minor_locator(mticker.LogLocator(numticks=999, subs="auto"))


def SaveFigList(figList, saveFolder, figSize, dpi, ClearSaved=False):
    # cmPerInch = 2.54


    if type(figList) != list:
        figList = [figList] # encapsulate

    fLen = len(figList)
    if type(figSize) != list:
        figSize = [figSize] * fLen # encapsulate

    if type(dpi) != list:
        figDPI = [dpi] * fLen # encapsulate

    for _iFig in range(fLen):
        fig = figList[_iFig]
        size = figSize[_iFig]
        dpi = figDPI[_iFig]

        sFilepath = fig._suptitle._text
        sFilepath = sFilepath.replace("\n", " ")
        sFilepath = sFilepath.replace(":", "")
        sFilepath = join(saveFolder, sFilepath) + ".png"
        print("Saving: " + sFilepath)
        if dpi == None:
            dpi = 150
        if size != None:
            fig.set_size_inches(size) #np.divide(size, cmPerInch))

        fig.savefig(sFilepath, dpi=dpi)
        if ClearSaved:
            fig.clf()
        # LogLineOK()



def ReadElAsDP(elFilePath):
    h, d = fe.ReadDataFile(elFilePath)
    dp = fe.DataProvider(h,d)
    return dp

def ReadSwpAsDP(swpFilePath):
    h, d, dmy = fe.ReadSweepFile(swpFilePath)
    dp = fe.DataProvider(h,d)
    return dp

def ReadSwpAsDPFromFolder(FolderPath):
    swPath = glob.glob(join(FolderPath, "*.swp"))[0]
    return ReadSwpAsDP(swPath)

def ReadPkl(pklFilePath):
    f = open(pklFilePath, "rb")
    pkl = pickle.load(f)
    f.close()
    return pkl

def ReadResistor(resistorFilePath):
    f = open(resistorFilePath, "r")
    strVal = f.readlines()[0]
    f.close()
    return float(strVal)

def ReadResistorFromFolder(FolderPath):
    rFilePath = glob.glob(join(FolderPath, "*.resistor"))[0]
    return ReadResistor(rFilePath)






def GetQuadrantOfSpot(spotCoord, imgWH):
    imgW2 = imgWH[0]//2
    imgH2 = imgWH[1]//2

    _sptX = spotCoord[0]
    _sptY = spotCoord[1]

    if (_sptX < imgW2) & (_sptY < imgH2):
        y = 0
        x = 0
    elif (_sptX > imgW2) & (_sptY < imgH2):
        y = 0
        x = 1
    elif (_sptX < imgW2) & (_sptY > imgH2):
        y = 1
        x = 0
    elif (_sptX > imgW2) & (_sptY > imgH2):
        y = 1
        x = 1
    
    return x, y