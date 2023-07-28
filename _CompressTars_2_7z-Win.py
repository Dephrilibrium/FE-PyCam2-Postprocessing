##################################################################################
# This script uses 7-zip (standard windows installation path) to compress the    #
# uncompressed tar-archives which were captured by the PyCam2-Server as 7z.      #
# Note:                                                                          #
# Tar-archives with a size of 21GB can be compressed to 1.4GB as most of the     #
# images are dark.                                                               #
#                                                                                #
# How to use (variable explanation):                                             #
# xCmd:                 Path to the 7-zip executable.                            #
# xArg:                 7-zip arguments (see options below).                     #
# globSearch4TarName:   The script filters the files using this filter-string    #
#                        (can contian reg-exp).                                  #
# targetArchiveName:    7-zip compresses the filtered files into an 7z-archive   #
#                        with this filename into the same folder.                #
# verbose:              When true, extra information is printed to the console.  #
# wds:                  A list of strings with the working-directories which are #
#                        scanned iteratively for tar-archives using the          #
#                        globSearch4Tarname filter.                              #
#                                                                                #
# 2023 © haum (OTH-Regensburg)                                                   #
##################################################################################





# Imports
import os
from os.path import join, basename, dirname
import subprocess
import glob
import natsort
    


##########################################################
# Script to extract the PiCam tar.gz to a Pics folder    #
# Tested on Win10 with standard-installation-path        #
##########################################################


###### USER AREA ######
### Command-Line generator (GIT): https://github.com/axelstudios/7z
### Command-Line generator:       https://axelstudios.github.io/7z/#!/

## Left side
# Archive format:                               7z
# Compression Level:                            Ultra
# Compression Method:                           LZMA2
# Dictionary size:                              64M
# Word size:                                    64
# Solid Block Size:                             4G
# Number of CPU Threads:                        16
# RAM-Usage Compression:                        8797M
# RAM-Usage Decompression:                      66M

## Right side
# Update mode:                                  Add an replace files
# Path Mode:                                    Relative pathnames
# Options - Create SFX:                         false
# Options - Compress shared:                    false
# Options - Delete files after compression:     true
# Encryption:                                   None

## Resulting Cmd-Line
# 7z a -mx9 -md128m -mfb128 -mmt24 -sdel <archive_name> [<file_names>...]

xCmd = 'C:\\Program Files\\7-Zip\\7z.exe'  # Path to 7zip
xArg = 'a -mx9 -sdel'       # 7-zip will delete the compressed tar-archives after successful compression
# xArg = 'a -mx9'             # 7-zip will keep the tars (test-flags for debug-reasons)


globSearch4TarName = '*_rPiHQCam2-*.tar'
targetArchiveName = 'Dev101_rPiHQCam2-tars.7z'


verbose = True

wds = [
    r"Z:\_FEMDAQ V2 for Measurement\Hausi\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen",
]


SkipBadSubdirs = False

_XXBadDirs = list()
for wd in wds:
    os.chdir(wd)
    wd = os.getcwd()
    print(f"wd is now: {wd}")
    
    for root, dirs, files in os.walk("."):
        # Firstly check if path contains one of the already marked bad measurement-folders
        if any(root.__contains__(_bDir) for _bDir in _XXBadDirs):
            print("Bad parent - skipped:" + root)
            continue
        # Folder marked as bad measurement -> Skip
        if root.endswith("_XX"):
            if SkipBadSubdirs == True:
                _XXBadDirs.append(root)
            print("Skipping:" + root)
            continue



        print(f"Scanning for tars in: \"{root}\"".ljust(100), end="")
        tarFiles = glob.glob(join(root, globSearch4TarName))
        tarFiles = natsort.os_sorted(tarFiles)
        nTars = len(tarFiles)
        if nTars > 0:
            print("") # new line
            print(f" - Found {nTars} tar-archives")
            archivePath = join(root, targetArchiveName)
            print(f" - Archiving to: {archivePath}")
            # cmprsFiles = '" "'.join(tarFiles)  # First and last " is missing, but added in cmd-concatenation!
            cmd = f'"{xCmd}" {xArg} "{archivePath}" "{root}/*.tar"'
            if verbose:
                print(f" - Cmd: {cmd}")
            print(f" - Starting compression...")
            subprocess.call(cmd)
            print(" - Compression done")
        else:
            print(f"Nothing found, going on...")
            continue

        print(f"Done with {root}. Going on...")
