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
import glob
from misc import bcolors, Logger, ClearLine, DiffTime, Time2Human, LogLine, LogLineOK


# Preamble & Helpers


def PrintProcessStats():
    print("Extracted *.7z:".ljust(20) + bcolors.OKGREEN + str(_nExtracted7z)   .rjust(24) + bcolors.ENDC)
    print("Extraced *.tar:".ljust(20) + bcolors.OKGREEN + str(_nExtractedTars) .rjust(24) + bcolors.ENDC)
    print("Deleted *.tar:" .ljust(20) + bcolors.OKGREEN + str(_nDeletedTars)   .rjust(24) + bcolors.ENDC)
    print("Deleted *.log:" .ljust(20) + bcolors.OKGREEN + str(_nDeletedCapLogs).rjust(24) + bcolors.ENDC)


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
# Your (parent)-folderpaths go here
r"<Drive>\<Input Pics folderpath here>", # Topmost Parent --> Scans the child-folders iteratively
]

fileTypes = [".raw", ".gray", ".jpg", ".jpeg", ".png", ".rgb", ".yuv", ".y"]  # List of filetype which is counted at the end for statistics

# Debug flags
debug               = False      # Debug-flag if 7zip should ouput infos to it's extraction progresses
verbose             = False      # Verbose output
skipCmd             = False      # Set to true to skip the cmd-exection (for test purposes)
log2File            = False      # Define if you want to have a log-file
SkipBadSubdirs      = True       # If a parent folder is marked as bad measurement, the subdirectories also skipped!y
DeleteCaptureLogs   = True       # Automatically searches for the extraced SSCapture.logs and deletes them too


###### DO NOT TOUCH AREA ######
print(f"\n\n\n\n")
print(f"------------- {bcolors.OKBLUE}Used options{bcolors.ENDC} (sometimes helpful, when \"weird\" things happen) -------------")
print(f" - {bcolors.WARNING}debug"            .ljust(25) + f"{bcolors.ENDC} = {debug}")
print(f" - {bcolors.WARNING}verbose"          .ljust(25) + f"{bcolors.ENDC} = {verbose}")
print(f" - {bcolors.WARNING}skipCmd"          .ljust(25) + f"{bcolors.ENDC} = {skipCmd}")
print(f" - {bcolors.WARNING}log2File"         .ljust(25) + f"{bcolors.ENDC} = {log2File}")
print(f" - {bcolors.WARNING}SkipBadSubdirs"   .ljust(25) + f"{bcolors.ENDC} = {SkipBadSubdirs}")
print(f" - {bcolors.WARNING}DeleteCaptureLogs".ljust(25) + f"{bcolors.ENDC} = {DeleteCaptureLogs}")
print(f"\n\n\n\n")

print(f"------------- {bcolors.OKBLUE}Unpacker-Script starts{bcolors.ENDC} -------------")
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
    _nExtracted7z = 0
    _nExtractedTars = 0
    _nDeletedTars = 0
    _nDeletedCapLogs = 0
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

            print(bcolors.WARNING + "Extracting:" + bcolors.ENDC + ' "' + _fPath + '" -> "' + _xPath,end="",)
            cmd = str.format(szCmd, _fPath, _xPath)
            RunCmd(cmd)
            if verbose == True:
                print(bcolors.OKGREEN + "Extracted".rjust(15) + bcolors.ENDC) # Keep line
            else:
                print(bcolors.OKGREEN + "Extracted".rjust(15) + bcolors.ENDC + "\033[K", end="\r") # Override line
            _nExtracted7z +=  + 1
            print("\r\n")


            print("Extract nested *.tars:")
            filenames = os.listdir(os.path.join(dirpath, xPath))
            filenames = [f for f in filenames if f.endswith(".tar")] # Grab the *.tars
            for filename in filenames:
                _fPath = os.path.join(dirpath, xPath, filename)
                _fPathAbs = os.path.abspath(_fPath)
                _xPath = os.path.join(dirpath, xPath)
                _xPathAbs = os.path.abspath(_xPath)
                if debug == True:
                    PrintVerbosePaths(_fPath, _xPath, _fPathAbs, _xPathAbs)

                print( bcolors.WARNING + "Extracting:" + bcolors.ENDC + ' "' + _fPath + '" -> "' + _xPath, end="",)
                cmd = str.format(szCmd, _fPath, _xPath)
                RunCmd(cmd)
                if verbose == True:
                    print(bcolors.OKGREEN + "Extracted".rjust(15) + bcolors.ENDC, end="") # Keep line
                else:
                    print(bcolors.OKGREEN + "Extracted".rjust(15) + bcolors.ENDC + "\033[K", end="") # Override line
                _nExtractedTars += 1


                os.remove(_fPath)
                if verbose == True:
                    print(" and " + bcolors.OKGREEN + "deleted" + bcolors.ENDC) # Keep line
                else:
                    print(" and " + bcolors.OKGREEN + "deleted" + bcolors.ENDC + "\033[K", end="\r") # Override line
                _nDeletedTars += 1
            print("\r\n")




            if DeleteCaptureLogs == True:
                print("Search and delete *SSCapture.log:")
                filenames = os.listdir(os.path.join(dirpath, xPath))
                filenames = [f for f in filenames if f.endswith("SSCapture.log")] # Grab the *.tars
                for filename in filenames:
                    _fPath = os.path.join(dirpath, xPath, filename)
                    print( bcolors.WARNING + "Deleting:" + bcolors.ENDC + ' "' + _fPath +'"', end="",)
                    os.remove(_fPath)
                    if verbose == True:
                        print(bcolors.OKGREEN + "Deleted".rjust(15) + bcolors.ENDC) # Keep line
                    else:
                        print(bcolors.OKGREEN + "Deleted".rjust(15) + bcolors.ENDC + "\033[K", end="\r") # Override line
                    _nDeletedCapLogs += 1
            print("\r\n\r\n")

            # print("Delete nested *.tars:")
            # # filenames = os.listdir(os.path.join(dirpath, xPath))           # Unchanged from the block above
            # # for filename in [f for f in filenames if f.endswith(".tar")]:  # Unchanged from the block above
            # for filename in filenames:
            #     _fPath = os.path.join(dirpath, xPath, filename)
            #     _fPathAbs = os.path.abspath(_fPath)
            #     _xPath = "-"  # Not existing
            #     _xPathAbs = "-"  # Not existing
            #     if debug == True:
            #         PrintVerbosePaths(_fPath, _xPath, _fPathAbs, _xPathAbs)

            #     print(bcolors.FAIL + "Cleaning up:" + bcolors.ENDC + ' "' + _fPath, end="")
            #     # cmd = str.format(rmCmd, _fPath)
            #     # RunCmd(cmd) # Replaced with os.remove(fPath)
            #     os.remove(_fPath)
            #     if verbose == True:
            #         print(bcolors.OKGREEN + "Deleted".rjust(15) + bcolors.ENDC) # Keep line
            #     else:
            #         print(bcolors.OKGREEN + "Deleted".rjust(15) + bcolors.ENDC + "\033[K", end="\r") # Override line

            #     _nDeletedTars = _nDeletedTars + 1
            # print("\r\n\r\n")

    # t1 = time.time()
    # ClearLine() # Be sure, current line is empty
    # PrintProcessStats(t0, t0, t1)

    # # Extract .tar
    # print("\r\n")
    # print("Extracting *.tar:")
    # fCnt = 0
    # for dirpath, dirnames, filenames in os.walk("."):
    #     for filename in [f for f in filenames if f.endswith(".tar")]:
    #         _fPath = os.path.join(dirpath, filename)
    #         _fPathAbs = os.path.abspath(_fPath)
    #         _xPath = os.path.join(dirpath)
    #         _xPathAbs = os.path.abspath(_xPath)
    #         if debug == True:
    #             PrintVerbosePaths(_fPath, _xPath, _fPathAbs, _xPathAbs)

    #         print( bcolors.WARNING + "Unpacking:" + bcolors.ENDC + ' "' + _fPath + '" -> "' + _xPath, end="",)
    #         cmd = str.format(szCmd, _fPath, _xPath)
    #         RunCmd(cmd)
    #         if verbose == True:
    #             print(bcolors.OKGREEN + "Extracted".rjust(15) + bcolors.ENDC) # Keep line
    #         else:
    #             print(bcolors.OKGREEN + "Extracted".rjust(15) + bcolors.ENDC + "\033[K", end="\r") # Override line
    #         fCnt = fCnt + 1
    # t2 = time.time()
    # ClearLine()
    # PrintProcessStats(t0, t1, t2)

    # Clean up .tar
    # print("\r\n")
    # print("Cleaning up *.tar:")
    # fCnt = 0
    # for dirpath, dirnames, filenames in os.walk("."):
    #     for filename in [f for f in filenames if f.endswith(".tar")]:
    #         _fPath = os.path.join(dirpath, filename)
    #         _fPathAbs = os.path.abspath(_fPath)
    #         _xPath = "-"  # Not existing
    #         _xPathAbs = "-"  # Not existing
    #         if debug == True:
    #             PrintVerbosePaths(_fPath, _xPath, _fPathAbs, _xPathAbs)

    #         print(bcolors.FAIL + "Cleaning up:" + bcolors.ENDC + ' "' + _fPath, end="")
    #         # cmd = str.format(rmCmd, _fPath)
    #         # RunCmd(cmd) # Replaced with os.remove(fPath)
    #         os.remove(_fPath)
    #         if verbose == True:
    #             print(bcolors.OKGREEN + "Deleted".rjust(15) + bcolors.ENDC) # Keep line
    #         else:
    #             print(bcolors.OKGREEN + "Deleted".rjust(15) + bcolors.ENDC + "\033[K", end="\r") # Override line

    #         fCnt = fCnt + 1
    # t3 = time.time()
    # ClearLine()
    # PrintProcessStats(t0, t2, t3)


    # Count pictures
    print(str.format("-------------- Process stats --------------"))
    PrintProcessStats()
    print("\r\n")
    print(str.format("--------------- Image stats ---------------"))
    print(str.format("Counting files of type: {}", fileTypes))
    imgCnt = 0
    for dirpath, dirnames, filenames in os.walk("."):
        _filenames = [fn for fn in os.listdir(dirpath) if any(fn.lower().endswith(fType) for fType in fileTypes)]

        _fCnt = len(_filenames)
        imgCnt = imgCnt + _fCnt
        if verbose == True:
            print("Found" + bcolors.OKGREEN + str(_fCnt).rjust(10) + bcolors.ENDC + '   files in "' + dirpath + '"')
        else:
            if not _fCnt == 0:
                print("Found" + bcolors.OKGREEN + str(_fCnt).rjust(10) + bcolors.ENDC + '   files in "' + dirpath + '"')
    t4 = time.time()
    print("Found" + bcolors.OKBLUE + str(imgCnt).rjust(10) + bcolors.ENDC + "   files overall")


print("EOS")
sys.stdout.flush() # be sure everything is written to the log-file!