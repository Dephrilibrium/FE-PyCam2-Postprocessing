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







def GrabSSFromFilenames(ImgDir:str, Format:str, FileTypes, iSSPlaceholder:int, AllowedDeviationPercent:float = 2.5):
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

  percAsFactor = AllowedDeviationPercent / 100

  SS      = np.array([]).astype(np.uint32)
  SSCount = np.array([]).astype(np.uint32)
  for file in fList:
    if not any(file.endswith("." + fType) for fType in FileTypes): # Be sure only scanning filetype of interest! Sometimes a 0kb tar.gz can be within the pictures
      if not file.endswith(".log"):
        print(bcolors.FAIL + "Non-matching filetype detected: " + bcolors.ENDC + file)
    else:
      numbers = parse.parse(Format, file)
      if numbers == None:
        continue
      
      _ssVal   = int(numbers[iSSPlaceholder])
      _ssUpper = int(_ssVal * (1+percAsFactor))
      _ssLower = int(_ssVal * (1-percAsFactor))
      _ssInList = np.where((SS <= _ssUpper) & (SS >= _ssLower))[0]
      if (_ssInList.size > 0):
        _ssIndex = _ssInList[0]

        _ssCurrCnt = SSCount[_ssIndex]
        _ssValOfList = SS[_ssIndex]

        _ssValOfList = _ssValOfList * _ssCurrCnt + _ssVal
        _ssCurrCnt += 1
        _ssValOfList = _ssValOfList // _ssCurrCnt

        SS     [_ssIndex] = int(_ssValOfList)
        SSCount[_ssIndex] = _ssCurrCnt
        continue
      SS      = np.append(SS     , int(_ssVal)).astype(np.uint32)
      SSCount = np.append(SSCount,           1).astype(np.uint32)

  SS = natsort.os_sorted(SS)
  SS = [int(ss) for ss in SS]

  return SS, numbers[-1]



def ReadImageFilepaths(FolderPath:str, Format:str, GlobFlags=natsort.ns.IGNORECASE, IgnorePathVector=None):
  """Reads a list of filenames from FolderPath using Format as filter.

  Args:
      FolderPath (str): Scan-Folder path
      Format (str): Filter-Format.
      GlobFlags (flags): Flags for glob.
      IgnorePathVector (iterable, str, optional): A list of strings which should be ignored during read (e.g. skip black images). Defaults to None.
  
  Returns:
      _imgFilenames: List of os-sorted filenames.
  """
  filter = os.path.join(FolderPath, Format)
  _fPaths = glob.glob(filter)
  _fPaths = natsort.natsorted(_fPaths, alg=GlobFlags) # Be sure that all pictures sorted correctly!

  if IgnorePathVector != None and type(IgnorePathVector) == list:
    for _ignorePath in IgnorePathVector:
      if _fPaths.__contains__(_ignorePath):
        _fPaths.remove(_ignorePath)
        
  return _fPaths



def ReadImagesFromPaths(Filepaths, cvFlags=cv.IMREAD_ANYDEPTH | cv.IMREAD_GRAYSCALE, CropWindow=None, ShowImg=False):
  """Reads one image and returns it as 2d matrix.

  Args:
      Filepaths (iterable, str): Single filepath or List of all paths to image-files.
      cvFlags (_type_, optional): Flags for open-cv (if the target is not a pickle-type!). Defaults to cv.IMREAD_ANYDEPTH | cv.IMREAD_GRAYSCALE.
      CropWindow (_type_, optional): Can be used to pre-crop an image. Defaults to None.
      ShowImg (bool, optional): Shows each read image. Defaults to False.

  Returns:
      NDArray, images; NDArray, str: Image-collecton and Filepath-Collection
  """
  if type(Filepaths) == str:
    Filepaths = [Filepaths]

  _imgs = []
  for _fPath in Filepaths:
    if _fPath.endswith((".gray", ".raw")):
      fImg = open(_fPath, "rb")
      _cImg = pickle.load(fImg)
      fImg.close()
    else:
      _cImg = cv.imread(_fPath, cvFlags)
      _cImg[_cImg < 2] = 0
    if CropWindow != None:
      _cImg = CropImage(_cImg, CropWindow)

    _imgs.append(_cImg)
    
    if ShowImg == True:
      cv.imshow("Raw-image...", _cImg.astype(np.uint8))

  _imgs = np.array(_imgs)
  return _imgs



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
  _fPaths = ReadImageFilepaths(FolderPath=FolderPath, Format=Format, GlobFlags=natsort.ns.IGNORECASE)
  # filter = os.path.join(FolderPath, Format)                                                                        # Moved into "ReadImageFilepaths"
  # _fPaths = glob.glob(filter)                                                                                      # Moved into "ReadImageFilepaths"
  # _fPaths = natsort.natsorted(_fPaths, alg=natsort.ns.IGNORECASE) # Be sure that all pictures sorted correctly!    # Moved into "ReadImageFilepaths"

  # if IgnorePathVector != None and type(IgnorePathVector) == list:                                                  # Moved into "ReadImageFilepaths"
  #   for _ignorePath in IgnorePathVector:                                                                           # Moved into "ReadImageFilepaths"
  #     if _fPaths.__contains__(_ignorePath):                                                                        # Moved into "ReadImageFilepaths"
  #       _fPaths.remove(_ignorePath)                                                                                # Moved into "ReadImageFilepaths"
  
  _imgPaths = list()
  _imgList = list()

  for _imgPath in _fPaths:
    cImg = ReadImagesFromPaths(_imgPath)[0]
    # if _imgPath.endswith((".gray", ".raw")):                # Moved into "ReadImage"
    #   fImg = open(_imgPath, "rb")                           # Moved into "ReadImage"
    #   cImg = pickle.load(fImg)                              # Moved into "ReadImage"
    #   fImg.close()                                          # Moved into "ReadImage"
    # else:                                                   # Moved into "ReadImage"
    #   cImg = cv.imread(_imgPath, cvFlags)                   # Moved into "ReadImage"
    #   cImg[cImg < 2] = 0                                    # Moved into "ReadImage"
    # if CropWindow != None:                                  # Moved into "ReadImage"
    #   cImg = CropImage(cImg, CropWindow)                    # Moved into "ReadImage"
                                                              # Moved into "ReadImage"
    # if ShowImg == True:                                     # Moved into "ReadImage"
    #   cv.imshow("Raw-image...", cImg.astype(np.uint8))      # Moved into "ReadImage"

    _imgPaths.append(_imgPath)
    _imgList.append(cImg)

  if ShowImg == True:
    cv.destroyAllWindows()

  _imgList = np.array(_imgList)
  return _imgList, _imgPaths


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


