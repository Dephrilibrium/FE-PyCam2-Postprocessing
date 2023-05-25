import os
from os.path import join, split, dirname, basename, exists
import subprocess
import sys
from time import time
import glob
import pickle

import numpy as np


# Preamble & Helpers
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Logger():
    def __init__(self, LogFilePath):
        """_summary_

        Args:
            LogFilePath (string): Filepath of logfile. (existing one gets overwritten)
        """
        self.terminal = sys.stdout
        self.log = open(LogFilePath, "w")
        sys.stdout = self

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        self.terminal.flush()
        self.log.flush()
        pass
    
    def close(self):
        self.__del__()

    def __del__(self):
        sys.stdout = self.terminal
        self.terminal = None
        # self.log.flush() # Ensure everything is written
        self.log.close() # Close file


def DiffTime(t0, t1):
  """t1 - t0"""
  return t1 - t0

def DiffToNow(t0):
  """Current time - t0"""
  return DiffTime(t0, time())

def Time2Human(time):
    DD = int(time / (3600 * 24))  # Get integer days
    time = time - (3600 * 24 * DD)  # Remove days from time
    HH = int(time / 3600)  # Get integer hours
    time = time - (3600 * HH)  # Remove hours from time
    MM = int(time / 60)  # Get integer minutes
    time = time - (60 * MM)  # Remove hours from time
    SS = int(time % 60)  # Get integer minutes
    MS = int((time % 1) * 100)  # Get integer milliseconds

    # Check the cases and return correct string
    if not DD == 0:
        return "[%02dd %02dh %02dm %02ds %03dms]" % (DD, HH, MM, SS, MS)
    elif not HH == 0:
        return "[%02dh %02dm %02ds %03dms]" % (HH, MM, SS, MS)
    elif not MM == 0:
        return "[%02dm %02ds %03dms]" % (MM, SS, MS)
    elif not SS == 0:
        return "[%02ds %03dms]" % (SS, MS)
    else:
        return "[%03dms]" % (MS)

def ClearLine():
    print("\r\033[K", end="\r", flush=True)


def LogLine(t0, yellowMsg="", whiteMessage="", yFill = 0, wFill=65, end=""):
    wFill -= yellowMsg.__len__()
    if yFill > wFill:
        wFill = yFill
        
    if t0 == None:
        print("".rjust(18) + bcolors.WARNING + " " + yellowMsg.ljust(yFill) + bcolors.ENDC + whiteMessage.ljust(wFill-yFill), end=end)
    elif t0 < 0:
        print(bcolors.WARNING + " " + yellowMsg.ljust(yFill) + bcolors.ENDC + whiteMessage.ljust(wFill-yFill), end=end)
    else:
        print(bcolors.OKBLUE + Time2Human(DiffToNow(t0)).rjust(18) + bcolors.WARNING + " " + yellowMsg.ljust(yFill) + bcolors.ENDC + whiteMessage.ljust(wFill), end=end)

def LogLineOK(greenMsg="Ok"):
    print(bcolors.OKGREEN + greenMsg + bcolors.ENDC)


def GrabPklFile(PklPath):

  _pklPath = glob.glob(PklPath)
  if _pklPath.__len__() == 1:
    LogLine(None, " - Found: ", basename(_pklPath[0]), yFill=15, wFill=0, end="\n")
    f = open(_pklPath[0], "rb")
    pkl = pickle.load(f)
    f.close()
    return pkl

  LogLine(None, " - Missing: ", "Wasn't able to find any " + basename(PklPath), yFill=15, wFill=0, end="\n")
  return


def CollectEachValueOnceFromVector(vec):
    onceVals = list()

    for v in vec:
        if onceVals.__contains__(v):
            continue
        onceVals.append(v)
    
    return onceVals



def PlotLegend(fig, loc, ncol=1):
  lines = []
  labels = []
  for axis in fig.axes:
    Line, Label = axis.get_legend_handles_labels()
    # print(Label)
    for _iLab in range(len(Label)):
      if labels.__contains__(Label[_iLab]):
        continue
      lines.append(Line[_iLab])
      labels.append(Label[_iLab])
  fig.legend(lines, labels, loc=loc, ncol=ncol)
  return

def PlotSupTitleAndLegend(fig, suptitle, loc="upper right", ncol=1):
  PlotLegend(fig, loc, ncol)
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




def SaveFigList(figList, saveFolder, figSize, dpi):
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

        sFilepath = join(saveFolder, fig._suptitle._text) + ".png"
        LogLine(None, "Saving: ", sFilepath, wFill=90)
        if dpi == None:
            dpi = 150
        if size != None:
            fig.set_size_inches(size) #np.divide(size, cmPerInch))

        fig.savefig(sFilepath, dpi=dpi)
        fig.clf()
        LogLineOK()

    # LogLine(None, "Saving figures:", end="\n")
    # if not exists(saveFolder):
    #     os.makedirs(saveFolder)
    # for _iFig in range(len(figs)):
    #     figFilename = join(saveFolder, figNames[_iFig] + ".png")
    #     LogLine(None, "Saving: ", basename(figFilename), wFill=90)
    #     figs[_iFig].set_size_inches(figWidth_cm / cmPerInch, figHeight_cm / cmPerInch)
    #     figs[_iFig].savefig(figFilename, dpi=figDPI)
    #     figs[_iFig].clf()
    #     LogLineOK()
    # plt.close('all')



def DurationOfLambda(msg:str, process):
    start = time()
    process()
    print(f"{msg} took {time()-start:.4f}s")
    return




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
    
    return y, x

