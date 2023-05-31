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


SS_Index  = 2                                                  # Index of the ShutterSpeed within the ImageFormat
# BlackFormat = "{}_HQCam-BlackSubtraction_ss={}_{}.{}"        # PiCam1
# ImageFormat = "{}_HQCam-{}_ss={}_{}.{}"                      # PiCam1
BlackFormat = "{}_rPiHQCam2-BlackSubtraction_ss={}_{}.{}"      # PiCam2
ImageFormat = "{}_rPiHQCam2-{}_ss={}_{}.{}"                    # PiCam2

LoadPickleTypes = ["gray", "raw"]
LoadFileTypes = LoadPickleTypes + ["jpg", "png"]
SaveFileType  = "png"







def GrabSSFromFilenames(ImgDir:str, Format:str, FileTypes, iSSPlaceholder:int):
  """Reading all files of the given folder, parsing the numbers and trying to collect all shutterspeeds in ascending order.

  Args:
      ImgDir (str): Path with image-files to scan.
      Format (str): Parse-Format-String (see default for how to use)
      FileTypes (iterable, str): Iterable object of strings containing valid file-types
      iSSPlaceholder (int): Index of {} in which the Shutterspeed-value is located in Format

  Returns:
      list, int: List of ascending sorted shutterspeeds
      str: File-extension (of the last read image-file)
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



def ReadImages(FolderPath, Format:str, cvFlags=cv.IMREAD_ANYDEPTH | cv.IMREAD_GRAYSCALE, CropWindow=None, IgnorePathVector=None, ShowImg=False):
  """Simple function which opens and crops all the given image-paths and returns images and paths.

  Args:
      FolderPath (str): String to the image-folder.
      Format (str): Filter-Format to filter specific filenames (attached to fPath)
      cvFlags (cv.IMREAD-Flags, optional): A combination of opencvs IMREAD-Flags. Defaults to cv.IMREAD_ANYDEPTH | cv.IMREAD_GRAYSCALE.
      CropWindow (Quadtuple, optional): If [x, y, w, h] given xy defines the left upper corner and wh the image size. None does no image-clipping. Defaults to None.
      IgnorePathVector (iterable, str, optional): A list of strings which should be ignored during read (e.g. skip black images). Defaults to None.
      ShowImg (bool, optional): Shows each image during debug. Defaults to False.

  Returns:
      _imgList: A list of the read images.
      _imgPaths: A list of the corresponding paths of read images.
  """
  filter = os.path.join(FolderPath, Format)
  _fPaths = glob.glob(filter)
  _fPaths = natsort.natsorted(_fPaths, alg=natsort.ns.IGNORECASE) # Be sure that all pictures sorted correctly!

  _imgPaths = list()
  _imgList = list()

  if IgnorePathVector != None and type(IgnorePathVector) == list:
    for _ignorePath in IgnorePathVector:
      if _fPaths.__contains__(_ignorePath):
        _fPaths.remove(_ignorePath)

  for _imgPath in _fPaths:
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




  '''

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

def SaveImageCollection(ImgCollection, FileFormat,  SaveDir):
  """Saves a given image-collection under the given fileFormat in the save-dir with increasing picture-number.

  Args:
      ImgCollection (iterable, images): A iterable image-dataset.
      FileFormat (str): A format string, containing a {} where the picture number is written to.
      SaveDir (str): Folderpath where the images should be stored

  Returns:
      paths: A list of the stored filepaths.
  """
  paths = list()
  if not os.path.exists(SaveDir):
    os.makedirs(SaveDir)
  for i in range(ImgCollection.__len__()):
    fName = str.format(FileFormat, i)
    paths.append(os.path.join(SaveDir, fName))
    cv.imwrite(paths[i], ImgCollection[i])
  return paths


