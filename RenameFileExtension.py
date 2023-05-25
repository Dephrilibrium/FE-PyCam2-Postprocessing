##################################################################################
# This script can be used, to change the file-extension from srcExtension into   #
# dstExtension. It scans recursively all subfolders of the wds paths. Folders    #
# which ending with _XX are ignored.                                             #
#                                                                                #
# How to use (variable explanation):                                             #
# wds:              contains a list of paths which is scanned for files with the #
#                    srcExtension                                                #
# srcExtension:     wds are searched for ending with this string                 #
# dstExtension:     The files srcExtension gets replaced with this string        #
# SkipBadSubdirs:   If this is enabled, the subfolders of any _XX marked parent  #
#                    are skipped in addition.                                    #
#                                                                                #
# 2023 © haum (OTH-Regensburg)                                                   #
##################################################################################

# Imports
import os
from os.path import join, basename, dirname
import glob
import natsort
  

srcExtension = '.tar.gz'
dstExtension = '.tar'

wds = [
r"<Drive>\<My folderpath here>",
]


SkipBadSubdirs = True

_XXBadDirs = list()
for wd in wds: # Iterate wds
    os.chdir(wd)
    wd = os.getcwd()
    print(f"wd is now: {wd}")
    
    for root, dirs, files in os.walk("."):  # Iterate all folders recursively
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
        tarFiles = glob.glob(join(root, "*"+srcExtension))
        tarFiles = natsort.os_sorted(tarFiles)
        nTars = len(tarFiles)
        if nTars > 0:
            print("") # new line
            print(f" - Found {nTars} tar-archives")
            for srcTar in tarFiles:
                dstTar = srcTar.replace(srcExtension, dstExtension)
                print(f"{srcTar} -> {dstTar}", end="")
                os.rename(src=srcTar, dst=dstTar)
            print("")
        else:
            print(f"Nothing found, going on...")
            continue

        print(f"Done with {root}. Going on...")
