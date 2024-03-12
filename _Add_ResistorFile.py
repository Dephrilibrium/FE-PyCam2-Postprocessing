##################################################################################
# This script adds a "value.resistor" file to the folders which contain measure- #
# ment data. This can be used to automatically load the used resistor-value to   #
# remove the resitance-dependency of electrical measurement-data.                #
#                                                                                #
# How to use (variable explanation):                                             #
# opt.SkipBadSubdirs: If this is enabled, the subfolders of any _XX marked pa-   #
#                      rents are skipped in addition.                            #
# parentDir:          Folder which is scanned recursevly for measurement-files.  #
# picDir:             Name of the subfolder where the PyCam2 pictures are stored #
#                      in.                                                       #
# ResistorValue:      The value which gets stored in the value.resistor file.    #
#                                                                                #
# 2023 © haum (OTH-Regensburg)                                                   #
##################################################################################

import os
import time

from PMPLib.PiMageOptions import PiMageOptions
from misc import bcolors, Time2Human, DiffToNow, LogLine, LogLineOK



###### USER AREA ######
opt = PiMageOptions()
opt.SkipBadSubdirs = False                                   # If a parent folder is marked as bad measurement, the subdirectories also skipped!y


wds = [
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\02_01 Activation",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_00 Kritischer Strom (10nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_01 Kritischer Strom (15nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_02 Kritischer Strom (20nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_03 Kritischer Strom (25nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_04 Kritischer Strom (30nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_05 Kritischer Strom (40nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_06 Kritischer Strom (50nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_07 Kritischer Strom (65nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_08 Kritischer Strom (80nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_09 Kritischer Strom (100nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_10 Kritischer Strom (125nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_11 Kritischer Strom (150nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_12 Kritischer Strom (175nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_13 Kritischer Strom (200nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_14 Kritischer Strom (250nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_15 Kritischer Strom (300nA)+DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\240229 UncoatedCam Remeasure\Messungen\03_16 Kritischer Strom (350nA)+DarkShots",
]
picDir = "Pics"


OverrideValue = False
ResistorValue = 10e6







###### DO NOT TOUCH AREA ######
t0 = time.time()
_XXBadDirs = list()

for parentDir in wds:
    for root, dirs, files in os.walk(parentDir): # Iterate recursevily through parentDir
        # Firstly check if path contains one of the already marked bad measurement-folders
        if any(root.__contains__(_bDir) for _bDir in _XXBadDirs):
            print(bcolors.OKBLUE + Time2Human(DiffToNow(t0)).rjust(18) + bcolors.WARNING + " Bad parent - skipped: " + bcolors.ENDC + root)
            continue
        # Folder marked as bad measurement -> Skip
        if root.endswith("_XX"):
            if opt.SkipBadSubdirs == True:
                _XXBadDirs.append(root)
            print(bcolors.OKBLUE + Time2Human(DiffToNow(t0)).rjust(18) + bcolors.WARNING + " Marked as bad - skipped: " + bcolors.ENDC + root)
            continue

        print("\n" + bcolors.OKBLUE + Time2Human(DiffToNow(t0)).rjust(18) + bcolors.WARNING + " Entering: " + bcolors.ENDC + root)

        #Check if current directory contains measurement-files
        #    Directory found when it contains a Pics directory and *.dat files
        # if not dirs.__contains__(picDir) or not any(f.endswith(".dat") for f in files): # Old one, but sometime i want to have value.resistor also in folders were the pictures are not extracted yet!
        if not any(f.endswith(".dat") for f in files):
            print("".rjust(18) + bcolors.WARNING + " Nothing interesting here" + bcolors.ENDC)
        else:
            print(bcolors.OKBLUE + Time2Human(DiffToNow(t0)).rjust(18) + bcolors.WARNING + " Possible directory found: " + bcolors.ENDC + root)
            _fPathResistor = os.path.join(root, "value.resistor")
            if OverrideValue == False:
                if os.path.exists(_fPathResistor):  # When file exists already
                    LogLine(t0=t0, yellowMsg=f'"value.resistor"', whiteMessage=f" already exsist (Override=Off)", wFill=0, end="\n" )
                    continue                        #  Jump over
            _output = "%e" % ResistorValue
            f = open(_fPathResistor, "w")
            f.write(_output)
            f.close()
            LogLine(None, "Saved: ", _output + " to " + os.path.basename(_fPathResistor), wFill=0, end="\n" )