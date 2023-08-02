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
r"P:\MIKRO\Mikrosensorik\Mitarbeiter\Hausladen\Veröffentlichung, Vorträge, etc\230403 IEEE PyCam2\Measurements 21x21",
]
picDir = "Pics"


OverrideValue = False
ResistorValue = 10e3







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
            print("".rjust(18) + bcolors.WARNING + " Nothing interesting here" + bcolors.ENDC + root)
        else:
            print(bcolors.OKBLUE + Time2Human(DiffToNow(t0)).rjust(18) + bcolors.WARNING + " Possible directory found: " + bcolors.ENDC + root)
            _fPathResistor = os.path.join(root, "value.resistor")
            if OverrideValue == False:
                if os.path.exists(_fPathResistor):  # When file exists already
                    LogLine(t0=t0, yellowMsg=f'"value.resistor"', whiteMessage=f" already exsist (Override=Off)", wFill=0, end="\n" )
                    continue                        #  Jump over
            _output = "%.0e" % ResistorValue
            f = open(_fPathResistor, "w")
            f.write(_output)
            f.close()
            LogLine(None, "Saved: ", _output + " to " + os.path.basename(_fPathResistor), wFill=0, end="\n" )