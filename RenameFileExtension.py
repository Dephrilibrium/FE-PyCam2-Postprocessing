# Imports
import os
from os.path import join, basename, dirname
import glob
import natsort
  

srcExtension = '.tar.gz'
dstExtension = '.tar'

verbose = True

wds = [
r"Z:\_FEMDAQ V2 for Measurement\Hausi\230404\Messungen\03_02 Unreg Kombis (IMax5V)",
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
