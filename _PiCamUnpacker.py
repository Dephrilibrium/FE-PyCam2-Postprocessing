##################################################################################
# This script uses 7-zip (standard windows installation path) to extract the     #
# images which were captured by the PyCam2-Server and stores it into a new sub-  #
# directory (selectable foldername) for subsequent pre-clipping or data-extrac-  #
# tion.                                                                          #
# Because of file size reasons the tars additionally compressed by the PyCam2-   #
# Server as tar.gz directly (server option/command) or the tars are manually     #
# compressed to a 7z using 7-zip (see _CompressTars_2_7z.py).                    #
#                                                                                #
# How to use (variable explanation):                                             #
# xCmd:             Path to the 7-zip executable.                                #
# xPath:            Name of the new subfolder where the images decompressed to.  #
# xLog:             Filename of the additional logfile. (None = only console)    #
# workDirs:         This folder is scanned recursevly for possible candidates of #
#                    a possible measurement-folder.                              #
# picDir:           Name of the subfolder where the PyCam2 pictures are stored   #
#                    in.                                                         #
# SkipBadSubdirs:   If this is enabled, the subfolders of any _XX marked parent  #
#                    are skipped in addition.                                    #
# imgWin:           Is used to define the area of interest:                      #
#                   1.) [w, h]:       Defines width and height of the image      #
#                                      around the image center                   #
#                    1.) [x, y, w, h]: Defines the left upper corner (x, y) and  #
#                                      the image size (width, height).           #
#                                                                                #
# 2023 © haum (OTH-Regensburg)                                                   #
##################################################################################


# Imports
import os
import os.path
import subprocess
import sys
import time
from misc import bcolors, Logger, ClearLine, DiffTime, Time2Human


# Preamble & Helpers


def PrintProcessStats(t0, t1, t2):
    print("Processed files:" + bcolors.OKGREEN + str(fCnt).rjust(24) + bcolors.ENDC)
    print("Process time:   " + bcolors.OKBLUE + Time2Human(DiffTime(t1, t2)).rjust(24) + bcolors.ENDC)
    print("Cumulative time:" + bcolors.OKBLUE + Time2Human(DiffTime(t0, t2)).rjust(24) + bcolors.ENDC)


def PrintVerbosePaths(fPath, xPath, fPathAbs, xPathAbs):
    print("rel. fPath: " + fPath)
    print("rel. xPath: " + xPath)
    print("abs. fPath: " + fPathAbs)
    print("abs. xPath: " + xPathAbs)


def RunCmd(cmd):
    if skipCmd == True:
        return

    if debug == True:
        subprocess.call(cmd)
    else:
        subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)  # Only catch errors


##########################################################
# Script to extract the PiCam tar.gz to a Pics folder    #
# Tested on Win10 with standard-installation-path        #
##########################################################


###### USER AREA ######
xCmd = '"C:\\Program Files\\7-Zip\\7z.exe"'  # Path to 7zip
xPath = "Pics"  # Subdirectory where extract to. !!! Do not add a leading / or \ !!!
xLog = "_PiCamUnpacker.log"  # Filename to log output

workDirs = [
# ### Before Cam-Change!
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_185118 Tip Ch1",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_193753 Tip Ch2",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_202712 Tip Ch3",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230408_114847 Tip Ch4",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_131817 Tip1-4 1kV 250nA (Reg. for Tip-Quality)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_143425 Tip1, 3 700V (Sat)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_150043 Tip1, 3 600V (UnSat)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_152323 Tip2, 4 400V (Sat)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_154730 Tip1, 4 400V (UnSat)",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_112532 800V T1-4=2.5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_120802 800V T1-4=0",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_124826 800V T1,4=2.5, T2,3=0",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_133017 800V T1,3=2.5, T2,4=0",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_152121 300V T1-4=5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_153855 500V T1-4=5",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230411_161431 850V T1=2.5, T2-4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230411_170007 600V T1=5, T2-4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230411_173651 850V T2=2.5, T1,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_095047 300V T2=2.5, T1,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_104129 850V T3=2.5, T1,2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_112600 550V T3=2.5, T1,2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_120205 850V T4=2.5, T1,2,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_121044 275V T4=2.5, T1,2,3=f",

# ### After Cam-Change
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230414_142228 850V T1=2.5, T2,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230414_162436 850V T2=2.5, T1,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230414_171309 1kV T3=2.5, T1,2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230416_113420 1kV T4=2.5, T1,2,3=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_124224 850V T1-4=2.5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_130710 650V T1-4=2.5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_132804 600V T1-4=2.5",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_140248 850V T2,3,4=2.5, T1=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_143702 650V T2,3,4=5, T1=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_151519 850V T2,4=2.5, T1,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_153805 650V T2,4=5, T1,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_155756 575V T2,4=5, T1,3=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_164211 850V T2,3=2.5, T1,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_091311 650V T2,3=5, T1,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_093726 650V T2,3=5, T1,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_100014 650V T2,3=5, T1,4=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_103529 850V T3,4=2.5, T1,2=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_111937 600V T3,4=5, T1,2=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_120247 850V T1,2=2.5, T3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_124704 650V T1,2=5, T3,4=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_132015 850V T1,3=2.5, T2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_140546 550V T1,3=5, T2,4=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_154117 550V T1,4=2.5, T2,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_163540 550V T1,4=2.5, T2,3=f",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230417_171941 850V T1-4=2.5",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230417_174418 700V T1-4=1",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230418_085317 850V T1-4=2.5",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_094854 450V T1=2.5, T2,3,4=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_101154 450V T1=5, T2,3,4=gnd",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_104503 850V T2=2.5, T1,3,4=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_112114 950V T2=5, T1,3,4=gnd",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_115301 750V T3=2.5, T1,2,4=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_121938 750V T3=5, T1,2,4=gnd",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_124726 650V T4=2.5, T1,2,3=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_131423 650V T4=5, T1,2,3=gnd",
]

fileTypes = [".raw", ".gray", ".jpg", ".jpeg", ".png", ".rgb", ".yuv", ".y"]  # List of filetype which is counted at the end for statistics

# Debug flags
debug               = False      # Debug-flag if 7zip should ouput infos to it's extraction progresses
verbose             = False      # Verbose output
skipCmd             = False      # Set to true to skip the cmd-exection (for test purposes)
log2File            = False      # Define if you want to have a log-file
SkipBadSubdirs      = True       # If a parent folder is marked as bad measurement, the subdirectories also skipped!y


###### DO NOT TOUCH AREA ######
t0 = time.time()  # Script starts
szCmd = xCmd + ' x "{}" -o"{}" -r -y' # Prepared format-string for 7zip


# Change working-directory
owdPath = os.getcwd()
pyPath = os.path.dirname(__file__)

for workDir in workDirs:                # Iterate the working directories
    os.chdir(workDir)                   # Change path to wd
    cwdPath = os.getcwd()               #  read back for debugging-resons
    if verbose == True:
        print(bcolors.WARNING + "Changing WD..." + bcolors.ENDC)
        print(bcolors.FAIL + "Old" + bcolors.ENDC + " working dir:\t" + owdPath)
        print("Python File dir:\t" + pyPath)
        print("Working dir:\t" + pyPath)
    print(bcolors.OKBLUE + "New" + bcolors.ENDC + " working dir:\t" + cwdPath)
    print("Changing WD " + bcolors.OKGREEN + "OK" + bcolors.ENDC)

    # Open STDOUT&Log-File Logger
    if log2File == True:
        sys.stdout = Logger()



    # Extract tar.gz or 7z files
    print("\r\n")
    print("Extracting *.tar.gz/*.7z:")
    fCnt = 0
    _XXBadDirs = list()
    for dirpath, dirnames, filenames in os.walk("."):

        # Firstly check if path contains one of the already marked bad measurement-folders
        if any(dirpath.__contains__(_bDir) for _bDir in _XXBadDirs):
            print(bcolors.WARNING + "Bad parent - skipped:" + bcolors.ENDC + ' "' + dirpath)
            continue
        # Folder marked as bad measurement -> Skip
        if dirpath.endswith("_XX"):
            if SkipBadSubdirs == True:
                _XXBadDirs.append(dirpath)
            print(bcolors.WARNING + "Skipping:" + bcolors.ENDC + ' "' + dirpath)
            continue

        for filename in [f for f in filenames if f.lower().endswith((".7z", ".tar.gz"))]:
            _fPath = os.path.join(dirpath, filename)
            _fPathAbs = os.path.abspath(_fPath)
            _xPath = os.path.join(dirpath, xPath)
            _xPathAbs = os.path.abspath(_xPath)
            if debug == True:
                PrintVerbosePaths(_fPath, _xPath, _fPathAbs, _xPathAbs)

            print(bcolors.WARNING + "Unpacking:" + bcolors.ENDC + ' "' + _fPath + '" -> "' + _xPath,end="",)
            cmd = str.format(szCmd, _fPath, _xPath)
            RunCmd(cmd)
            if verbose == True:
                print(bcolors.OKGREEN + "Extracted".rjust(15) + bcolors.ENDC) # Keep line
            else:
                print(bcolors.OKGREEN + "Extracted".rjust(15) + bcolors.ENDC + "\033[K", end="\r") # Override line

            fCnt = fCnt + 1
    t1 = time.time()
    ClearLine() # Be sure, current line is empty
    PrintProcessStats(t0, t0, t1)

    # Extract .tar
    print("\r\n")
    print("Extracting *.tar:")
    fCnt = 0
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if f.endswith(".tar")]:
            _fPath = os.path.join(dirpath, filename)
            _fPathAbs = os.path.abspath(_fPath)
            _xPath = os.path.join(dirpath)
            _xPathAbs = os.path.abspath(_xPath)
            if debug == True:
                PrintVerbosePaths(_fPath, _xPath, _fPathAbs, _xPathAbs)

            print( bcolors.WARNING + "Unpacking:" + bcolors.ENDC + ' "' + _fPath + '" -> "' + _xPath, end="",)
            cmd = str.format(szCmd, _fPath, _xPath)
            RunCmd(cmd)
            if verbose == True:
                print(bcolors.OKGREEN + "Extracted".rjust(15) + bcolors.ENDC) # Keep line
            else:
                print(bcolors.OKGREEN + "Extracted".rjust(15) + bcolors.ENDC + "\033[K", end="\r") # Override line
            fCnt = fCnt + 1
    t2 = time.time()
    ClearLine()
    PrintProcessStats(t0, t1, t2)

    # Clean up .tar
    print("\r\n")
    print("Cleaning up *.tar:")
    fCnt = 0
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if f.endswith(".tar")]:
            _fPath = os.path.join(dirpath, filename)
            _fPathAbs = os.path.abspath(_fPath)
            _xPath = "-"  # Not existing
            _xPathAbs = "-"  # Not existing
            if debug == True:
                PrintVerbosePaths(_fPath, _xPath, _fPathAbs, _xPathAbs)

            print(bcolors.FAIL + "Cleaning up:" + bcolors.ENDC + ' "' + _fPath, end="")
            # cmd = str.format(rmCmd, _fPath)
            # RunCmd(cmd) # Replaced with os.remove(fPath)
            os.remove(_fPath)
            if verbose == True:
                print(bcolors.OKGREEN + "Deleted".rjust(15) + bcolors.ENDC) # Keep line
            else:
                print(bcolors.OKGREEN + "Deleted".rjust(15) + bcolors.ENDC + "\033[K", end="\r") # Override line

            fCnt = fCnt + 1
    t3 = time.time()
    ClearLine()
    PrintProcessStats(t0, t2, t3)


    # Count pictures
    print("\r\n")
    print(str.format("Counting files of type: {}", fileTypes))
    fCnt = 0
    for dirpath, dirnames, filenames in os.walk("."):
        _filenames = [fn for fn in os.listdir(dirpath) if any(fn.lower().endswith(fType) for fType in fileTypes)]

        _fCnt = len(_filenames)
        fCnt = fCnt + _fCnt
        if verbose == True:
            print("Found" + bcolors.OKGREEN + str(_fCnt).rjust(10) + bcolors.ENDC + '   files in "' + dirpath + '"')
        else:
            if not _fCnt == 0:
                print("Found" + bcolors.OKGREEN + str(_fCnt).rjust(10) + bcolors.ENDC + '   files in "' + dirpath + '"')
    t4 = time.time()
    print("Found" + bcolors.OKBLUE + str(fCnt).rjust(10) + bcolors.ENDC + "   files overall")
    PrintProcessStats(t0, t3, t4)


sys.stdout.flush() # be sure everything is written to the log-file!