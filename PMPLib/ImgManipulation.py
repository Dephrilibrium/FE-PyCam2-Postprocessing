import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt






def CropImage(Image, CropWindow):
  # Image = Image.copy() # Create own copy! -> Copy only the cropped image! -> RAM-usage-improvement was unbelievable 😅

  if type(CropWindow) == list and CropWindow.__len__() == 4:
    x = CropWindow[0]
    y = CropWindow[1]
    w = CropWindow[2]
    h = CropWindow[3]
    # image is build up in [rows, columns] therefore x and y are switched!
    Image = Image[y:y+h, x:x+w].copy()
    
  elif CropWindow == None or type(CropWindow) == bool:
    pass # maybe later a warning!

  else:
    raise Exception(str.format("cropWindow should be in the form of [x, y, w, h] - current type: {}, content: {}", type(CropWindow), CropWindow))

  return Image






# def CropImages(imgCollection, cropWindow):
#   """Simple function which opens, crops and means all paths of the given list of filenames together into one image

#   Input:
#   ----------
#   picPathVector: List of image-paths which will combined to one mean-image

#   Return:
#   ----------
#   imgMean: Represents the cropped and meaned image
#   """
#   croppedImgs = list()
#   for cImg in imgCollection:
#     cImg = CropImage(cImg, cropWindow)
#     croppedImgs.append(cImg) # read image as np-array (380x507), 0 means grayscale

#   return croppedImgs






def MeanImages(ImgCollection, ImgsPerMean, ShowImg=False):
  if ImgsPerMean < 2:
    return ImgCollection.copy()

  _imgCnt = ImgCollection.__len__()
  _meanSteps = _imgCnt / ImgsPerMean

  if _meanSteps % 1 != 0:
    raise Exception(str.format("Amount of images not matching with amount of images to mean. (ImageCount / ImagesPerMean = {} != 0", _meanSteps))
  _meanSteps = int(_meanSteps)
  
  meanImages = list()
  for _step in range(_meanSteps):
    _iStart = _step * ImgsPerMean
    _iStop = _iStart + ImgsPerMean
    try:
      _meanImg = np.mean(ImgCollection[_iStart:_iStop], axis=0, dtype=np.uint16)
    except:
      pass
    meanImages.append(_meanImg)

    if ShowImg == True:
      cv.imshow("Mean image...", _meanImg.astype(np.uint8))

  if ShowImg == True:
    cv.destroyAllWindows()

  meanImages = np.array(meanImages)
  return meanImages







def SubtractFromImgCollection(ImgCollection, ImgOrBlacklevel:int, ShowImg=False):
  '''
  Subtracts samesize-img or value. Func is designed for 12-bit images! (necessary for overflow-detection")
  ImgCollection: Iterable of images
  ImgOrBlacklevel: Single image (same size) or single value (blacklevel)
  ShowImg=False'''
  # if type(ImgOrBlacklevel) != np.ndarray:  # Now also black-levels supported!
  #   raise Exception("Darkfield-image should be a single image (2d-array, np.ndarray)")

  # int   # ? here because of input error?
  _subImgs = list()
  for _iImg in range(len(ImgCollection)):
    _img = ImgCollection[_iImg]
    # _img = _img.copy() # Create separate copy of the image
    _img = np.subtract(_img, ImgOrBlacklevel, dtype=np.uint16) # Remove darkfield
    _img[_img > 0xFFF] = 0 # Where _subImg is negative ) -> set 0
    # _whereNegative = np.where(_subImg.astype(np.int16) < 0)
    # for ix,iy in zip(_whereNegative[0], _whereNegative[1]):
    #   _subImg[ix][iy] = 0

    _subImgs.append(_img)

    if ShowImg == True:
      cv.imshow("Subtracted image...", _img.astype(np.uint8))

  if ShowImg == True:
    cv.destroyAllWindows()
  return _subImgs







def ConvertImgCollectionDataType(ImgCollection, DataType=np.uint8, ShiftRight=4):
  _uint8Imgs = list()
  for _img in ImgCollection:
    # _img = _img.copy() # Create separate copy of the image
    _uint8Imgs.append(np.right_shift(_img, ShiftRight).astype(DataType))

  return _uint8Imgs







def BuildThreshold(ImgCollection, Threshold, ThreshType, OtsuDiv, OverexposedValue):
  
  _thresImgs = list()
  for _iImg in range(len(ImgCollection)):
    _img = ImgCollection[_iImg]
    # _img = _img.copy() # Create separate copy of the image

    if ThreshType == cv.THRESH_OTSU: # Otsu determines one threshholdvalue!
      thrVal, threshImg = cv.threshold(src=_img, thresh=1, maxval=OverexposedValue, type=cv.THRESH_BINARY + cv.THRESH_OTSU) # Auto-Creates a copy of type uint8 (because input is also uint8? or by default? don't know exactly)
      thrVal /= OtsuDiv
      if thrVal < Threshold: # if found threshhold is smaller than custom value, recalculate the picture!
        thrVal, threshImg = cv.threshold(src=_img, thresh=Threshold, maxval=OverexposedValue, type=cv.THRESH_BINARY)

      else: # Otherwise use reduced otsu again
        thrVal, threshImg = cv.threshold(src=_img, thresh=thrVal, maxval=OverexposedValue, type=cv.THRESH_BINARY)

    elif (ThreshType == cv.ADAPTIVE_THRESH_GAUSSIAN_C) or (ThreshType == cv.ADAPTIVE_THRESH_MEAN_C): # This determines a bunch of threshhold-values!
        threshImg = cv.adaptiveThreshold(src=_img, maxValue=OverexposedValue, adaptiveMethod=ThreshType, thresholdType=cv.THRESH_BINARY, blockSize=11, C=2)
        # threshImg = cv.adaptiveThreshold(_img, 1, OverexposedValue, cv.THRESH_BINARY + cv.ADAPTIVE_THRESH_GAUSSIAN_C) # Auto-Creates a copy of type uint8 (because input is also uint8? or by default? don't know exactly)

    else:
      thrVal, threshImg = cv.threshold(_img, Threshold, OverexposedValue, cv.THRESH_BINARY)

    _thresImgs.append(threshImg);
  
  _thresImgs = np.array(_thresImgs)
  return _thresImgs







def CircleDraw(ImgCollection, CircleCollection, bgrColor=(255, 255, 255), pxRadius = 12, AddPxRadius=False, ShowImg=False):
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
  _drawnImgs = list()
  if not AddPxRadius: # When pxRadius is not added it's a constant -> Saves computation time
    _radius = pxRadius

  for _iImg in range(ImgCollection.__len__()):
    _drawImg = ImgCollection[_iImg].copy()

    _imgCircles = CircleCollection[_iImg]
    for _iCircle in range(_imgCircles.__len__()):
      _midPnt = _imgCircles[_iCircle]["center"]

      if AddPxRadius: # When not added radius is a constant -> See begin of the
        _radius = _imgCircles[_iCircle]["radius"] + pxRadius

      _drawImg = cv.circle(_drawImg, _midPnt, _radius, bgrColor, thickness=1)


    if ShowImg:
      cv.imshow("Circles on image...", _drawImg)
      
    _drawnImgs.append(_drawImg)
  if ShowImg:
    cv.destroyAllWindows()

  _drawnImgs = np.array(_drawnImgs)
  return _drawnImgs





def DemosaicBayer(BayerCollection): #, showImgs=True):
  grayCollection = []

  # if showImgs:
  #   fRIm, aRIm = plt.subplots()
  #   fCIm, aCIm = plt.subplots()

  for _iImg in range(len(BayerCollection)):
    bayerImg = BayerCollection[_iImg].astype(np.uint16)
    BayerInGrayShape = (bayerImg.shape[0], int(bayerImg.shape[1] // 1.5))
    gsImg = np.empty(BayerInGrayShape, dtype=np.uint16)

    for byte in range(2):
      gsImg[:, byte::2] = ( (bayerImg[:, byte::3] << 4) | ((bayerImg[:, 2::3] >> (byte * 4)) & 0b1111) )
    
    grayCollection.append(gsImg)

    # if showImgs:
    #   aRIm.cla()
    #   aCIm.cla()
    #   if "cbR" in locals():
    #     cbR.remove()
    #   if "cbC" in locals():
    #     cbC.remove()
    #   iS = aRIm.imshow(bayerImg)
    #   cbR = plt.colorbar(iS, ax=aRIm)
    #   iS = aCIm.imshow(gsImg)
    #   cbC = plt.colorbar(iS, ax=aCIm)
    #   aRIm.set_xlabel("x coordinate")
    #   aCIm.set_xlabel("x coordinate")
    #   aRIm.set_ylabel("y coordinate")
    #   aCIm.set_ylabel("y coordinate")

  grayCollection = np.array(grayCollection)
  return grayCollection


def ConvertBitsPerPixel(ImgCollection, originBPP:int, targetBPP:int):
    bitshift = targetBPP - originBPP

    shiftFunc = None
    if bitshift == 0:
        return ImgCollection.copy()
    elif bitshift > 0:
        shiftFunc = np.left_shift
    elif bitshift < 0:
        shiftFunc = np.right_shift
        bitshift = abs(bitshift)

    targetImgs = []
    for _iImg in range(len(ImgCollection)):
        _oriImg = ImgCollection[_iImg]
        targetImg = shiftFunc(_oriImg, bitshift)
        if targetBPP <= 8:
          targetImg = targetImg.astype(np.uint8)
        elif targetBPP <= 16:
          targetImg = targetImg.astype(np.uint16)
        else:
          targetImg = targetImg.astype(np.uint32)

        targetImgs.append(targetImg)
    
    targetImgs = np.array(targetImgs)
    
    return targetImgs


def StretchBrightness(ImgCollection, blackLevel:256, whiteLevel=0xFFF):
  '''
  Designed for 12bit images!
  OriImgCollection: Collection of images which should be subtracted
  zeroValue:int
  maxVal:int=0xFFF
  '''
  
  stretchedImgs = []
  stretchFac = whiteLevel / (whiteLevel - blackLevel)
  for _iImg in range(len(ImgCollection)):
    _img = np.around(np.multiply(ImgCollection[_iImg], stretchFac)).astype(np.uint16)
    _img[_img > whiteLevel] = whiteLevel # Should not be possible, but added to be absolute sure!
    stretchedImgs.append(_img)
  stretchedImgs = np.array(stretchedImgs)

  return stretchedImgs