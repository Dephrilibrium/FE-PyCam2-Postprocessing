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
# 21x21
r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_171103 700V IMax1V",
# r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_173431 500V IMax1V - 15m",
# r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_175303 700V IMax1V",
# r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_181207 700V IMax1V - 15m",
# r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_183133 700V IMax1V",
# r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_185401 1000V IMax1V - 15m",
# r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_193006 700V IMax1V",
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


print("EOS")
sys.stdout.flush() # be sure everything is written to the log-file!