##################################################################################
# misc contains some helper-functions used by other scripts                      #
#                                                                                #
# 2023 © haum (OTH-Regensburg)                                                   #
##################################################################################

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
    """Creates a Logger-Instance writing to console as well as to a file.
    """

    def __init__(self, LogFilePath):
        """Creates a Logger-Instance writing to console as well as to a file.

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
    """t1 - t0

    Args:
        t0 (time): Timestamp
        t1 (time): Timestamp

    Returns:
        time: Difference time between t1 and t0
    """
    return t1 - t0






def DiffToNow(t0):
    """Current time - t0

    Args:
        t0 (time): Timestamp

    Returns:
        time: Difference time between now and t0
    """
    return DiffTime(t0, time())





def Time2Human(time):
    """Converts the given time into \"[dd hh mm ss ms]\"

    Args:
        time (time): Time-value

    Returns:
        _type_: None
    """
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
    """Cleans the current written line of the console
    """
    print("\r\033[K", end="\r", flush=True)


def LogLine(t0, yellowMsg="", whiteMessage="", yFill = 0, wFill=65, end=""):
    """Writes a colorized log-line

    Args:
        t0 (time): Time-value
        yellowMsg (str, optional): Yellow infotext. Defaults to "".
        whiteMessage (str, optional): White infotext. Defaults to "".
        yFill (int, optional): Ensures the yellow messages is int chars long. Defaults to 0.
        wFill (int, optional): Ensured the entire message is int chars long. Defaults to 65.
        end (str, optional): Custom line-end. Defaults to "".
    """
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
    """Loads a binary pickle file.

    Args:
        PklPath (str): Path to pickle file

    Returns:
        var: pickle content
    """
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
    """Collects each value only once from a given iterable object.

    Args:
        vec (iterable): Iterable object.

    Returns:
        iterable: List containing the different vec-values once.
    """
    onceVals = list()

    for v in vec:
        if onceVals.__contains__(v):
            continue
        onceVals.append(v)
    
    return onceVals






def PlotLegend(fig, loc, ncol=1):
    """Plots the legend of a figure, but removes double labels.

    Args:
        fig (iterable): Figure object.
        loc (str): Location of the legend.
        ncol (int, optional): Defines n columns for the legend. Defaults to 1.
    """
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
    """Plots a suptitle and the legend of a figure, but removes double labels.

    Args:
        fig (figure): Figure object.
        suptitle (str): String used as suptitle.
        loc (str): Location of the legend.
        ncol (int, optional): Defines n columns for the legend. Defaults to 1.
    """
    PlotLegend(fig, loc, ncol)
    fig.suptitle(suptitle)
    return




def SaveFigList(figList, saveFolder, figSize, dpi):
    """Accepts a list of figures which are stored using their title as savename.

    Args:
        figList (iterable): Iterable of figures.
        saveFolder (str): Folder-location where the figures are saved.
        figSize (tuple): Size of the figure as (<w>, <h>). w, h = inches.
        dpi (uint): Resoluton (dots per inch).
    """
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
            fig.set_size_inches(size)

        fig.savefig(sFilepath, dpi=dpi)
        fig.clf()
        LogLineOK()







def DurationOfLambda(msg:str, process):
    """Measures the time consumed by the given lambda-function.

    Args:
        msg (str): String describing the process-functionality.
        process (function): Executable function.
    """
    start = time()
    process()
    print(f"{msg} took {time()-start:.4f}s")
    return








def GetQuadrantOfSpot(spotCoord, imgWH):
    """Returns the x, y indicies of the quadrant in which the given spotCoord is located within an target image size of imgWH.

    Args:
        spotCoord (tuple): X and y coordinate (x, y).
        imgWH (tuple): Width and height (w, h) in which the XY-quadrant should be determined.

    Returns:
        int, int: y, x quadrant indicies.
    """
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

