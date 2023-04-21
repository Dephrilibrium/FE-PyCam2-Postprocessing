###from math import isnan
import cv2 as cv
import numpy as np
###import matplotlib.pyplot as plt
import pickle

###from misc import bcolors










def DetectSpots(ImgCollection, pxDetectRadiusMin, pxDetectRadiusMax, Dilate:np.uint8 = 0, Erode:np.uint8 = 0, ShowImg=False):
  '''Searching for contours on the given (already converted) threshhold-image-collection.
     The function is always supposing circles as contours!
     Each contour-radius must be:   0 < r < pxDetectRadiusMax   with r [px]

  Inputs:
  ----------
  imgCollection: List of threshhold-images used for contour-detection
  pxDetectRadiusMax: Maximum radius a spot can occur without beeing in the range of another spot!
  DilateErode: Iteration steps for 1px-dilations (fill small gaps) and 1px-erodes (fix dialation)
  showImg: False: Silent process; True: Shows a preview-window

  Returns:
  ----------
  detectionImgs: List of images used for the spot-detection
  imgCircles: List of circles found on each img
  '''
  _detectionImgs = list()
  _imgCircles = list()

  for _iImg in range(ImgCollection.__len__()):
    _img = ImgCollection[_iImg]
    if _img.dtype != np.dtype("uint8"):
      raise Exception(str.format("Type uint8 necessary! Actual type is {}", _img.dtype))

    # _img = _img.copy() # Make copy, when dilate/erode is used
    if (Dilate + Erode) > 0:
      _dImg = cv.dilate(_img, None, iterations=Dilate) # Auto-creates a copy
      _dImg = cv.erode(_dImg, None, iterations=Erode) # Auto-creates a copy -> Override first copy so save RAM
    else:
      _dImg = _img.copy()

    if ShowImg:
      cv.imshow("Image of detection...", _dImg)

    # Find Contours for dummies:
    #  https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html
    # Used retrieve-mode:         cv.RETR_LIST              - get a hierachical less list of xy-points
    # Used chain-approx-mode:     cv.CHAIN_APPROX_SIMPLE    - keep only the corners of a rectangle with the outer dimensions

    _contours, _h1 = cv.findContours(_dImg, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

    # Prepare circles-data-dict for current picture
    _circleData = list()

    # Calculate center-point and radius of all detected contours
    for _cont in _contours:
      (x, y), r = cv.minEnclosingCircle(_cont)
      # Build nearest integer (drawable) values
      (x, y) = tuple(int(round(f)) for f in (x, y))
      r = int(round(r))

      # Check the diameter and append when it is detected as a separate detected spot
      if r <= pxDetectRadiusMax and r >= pxDetectRadiusMin:
        _circleData.append(dict())
        _circleData[_circleData.__len__()-1]["center"] = (x, y)
        _circleData[_circleData.__len__()-1]["radius"] = r
        _circleData[_circleData.__len__()-1]["ImageIndex"] = _iImg

    _detectionImgs.append(_dImg)
    _imgCircles.append(_circleData)

  if ShowImg:
    cv.destroyWindow("Image of detection...")
  return _detectionImgs, _imgCircles







def CollectCirclesAsXYKeys(CircleCollection, pxRadius = 12, AddPxRadius=False, FollowSpots=False):
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
  _spotsByXY = dict()

  # Create a working copy of the circle-list (deep-copy)
  _cCol = pickle.loads(pickle.dumps(CircleCollection))

  if not AddPxRadius: # When a constant its enough to set it once (saves calculation time)
    r2 = pxRadius ** 2

  _imgCnt = _cCol.__len__()
  for _iImg in range(_imgCnt):
    _circleCnt =  _cCol[_iImg].__len__()
    if _circleCnt == 0: # Skip empty images
      continue

    for _iCrcl in range(_circleCnt):
      _associatedCircles = list()
      _associatedCirclesImgIndicies = list()
      _foundOnImgs = 1

      _circle = _cCol[_iImg].pop(0) # Grab first circle and remove from list
      _circle["ImageIndex"] = _iImg
      _associatedCircles.append(_circle)
      _associatedCirclesImgIndicies.append(_iImg)
      x = _circle["center"][0] # Get starting x
      y = _circle["center"][1] # Get starting y
      r = _circle["radius"]    # Get starting radius, only used when addPxTolerance=True


      # Iterate through all other pictures and search
      #  for circles in pxTolerance of the same position
      for iCmpImg in range(_iImg + 1, _imgCnt):
        cmpCircleCnt = _cCol[iCmpImg].__len__() # Get amount of circles of current image
        if cmpCircleCnt == 0: # Skip empty images
          continue

        # Old check! Is not possible anymore since range(currentImg + 1, LastImage)
        # if iImg == iCmpImg: # Skip itself
        #   continue

        for iCmpCrcl in range(cmpCircleCnt):
          cmpCircle = _cCol[iCmpImg].pop(0) # Grab first one and remove from list. When it matches to "circle" it keeps removed, otherwise it gets attached again! -> see below @: if x² + y² > r²

          if _circle["center"] == cmpCircle["center"] and _circle["radius"] == cmpCircle["radius"]: # If it is exactly! the same circle, then you can go on, because it would have not effect on x, y, r
            _foundOnImgs += 1 # But increase divider to have that information
            cmpCircle["ImageIndex"] = iCmpImg
            _associatedCircles.append(cmpCircle)
            _associatedCirclesImgIndicies.append(iCmpImg)
            continue

          xCmp = cmpCircle["center"][0] # Get starting x
          yCmp = cmpCircle["center"][1] # Get starting y
          rCmp = cmpCircle["radius"]    # Get starting radius, only used when addPxTolerance=True

          if AddPxRadius: # When True, the spot-range must be recalculated each time! otherwise its a constant see start of function!
            r2 = (r + pxRadius) ** 2

          x2 = (x - xCmp) ** 2
          y2 = (y - yCmp) ** 2
          if (x2 + y2) > r2: # Compare-Spot is outside of the tolerance-range of the old spot!
            cmpCircle = _cCol[iCmpImg].append(cmpCircle) # Put circle back into the detected circles of the current compare-img (see @ the begin of this loop!)
            continue

          if FollowSpots: # When true the algorithm tries to follow the point by generating a new meaned xy-coordinate pair!
            # Restore old sum-value
            x = x * _foundOnImgs
            y = y * _foundOnImgs
            r = r * _foundOnImgs
            _foundOnImgs += 1 # Increase mean-divider/img-counter
            # Build mean
            x = (x + xCmp) / _foundOnImgs
            y = (y + yCmp) / _foundOnImgs
            r = (r + rCmp) / _foundOnImgs
          else: # When not, then only increase the counter on how much images that spot was found
            _foundOnImgs += 1 # Increase mean-divider/img-counter

          cmpCircle["ImageIndex"] = iCmpImg
          _associatedCircles.append(cmpCircle)
          _associatedCirclesImgIndicies.append(iCmpImg)


      # Coordinates and radius must be an integer number!
      x = int(x)
      y = int(y)
      r = int(r)
      _spotsByXY[(x, y)] = dict()
      _spotsByXY[(x, y)]["x"] = x
      _spotsByXY[(x, y)]["y"] = y
      _spotsByXY[(x, y)]["radius"] = r
      _spotsByXY[(x, y)]["ImageCount"] = _imgCnt # Amount of images available
      _spotsByXY[(x, y)]["FoundOnImgs"] = _foundOnImgs # Should be the same as length of associated sep(arate)Circles
      _spotsByXY[(x, y)]["ImageIndex"] = _associatedCirclesImgIndicies
      _spotsByXY[(x, y)]["ImgCircles"] = _associatedCircles


  # SaveSpotsByXY(spotsByXY, savePath)
  return _spotsByXY













def CorrectXYSortKeys(ssData, pxCorrectionRadius = 12):
  '''Correcting the shutterspeed circle sorting keys
  !!!ATTENTION!!!
  Function directly manupulates the data in ssData!'''
  # i = index
  # uncor = uncorrected
  # cor = corrected
  # srtd = sorted
  # Coll = Collection

  # Collect spot-sorts of all shutterspeeds in local list (faster access)
  _srtdColl = list()
  for _ss in ssData.keys():
     _srtdColl.append(ssData[_ss]["Circles"]["XYKeys"]) # Due to structure gets updated anyway, no deep copy is neccessary

  _collCnt = _srtdColl.__len__()
  _refColl = _srtdColl[0]

  _corColls = list()
  for _i in range(_collCnt): # Must be initalized before, because the sort algorithm would add _collCnt dicts per Key
    _corColls.append(dict())

  r2 = pxCorrectionRadius ** 2
  for _refKey in _refColl:
    _xRef = _refKey[0]
    _yRef = _refKey[1]

    for _iUncorColl in range(1, _collCnt):
      _uncorColl = _srtdColl[_iUncorColl]

      _uncorKeys = list(_uncorColl.keys())
      _uncorKeyCnt = _uncorKeys.__len__()
      for _iUncorKey in range(_uncorKeyCnt):
        _uncorKey = _uncorKeys[_iUncorKey]
        _cItem = _uncorColl.pop(_uncorKey) # Reappended at the end!
        _xCor = _uncorKey[0]
        _yCor = _uncorKey[1]

        _x2 = (_xRef - _xCor) ** 2
        _y2 = (_yRef - _yCor) ** 2

        if _x2 + _y2 <= r2: # When coordinates machted, add under new key otherwise
          _corColls[_iUncorColl][_refKey] = _cItem
          break

        _uncorColl[_uncorKey] = _cItem # Put back for other keys


  # Override uncorrected collection with corrected one
  # !!! ATTENTION !!!
  # Shutterspeed[0] (first one) is the key-reference!
  # In the other shutterspeeds[>0] unmatching keys will be deleted! (may good, may bad, it depends)
  ssKeys = list(ssData.keys())
  for _i in range(1, _collCnt): # Index 0 is the refCol from srtdColl and empty in _corColl
    ssData[ssKeys[_i]]["Circles"]["XYKeys"] = _corColls[_i]

  return














def SortXYFromLUtoRL(ssData, pxRowband):
  # Get keys for sorting by x and then y to get an ordered vector like:
  # 1   2 3
  # 4 5   6
  # 7     8
  # ... and so on
  # Key-Tuple: (x, y)

  # Implementation found on: https://stackoverflow.com/questions/29630052/ordering-coordinates-from-top-left-to-bottom-right
  #  Algorithm based on: https://www.researchgate.net/publication/282446068_Automatic_chessboard_corner_detection_method
  ssKeyList = list(ssData.keys())
  _keys = list(ssData[ssKeyList[0]]["Circles"]["XYKeys"].keys())

  # Find top left and top right
  d = pxRowband / 2
  _sortedKeys = []
  _searchKeys = _keys[:]
  while len(_searchKeys) > 0:
    a = sorted(_searchKeys, key=lambda p: (p[0] + p[1]))[0]       # Top-Left
    b = sorted(_searchKeys, key=lambda p: (p[0] - p[1]))[-1]      # Top-Right

    rowPoints = []
    remaining_points = []
    for keyPnt in _searchKeys:
      p = np.array([keyPnt[0], keyPnt[1]])

      paSub = np.subtract(p, a)
      baSub = np.subtract(b, a)
      pabCross = np.cross(paSub, baSub)
      pabNorm = np.linalg.norm(pabCross)
      bNorm = np.linalg.norm(b)
      dist = pabNorm / bNorm   # distance between keypoint and line a->b

      if d > dist:
        rowPoints.append(keyPnt)
      else:
        remaining_points.append(keyPnt)

    _sortedKeys.extend(sorted(rowPoints, key=lambda k: k[0]))
    _searchKeys = remaining_points

  for ss in ssKeyList:
    xySpots = ssData[ss]["Circles"]["XYKeys"]
    for _iKey in range(_sortedKeys.__len__()):
      try:                                       # Smaller shutterspeed may not detected all points from higher shutterspeeds! So try to:
        _spot = xySpots.pop(_sortedKeys[_iKey])  # - Pop out from collection and
        xySpots[_sortedKeys[_iKey]] = _spot      # - Reattach it to the tail
      except:
        pass

  return