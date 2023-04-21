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
xArg = 'a -mx9 -sdel'

targetArchiveName = 'Dev101_rPiHQCam2-tars.7z'

globSearch4TarName = '*_rPiHQCam2-*.tar'

verbose = False

wds = [
r"\\rfhmik164\Samba\_FEMDAQ V2 for Measurement\Hausi\230215",
]


SkipBadSubdirs = True

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



        print(f"Scanning for tars")
        tarFiles = glob.glob(join(root, globSearch4TarName))
        tarFiles = natsort.os_sorted(tarFiles)
        nTars = len(tarFiles)
        if nTars > 0:
            print(f"Found {nTars} tar-archives in {root}")
            archivePath = join(root, targetArchiveName)
            cmprsFiles = '" "'.join(tarFiles)
            cmd = f'"{xCmd}" {xArg} "{archivePath}" "{cmprsFiles}"'
            if verbose:
                print(f"Cmd: {cmd}")
            print(f"Starting compression...")
            subprocess.call(cmd)
            print("Compression done")
        else:
            print(f"Nothing found, going on...")
            continue

        print(f"Done with {root}. Going on...")
