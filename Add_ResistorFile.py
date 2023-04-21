import os
import time

from PMPLib.PiMageOptions import PiMageOptions
from misc import bcolors, Time2Human, DiffToNow, LogLine, LogLineOK


opt = PiMageOptions()
opt.SkipBadSubdirs = True                                   # If a parent folder is marked as bad measurement, the subdirectories also skipped!y



parentDir = r"C:\Users\ham38517\Downloads\PiCam\221202 PiCam Paper Messung\Messung"
picDir = "Pics"


ResistorValue = 10e6


t0 = time.time()
_XXBadDirs = list()
for root, dirs, files in os.walk(parentDir):
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
  #  Directory found when it contains a Pics directory and *.dat files
  if not dirs.__contains__(picDir) or not any(f.endswith(".dat") for f in files):
    print("".rjust(18) + bcolors.WARNING + " Nothing interesting here" + bcolors.ENDC + root)
  else:
    print(bcolors.OKBLUE + Time2Human(DiffToNow(t0)).rjust(18) + bcolors.WARNING + " Possible directory found: " + bcolors.ENDC + root)
    _fPathResistor = os.path.join(root, "value.resistor")
    _output = "%.0e" % ResistorValue
    f = open(_fPathResistor, "w")
    f.write(_output)
    f.close()
    LogLine(None, "Saved: ", _output + " to " + os.path.basename(_fPathResistor), wFill=0, end="\n" )