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
import colorama as col
    



##########################################################
# Script to extract the PiCam tar.gz to a Pics folder    #
# Tested on Win10 with standard-installation-path        #
##########################################################

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






###### USER AREA ######
xCmd = 'C:\\Program Files\\7-Zip\\7z.exe'  # Path to 7zip
xArg = 'a -mx9 -sdel'       # 7-zip will delete the compressed tar-archives after successful compression
# xArg = 'a -mx9'             # 7-zip will keep the tars (test-flags for debug-reasons)


globSearch4TarName = '*_rPiHQCam2-*.tar'
targetArchiveName = 'Dev101_rPiHQCam2-tars.7z'


verbose = True

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


SkipBadSubdirs = False













###### DO NOT TOUCH AREA ######
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
        
        tarFilter = join(os.getcwd(), root, globSearch4TarName)
        if any([tarFilter.__contains__(umlaut) for umlaut in ['ä', 'ö', 'ü', '[', ']']]):
               print(f"{col.Fore.RED}!!!! ATTENTION !!!! ==> {col.Fore.YELLOW}glob.glob has a problem with {['ä', 'ö', 'ü', '[', ']']} and may ignore your tars!{col.Fore.RESET}")
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
