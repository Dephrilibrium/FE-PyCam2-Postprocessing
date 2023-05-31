import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt






def CropImage(Image, CropWindow):
  """Crops a given image.

  Args:
      Image (image): Image which should be cropped.
      CropWindow (Quadtuple): [x,y,w,h], xy = left upper corner, wh = image size; None = No crop

  Raises:
      Exception: If CropWindow is not in the right format.

  Returns:
      image: Returns a cropped copy of the input-image
  """
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






def MeanImages(ImgCollection, ImgsPerMean, ShowImg=False):
  """Means always n pictures into one mean image.

  Args:
      ImgCollection (iterable, images): A iterable collection of images (must have an integer length of ImgsPerMean)
      ImgsPerMean (int): Always n images in a row meaned together.
      ShowImg (bool, optional): Show each image (during debugging). Defaults to False.

  Raises:
      Exception: If the amount of images is not an integer of ImgsPerMean.

  Returns:
      ImageCollection: A list of meaned images with length = len(ImgCollection/ImgsPerMean)
  """
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





  '''
  
  ImgCollection: Iterable of images
  ImgOrBlacklevel: Single image (same size) or single value (blacklevel)
  ShowImg=False'''

def SubtractFromImgCollection(ImgCollection, ImgOrBlacklevel:int, ShowImg=False):
  """Subtracts a samesize-image or an int-value from each image of the given ImgCollection.

  Args:
      ImgCollection (iterable, image): Iterable collection of images
      ImgOrBlacklevel (int): Integer value or samesize-image which is subtracted from each ImgCollection-element.
      ShowImg (bool, optional): Show each image (during debugging). Defaults to False.

  Returns:
      subtracted images: A list of images from which ImgOrBlacklevel was subtracted.
  """
  _subImgs = list()
  for _iImg in range(len(ImgCollection)):
    _img = ImgCollection[_iImg]
    _img = np.subtract(_img, ImgOrBlacklevel, dtype=np.uint16) # Remove darkfield
    _img[_img > 0xFFF] = 0 # Where _subImg is negative ) -> set 0

    _subImgs.append(_img)

    if ShowImg == True:
      cv.imshow("Subtracted image...", _img.astype(np.uint8))

  if ShowImg == True:
    cv.destroyAllWindows()
  return _subImgs







def BuildThreshold(ImgCollection, Threshold:int, ThreshType, OtsuDiv:int, OverexposedValue:int):
  """Builds a set of threshold images from the incoming ImgCollection.

  Args:
      ImgCollection (iterable, image): Iterable object containing the images which should be thresholded
      Threshold (int): Minimum threshold which is applied to the images
      ThreshType (cv.THRESH-Flags): Defines the auto-thres-algorithm
      OtsuDiv (int): Divides the resulting auto-threshold value to fine tune the value.
      OverexposedValue (int): Defines the value which is inserted into threshed pixels

  Returns:
      images: List of thresholded images
  """
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




def CircleDraw(ImgCollection, CircleCollection, bgrColor:tuple = (255, 255, 255), pxRadius:int = 12, AddPxRadius:bool = False, ShowImg:bool = False):
  """Draws all circle of the given circleCollection on the images of the given image-collection

  Args:
      ImgCollection (iterable, image): Iterable object with images on which should be drawn on.
      CircleCollection (iterable, circle): Iterable object of circles with same length. Their center-coordinates to a circle with pxRadius around.
      bgrColor (Trituple, optional): 24bit color of the circle in (R, G, B). Defaults to (255, 255, 255).
      pxRadius (int, optional): Radius of the draw-circles. Defaults to 12.
      AddPxRadius (bool, optional): The circles radius is added to pxRadius. Defaults to False.
      ShowImg (bool, optional): Show each image (during debugging). Defaults to False.

  Returns:
      images: A list with images containing circles around the centers of the given CircleCollection
  """
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





def DemosaicBayer(BayerCollection):
  """Decodes the raw Bayer-Images into visible 16bit image-data

  Args:
      BayerCollection (iterable, bayer-image): Iterable object of RAW-Bayer-Images

  Returns:
      images: List of 16bit images.
  """
  grayCollection = []

  for _iImg in range(len(BayerCollection)):
    bayerImg = BayerCollection[_iImg].astype(np.uint16)
    BayerInGrayShape = (bayerImg.shape[0], int(bayerImg.shape[1] // 1.5))
    gsImg = np.empty(BayerInGrayShape, dtype=np.uint16)

    for byte in range(2):
      gsImg[:, byte::2] = ( (bayerImg[:, byte::3] << 4) | ((bayerImg[:, 2::3] >> (byte * 4)) & 0b1111) )
    
    grayCollection.append(gsImg)

  grayCollection = np.array(grayCollection)
  return grayCollection





def ConvertBitsPerPixel(ImgCollection, originBPP:int, targetBPP:int):
    """Converts the incoming ImgCollection into another value-range and adjusts the data-type if necessary.

    Args:
        ImgCollection (iterable, image): Iterable object of images.
        originBPP (int): The current images color-bit-width
        targetBPP (int): The target color-bit-width

    Returns:
        converted images: NDArray of converted images
    """
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




def StretchBrightness(ImgCollection, blackLevel:int = 256, whiteLevel:int = 0xFFF):
    """Stretches the pixel-values by: whitelevel / (whiteLevel - blackLevel)
    !!!ATTENTION!!! Function assumes images with 12bit values!

    Args:
        ImgCollection (iterable, images): Iterable object of images.
        blackLevel (int, optional): Blacklevel-value. Defaults to 256.
        whiteLevel (int, optional): _description_. Defaults to 0xFFF.

    Returns:
        _type_: _description_
    """
    stretchedImgs = []
    stretchFac = whiteLevel / (whiteLevel - blackLevel)
    for _iImg in range(len(ImgCollection)):
        _img = np.around(np.multiply(ImgCollection[_iImg], stretchFac)).astype(np.uint16)
        _img[_img > whiteLevel] = whiteLevel # Should not be possible, but added to be absolute sure!
        stretchedImgs.append(_img)
    stretchedImgs = np.array(stretchedImgs)

    return stretchedImgs