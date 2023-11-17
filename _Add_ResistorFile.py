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
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\01_02 DarkShots pre+Post",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\01_03 Burn-In",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\02_00 DarkShots",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\02_01 Rumprobieren USwp, IRot, UHold",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\03_00 DarkShots Pre+Post",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\03_01 Change 10Meg 4 UIB Plot",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\04_00 Darkshots Pre+Post",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\04_01 Gut eingefahrene Probe",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\05_00 + 06_00 Darkshots Pre+Post",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\05_01 Swp Gain changed",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\06_01 90min",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\07_01 IRotations",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\08_01 USwp 4 diff IMax",
r"Z:\_FEMDAQ V2 for Measurement\Hausi\231023 150nm HQCam SOI2x2_0036\Messungen\09_01 Brightness vs. SS (cam-linearity)",

r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\01_02 DarkShots pre+Post",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\01_03 Burn-In",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\02_00 DarkShots",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\02_01 Rumprobieren USwp, IRot, UHold",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\03_00 DarkShots Pre+Post",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\03_01 Change 10Meg 4 UIB Plot",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\04_00 Darkshots Pre+Post",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\04_01 Gut eingefahrene Probe",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\05_00 + 06_00 Darkshots Pre+Post",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\05_01 Swp Gain changed",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\06_01 90min",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\07_01 IRotations",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\08_01 USwp 4 diff IMax",
r"D:\05 PiCam\231023 150nm HQCam SOI2x2_0036\Messungen\09_01 Brightness vs. SS (cam-linearity)",
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