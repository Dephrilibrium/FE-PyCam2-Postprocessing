# from ast import Break
# from logging import exception
# from posixpath import splitext
# from statistics import median
# from tkinter import image_names
# import cv2 as cv
# import numpy as np
# import matplotlib.pyplot as plt
# import glob
# from extract_tar import extract_tar
# from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
# from matplotlib.colors import LogNorm
# import math
# from enum import Enum


from base64 import encode
import csv
import os
from pickle import NONE
# import warnings
from pickletools import uint8
# from xmlrpc.server import XMLRPCDocGenerator
import numpy as np
import parse
import glob
import natsort
import cv2 as cv
import matplotlib.pyplot as plt
# import imutils
from misc import bcolors
from collections import OrderedDict
from operator import getitem



# So does the files typically look like
# Dev101_rPiHQCam-BlackSubtraction_ss=100000_0000.jpg
# Dev101_rPiHQCam-BlackSubtraction_ss=100000_0001.jpg
# Dev101_rPiHQCam-BlackSubtraction_ss=100000_0002.jpg
# Dev101_rPiHQCam-BlackSubtraction_ss=100000_0003.jpg

#Dev101_rPiHQCam-0000_ss=100000_0000.jpg
#Dev101_rPiHQCam-0000_ss=100000_0001.jpg
#Dev101_rPiHQCam-0000_ss=100000_0002.jpg
#Dev101_rPiHQCam-0000_ss=100000_0003.jpg




def __CreateClippedMeanImage__(picPathVector, cropWindow):
  """Simple function which opens, crops and means all paths of the given list of filenames together into one image

  Input:
  ----------
  picPathVector: List of image-paths which will combined to one mean-image

  Return:
  ----------
  imgMean: Represents the cropped and meaned image
  """
  imgList = list()
  for picPath in picPathVector:
    cImg = cv.imread(picPath, cv.IMREAD_GRAYSCALE).astype(np.float64)
    if type(cropWindow) == list and cropWindow.__len__() == 4:
      x = cropWindow[0]
      y = cropWindow[1]
      w = cropWindow[2]
      h = cropWindow[3]
      # image is build up in [rows, columns] therefore x and y are switched!
      cImg = cImg[y:y+h, x:x+w]
    elif cropWindow == None or type(cropWindow) == bool:
      pass # maybe later a warning!
    else:
      raise Exception(str.format("cropWindow should be in the form of [x, y, w, h] - current type: {}, content: {}", type(cropWindow), cropWindow))
    imgList.append(cImg) # read image as np-array (380x507), 0 means grayscale

  imgMean = np.mean(imgList, axis=0)#.astype(np.uint8)
  return imgMean





def __SplitPicPaths__(picPathVector, nDatPnts, nPicsPerSS):
  """Simple function with iterates through a big list of pictures and split it into sets of n = nDatPnts, nPicsPerSS
  Keep in mind, that the function is straight forward, so you have to be sure, that your list is sorted correctly!

  Input:
  ----------
  nDatPnts: Repeats of one line (measurements per target-voltage)
  nPicsPerSS: Amount of pictures taken per shutterspeed

  Return:
  ----------
  fPathSets: List of picture-sets -> list(list())
  """
  picCnt = picPathVector.__len__()
  nPicsMean =  nDatPnts * nPicsPerSS
  meanPics = picCnt / (nPicsMean)
  # Check if file-count would match
  if picCnt < nPicsMean: # Not enough pictures for one mean-image
    raise Exception(str.format("Less pictures than requested for mean! (nFiles: {} of nMean: {})", picCnt, nPicsMean))
  if meanPics % 1 != 0: # Odd amount of pictures to amount images to mean
    raise Exception(str.format("Incompatible amount of pictures! {}/({}*{}) % 1 != 0", picCnt, nDatPnts, nPicsPerSS))
  meanPics = int(meanPics) # Checks ok --> Convert to int

  fPathSets = list()
  for iMean in range(meanPics):
    iCopyFrom = iMean * nPicsMean
    iCopyTo = (iMean + 1) * nPicsMean
    fPathSets.append(picPathVector[iCopyFrom:iCopyTo])

  return fPathSets





def __MakeMeanImages__(picPathVector, nDatPnts, nPicsPerSS, cropWindow):
  '''Simple function that creates n = nDatPnts * nPicsPerSS mean images and crops them.
     Keep in mind, that the function is straight forward, so you have to be sure, that your list is sorted correctly!
  
  Input:
  ----------
  picPathVector: A sorted and complete list of filepaths inkluding filenames and extension
  nDatPnts: Amount of sequenced measurements
  nPicsPerSS: Amount of pictures were taken per shutter-speed
  cropWindow: [x, y, w, h] list where xy is the left upper corner wh defines the size in [px]

  Returns:
  ----------
  meanImgs: List of mean images
  meanSets: List of path-sets which were meaned together
  '''
  meanImgs = list()
  # meanNames = list()
  # meanSets = __SplitPicPaths__(picPathVector, nDatPnts, nPicsPerSS)
  meanSets = __SplitPicPaths__(picPathVector, nDatPnts, nPicsPerSS)
  for meanSet in meanSets:
    meanImgs.append(__CreateClippedMeanImage__(meanSet, cropWindow))

  return meanImgs, meanSets






def GetShutterspeeds(Path, Format="Dev101_rPiHQCam-{}_ss={}_{}.jpg", iSS = 1):
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
  fList = os.listdir(Path)

  SS = list()
  for file in fList:
    if not file.endswith(os.path.splitext(Format)[1]): # Be sure only scanning filetype of interest! Sometimes a 0kb tar.gz can be within the pictures
      print(bcolors.FAIL + "Non-matching filetype detected: " + bcolors.ENDC + file)
    else:
      numbers = parse.parse(Format, file)
      if SS.__contains__(numbers[iSS]):
        continue
      SS.append(numbers[iSS])

  SS = natsort.os_sorted(SS)
  SS = [int(ss) for ss in SS]

  return SS






def GetMeanImages(Path, SS, nRptPnts, cropWindow, showImg=False, FormatBlack="Dev101_rPiHQCam-BlackSubtraction_ss={}_{}.jpg", FormatPics="Dev101_rPiHQCam-{}_ss={}_{}.jpg"):
  '''

  Inputs:
  ----------
  Path: Directorypath to the pictures-folder
  SS: Shutterspeed which should be processed
  nRptPnts: Amound of sequenced measurements
  cropWindow: [x, y, w, h] list where xy is the left upper corner wh defines the size in [px]
  showImg: False: silent processing; True: Opens preview-windows

  !!! ATTENTION !!!
  For the following 2 you MAY HAVE TO ADJUST the internal filter for correct functionality!
  FormatBlack: Format you want to scan for dark-field-images (see default value for how to use!)
  FormatPics: Format you want to scan for dark-field-images (see default value for how to use!)

  Returns:
  ----------
  bImg: List of mean darkfield-image (normally only with 1 entry!)
  pImgs: List of mean images
  '''
  # Grab filenames with shutterspeed and mean them
  # Read Black images
  filter = os.path.join(Path, str.format(FormatBlack, SS, "*"))
  fPathBlack = glob.glob(filter)
  fPathBlack = natsort.natsorted(fPathBlack, alg=natsort.ns.IGNORECASE) # Be sure that all pictures sorted correctly!
  nPicsPerSS = fPathBlack.__len__()
  bImg, bPaths = __MakeMeanImages__(fPathBlack, 1, nPicsPerSS, cropWindow) #

  if showImg:
    cv.imshow("Darkfield image...", bImg[0].astype(np.uint8))


  # Read Pics
  filter = os.path.join(Path, str.format(FormatPics, "*", SS, "*"))
  fPathPics = glob.glob(filter)
  fPathPics = natsort.natsorted(fPathPics, alg=natsort.ns.IGNORECASE) # Be sure that all pictures sorted correctly!
  for blackPath in fPathBlack: # Remove black pictures in case of getting filtered also!
    if fPathPics.__contains__(blackPath):
      fPathPics.remove(blackPath)
  pImgs, pPaths = __MakeMeanImages__(fPathPics, nRptPnts, nPicsPerSS, cropWindow)
  if showImg:
    for img in pImgs:
      cv.imshow("Images...", img.astype(np.uint8))

  if showImg:
    cv.destroyAllWindows()
  return bImg, pImgs




def SaveImageCollection(imgCollection, fileFormat,  saveDir):
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
  if not os.path.exists(saveDir):
    os.makedirs(saveDir)
  for i in range(imgCollection.__len__()):
    fName = str.format(fileFormat, i)
    paths.append(os.path.join(saveDir, fName))
    cv.imwrite(paths[i], imgCollection[i])
  return paths





def ConvertColletion2uint8(imgCollection):
  '''Converts pictures to uint8 images because opencv can't handle float-pictures.
  
  Inputs:
  ----------
  imgCollection: List of images

  Returns:
  ----------
  uint8Imgs: List of uint8-images
  '''
  uint8Imgs = list()
  for img in imgCollection:
    img = img.copy() # Create separate copy of the image
    uint8Imgs.append(img.astype(np.uint8))

  return uint8Imgs





def SubtractDarkFromCollection(imgCollection, darkImg):
  '''Subtracts a darkfieldimage
  
  Inputs:
  ----------
  imgCollection: List of images from which the darkImg should be subtracted
  darkImg: Darkfield image which get's ubtracted

  Returns:
  ----------
  subImgs: List of subtracted images
  '''

  if type(darkImg) != np.ndarray:
    raise Exception("Darkfield-image should be a single image (2d-uint8-array, np.ndarray)")

  subImgs = list()
  for img in imgCollection:
    img = img.copy() # Create separate copy of the image
    subImg = np.subtract(img, darkImg) # Remove darkfield
    for ix,iy in zip(np.where(subImg < 0)[0],np.where(subImg < 0)[1]):
      subImg[ix][iy] = 0
    subImgs.append(subImg)

  return subImgs






def ProcessThreshholdOnCollection(imgCollection, bThrsh):
  '''Builds thresh-hold images from the given image-collection
  
  Inputs:
  ----------
  imgCollection: List of images from which the darkImg should be subtracted
  bThrsh: Threshholdvalue which is used, when the automatically generated value (otsu-algorithm) is lower than bThres
          Use 0 or 1 to deactivate!

  Returns:
  ----------
  subImgs: List of subtracted images
  '''
  thrshImgs = list()
  for img in imgCollection:
    img = img.copy() # Create separate copy of the image
    thrVal, threshImg = cv.threshold(img, 1, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    if thrVal < bThrsh: # if found threshhold is smaller than custom value, recalculate the picture!
      thrVal, threshImg = cv.threshold(img, bThrsh, 255, cv.THRESH_BINARY)

    thrshImgs.append(threshImg);

  return thrshImgs







def DetectSpots(imgCollection, pxMaxDiameter, DilateErode:uint8 = -1, showImg=False):
  '''Searching for contours on the given (already converted) threshhold-image-collection.
     The function is always supposing circles as contours!
     Each contour-radius must be:   0 < r < pxMaxDiameter   with r [px]
  
  Inputs:
  ----------
  imgCollection: List of threshhold-images used for contour-detection
  pxMaxDiameter: Maximum diameter a spot can occur without beeing in the range of another spot!
  DilateErode: Iteration steps for 1px-dilations (fill small gaps) and 1px-erodes (fix dialation)
  showImg: False: Silent process; True: Shows a preview-window

  Returns:
  ----------
  detectionImgs: List of images used for the spot-detection
  imgCircles: List of circles found on each img
  '''
  detectionImgs = list()
  imgCircles = list()

  for img in imgCollection:
    if img.dtype != np.dtype("uint8"):
      raise Exception(str.format("Type uint8 necessary! Actual type is {}", img.dtype))

    if DilateErode > 0:
      dImg = cv.dilate(img, None, iterations=DilateErode)
      dImg = cv.erode(dImg, None, iterations=DilateErode)
    else:
      dImg = img

    if showImg:
      cv.imshow("Image of detection...", dImg)

    # Find Contours for dummies:
    #  https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html
    # Used retrieve-mode:         cv.RETR_LIST              - get a hierachical less list of xy-points
    # Used chain-approx-mode:     cv.CHAIN_APPROX_SIMPLE    - keep only the corners of a rectangle with the outer dimensions

    contours, h1 = cv.findContours(dImg, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    # try:
    #   cnts = imutils.grab_contours(contours)
    # except:
    #   pass


    # Prepare circles-data-dict for current picture
    cDat = list()
    # cDat["center"] = list()
    # cDat["radius"] = list()

    # Calculate center-point and radius of all detected contours
    for cont in contours:
      (x, y), r = cv.minEnclosingCircle(cont)
      # Build nearest integer (drawable) values
      (x, y) = tuple(int(round(f)) for f in (x, y))
      r = int(round(r))

      # Check the diameter and append when it is detected as a separate detected spot
      if (2 * r) <= pxMaxDiameter and r >= 1:
        cDat.append({"center": (x, y),
                     "radius": r})


    detectionImgs.append(dImg)
    imgCircles.append(cDat)

  if showImg:
    cv.destroyWindow("Image of detection...")
  return detectionImgs, imgCircles



def DrawCirclesOnImages(imgCollection, circleCollection, bgrColor=(255, 255, 255), pxRadius = 12, addPxRadius=False, showImg=False):
  drawnImgs = list()
  '''Draws all circle of the given circleCollection on the images of the given image-collection
  
  Inputs:
  ----------
  imgCollection: List of images to draw the circles on
  circleCollection: List with circles for all images
  bgrColor: Triple with color values for the circles
  pxRadius: Radius of the drawn circles
  addPxRadius: False: pxRadius is fix; True: pxRadius is added to the circle-radius!
  showImg: False: Silent process; True: Shows a preview

  Returns:
  ----------
  drawnImgs: List of images with the circles drawn in
  '''
  if not addPxRadius: # When pxRadius is not added it's a constant -> Saves computation time
    radius = pxRadius

  for iImg in range(imgCollection.__len__()):
    drawImg = imgCollection[iImg].copy()

    imgCircles = circleCollection[iImg]
    for iCircle in range(imgCircles.__len__()):
      midPnt = imgCircles[iCircle]["center"]
      # if midPnt == []: # Skip pictures without points
      #   continue

      if addPxRadius: # When not added radius is a constant -> See begin of the
        radius = imgCircles[iCircle]["radius"] + pxRadius

      drawImg = cv.circle(drawImg, midPnt, radius, bgrColor, thickness=1)


    if showImg:
      cv.imshow("Circles on image...", drawImg)
      
    drawnImgs.append(drawImg)
  if showImg:
    cv.destroyAllWindows()
  return drawnImgs















def SaveSpotCollection(spotCollection, savePath:str):
  '''Saves the given spotcollection unter the given savepath.
  ATTENTION! The collection must be complete, means run:
  - SortSpotsByXY
  - AppendBrightnessToSpots
  first!
  
  Inputs:
  ----------
  spotCollection: List of detected and sorted spots
  SavePath: Savepath including filename and extension where to save!

  Returns:
  ----------
  None
  '''  
  if savePath == None or savePath == "":
    return

  sptsCntnt = "# Raw Spotsfile v1.0\n" # Build empty output for += operator
  sptsCntnt += "#[x, y]                 -> Key\n"
  sptsCntnt += "#xMean=uint             -> Mean x-coordinate\n"
  sptsCntnt += "#yMean=uint             -> Mean y-coordinate\n"
  sptsCntnt += "#rMean=uint             -> Mean radius\n"
  sptsCntnt += "#FoundOnImgs=uint       -> Amount of Circles/Images, ...\n"
  sptsCntnt += "#ImgIndex=list(uint)    -> Image Index list (csv)\n"
  sptsCntnt += "#ImgX=                  -> Each circle x-coordinate (csv)\n"
  sptsCntnt += "#ImgY=                  -> Each circle y-coordinate (csv)\n"
  sptsCntnt += "#ImgR=                  -> Each circle radius (csv)\n"
  sptsCntnt += "#ImgBright=             -> Entire image brightness (csv)\n"
  sptsCntnt += "#CircleBright=          -> Each circle-area brightness (csv)\n"
  sptsCntnt += "#Overexposed=           -> Boolean if circle is overexposed (at least 1 px >= 255)\n"
  sptsCntnt += "\n\n\n"

  for xy in spotCollection:
    spot = spotCollection[xy]
    sptsCntnt += str.format("[{}, {}]\n", spot["x"], spot["y"])
    sptsCntnt += str.format("xMean={}\n", spot["x"])
    sptsCntnt += str.format("yMean={}\n", spot["y"])
    sptsCntnt += str.format("rMean={}\n", spot["radius"])
    sptsCntnt += str.format("FoundOnImgs={}\n", spot["FoundOnImgs"])
    
    circImgIndicies = str.format("ImgIndex=".ljust(15))
    circImgX = str.format("ImgX=".ljust(15))              # X-Coordinate of center
    circImgY = str.format("ImgY=".ljust(15))              # X-Coordinate of center
    circImgR = str.format("ImgR=".ljust(15))              # Circle Radius
    circImgB = str.format("ImgBright=".ljust(15))         # Circle-corresponding image-brightness
    circAreB = str.format("CircleBright=".ljust(15))      # Circle area brightness
    circOExp = str.format("Overexposed=".ljust(15))       # Circle is overexposed

    imgCnt = len(spot["ImgIndex"])
    for i in range(imgCnt):
      # Justify values experimentically to be aligned together
      circImgIndicies += str(spot["ImgIndex"][i]).rjust(15) + ","
      circImgX += str(spot["ImgCircles"][i]["center"][0]).rjust(15) + ","
      circImgY += str(spot["ImgCircles"][i]["center"][1]).rjust(15) + ","
      circImgR += str(spot["ImgCircles"][i]["radius"]).rjust(15) + ","
      circImgB += str(spot["ImgCircles"][i]["ImgBrightness"]).rjust(15) + ","
      circAreB += str(spot["ImgCircles"][i]["AreaBrightness"]).rjust(15) + ","
      circOExp += str(spot["ImgCircles"][i]["Overexposed"]).rjust(15) + ","

    sptsCntnt += circImgIndicies + "\n"
    sptsCntnt += circImgX + "\n"
    sptsCntnt += circImgY + "\n"
    sptsCntnt += circImgR + "\n"
    sptsCntnt += circImgB + "\n"
    sptsCntnt += circAreB + "\n"
    sptsCntnt += circOExp + "\n\n" # Last one with extra separation line

  if savePath != "":
    dirPath = os.path.dirname(savePath)
    if not os.path.exists(dirPath):
      os.makedirs(dirPath)

  f = open(savePath, "w")
  f.write(sptsCntnt)
  f.close();
  return










def SortSpotsByXY(circleCollection, pxTolerance = 12, addPxTolerance=False, followSpots=False): #, savePath = ""):
  '''Loops through all circles and tries to sort them by its location + tolerance
  
  Inputs:
  ----------
  circleCollection: List of circles detected on each image
  pxTolerance: Tolerance-Radius in [px]
  addPxRadius: False: pxTolerance is fix; True: pxTolerance is added to the circle-radius!
  SavePath: Savepath including filename and extension where to save!

  Returns:
  ----------
  spotsByXY: Dictionary of circles with (xMean, yMean)-tuple-Key
  '''
  spotsByXY = dict()
  cCol = circleCollection.copy() # Working copy

  if not addPxTolerance: # When a constant its enough to set it once (saves calculation time)
    r2 = pxTolerance ** 2

  imgCnt = cCol.__len__()
  for iImg in range(imgCnt):
    circleCnt =  cCol[iImg].__len__()
    if circleCnt == 0: # Skip empty images
      continue

    for iCrcl in range(circleCnt):
      associatedCircles = list()
      associatedCirclesImgIndicies = list()
      foundOnImgs = 1

      circle = cCol[iImg].pop(0) # Grab first circle and remove from list
      circle["ImgIndex"] = iImg
      associatedCircles.append(circle)
      associatedCirclesImgIndicies.append(iImg)
      x = circle["center"][0] # Get starting x
      y = circle["center"][1] # Get starting y
      r = circle["radius"]    # Get starting radius, only used when addPxTolerance=True


      for iCmpImg in range(iImg + 1, imgCnt):
        cmpCircleCnt = cCol[iCmpImg].__len__() # Get amount of circles of current image
        if cmpCircleCnt == 0: # Skip empty images
          continue

        # Old check! Is not possible anymore since range(currentImg + 1, LastImage)
        # if iImg == iCmpImg: # Skip itself
        #   continue

        for iCmpCrcl in range(cmpCircleCnt):
          cmpCircle = cCol[iCmpImg].pop(0) # Grab first one and remove from list. When it matches to "circle" it keeps removed, otherwise it gets attached again! -> see below @: if x² + y² > r²

          if circle["center"] == cmpCircle["center"] and circle["radius"] == cmpCircle["radius"]: # If it is exactly! the same circle, then you can go on, because it would have not effect on x, y, r
            foundOnImgs += 1 # But increase divider to have that information
            cmpCircle["ImgIndex"] = iCmpImg
            associatedCircles.append(cmpCircle)
            associatedCirclesImgIndicies.append(iCmpImg)
            continue

          xCmp = cmpCircle["center"][0] # Get starting x
          yCmp = cmpCircle["center"][1] # Get starting y
          rCmp = cmpCircle["radius"]    # Get starting radius, only used when addPxTolerance=True
          x2 = (x - xCmp) ** 2
          y2 = (y - yCmp) ** 2

          if addPxTolerance: # When True, the spot-range must be recalculated each time! otherwise its a constant see start of function!
            r2 = (r + pxTolerance) ** 2

          if (x2 + y2) > r2: # Compare-Spot is outside of the tolerance-range of the old spot!
            cmpCircle = cCol[iCmpImg].append(cmpCircle) # Put circle back into the detected circles of the current compare-img (see @ the begin of this loop!)
            continue

          if followSpots: # When true the algorithm tries to follow the point by generating a new meaned xy-coordinate pair!
            # Restore old sum-value
            x = x * foundOnImgs
            y = y * foundOnImgs
            r = r * foundOnImgs
            foundOnImgs += 1 # Increase mean-divider/img-counter
            # Build mean
            x = (x + xCmp) / foundOnImgs
            y = (y + yCmp) / foundOnImgs
            r = (r + rCmp) / foundOnImgs
          else: # When not, then only increase the counter on how much images that spot was found
            foundOnImgs += 1 # Increase mean-divider/img-counter

          cmpCircle["ImgIndex"] = iCmpImg
          associatedCircles.append(cmpCircle)
          associatedCirclesImgIndicies.append(iCmpImg)


      # Coordinates and radius must be an integer number!
      x = int(x)
      y = int(y)
      r = int(r)
      spotsByXY[(x, y)] = dict()
      spotsByXY[(x, y)]["x"] = x
      spotsByXY[(x, y)]["y"] = y
      spotsByXY[(x, y)]["radius"] = r
      spotsByXY[(x, y)]["FoundOnImgs"] = foundOnImgs # Should be the same as length of associated sep(arate)Circles
      spotsByXY[(x, y)]["ImgIndex"] = associatedCirclesImgIndicies
      spotsByXY[(x, y)]["ImgCircles"] = associatedCircles
  

  # SaveSpotsByXY(spotsByXY, savePath)
  return spotsByXY












def AppendBrightnessToSpots(imgCollection, spotCollection, pxTolerance = 12, addPxTolerance=False, showImg=False):
  '''Reads out all brighntesses for image and circlearea of all detected spots/circles.
  The results get attached to the circle-structure
  
  Inputs:
  ----------
  imgCollection: List of images where the circle-brightness should be readout
  spotCollection: List of circles detected on each image
  pxTolerance: Tolerance-width and height in [px] (symmetric around circle-center)
  addPxRadius: False: pxTolerance is fix; True: pxTolerance is added to the circle-radius!
  SavePath: Savepath including filename and extension where to save!

  Returns:
  ----------
  spotsCollection: (same spot-dict as from input)
  '''
  if pxTolerance == 0:
   return spotCollection

  halfTol = pxTolerance / 2
  if halfTol % 1 != 0:
    print(str.format("Half tolerance is not integer! Asymetric brightness-detection by 1 pixel", int(halfTol)))
  halfTol = int(halfTol)

  for xyKey in spotCollection: # Iterate all spots
    spot = spotCollection[xyKey]

    for circle in spot["ImgCircles"]: # Iterate all imgs
      img = imgCollection[circle["ImgIndex"]]
      drawImg = img.copy() # Create separate image for drawing current area
      if addPxTolerance == True:
        x = circle["center"][0] - circle["radius"] - halfTol
        y = circle["center"][1] - circle["radius"] - halfTol
        x2 = x + 2*circle["radius"] + pxTolerance
        y2 = y + 2*circle["radius"] + pxTolerance
      else:
        x = circle["center"][0] - halfTol
        y = circle["center"][1] - halfTol
        x2 = x + pxTolerance
        y2 = y + pxTolerance


      if showImg:
        drawImg = cv.rectangle(drawImg, [x, y], [x2, y2], (255, 255, 255))
        cv.imshow("Circle-Image", drawImg)
      
      imgArea = img[y:y2, x:x2]               # Image area of interest
      imgBright = cv.sumElems(img)[0]         # Returnin 4-value list. Don't now what 1, 2 and 3 are
      areaBright = cv.sumElems(imgArea)[0]    # Returnin 4-value list. Don't now what 1, 2 and 3 are
      overexposed = False;
      if np.any(imgArea >= 255):
        overexposed = True

      circle["ImgBrightness"] = imgBright
      circle["AreaBrightness"] = areaBright
      circle["Overexposed"] = overexposed

  if showImg:
    cv.destroyAllWindows()

  return spotCollection









def BuildUnoverexposedSpots(spotCollectionList, shutterspeeds):
  '''Combines all shutterspeed spot-circle data to a not overexposed spot on all images!
  !!!ATTENTION!!!
  SpotListCollection must be in same order as Shutterspeed (ordered descending)!
  
  Inputs:
  ----------
  spotCollection: List of circles detected on each image
  pxTolerance: Tolerance-width and height in [px] (symmetric around circle-center)
  addPxRadius: False: pxTolerance is fix; True: pxTolerance is added to the circle-radius!
  SavePath: Savepath including filename and extension where to save!

  Returns:
  ----------
  spotsCollection: (same spot-dict as from input)
  '''

  combiSpots = dict()
  iRef = 0
  cntSS = shutterspeeds.__len__()

  refSpots = spotCollectionList[iRef]
  for xyKey in refSpots: # Highest Shutterspeed
    spot = refSpots[xyKey]
    combiSpots[xyKey] = dict()
    combiSpots[xyKey]["x"] = spot["x"]
    combiSpots[xyKey]["y"] = spot["y"]
    combiSpots[xyKey]["radius"] = spot["radius"]
    combiSpots[xyKey]["FoundOnImgs"] = spot["FoundOnImgs"]
    combiSpots[xyKey]["ImgIndex"] = spot["ImgIndex"]

    combiSpots[xyKey]["CombiCircles"] = list()

    iSS = 0
    for iCirc in range(spot["ImgCircles"].__len__()):
      refCircle = refSpots[xyKey]["ImgCircles"][iCirc]
      circle = refCircle
      if circle["Overexposed"] == True:
        for iSS in range(1, cntSS):
          nCirc = spotCollectionList[iSS][xyKey]["ImgCircles"][iCirc]
          if nCirc["Overexposed"] == True:
            continue
          circle = nCirc
          break
      

      combiSpots[xyKey]["CombiCircles"].append(dict())
      stillOverexposed = False
      if (    iSS == cntSS-1    # Make cnt to max-index
          and circle == nCirc):
        stillOverexposed = True
        print(str.format(bcolors.WARNING + "Warning: Spot@ x:{}, y:{} saturated on all different shutterspeed-images!" + bcolors.ENDC,
                                                        circle["center"][0],    # x
                                                        circle["center"][1]))   # y
      combiSpots[xyKey]["CombiCircles"][iCirc]["StillOverexposed"] = stillOverexposed

      # Create copy of circle and add additional info
      combiSpots[xyKey]["CombiCircles"][iCirc]["center"] = list()
      combiSpots[xyKey]["CombiCircles"][iCirc]["center"].append(circle["center"][0]) # x
      combiSpots[xyKey]["CombiCircles"][iCirc]["center"].append(circle["center"][1]) # y
      combiSpots[xyKey]["CombiCircles"][iCirc]["radius"] = circle["radius"] # radius

      combiSpots[xyKey]["CombiCircles"][iCirc]["OriginalCircleBrightness"] = circle["AreaBrightness"] # Original spot-brightness of the valid dot
      combiSpots[xyKey]["CombiCircles"][iCirc]["OriginalCircleShutterspeed"] = shutterspeeds[iSS] # Shutterspeed of the valid dot
      combiSpots[xyKey]["CombiCircles"][iCirc]["OriginalImgBrightness"] = circle["ImgBrightness"] # Original image brightness of the valid dot

      combiSpots[xyKey]["CombiCircles"][iCirc]["RefImgBrightness"] = refCircle["ImgBrightness"] # Reference (entire) image-brightness
      combiSpots[xyKey]["CombiCircles"][iCirc]["RefShutterspeed"] = shutterspeeds[iRef] # Reference-Shutterspeed

      mulFactor = shutterspeeds[iRef] / shutterspeeds[iSS] # Otherwise build real factor
      if stillOverexposed == True: # When overexposed on all shutterspeeds, then keep reference-values
        mulFactor = 1.0 # RefSS / RefSS = 1
      combiSpots[xyKey]["CombiCircles"][iCirc]["BrightnessFactor"] = mulFactor # Reference-Shutterspeed
      combiSpots[xyKey]["CombiCircles"][iCirc]["CalculatedCircleBrightness"] = circle["AreaBrightness"] * mulFactor

    spot["combiExposed"] = combiSpots

  return combiSpots







def SaveCombiSpots(spotCollection, savePath):
  '''Saves the given combined-shutterspeed spotcollection unter the given savepath.
  ATTENTION! The collection is created by BuildUnoverexposedSpots()
  
  Inputs:
  ----------
  spotCollection: List of detected and sorted spots
  SavePath: Savepath including filename and extension where to save!

  Returns:
  ----------
  None
  '''  
  if savePath == None or savePath == "":
    return

  sptsCntnt = "# Combined Spotsfile (for graphical data) v1.0\n" # Build empty output for += operator
  sptsCntnt += "# Calc(ulated) Bright(ness) = OriBrigh * FacBright\n"
  sptsCntnt += "#[x, y]                -> Key\n"
  sptsCntnt += "#xMean=uint            -> Mean x-coordinate\n"
  sptsCntnt += "#yMean=uint            -> Mean y-coordinate\n"
  sptsCntnt += "#rMean=uint            -> Mean radius\n"
  sptsCntnt += "#FoundOnImgs=uint      -> Amount of circles/image... (length of lists)\n"
  sptsCntnt += "#ImgIndex=list(uint)   -> Image indicies (csv)\n"
  sptsCntnt += "#ImgX=                 -> Each circle x-coordinate (csv)\n"
  sptsCntnt += "#ImgY=                 -> Each circle y-coordinate (csv)\n"
  sptsCntnt += "#ImgR=                 -> Each circle radius (csv)\n"
  sptsCntnt += "#OriBright=            -> Circle brightness @original shutterspeed (csv)\n"
  sptsCntnt += "#OriSS=                -> Original Shutterspeed (csv)\n"
  sptsCntnt += "#OriImgBright=         -> Image Brightness @orignal shutterspeed (csv)\n"
  sptsCntnt += "#RefSS=                -> Reference Shutterspeed (csv)\n"
  sptsCntnt += "#RefImgBright=         -> Reference image brightness (csv)\n"
  sptsCntnt += "#BFactor=              -> Brightnessfactor = RefSS / OriSS (csv)\n"
  sptsCntnt += "#CalcedBright=         -> Calculated brightness = OriBright * BFactor (csv)\n\n\n"

  for xy in spotCollection:
    spot = spotCollection[xy]
    sptsCntnt += str.format("[{}, {}]\n", spot["x"], spot["y"])
    sptsCntnt += str.format("xMean= {}", spot["x"]) + "\n"
    sptsCntnt += str.format("yMean= {}", spot["y"]) + "\n"
    sptsCntnt += str.format("rMean= {}", spot["radius"]) + "\n"
    sptsCntnt += str.format("FoundOnImgs= {}", spot["FoundOnImgs"]) + "\n"    

    imgIndex =         "ImgIndex="         .ljust(18)
    stillOverExposed = "StillOverexposed= ".ljust(18)
    oriX =             "ImgX= "            .ljust(18)
    oriY =             "ImgY= "            .ljust(18)
    oriRadius =        "ImgR= "            .ljust(18)
    oriBright =        "OriBright= "       .ljust(18)
    oriSS =            "OriSS= "           .ljust(18)
    oriImgBright =     "OriImgBright= "    .ljust(18)
    refSS =            "RefSS= "           .ljust(18)
    refImgBright =     "RefImgBright= "    .ljust(18)
    mathFactor =       "BFactor= "         .ljust(18)
    mathBright =       "CalcedBright= "    .ljust(18)

    for iCirc in range(spot["CombiCircles"].__len__()):
      circle = spot["CombiCircles"][iCirc]

      imgIndex +=         str.format("{},", spot["ImgIndex"][iCirc]             ).rjust(15)
      stillOverExposed += str.format("{},", circle["StillOverexposed"]          ).rjust(15)
      oriX +=             str.format("{},", circle["center"][0]                 ).rjust(15)
      oriY +=             str.format("{},", circle["center"][1]                 ).rjust(15)
      oriRadius +=        str.format("{},", circle["radius"]                    ).rjust(15)
      oriBright +=        str.format("{},", circle["OriginalCircleBrightness"]  ).rjust(15)
      oriSS +=            str.format("{},", circle["OriginalCircleShutterspeed"]).rjust(15)
      oriImgBright +=     str.format("{},", circle["OriginalImgBrightness"]     ).rjust(15)
      refSS +=            str.format("{},", circle["RefShutterspeed"]           ).rjust(15)
      refImgBright +=     str.format("{},", circle["RefImgBrightness"]          ).rjust(15)
      mathFactor +=       str.format("{},", circle["BrightnessFactor"]          ).rjust(15)
      mathBright +=       str.format("{},", circle["CalculatedCircleBrightness"]).rjust(15)

    sptsCntnt += imgIndex + "\n"
    sptsCntnt += stillOverExposed + "\n"
    sptsCntnt += oriX + "\n"
    sptsCntnt += oriY + "\n"
    sptsCntnt += oriRadius + "\n"
    sptsCntnt += oriBright + "\n"
    sptsCntnt += oriSS + "\n"
    sptsCntnt += oriImgBright + "\n"
    sptsCntnt += refSS + "\n"
    sptsCntnt += refImgBright + "\n"
    sptsCntnt += mathFactor + "\n"
    sptsCntnt += mathBright + "\n\n"
  
  if savePath != "":
    dirPath = os.path.dirname(savePath)
    if not os.path.exists(dirPath):
      os.makedirs(dirPath)

  f = open(savePath, "w")
  f.write(sptsCntnt)
  f.close();


    # sptsCntnt += str.format("[{}, {}]\n", spot["x"], spot["y"])
    # sptsCntnt += str.format("xMean={}\n", spot["x"])
    # sptsCntnt += str.format("yMean={}\n", spot["y"])
    # sptsCntnt += str.format("rMean={}\n", spot["radius"])
    # sptsCntnt += str.format("FoundOnImgs={}\n", spot["FoundOnImgs"])
    
    # circImgIndicies = str.format("ImgIndex=".ljust(15))
    # circImgX = str.format("ImgX=".ljust(15))              # X-Coordinate of center
    # circImgY = str.format("ImgY=".ljust(15))              # X-Coordinate of center
    # circImgR = str.format("ImgR=".ljust(15))              # Circle Radius
    # circImgB = str.format("ImgBright=".ljust(15))         # Circle-corresponding image-brightness
    # circAreB = str.format("CircleBright=".ljust(15))      # Circle area brightness
    # circOExp = str.format("Overexposed=".ljust(15))       # Circle is overexposed

    # imgCnt = len(spot["ImgIndex"])
    # for i in range(imgCnt):
    #   # Justify values experimentically to be aligned together
    #   circImgIndicies += str(spot["ImgIndex"][i]).rjust(15) + ","
    #   circImgX += str(spot["ImgCircles"][i]["center"][0]).rjust(15) + ","
    #   circImgY += str(spot["ImgCircles"][i]["center"][1]).rjust(15) + ","
    #   circImgR += str(spot["ImgCircles"][i]["radius"]).rjust(15) + ","
    #   circImgB += str(spot["ImgCircles"][i]["ImgBrightness"]).rjust(15) + ","
    #   circAreB += str(spot["ImgCircles"][i]["AreaBrightness"]).rjust(15) + ","
    #   circOExp += str(spot["ImgCircles"][i]["Overexposed"]).rjust(15) + ","

    # sptsCntnt += circImgIndicies + "\n"
    # sptsCntnt += circImgX + "\n"
    # sptsCntnt += circImgY + "\n"
    # sptsCntnt += circImgR + "\n"
    # sptsCntnt += circImgB + "\n"
    # sptsCntnt += circAreB + "\n"
    # sptsCntnt += circOExp + "\n\n" # Last one with extra separation line

  # if savePath != "":
  #   dirPath = os.path.dirname(savePath)
  #   if not os.path.exists(dirPath):
  #     os.makedirs(dirPath)

  # f = open(savePath, "w")
  # f.write(sptsCntnt)
  # f.close();
  return
