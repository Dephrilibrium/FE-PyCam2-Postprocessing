# Blank
import os
###from tokenize import Ignore
import parse
import natsort
import glob
import pickle

# Remapped
import cv2 as cv
import numpy as np
import numpngw as npng

# Custom
from misc import bcolors
from PMPLib.ImgManipulation import CropImage


# OTH_SS_Index  = 2
# OTH_BlkFormat = "{}_rPiHQCam-BlackSubtraction_ss={}_{}.{}"
# OTH_ImgFormat = "{}_rPiHQCam-{}_ss={}_{}.{}"
OTH_SS_Index  = 2
# OTH_BlkFormat = "{}_HQCam-BlackSubtraction_ss={}_{}.{}"        # PiCam1
# OTH_ImgFormat = "{}_HQCam-{}_ss={}_{}.{}"                      # PiCam1
OTH_BlkFormat = "{}_rPiHQCam2-BlackSubtraction_ss={}_{}.{}"      # PiCam2
OTH_ImgFormat = "{}_rPiHQCam2-{}_ss={}_{}.{}"                    # PiCam2

OTH_LoadPickleTypes = ["gray", "raw"]
OTH_LoadFileTypes = OTH_LoadPickleTypes + ["jpg", "png"]
OTH_SaveFileType  = "png"







def GrabSSFromFilenames(ImgDir, Format, FileTypes, iSSPlaceholder):
  """Reading all files of the given folder, parsing the numbers and trying to collect all shutterspeeds in ascending order.

  Inputs:
  ----------
  Path: Path with files to scan
  Format: Parse-String (see default for how to use)
  iSS: Index of {} where the Shutterspeed-values are located in "Format".

  Returns:
  ----------
  SS: List of shutterspeeds (sorted ascending) as [int]
    """
  fList = os.listdir(ImgDir)

  SS = list()
  for file in fList:
    if not any(file.endswith("." + fType) for fType in FileTypes): # Be sure only scanning filetype of interest! Sometimes a 0kb tar.gz can be within the pictures
      if not file.endswith(".log"):
        print(bcolors.FAIL + "Non-matching filetype detected: " + bcolors.ENDC + file)
    else:
      numbers = parse.parse(Format, file)
      if numbers == None:
        continue
      
      if SS.__contains__(numbers[iSSPlaceholder]):
        continue
      SS.append(numbers[iSSPlaceholder])

  SS = natsort.os_sorted(SS)
  SS = [int(ss) for ss in SS]

  return SS, numbers[-1]







def ReadImages(fPaths, Format, cvFlags=cv.IMREAD_ANYDEPTH | cv.IMREAD_GRAYSCALE, CropWindow=None, IgnorePathVector=None, ShowImg=False):
  """Simple function which opens, crops and means all paths of the given list of filenames together into one image

  Input:
  ----------
  picPathVector: List of image-paths which will combined to one mean-image

  Return:
  ----------
  imgMean: Represents the cropped and meaned image
  """
  filter = os.path.join(fPaths, Format)
  fPaths = glob.glob(filter)
  fPaths = natsort.natsorted(fPaths, alg=natsort.ns.IGNORECASE) # Be sure that all pictures sorted correctly!

  _imgPaths = list()
  _imgList = list()

  if IgnorePathVector != None and type(IgnorePathVector) == list:
    for _ignorePath in IgnorePathVector:
      if fPaths.__contains__(_ignorePath):
        fPaths.remove(_ignorePath)

  for _imgPath in fPaths:
    if _imgPath.endswith((".gray", ".raw")):
      fImg = open(_imgPath, "rb")
      cImg = pickle.load(fImg)
      fImg.close()
    else:
      cImg = cv.imread(_imgPath, cvFlags)
      cImg[cImg < 2] = 0
    if CropWindow != None:
      cImg = CropImage(cImg, CropWindow)

    if ShowImg == True:
      cv.imshow("Raw-image...", cImg.astype(np.uint8))

    _imgPaths.append(_imgPath)
    _imgList.append(cImg)

  if ShowImg == True:
    cv.destroyAllWindows()

  _imgList = np.array(_imgList)
  return _imgList, _imgPaths






def SaveImageCollection(ImgCollection, FileFormat,  SaveDir):
  '''Simply saves a given image-collection under the given fileFormat in the save-dir with increasing picture-number.

  Inputs:
  ----------
  imgCollection: List of images you want to save
  fileFormat: Format of how the files should be named. e.g.:
              fileFormat = str.format("Dev101_rPiHQCam-{}_ss={}_{}.jpg", "{:04d}", SS, "Thres")
  saveDir: Directory where to store the files. e.g.:
           saveDir = os.path.join(cSaveDir, str.format("ThreshImgs SS={}", SS))

  Returns:
  ----------
  paths: List of the file-savepaths
  '''
  paths = list()
  if not os.path.exists(SaveDir):
    os.makedirs(SaveDir)
  for i in range(ImgCollection.__len__()):
    fName = str.format(FileFormat, i)
    paths.append(os.path.join(SaveDir, fName))
    cv.imwrite(paths[i], ImgCollection[i])
  return paths


