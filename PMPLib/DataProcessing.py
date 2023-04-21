###from math import isnan
###import cv2 as cv
###import numpy as np
###import matplotlib.pyplot as plt
###import pickle
###
###from PMPLib.Factors_ImgSets import BuildFactorImgSets
###
###from misc import bcolors




###def DetectSpots(ImgCollection, pxDetectRadiusMax, DilateErode:np.uint8 = -1, ShowImg=False):
###  '''Searching for contours on the given (already converted) threshhold-image-collection.
###     The function is always supposing circles as contours!
###     Each contour-radius must be:   0 < r < pxDetectRadiusMax   with r [px]
###
###  Inputs:
###  ----------
###  imgCollection: List of threshhold-images used for contour-detection
###  pxDetectRadiusMax: Maximum radius a spot can occur without beeing in the range of another spot!
###  DilateErode: Iteration steps for 1px-dilations (fill small gaps) and 1px-erodes (fix dialation)
###  showImg: False: Silent process; True: Shows a preview-window
###
###  Returns:
###  ----------
###  detectionImgs: List of images used for the spot-detection
###  imgCircles: List of circles found on each img
###  '''
###  _detectionImgs = list()
###  _imgCircles = list()
###
###  for _iImg in range(ImgCollection.__len__()):
###    _img = ImgCollection[_iImg]
###    if _img.dtype != np.dtype("uint8"):
###      raise Exception(str.format("Type uint8 necessary! Actual type is {}", _img.dtype))
###
###    # _img = _img.copy() # Make copy, when dilate/erode is used
###    if DilateErode > 0:
###      _dImg = cv.dilate(_img, None, iterations=DilateErode) # Auto-creates a copy
###      _dImg = cv.erode(_dImg, None, iterations=DilateErode) # Auto-creates a copy -> Override first copy so save RAM
###    else:
###      _dImg = _img.copy()
###
###    if ShowImg:
###      cv.imshow("Image of detection...", _dImg)
###
###    # Find Contours for dummies:
###    #  https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html
###    # Used retrieve-mode:         cv.RETR_LIST              - get a hierachical less list of xy-points
###    # Used chain-approx-mode:     cv.CHAIN_APPROX_SIMPLE    - keep only the corners of a rectangle with the outer dimensions
###
###    _contours, _h1 = cv.findContours(_dImg, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
###
###    # Prepare circles-data-dict for current picture
###    _circleData = list()
###
###    # Calculate center-point and radius of all detected contours
###    for _cont in _contours:
###      (x, y), r = cv.minEnclosingCircle(_cont)
###      # Build nearest integer (drawable) values
###      (x, y) = tuple(int(round(f)) for f in (x, y))
###      r = int(round(r))
###
###      # Check the diameter and append when it is detected as a separate detected spot
###      if r <= pxDetectRadiusMax and r >= 1:
###        _circleData.append(dict())
###        _circleData[_circleData.__len__()-1]["center"] = (x, y)
###        _circleData[_circleData.__len__()-1]["radius"] = r
###        _circleData[_circleData.__len__()-1]["ImageIndex"] = _iImg
###
###    _detectionImgs.append(_dImg)
###    _imgCircles.append(_circleData)
###
###  if ShowImg:
###    cv.destroyWindow("Image of detection...")
###  return _detectionImgs, _imgCircles





###def CollectCirclesAsXYKeys(CircleCollection, pxRadius = 12, AddPxRadius=False, FollowSpots=False):
###  '''Loops through all circles and tries to sort them by its location + tolerance
###
###  Inputs:
###  ----------
###  circleCollection: List of circles detected on each image
###  pxTolerance: Tolerance-Radius in [px]
###  addPxRadius: False: pxTolerance is fix; True: pxTolerance is added to the circle-radius!
###  SavePath: Savepath including filename and extension where to save!
###
###  Returns:
###  ----------
###  spotsByXY: Dictionary of circles with (xMean, yMean)-tuple-Key
###  '''
###  _spotsByXY = dict()
###
###  # Create a working copy of the circle-list (deep-copy)
###  _cCol = pickle.loads(pickle.dumps(CircleCollection))
###
###  if not AddPxRadius: # When a constant its enough to set it once (saves calculation time)
###    r2 = pxRadius ** 2
###
###  _imgCnt = _cCol.__len__()
###  for _iImg in range(_imgCnt):
###    _circleCnt =  _cCol[_iImg].__len__()
###    if _circleCnt == 0: # Skip empty images
###      continue
###
###    for _iCrcl in range(_circleCnt):
###      _associatedCircles = list()
###      _associatedCirclesImgIndicies = list()
###      _foundOnImgs = 1
###
###      _circle = _cCol[_iImg].pop(0) # Grab first circle and remove from list
###      _circle["ImageIndex"] = _iImg
###      _associatedCircles.append(_circle)
###      _associatedCirclesImgIndicies.append(_iImg)
###      x = _circle["center"][0] # Get starting x
###      y = _circle["center"][1] # Get starting y
###      r = _circle["radius"]    # Get starting radius, only used when addPxTolerance=True
###
###
###      # Iterate through all other pictures and search
###      #  for circles in pxTolerance of the same position
###      for iCmpImg in range(_iImg + 1, _imgCnt):
###        cmpCircleCnt = _cCol[iCmpImg].__len__() # Get amount of circles of current image
###        if cmpCircleCnt == 0: # Skip empty images
###          continue
###
###        # Old check! Is not possible anymore since range(currentImg + 1, LastImage)
###        # if iImg == iCmpImg: # Skip itself
###        #   continue
###
###        for iCmpCrcl in range(cmpCircleCnt):
###          cmpCircle = _cCol[iCmpImg].pop(0) # Grab first one and remove from list. When it matches to "circle" it ###keeps removed, otherwise it gets attached again! -> see below @: if x² + y² > r²
###
###          if _circle["center"] == cmpCircle["center"] and _circle["radius"] == cmpCircle["radius"]: # If it is ###exactly! the same circle, then you can go on, because it would have not effect on x, y, r
###            _foundOnImgs += 1 # But increase divider to have that information
###            cmpCircle["ImageIndex"] = iCmpImg
###            _associatedCircles.append(cmpCircle)
###            _associatedCirclesImgIndicies.append(iCmpImg)
###            continue
###
###          xCmp = cmpCircle["center"][0] # Get starting x
###          yCmp = cmpCircle["center"][1] # Get starting y
###          rCmp = cmpCircle["radius"]    # Get starting radius, only used when addPxTolerance=True
###
###          if AddPxRadius: # When True, the spot-range must be recalculated each time! otherwise its a constant see ###start of function!
###            r2 = (r + pxRadius) ** 2
###
###          x2 = (x - xCmp) ** 2
###          y2 = (y - yCmp) ** 2
###          if (x2 + y2) > r2: # Compare-Spot is outside of the tolerance-range of the old spot!
###            cmpCircle = _cCol[iCmpImg].append(cmpCircle) # Put circle back into the detected circles of the current ###compare-img (see @ the begin of this loop!)
###            continue
###
###          if FollowSpots: # When true the algorithm tries to follow the point by generating a new meaned ###xy-coordinate pair!
###            # Restore old sum-value
###            x = x * _foundOnImgs
###            y = y * _foundOnImgs
###            r = r * _foundOnImgs
###            _foundOnImgs += 1 # Increase mean-divider/img-counter
###            # Build mean
###            x = (x + xCmp) / _foundOnImgs
###            y = (y + yCmp) / _foundOnImgs
###            r = (r + rCmp) / _foundOnImgs
###          else: # When not, then only increase the counter on how much images that spot was found
###            _foundOnImgs += 1 # Increase mean-divider/img-counter
###
###          cmpCircle["ImageIndex"] = iCmpImg
###          _associatedCircles.append(cmpCircle)
###          _associatedCirclesImgIndicies.append(iCmpImg)
###
###
###      # Coordinates and radius must be an integer number!
###      x = int(x)
###      y = int(y)
###      r = int(r)
###      _spotsByXY[(x, y)] = dict()
###      _spotsByXY[(x, y)]["x"] = x
###      _spotsByXY[(x, y)]["y"] = y
###      _spotsByXY[(x, y)]["radius"] = r
###      _spotsByXY[(x, y)]["ImageCount"] = _imgCnt # Amount of images available
###      _spotsByXY[(x, y)]["FoundOnImgs"] = _foundOnImgs # Should be the same as length of associated sep(arate)Circles
###      _spotsByXY[(x, y)]["ImageIndex"] = _associatedCirclesImgIndicies
###      _spotsByXY[(x, y)]["ImgCircles"] = _associatedCircles
###
###
###  # SaveSpotsByXY(spotsByXY, savePath)
###  return _spotsByXY





###def CorrectCircleSortKeys(ssData, pxCorrectionRadius = 12):
###  '''Correcting the shutterspeed circle sorting keys
###  !!!ATTENTION!!!
###  Function directly manupulates the data in ssData!'''
###  # i = index
###  # uncor = uncorrected
###  # cor = corrected
###  # srtd = sorted
###  # Coll = Collection
###
###  # Collect spot-sorts of all shutterspeeds in local list (faster access)
###  _srtdColl = list()
###  for _ss in ssData.keys():
###     _srtdColl.append(ssData[_ss]["Circles"]["XYKeys"]) # Due to structure gets updated anyway, no deep copy is neccessary
###
###  _collCnt = _srtdColl.__len__()
###  _refColl = _srtdColl[0]
###
###  _corColls = list()
###  for _i in range(_collCnt): # Must be initalized before, because the sort algorithm would add _collCnt dicts per Key
###    _corColls.append(dict())
###
###  r2 = pxCorrectionRadius ** 2
###  for _refKey in _refColl:
###    _xRef = _refKey[0]
###    _yRef = _refKey[1]
###
###    for _iUncorColl in range(1, _collCnt):
###      _uncorColl = _srtdColl[_iUncorColl]
###
###      _uncorKeys = list(_uncorColl.keys())
###      _uncorKeyCnt = _uncorKeys.__len__()
###      for _iUncorKey in range(_uncorKeyCnt):
###        _uncorKey = _uncorKeys[_iUncorKey]
###        _cItem = _uncorColl.pop(_uncorKey) # Reappended at the end!
###        _xCor = _uncorKey[0]
###        _yCor = _uncorKey[1]
###
###        _x2 = (_xRef - _xCor) ** 2
###        _y2 = (_yRef - _yCor) ** 2
###
###        if _x2 + _y2 <= r2: # When coordinates machted, add under new key otherwise
###          _corColls[_iUncorColl][_refKey] = _cItem
###          break
###
###        _uncorColl[_uncorKey] = _cItem # Put back for other keys
###
###
###  # Override uncorrected collection with corrected one
###  # !!! ATTENTION !!!
###  # Shutterspeed[0] (first one) is the key-reference!
###  # In the other shutterspeeds[>0] unmatching keys will be deleted! (may good, may bad, it depends)
###  ssKeys = list(ssData.keys())
###  for _i in range(1, _collCnt): # Index 0 is the refCol from srtdColl and empty in _corColl
###    ssData[ssKeys[_i]]["Circles"]["XYKeys"] = _corColls[_i]
###
###  return







###def SortXYFromLUtoRL(ssData, pxRowband):
###    # Get keys for sorting by x and then y to get an ordered vector like:
###  # 1   2 3
###  # 4 5   6
###  # 7     8
###  # ... and so on
###  # Key-Tuple: (x, y)
###
###  # Implementation found on: https://stackoverflow.com/questions/29630052/ordering-coordinates-from-top-left-to-bottom-right
###  #  Algorithm based on: https://www.researchgate.net/publication/282446068_Automatic_chessboard_corner_detection_method
###  ssKeyList = list(ssData.keys())
###  _keys = list(ssData[ssKeyList[0]]["Circles"]["XYKeys"].keys())
###
###  # Find top left and top right
###  d = pxRowband / 2
###  _sortedKeys = []
###  _searchKeys = _keys[:]
###  while len(_searchKeys) > 0:
###    a = sorted(_searchKeys, key=lambda p: (p[0] + p[1]))[0]       # Top-Left
###    b = sorted(_searchKeys, key=lambda p: (p[0] - p[1]))[-1]      # Top-Right
###
###    rowPoints = []
###    remaining_points = []
###    for keyPnt in _searchKeys:
###      p = np.array([keyPnt[0], keyPnt[1]])
###
###      paSub = np.subtract(p, a)
###      baSub = np.subtract(b, a)
###      pabCross = np.cross(paSub, baSub)
###      pabNorm = np.linalg.norm(pabCross)
###      bNorm = np.linalg.norm(b)
###      dist = pabNorm / bNorm   # distance between keypoint and line a->b
###
###      if d > dist:
###        rowPoints.append(keyPnt)
###      else:
###        remaining_points.append(keyPnt)
###
###    _sortedKeys.extend(sorted(rowPoints, key=lambda k: k[0]))
###    _searchKeys = remaining_points
###
###  for ss in ssKeyList:
###    xySpots = ssData[ss]["Circles"]["XYKeys"]
###    for _iKey in range(_sortedKeys.__len__()):
###      try:                                       # Smaller shutterspeed may not detected all points from higher shutterspeeds! So try to:
###        _spot = xySpots.pop(_sortedKeys[_iKey])  # - Pop out from collection and
###        xySpots[_sortedKeys[_iKey]] = _spot      # - Reattach it to the tail
###      except:
###        pass
###
###  return






###def GetCircleArea_XYX2Y2(Circle, pxTolerance, AddPxTolerance):
###
###  halfTol = int(pxTolerance / 2)
###
###  if AddPxTolerance == True:
###    x = Circle["center"][0] - Circle["radius"] - halfTol
###    y = Circle["center"][1] - Circle["radius"] - halfTol
###    x2 = x + 2*Circle["radius"] + pxTolerance
###    y2 = y + 2*Circle["radius"] + pxTolerance
###  else:
###    x = Circle["center"][0] - halfTol
###    y = Circle["center"][1] - halfTol
###    x2 = x + pxTolerance
###    y2 = y + pxTolerance
###
###  return x, y, x2, y2







###def __BrightnessFactors_BuildImgSubSet__(ImgCollection, XYCollection, pxSidelen, AddPxSidelen, OverexposedBright, CleanMask):
###  subSet = dict()
###  subSet["Full"] = dict()
###  subSet["Full"]["Blank"] = list()
###  subSet["Full"]["Clean"] = list()
###  subSet["Full"]["OverexposedMask"] = list()
###  subSet["Full"]["CleanMask"] = list()
###
###  subSet["Spot"] = dict()
###  # subSet["Spot"]["Blank"] = dict()
###  # subSet["Spot"]["Clean"] = dict()
###  # subSet["Spot"]["OverexposedMask"] = list()
###
###
###  for _iImg in range(len(ImgCollection)):
###    subSet["Full"]["Blank"].append(ImgCollection[_iImg])
###    cleanImg = subSet["Full"]["Blank"][-1].copy()
###    overexposedMask = cleanImg >= OverexposedBright
###    subSet["Full"]["OverexposedMask"].append(overexposedMask)
###
###    if CleanMask == None:
###      subSet["Full"]["CleanMask"].append(subSet["Full"]["OverexposedMask"][-1]) # Overexpose == Clean -> Img is base-SS
###    else:
###      subSet["Full"]["CleanMask"].append(CleanMask[_iImg])   # Use cleanMask vom given base to indicate which pixels are purged
###
###    cleanImg[subSet["Full"]["CleanMask"][-1]] = 0
###    subSet["Full"]["Clean"].append(cleanImg)
###
###  _xyKeys = list(XYCollection.keys())
###  # _imgShape = ImgCollection[0].shape;
###  _imgShape = (pxSidelen, pxSidelen) # Size of an spot!
###  for _iXY in range(len(_xyKeys)):
###    _xyKey = _xyKeys[_iXY]
###    subSet["Spot"][_xyKey] = dict()
###    subSet["Spot"][_xyKey]["Blank"] = list()
###    subSet["Spot"][_xyKey]["Clean"] = list()
###    subSet["Spot"][_xyKey]["OverexposedMask"] = list()
###    subSet["Spot"][_xyKey]["CleanMask"] = list()
###    subSet["Spot"][_xyKey]["Area"] = list()
###
###    for _iImg in range(len(ImgCollection)):
###      try:
###        _iIndex = XYCollection[_xyKey]["ImageIndex"].index(_iImg)
###        _circle = XYCollection[_xyKey]["ImgCircles"][_iIndex]
###
###        x1, y1, x2, y2 = GetCircleArea_XYX2Y2(Circle=_circle, pxTolerance=pxSidelen, AddPxTolerance=AddPxSidelen)
###        subSet["Spot"][_xyKey]["Blank"].append(subSet["Full"]["Blank"][_iImg][y1:y2, x1:x2])                      # Add references to full-dataset
###        subSet["Spot"][_xyKey]["Clean"].append(subSet["Full"]["Clean"][_iImg][y1:y2, x1:x2])                      # Add references to full-dataset
###        subSet["Spot"][_xyKey]["OverexposedMask"].append(subSet["Full"]["OverexposedMask"][_iImg][y1:y2, x1:x2])  # Add references to full-dataset
###        subSet["Spot"][_xyKey]["CleanMask"].append(subSet["Full"]["CleanMask"][_iImg][y1:y2, x1:x2])              # Add references to full-dataset
###        subSet["Spot"][_xyKey]["Area"].append([x1, y1, x2, y2])
###      except Exception as e:
###        subSet["Spot"][_xyKey]["Blank"].append(np.zeros(_imgShape))
###        subSet["Spot"][_xyKey]["Clean"].append(np.zeros(_imgShape))
###        subSet["Spot"][_xyKey]["OverexposedMask"].append(np.zeros(_imgShape, dtype=bool))
###        subSet["Spot"][_xyKey]["CleanMask"].append(subSet["Spot"][_xyKey]["OverexposedMask"][-1])
###        subSet["Spot"][_xyKey]["Area"].append([0, 0, 0, 0])
###
###  return subSet

# def __BrightnessFactors_PurgeImageSets__(ImgCollection, OverexposedValue, Overexposed):

#   _bKeys = list(bImgs.keys())
#   for _iBase in range(len(_bKeys)):
#     _bKey = _bKeys[_iBase]

#   return


###def __BrightnessFactors_BuildImageSets___(ssData, ImgKey, pxSidelen, AddPxSidelen, OverexposedValue):
###
###  _ssKeys = list(ssData.keys())
###
###  bImgs = dict()
###
###  for _iBase in range(len(_ssKeys) -1):
###    _bKey = _ssKeys[_iBase]
###
###    # Prepare dict for full base-images
###    bImgs[_bKey] = __BrightnessFactors_BuildImgSubSet__(ImgCollection=pickle.loads(pickle.dumps(ssData[_bKey]["Images"][ImgKey])), XYCollection=ssData[_bKey]["Circles"]["XYKeys"], pxSidelen=pxSidelen, AddPxSidelen=AddPxSidelen, OverexposedBright=OverexposedValue, CleanMask=None)
###    bImgs[_bKey]["Div"] = dict()
###
###
###    #######################      ^--- Appends Base Images ---^     #######################
###    ######################################################################################
###    #######################      v--- Appends Div-Images  ---v     #######################
###    for _iDiv in range(_iBase + 1, len(_ssKeys)):
###      _dKey = _ssKeys[_iDiv]
###
###      # Prepare dict for div
###      bImgs[_bKey]["Div"][_dKey] = __BrightnessFactors_BuildImgSubSet__(ImgCollection=pickle.loads(pickle.dumps(ssData[_dKey]["Images"][ImgKey])), XYCollection=ssData[_dKey]["Circles"]["XYKeys"], pxSidelen=pxSidelen, AddPxSidelen=AddPxSidelen, OverexposedBright=OverexposedValue, CleanMask=bImgs[_bKey]["Full"]["OverexposedMask"])
###
###  return bImgs





###def __GetBrightnessFromImageCollection__(ImgCollection):
###  return [np.sum(img) for img in ImgCollection]


###def __BrightnessFactors_BuildBrightSubSet__(ImgSet):
###  subSet = dict()
###
###  subSet["Blank"] = __GetBrightnessFromImageCollection__(ImgSet["Blank"])
###  subSet["Clean"] = __GetBrightnessFromImageCollection__(ImgSet["Clean"])
###
###  return subSet

###def __BrightnessFactors_GetBrightSets__(imgSets):
###  brightSets = dict()
###
###  _bKeys = list(imgSets.keys())
###  for _iBase in range(len(_bKeys)):
###    _bKey = _bKeys[_iBase]
###
###    brightSets[_bKey] = dict()
###    brightSets[_bKey]["Full"] = __BrightnessFactors_BuildBrightSubSet__(imgSets[_bKey]["Full"])
###    brightSets[_bKey]["Spot"] = dict()  # Empty dict for "correct" order
###    brightSets[_bKey]["Div"] = dict()
###
###
###    _dKeys = list(imgSets[_bKey]["Div"].keys())
###    for _iDiv in range(len(_dKeys)):
###      _dKey = _dKeys[_iDiv]
###
###      brightSets[_bKey]["Div"][_dKey] = dict()
###      brightSets[_bKey]["Div"][_dKey]["Full"] = __BrightnessFactors_BuildBrightSubSet__(imgSets[_bKey]["Div"][_dKey]["Full"])
###      brightSets[_bKey]["Div"][_dKey]["Spot"] = dict()
###
###      _xyKeys = list(imgSets[_bKey]["Spot"].keys())
###      for _iXY in range(len(_xyKeys)):
###        _xyKey = _xyKeys[_iXY]
###        brightSets[_bKey]["Spot"][_xyKey] = __BrightnessFactors_BuildBrightSubSet__(imgSets[_bKey]["Spot"][_xyKey])
###
###        try:
###          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey] = __BrightnessFactors_BuildBrightSubSet__(imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey])
###        except Exception as e:
###          imgCnt = len(imgSets[_bKey]["Full"]["Blank"])
###
###          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey] = dict()
###          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Blank"] = np.zeros(imgCnt)
###          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Clean"] = np.zeros(imgCnt)
###
###
###
###  return brightSets


###def __GetPxAreaCntFromImageCollection__(ImgCollection):
###  return [cv.countNonZero(img) for img in ImgCollection]

###def __BrightnessFactors_BuildPxAreaCntSubSet__(ImgSet):
###  subSet = dict()
###
###  subSet["Blank"] = __GetPxAreaCntFromImageCollection__(ImgSet["Blank"])
###  subSet["Clean"] = __GetPxAreaCntFromImageCollection__(ImgSet["Clean"])
###  subSet["Blank-Clean"] = np.subtract(subSet["Blank"], subSet["Clean"]) # How much pixels are purged in clean-img
###
###  return subSet


###def __BrightnessFactors_GetPxAreaCnt__(imgSets):
###  pxAreas = dict()
###
###  _bKeys = list(imgSets.keys())
###  for _iBase in range(len(_bKeys)):
###    _bKey = _bKeys[_iBase]
###
###    pxAreas[_bKey] = dict()
###    pxAreas[_bKey]["Full"] = __BrightnessFactors_BuildPxAreaCntSubSet__(imgSets[_bKey]["Full"])
###    pxAreas[_bKey]["Spot"] = dict()  # Empty dict for "correct" order
###    pxAreas[_bKey]["Div"] = dict()
###
###
###    _dKeys = list(imgSets[_bKey]["Div"].keys())
###    for _iDiv in range(len(_dKeys)):
###      _dKey = _dKeys[_iDiv]
###
###      pxAreas[_bKey]["Div"][_dKey] = dict()
###      pxAreas[_bKey]["Div"][_dKey]["Full"] = __BrightnessFactors_BuildPxAreaCntSubSet__(imgSets[_bKey]["Div"][_dKey]["Full"])
###      pxAreas[_bKey]["Div"][_dKey]["Spot"] = dict()
###
###      _xyKeys = list(imgSets[_bKey]["Spot"].keys())
###      for _iXY in range(len(_xyKeys)):
###        _xyKey = _xyKeys[_iXY]
###
###        pxAreas[_bKey]["Spot"][_xyKey] = __BrightnessFactors_BuildPxAreaCntSubSet__(imgSets[_bKey]["Spot"][_xyKey])
###        try:
###          pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey] = __BrightnessFactors_BuildPxAreaCntSubSet__(imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey])
###        except Exception as e:
###          imgCnt = len(imgSets[_bKey]["Full"]["Blank"])
###
###          pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey] = dict()
###          pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Blank"] = np.zeros(imgCnt)
###          pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Clean"] = np.zeros(imgCnt)
###
###  return pxAreas








### def __BrightnessFactors_BuildSpotDivFactorSubSet__(bVec, dVec):
###   subSet = dict()
###   subSet["Blank"] = np.divide(bVec["Blank"], dVec["Blank"])
###   subSet["Clean"] = np.divide(bVec["Clean"], dVec["Clean"])
###   np.nan_to_num(subSet["Blank"], copy=False, nan=0, posinf=0, neginf=0)
###   np.nan_to_num(subSet["Clean"], copy=False, nan=0, posinf=0, neginf=0)
###   return subSet


###def __BrightnessFactors_BuildMeanPxDivFactor__(bImg, dImg, trustband, loMinBright):
###  _bMaxBright = 255
###  _bMinBright = 0
###
###  lower = trustband[0]
###  if lower < _bMinBright:
###    lower = _bMinBright
###
###  upper = trustband[1]
###  if upper > _bMaxBright:
###    upper = _bMaxBright
###
###  if lower > upper:
###    raise Exception("lower trusted brightness > higher trusted brightness")
###
###  # Remove non-trusted pixels
###  trustMask = (bImg < lower) | (bImg > upper)
###  minLoMask = dImg < loMinBright
###  bImg = bImg.copy()
###  # dImg = dImg.copy() # Not neccessary to manipulate divider-image -> Save RAM
###  bImg[trustMask] = 0
###  bImg[minLoMask] = 0
###  # dImg[mask] = 0
###
###  divImg = np.divide(bImg, dImg)
###  np.nan_to_num(divImg, copy=False, nan=np.nan, posinf=np.nan, neginf=np.nan)
###  meanDiv = np.nanmean(divImg)
###  if isnan(meanDiv):
###    meanDiv = 0
###  np.nan_to_num(divImg, copy=False, nan=0, posinf=0, neginf=0)
###  return meanDiv, divImg


###def __BrightnessFactors_BuildMeanPxDivFactorSubSet__(bImgs, dImgs, trustband, loMinBright):
###  subSet = dict()
###  subSet["Blank"] = list()
###  subSet["Clean"] = list()
###
###  for _iImg in range(len(bImgs["Blank"])):
###    meanDiv, divImg = __BrightnessFactors_BuildMeanPxDivFactor__(bImgs["Blank"][_iImg], dImgs["Blank"][_iImg], trustband, loMinBright)
###    subSet["Blank"].append(meanDiv)
###    meanDiv, divImg = __BrightnessFactors_BuildMeanPxDivFactor__(bImgs["Clean"][_iImg], dImgs["Clean"][_iImg], trustband, loMinBright)
###    subSet["Clean"].append(meanDiv)
###
###  np.nan_to_num(subSet["Blank"], copy=False, nan=0, posinf=0, neginf=0)
###  np.nan_to_num(subSet["Clean"], copy=False, nan=0, posinf=0, neginf=0)
###  return subSet
###
###def __BrightnessFactors_BuildPxAreaCntDivFactorSubSet__(bAreaCntSet, dAreaCntSet):
###  subSet = dict()
###  subSet["Blank"] = np.divide(bAreaCntSet["Blank"], dAreaCntSet["Blank"])
###  subSet["Clean"] = np.divide(bAreaCntSet["Clean"], dAreaCntSet["Clean"])
###
###  np.nan_to_num(subSet["Blank"], copy=False, nan=0, posinf=0, neginf=0)
###  np.nan_to_num(subSet["Clean"], copy=False, nan=0, posinf=0, neginf=0)
###  return subSet



###def __BrightnessFactors_BuildDivFactors__(imgSets, brightSets, pxAreaCntSets, PxDivTrustband, PxDivMinBright):
###  factors = dict()
###
###  _bKeys = list(imgSets.keys())
###  for _iBase in range(len(_bKeys)):
###    _bKey = _bKeys[_iBase]
###
###    factors[_bKey] = dict()
###
###    _dKeys = list(imgSets[_bKey]["Div"].keys())
###    for _iDiv in range(len(_dKeys)):
###      _dKey = _dKeys[_iDiv]
###
###      factors[_bKey][_dKey] = dict()
###      factors[_bKey][_dKey]["Theory"] = [_bKey / _dKey] * len(imgSets[_bKey]["Full"]["Blank"])
###      factors[_bKey][_dKey]["Full"] = dict()
###      factors[_bKey][_dKey]["Spot"] = dict()
###
###
###      factors[_bKey][_dKey]["Full"]["SpotDiv"] = __BrightnessFactors_BuildSpotDivFactorSubSet__(brightSets[_bKey]["Full"], brightSets[_bKey]["Div"][_dKey]["Full"])
###      # factors[_bKey][_dKey]["Spot"]["SpotDiv"] = dict()
###
###      factors[_bKey][_dKey]["Full"]["MeanPxDiv"] = __BrightnessFactors_BuildMeanPxDivFactorSubSet__(imgSets[_bKey]["Full"], imgSets[_bKey]["Div"][_dKey]["Full"], PxDivTrustband, PxDivMinBright)
###      # factors[_bKey][_dKey]["Spot"]["MeanPxDiv"] = dict()
###
###      factors[_bKey][_dKey]["Full"]["PxAreaDiv"] = __BrightnessFactors_BuildPxAreaCntDivFactorSubSet__(pxAreaCntSets[_bKey]["Full"], pxAreaCntSets[_bKey]["Div"][_dKey]["Full"])
###      # factors[_bKey][_dKey]["Spot"]["PxAreaDiv"] = dict()
###
###      _xyKeys = list(imgSets[_bKey]["Spot"].keys())
###      for _iXY in range(len(_xyKeys)):
###        _xyKey = _xyKeys[_iXY]
###
###        factors[_bKey][_dKey]["Spot"][_xyKey] = dict()
###        factors[_bKey][_dKey]["Spot"][_xyKey]["SpotDiv"] = __BrightnessFactors_BuildSpotDivFactorSubSet__(brightSets[_bKey]["Spot"][_xyKey], brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey])
###        try:
###          factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"] = __BrightnessFactors_BuildMeanPxDivFactorSubSet__(imgSets[_bKey]["Spot"][_xyKey], imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey], PxDivTrustband, PxDivMinBright)
###        except Exception as e:
###          factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"] = dict()
###          factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Blank"] = np.zeros(len(imgSets[_bKey]["Full"]["Blank"]))
###          factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Clean"] = factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Blank"] # Because all 0 -> Reuse!
###
###        try:
###          factors[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"] = __BrightnessFactors_BuildPxAreaCntDivFactorSubSet__(pxAreaCntSets[_bKey]["Spot"][_xyKey], pxAreaCntSets[_bKey]["Div"][_dKey]["Spot"][_xyKey])
###        except Exception as e:
###          factors[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"] = dict()
###          factors[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"]["Blank"] = np.zeros(len(imgSets[_bKey]["Full"]["Blank"]))
###          factors[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"]["Clean"] = factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Blank"] # Because all 0 -> Reuse!
###
###  return factors


###def __BrightnessFactors_BuildCombinedFactorSubSet__(divFactorSet):
###  subSet = dict()
###
###  subSet["SpotDiv"] = dict()
###  subSet["SpotDiv"]["Blank"] = dict()
###  subSet["SpotDiv"]["Clean"] = dict()
###  subSet["SpotDiv"]["Blank&Clean"] = dict()
###  subSet["SpotDiv"]["Blank"]["xAreaBlank"]       = np.multiply(divFactorSet["SpotDiv"]["Blank"], divFactorSet["PxAreaDiv"]["Blank"])
###  subSet["SpotDiv"]["Blank"]["xAreaClean"]       = np.multiply(divFactorSet["SpotDiv"]["Blank"], divFactorSet["PxAreaDiv"]["Clean"])
###  subSet["SpotDiv"]["Clean"]["xAreaBlank"]       = np.multiply(divFactorSet["SpotDiv"]["Clean"], divFactorSet["PxAreaDiv"]["Blank"])
###  subSet["SpotDiv"]["Clean"]["xAreaClean"]       = np.multiply(divFactorSet["SpotDiv"]["Clean"], divFactorSet["PxAreaDiv"]["Clean"])
###  subSet["SpotDiv"]["Blank&Clean"]["Mean"]       = np.mean([divFactorSet["SpotDiv"]["Blank"], divFactorSet["SpotDiv"]["Clean"]], axis=0)
###  subSet["SpotDiv"]["Blank&Clean"]["xAreaBlank"] = np.multiply(subSet["SpotDiv"]["Blank&Clean"]["Mean"], divFactorSet["PxAreaDiv"]["Blank"])
###  subSet["SpotDiv"]["Blank&Clean"]["xAreaClean"] = np.multiply(subSet["SpotDiv"]["Blank&Clean"]["Mean"], divFactorSet["PxAreaDiv"]["Clean"])
###  
###
###  subSet["MeanPxDiv"] = dict()
###  subSet["MeanPxDiv"]["Blank"] = dict()
###  subSet["MeanPxDiv"]["Clean"] = dict()
###  subSet["MeanPxDiv"]["Blank&Clean"] = dict()
###  subSet["MeanPxDiv"]["Blank"]["xAreaBlank"]       = np.multiply(divFactorSet["MeanPxDiv"]["Blank"], divFactorSet["PxAreaDiv"]["Blank"])
###  subSet["MeanPxDiv"]["Blank"]["xAreaClean"]       = np.multiply(divFactorSet["MeanPxDiv"]["Blank"], divFactorSet["PxAreaDiv"]["Clean"])
###  subSet["MeanPxDiv"]["Clean"]["xAreaBlank"]       = np.multiply(divFactorSet["MeanPxDiv"]["Clean"], divFactorSet["PxAreaDiv"]["Blank"])
###  subSet["MeanPxDiv"]["Clean"]["xAreaClean"]       = np.multiply(divFactorSet["MeanPxDiv"]["Clean"], divFactorSet["PxAreaDiv"]["Clean"])
###  subSet["MeanPxDiv"]["Blank&Clean"]["Mean"]       = np.mean([divFactorSet["MeanPxDiv"]["Blank"], divFactorSet["MeanPxDiv"]["Clean"]], axis=0)
###  subSet["MeanPxDiv"]["Blank&Clean"]["xAreaBlank"] = np.multiply(subSet["MeanPxDiv"]["Blank&Clean"]["Mean"], divFactorSet["PxAreaDiv"]["Blank"])
###  subSet["MeanPxDiv"]["Blank&Clean"]["xAreaClean"] = np.multiply(subSet["MeanPxDiv"]["Blank&Clean"]["Mean"], divFactorSet["PxAreaDiv"]["Clean"])
###
###  return subSet


###def __BrightnessFactors_BuildCombinedFactors__(divFactorSets):
###  cmbFactors = dict()
###
###  _bKeys = list(divFactorSets.keys())
###  for _iBase in range(len(_bKeys)):
###    _bKey = _bKeys[_iBase]
###
###    cmbFactors[_bKey] = dict()
###
###    _dKeys = list(divFactorSets[_bKey].keys())
###    for _iDiv in range(len(_dKeys)):
###      _dKey = _dKeys[_iDiv]
###
###      cmbFactors[_bKey][_dKey] = dict()
###      cmbFactors[_bKey][_dKey]["Full"] = __BrightnessFactors_BuildCombinedFactorSubSet__(divFactorSets[_bKey][_dKey]["Full"])
###      cmbFactors[_bKey][_dKey]["Full"]["Theory"] = dict()
###      cmbFactors[_bKey][_dKey]["Full"]["Theory"]["/BlankArea"] = np.divide(divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Full"]["PxAreaDiv"]["Blank"])
###      np.nan_to_num(cmbFactors[_bKey][_dKey]["Full"]["Theory"]["/BlankArea"], copy=False, nan=0, posinf=0, neginf=0)
###      cmbFactors[_bKey][_dKey]["Full"]["Theory"]["/CleanArea"] = np.divide(divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Full"]["PxAreaDiv"]["Clean"])
###      np.nan_to_num(cmbFactors[_bKey][_dKey]["Full"]["Theory"]["/CleanArea"], copy=False, nan=0, posinf=0, neginf=0)
###
###
###      cmbFactors[_bKey][_dKey]["Spot"] = dict()
###      _xyKeys = list(divFactorSets[_bKey][_dKey]["Spot"].keys())
###      for _iXY in range(len(_xyKeys)):
###        _xyKey = _xyKeys[_iXY]
###
###        cmbFactors[_bKey][_dKey]["Spot"][_xyKey] = __BrightnessFactors_BuildCombinedFactorSubSet__(divFactorSets[_bKey][_dKey]["Spot"][_xyKey])
###        cmbFactors[_bKey][_dKey]["Spot"][_xyKey]["Theory"] = dict()
###        cmbFactors[_bKey][_dKey]["Spot"][_xyKey]["Theory"]["/BlankArea"] = np.divide(divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"]["Blank"])
###        np.nan_to_num(cmbFactors[_bKey][_dKey]["Spot"][_xyKey]["Theory"]["/BlankArea"], copy=False, nan=0, posinf=0, neginf=0)
###        cmbFactors[_bKey][_dKey]["Spot"][_xyKey]["Theory"]["/CleanArea"] = np.divide(divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"]["Clean"])
###        np.nan_to_num(cmbFactors[_bKey][_dKey]["Spot"][_xyKey]["Theory"]["/CleanArea"], copy=False, nan=0, posinf=0, neginf=0)
###
###
###  return cmbFactors


###def __BrightUpscale_AnySpotbrightSubSet__(brightSet, theoryFactors, divFactors, combiFactors):
###  upscaledSpotAny = dict()
###
###  upscaledSpotAny = dict()
###  upscaledSpotAny["Blank"] = dict()
###  upscaledSpotAny["Clean"] = dict()
###
###  upscaledSpotAny["Blank"]["xTheory"] = np.multiply(brightSet["Blank"], theoryFactors)
###  # upscaledSpotAny["Blank"]["xTheory"] = np.multiply(brightSet["Blank"], theoryFactors)
###
###  upscaledSpotAny["Blank"]["xSpotDivBlank"] = np.multiply(brightSet["Blank"], divFactors["SpotDiv"]["Blank"])
###  upscaledSpotAny["Blank"]["xSpotDivClean"] = np.multiply(brightSet["Blank"], divFactors["SpotDiv"]["Clean"])
###
###  upscaledSpotAny["Blank"]["xMeanPxDivBlank"] = np.multiply(brightSet["Blank"], divFactors["MeanPxDiv"]["Blank"])
###  upscaledSpotAny["Blank"]["xMeanPxDivClean"] = np.multiply(brightSet["Blank"], divFactors["MeanPxDiv"]["Clean"])
###
###  upscaledSpotAny["Blank"]["xTheory/BlankArea"] = np.multiply(brightSet["Blank"], combiFactors["Theory"]["/BlankArea"])
###  upscaledSpotAny["Blank"]["xTheory/CleanArea"] = np.multiply(brightSet["Blank"], combiFactors["Theory"]["/CleanArea"])
###
###  upscaledSpotAny["Blank"]["xSpot_Mean(Blank,Clean)"]   = np.multiply(brightSet["Blank"], combiFactors["SpotDiv"]["Blank&Clean"]["Mean"])
###  upscaledSpotAny["Blank"]["xMeanPx_Mean(Blank,Clean)"] = np.multiply(brightSet["Blank"], combiFactors["MeanPxDiv"]["Blank&Clean"]["Mean"])
###
###
###  upscaledSpotAny["Clean"]["xTheory"] = np.multiply(brightSet["Clean"], theoryFactors)
###  # upscaledSpotAny["Clean"]["xTheory"] = np.multiply(brightSet["Clean"], theoryFactors)
###
###  upscaledSpotAny["Clean"]["xSpotDivBlank"] = np.multiply(brightSet["Clean"], divFactors["SpotDiv"]["Blank"])
###  upscaledSpotAny["Clean"]["xSpotDivClean"] = np.multiply(brightSet["Clean"], divFactors["SpotDiv"]["Clean"])
###
###  upscaledSpotAny["Clean"]["xMeanPxDivBlank"] = np.multiply(brightSet["Clean"], divFactors["MeanPxDiv"]["Blank"])
###  upscaledSpotAny["Clean"]["xMeanPxDivClean"] = np.multiply(brightSet["Clean"], divFactors["MeanPxDiv"]["Clean"])
###
###  upscaledSpotAny["Clean"]["xTheory/BlankArea"] = np.multiply(brightSet["Clean"], combiFactors["Theory"]["/BlankArea"])
###  upscaledSpotAny["Clean"]["xTheory/CleanArea"] = np.multiply(brightSet["Clean"], combiFactors["Theory"]["/CleanArea"])
###
###  upscaledSpotAny["Clean"]["xSpot_Mean(Blank,Clean)"]   = np.multiply(brightSet["Blank"], combiFactors["SpotDiv"]["Blank&Clean"]["Mean"])
###  upscaledSpotAny["Clean"]["xMeanPx_Mean(Blank,Clean)"] = np.multiply(brightSet["Blank"], combiFactors["MeanPxDiv"]["Blank&Clean"]["Mean"])
###
###
###  return upscaledSpotAny



###def __BrightUpscale_AnyPixlbrightSubSetEntry__(hiSSImg, loSSImg, factor, mask):
###
###  scaledPxlImg = np.multiply(loSSImg, factor, dtype=np.float32) # Try to save RAM by using half size Float   #, where=mask)
###  # scaledPxlImg[scaledPxlImg < 1] = 0.0
###  scaledLo = np.sum(scaledPxlImg)
###  scaledPxlImg[mask == False] = 0 # correct resolution errors from int -> float conversion
###
###  upscaledImg = np.add(hiSSImg, scaledPxlImg, dtype=np.float32)  #np.float64)
###  upscaledImg[upscaledImg < 1] = 0 # correct resolution errors from int -> float conversion
###  scaledOnOverexpose = np.sum(upscaledImg)
###
###  return scaledLo, scaledOnOverexpose, scaledPxlImg


###def __BrightUpscale_AnyPixlbrightSubSet__(hiSSImgSet, loSSImgSet, theoryFactors, divFactors, combiFactors):
###  upscaledAnyPxBright = dict()
###  # upscaledAnyPxBright = dict() # No Full-Upscale of loSS-Image saved -> But it's implemented. See "scldLo" variable below!
###  upscaledAnyPxBright["xTheory"]                    = list()
###  upscaledAnyPxBright["xSpotDivBlank"]              = list()
###  upscaledAnyPxBright["xSpotDivClean"]              = list()
###  upscaledAnyPxBright["xMeanPxDivBlank"]            = list()
###  upscaledAnyPxBright["xMeanPxDivClean"]            = list()
###  upscaledAnyPxBright["xTheory/BlankArea"]          = list()
###  upscaledAnyPxBright["xTheory/CleanArea"]          = list()
###  upscaledAnyPxBright["xSpot_Mean(Blank,Clean)"]    = list()
###  upscaledAnyPxBright["xMeanPx_Mean(Blank,Clean)"]  = list()
###
###  upscaledAnyPxlImgs = dict()
###  # upscaledAnyPxlImgs = dict()
###  upscaledAnyPxlImgs["xTheory"]                   = list()
###  upscaledAnyPxlImgs["xSpotDivBlank"]             = list()
###  upscaledAnyPxlImgs["xSpotDivClean"]             = list()
###  upscaledAnyPxlImgs["xMeanPxDivBlank"]           = list()
###  upscaledAnyPxlImgs["xMeanPxDivClean"]           = list()
###  upscaledAnyPxlImgs["xTheory/BlankArea"]         = list()
###  upscaledAnyPxlImgs["xTheory/CleanArea"]         = list()
###  upscaledAnyPxlImgs["xSpot_Mean(Blank,Clean)"]   = list()
###  upscaledAnyPxlImgs["xMeanPx_Mean(Blank,Clean)"] = list()
###
###  # dummy = list()
###  for _iImg in range(len(hiSSImgSet["Blank"])):
###    # Upscaling overexposed pixels!
###
###    #  * theory value (hiSS / loSS)
###    scldLo, scldOvrexpsd, scldImg = __BrightUpscale_AnyPixlbrightSubSetEntry__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], theoryFactors[_iImg], hiSSImgSet["OverexposedMask"][_iImg])
###    upscaledAnyPxBright["xTheory"].append(scldOvrexpsd)
###    upscaledAnyPxlImgs ["xTheory"].append(scldImg)
###
###    # Blank SpotDiv
###    scldLo, scldOvrexpsd, scldImg = __BrightUpscale_AnyPixlbrightSubSetEntry__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], divFactors["SpotDiv"]["Blank"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
###    upscaledAnyPxBright["xSpotDivBlank"].append(scldOvrexpsd)
###    upscaledAnyPxlImgs ["xSpotDivBlank"].append(scldImg)
###
###    # Cleaned SpotDiv
###    scldLo, scldOvrexpsd, scldImg = __BrightUpscale_AnyPixlbrightSubSetEntry__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], divFactors["SpotDiv"]["Clean"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
###    upscaledAnyPxBright["xSpotDivClean"].append(scldOvrexpsd)
###    upscaledAnyPxlImgs ["xSpotDivClean"].append(scldImg)
###
###    # Blank MeanPxDiv in trustband!
###    scldLo, scldOvrexpsd, scldImg = __BrightUpscale_AnyPixlbrightSubSetEntry__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], divFactors["MeanPxDiv"]["Blank"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
###    upscaledAnyPxBright["xMeanPxDivBlank"].append(scldOvrexpsd)
###    upscaledAnyPxlImgs ["xMeanPxDivBlank"].append(scldImg)
###
###    # Cleaned MeanPxDiv in trustband
###    scldLo, scldOvrexpsd, scldImg = __BrightUpscale_AnyPixlbrightSubSetEntry__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], divFactors["MeanPxDiv"]["Clean"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
###    upscaledAnyPxBright["xMeanPxDivClean"].append(scldOvrexpsd)
###    upscaledAnyPxlImgs ["xMeanPxDivClean"].append(scldImg)
###
###    # Theory / AreaDivBlank
###    scldLo, scldOvrexpsd, scldImg = __BrightUpscale_AnyPixlbrightSubSetEntry__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], combiFactors["Theory"]["/BlankArea"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
###    upscaledAnyPxBright["xTheory/BlankArea"].append(scldOvrexpsd)
###    upscaledAnyPxlImgs ["xTheory/BlankArea"].append(scldImg)
###
###    # Theory / AreaDivClean
###    scldLo, scldOvrexpsd, scldImg = __BrightUpscale_AnyPixlbrightSubSetEntry__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], combiFactors["Theory"]["/CleanArea"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
###    upscaledAnyPxBright["xTheory/CleanArea"].append(scldOvrexpsd)
###    upscaledAnyPxlImgs ["xTheory/CleanArea"].append(scldImg)
###
###    # Mean(SpotDivBlank, SpotDivClean)
###    scldLo, scldOvrexpsd, scldImg = __BrightUpscale_AnyPixlbrightSubSetEntry__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], combiFactors["SpotDiv"]["Blank&Clean"]["Mean"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
###    upscaledAnyPxBright["xSpot_Mean(Blank,Clean)"].append(scldOvrexpsd)
###    upscaledAnyPxlImgs ["xSpot_Mean(Blank,Clean)"].append(scldImg)
###
###    # Mean(MeanPxDivBlank, MeanPxDivClean)
###    scldLo, scldOvrexpsd, scldImg = __BrightUpscale_AnyPixlbrightSubSetEntry__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], combiFactors["MeanPxDiv"]["Blank&Clean"]["Mean"]
###    [_iImg], hiSSImgSet["OverexposedMask"][_iImg])
###    upscaledAnyPxBright["xMeanPx_Mean(Blank,Clean)"].append(scldOvrexpsd)
###    upscaledAnyPxlImgs ["xMeanPx_Mean(Blank,Clean)"].append(scldImg)
###
###  return upscaledAnyPxBright, upscaledAnyPxlImgs



###def __BrightUpscale_Any__(imgSets, brightSets, divFactorSets, combinedFactorSets):
###  upscaledBright = dict()
###  upscaledPxImgs = dict()
###  # upscaled["Full"] = __BrightUpscale_AnySubSet__()
###
###  _bKeys = list(brightSets.keys())
###  for _iBase in range(len(_bKeys)):
###    _bKey = _bKeys[_iBase]
###
###    upscaledBright[_bKey] = dict()
###    upscaledPxImgs[_bKey] = dict()
###
###    _dKeys = list(brightSets[_bKey]["Div"].keys())
###    for _iDiv in range(len(_dKeys)):
###      _dKey = _dKeys[_iDiv]
###
###      upscaledBright[_bKey][_dKey] = dict()
###      upscaledBright[_bKey][_dKey]["Full"] = dict()
###
###      upscaledPxImgs[_bKey][_dKey] = dict()
###      upscaledPxImgs[_bKey][_dKey]["Full"] = dict()
###
###      # Spotwise upscaling for full image
###      upscaledBright[_bKey][_dKey]["Full"]["SpotBright"] = __BrightUpscale_AnySpotbrightSubSet__(brightSets[_bKey]["Div"][_dKey]["Full"], divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Full"], combinedFactorSets[_bKey][_dKey]["Full"])
###
###      # Pxwise upscaling for full image
###      pxBright, pxImgs = __BrightUpscale_AnyPixlbrightSubSet__(imgSets[_bKey]["Full"], imgSets[_bKey]["Div"][_dKey]["Full"], divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Full"], combinedFactorSets[_bKey][_dKey]["Full"])
###      upscaledBright[_bKey][_dKey]["Full"]["PxlBright"] = pxBright
###      upscaledPxImgs[_bKey][_dKey]["Full"] = pxImgs
###
###      upscaledBright[_bKey][_dKey]["Spot"] = dict()
###      upscaledPxImgs[_bKey][_dKey]["Spot"] = dict()
###      _xyKeys = list(brightSets[_bKey]["Div"][_dKey]["Spot"].keys())
###      for _iXY in range(len(_xyKeys)):
###        _xyKey = _xyKeys[_iXY]
###
###        upscaledBright[_bKey][_dKey]["Spot"][_xyKey] = dict()
###        upscaledPxImgs[_bKey][_dKey]["Spot"][_xyKey] = dict()
###
###        # Spotwise upscaling for separate spots
###        upscaledBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"] = __BrightUpscale_AnySpotbrightSubSet__(brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey], divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Spot"][_xyKey], combinedFactorSets[_bKey][_dKey]["Spot"][_xyKey])
###
###        # Pxwise upscaling for separate spots
###        try:
###          pxBright, pxImgs = __BrightUpscale_AnyPixlbrightSubSet__(imgSets[_bKey]["Spot"][_xyKey], imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey], divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Spot"][_xyKey], combinedFactorSets[_bKey][_dKey]["Spot"][_xyKey])
###          upscaledBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"] = pxBright
###          upscaledPxImgs[_bKey][_dKey]["Spot"][_xyKey] = pxImgs
###        except Exception as e:
###          imgCnt = len(imgSets[_bKey]["Spot"][_xyKey]["Blank"])
###          imgShape = imgSets[_bKey]["Spot"][_xyKey]["Blank"][0].shape
###          upscaledBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"] = [0] * imgCnt
###          upscaledPxImgs[_bKey][_dKey]["Spot"][_xyKey] = [np.zeros(imgShape)] * imgCnt
###
###  return upscaledBright, upscaledPxImgs




###def __BrightUpscale_WhereOverexposedGenerateSubSetStructure__():
###  struct = dict()
###  struct["xTheory"]                   = list()
###  struct["xSpotDivBlank"]             = list()
###  struct["xSpotDivClean"]             = list()
###  struct["xMeanPxDivBlank"]           = list()
###  struct["xMeanPxDivClean"]           = list()
###  struct["xTheory/BlankArea"]         = list()
###  struct["xTheory/CleanArea"]         = list()
###  struct["xSpot_Mean(Blank,Clean)"]   = list()
###  struct["xMeanPx_Mean(Blank,Clean)"] = list()
###  return struct

###def __BrightUpscale_WhereOverexposedAppendBright2All__(bright, bValue):
###  bright["SpotBright"]["xTheory"]                  .append(bValue)
###  bright["SpotBright"]["xSpotDivBlank"]            .append(bValue)
###  bright["SpotBright"]["xSpotDivClean"]            .append(bValue)
###  bright["SpotBright"]["xMeanPxDivBlank"]          .append(bValue)
###  bright["SpotBright"]["xMeanPxDivClean"]          .append(bValue)
###  bright["SpotBright"]["xTheory/BlankArea"]        .append(bValue)
###  bright["SpotBright"]["xTheory/CleanArea"]        .append(bValue)
###  bright["SpotBright"]["xSpot_Mean(Blank,Clean)"]  .append(bValue)
###  bright["SpotBright"]["xMeanPx_Mean(Blank,Clean)"].append(bValue)
###
###  bright["PxlBright"]["xTheory"]                  .append(bValue)
###  bright["PxlBright"]["xSpotDivBlank"]            .append(bValue)
###  bright["PxlBright"]["xSpotDivClean"]            .append(bValue)
###  bright["PxlBright"]["xMeanPxDivBlank"]          .append(bValue)
###  bright["PxlBright"]["xMeanPxDivClean"]          .append(bValue)
###  bright["PxlBright"]["xTheory/BlankArea"]        .append(bValue)
###  bright["PxlBright"]["xTheory/CleanArea"]        .append(bValue)
###  bright["PxlBright"]["xSpot_Mean(Blank,Clean)"]  .append(bValue)
###  bright["PxlBright"]["xMeanPx_Mean(Blank,Clean)"].append(bValue)
###  return bright


###def __BrightUpscale_WhereOverexposedAppendPxImg2All__(pxImg, img):
###  pxImg["xTheory"]                  .append(img)
###  pxImg["xSpotDivBlank"]            .append(img)
###  pxImg["xSpotDivClean"]            .append(img)
###  pxImg["xMeanPxDivBlank"]          .append(img)
###  pxImg["xMeanPxDivClean"]          .append(img)
###  pxImg["xTheory/BlankArea"]        .append(img)
###  pxImg["xTheory/CleanArea"]        .append(img)
###  pxImg["xSpot_Mean(Blank,Clean)"]  .append(img)
###  pxImg["xMeanPx_Mean(Blank,Clean)"].append(img)
###  return pxImg


###def __BrightUpscale_WhereOverexposedAppendDataset__(bright2Append, pxImgs2Append, scaledAnyBright, scaledAnyPxImg, imgIndex):
###
###  bright2Append["SpotBright"]["xTheory"]                  .append(scaledAnyBright["SpotBright"]["Blank"]["xTheory"]                  [imgIndex])
###  bright2Append["SpotBright"]["xSpotDivBlank"]            .append(scaledAnyBright["SpotBright"]["Blank"]["xSpotDivBlank"]            [imgIndex])
###  bright2Append["SpotBright"]["xSpotDivClean"]            .append(scaledAnyBright["SpotBright"]["Blank"]["xSpotDivClean"]            [imgIndex])
###  bright2Append["SpotBright"]["xMeanPxDivBlank"]          .append(scaledAnyBright["SpotBright"]["Blank"]["xMeanPxDivBlank"]          [imgIndex])
###  bright2Append["SpotBright"]["xMeanPxDivClean"]          .append(scaledAnyBright["SpotBright"]["Blank"]["xMeanPxDivClean"]          [imgIndex])
###  bright2Append["SpotBright"]["xTheory/BlankArea"]        .append(scaledAnyBright["SpotBright"]["Blank"]["xTheory/BlankArea"]        [imgIndex])
###  bright2Append["SpotBright"]["xTheory/CleanArea"]        .append(scaledAnyBright["SpotBright"]["Blank"]["xTheory/CleanArea"]        [imgIndex])
###  bright2Append["SpotBright"]["xSpot_Mean(Blank,Clean)"]  .append(scaledAnyBright["SpotBright"]["Blank"]["xSpot_Mean(Blank,Clean)"]  [imgIndex])
###  bright2Append["SpotBright"]["xMeanPx_Mean(Blank,Clean)"].append(scaledAnyBright["SpotBright"]["Blank"]["xMeanPx_Mean(Blank,Clean)"][imgIndex])
###
###  bright2Append["PxlBright"]["xTheory"]                  .append(scaledAnyBright["PxlBright"]["xTheory"]                  [imgIndex])
###  bright2Append["PxlBright"]["xSpotDivBlank"]            .append(scaledAnyBright["PxlBright"]["xSpotDivBlank"]            [imgIndex])
###  bright2Append["PxlBright"]["xSpotDivClean"]            .append(scaledAnyBright["PxlBright"]["xSpotDivClean"]            [imgIndex])
###  bright2Append["PxlBright"]["xMeanPxDivBlank"]          .append(scaledAnyBright["PxlBright"]["xMeanPxDivBlank"]          [imgIndex])
###  bright2Append["PxlBright"]["xMeanPxDivClean"]          .append(scaledAnyBright["PxlBright"]["xMeanPxDivClean"]          [imgIndex])
###  bright2Append["PxlBright"]["xTheory/BlankArea"]        .append(scaledAnyBright["PxlBright"]["xTheory/BlankArea"]        [imgIndex])
###  bright2Append["PxlBright"]["xTheory/CleanArea"]        .append(scaledAnyBright["PxlBright"]["xTheory/CleanArea"]        [imgIndex])
###  bright2Append["PxlBright"]["xSpot_Mean(Blank,Clean)"]  .append(scaledAnyBright["PxlBright"]["xSpot_Mean(Blank,Clean)"]  [imgIndex])
###  bright2Append["PxlBright"]["xMeanPx_Mean(Blank,Clean)"].append(scaledAnyBright["PxlBright"]["xMeanPx_Mean(Blank,Clean)"][imgIndex])
###
###  pxImgs2Append["xTheory"]                  .append(scaledAnyPxImg["xTheory"]                  [imgIndex])
###  pxImgs2Append["xSpotDivBlank"]            .append(scaledAnyPxImg["xSpotDivBlank"]            [imgIndex])
###  pxImgs2Append["xSpotDivClean"]            .append(scaledAnyPxImg["xSpotDivClean"]            [imgIndex])
###  pxImgs2Append["xMeanPxDivBlank"]          .append(scaledAnyPxImg["xMeanPxDivBlank"]          [imgIndex])
###  pxImgs2Append["xMeanPxDivClean"]          .append(scaledAnyPxImg["xMeanPxDivClean"]          [imgIndex])
###  pxImgs2Append["xTheory/BlankArea"]        .append(scaledAnyPxImg["xTheory/BlankArea"]        [imgIndex])
###  pxImgs2Append["xTheory/CleanArea"]        .append(scaledAnyPxImg["xTheory/CleanArea"]        [imgIndex])
###  pxImgs2Append["xSpot_Mean(Blank,Clean)"]  .append(scaledAnyPxImg["xSpot_Mean(Blank,Clean)"]  [imgIndex])
###  pxImgs2Append["xMeanPx_Mean(Blank,Clean)"].append(scaledAnyPxImg["xMeanPx_Mean(Blank,Clean)"][imgIndex])
###  return bright2Append, pxImgs2Append


###def __BrightUpscale_WhereOverexposed__(imgSets, brightSets, scaledAnyBright, scaledAnyPxImgs):
###
###  # Prepare for full-data
###  bright = dict()
###  bright["Full"] = dict()
###  bright["Full"]["SpotBright"] = __BrightUpscale_WhereOverexposedGenerateSubSetStructure__()
###  bright["Full"]["PxlBright"] = __BrightUpscale_WhereOverexposedGenerateSubSetStructure__()
###  bright["Full"]["Overexposed"] = list()
###  bright["Full"]["BrightnessFromSS"] = list()
###
###  pxImgs = dict()
###  pxImgs["Full"] = __BrightUpscale_WhereOverexposedGenerateSubSetStructure__()
###
###  _bKeys = list(brightSets.keys())
###  _bKey = _bKeys[0] # To grab _xyKeys
###
###  # Prepare for spot-data
###  bright["Spot"] = dict()
###  pxImgs["Spot"] = dict()
###
###  _xyKeys = list(imgSets[_bKey]["Spot"].keys())
###  for _iXY in range(len(_xyKeys)):
###    _xyKey = _xyKeys[_iXY]
###
###    bright["Spot"][_xyKey] = dict()
###    bright["Spot"][_xyKey]["SpotBright"] = __BrightUpscale_WhereOverexposedGenerateSubSetStructure__()
###    bright["Spot"][_xyKey]["PxlBright"] = __BrightUpscale_WhereOverexposedGenerateSubSetStructure__()
###    bright["Spot"][_xyKey]["Overexposed"] = list()
###    bright["Spot"][_xyKey]["BrightnessFromSS"] = list()
###
###    # pxImgs["Spot"] = dict()
###    pxImgs["Spot"][_xyKey] = __BrightUpscale_WhereOverexposedGenerateSubSetStructure__()
###
###
###  for _iImg in range(len(imgSets[_bKey]["Full"]["Blank"])):
###
###    if imgSets[_bKey]["Full"]["OverexposedMask"][_iImg].max(): # Base-SS-Image has overexposed pixels
###
###      _dKeys = list(imgSets[_bKey]["Div"].keys())
###      for _iDiv in range(len(_dKeys)):
###        _dKey = _dKeys[_iDiv]
###        if imgSets[_bKey]["Div"][_dKey]["Full"]["OverexposedMask"][_iImg].max(): # Div-SS-Image also overexposed
###          continue                                                               #  -> Search in next div-SS
###
###        else: # Div-SS-Image not overexposed -> Add corresponding upscaled values to brightness-vectors
###          __BrightUpscale_WhereOverexposedAppendDataset__(bright2Append=bright["Full"], pxImgs2Append=pxImgs["Full"], scaledAnyBright=scaledAnyBright[_bKey][_dKey]["Full"], scaledAnyPxImg=scaledAnyPxImgs[_bKey][_dKey]["Full"], imgIndex=_iImg)
###          bright["Full"]["Overexposed"].append(False)
###          bright["Full"]["BrightnessFromSS"].append(_dKey)
###          break
###
###      else: # No unoverexposed (or no matching) Div-SS-Image has been found
###        __BrightUpscale_WhereOverexposedAppendBright2All__(bright=bright["Full"], bValue=0)
###        __BrightUpscale_WhereOverexposedAppendPxImg2All__(pxImg=pxImgs["Full"], img=imgSets[_bKey]["Full"]["Blank"][_iImg]) # Add original Image by default, but imply that:
###        bright["Full"]["Overexposed"].append(True)                                                                          #  by marking as overexposed
###        bright["Full"]["BrightnessFromSS"].append(-1)                                                                       #  and use -1 as "origin"-SS
###
###
###    else: # Base-SS-Image has no overexposed pixels
###      blankBright = brightSets[_bKey]["Full"]["Blank"][_iImg]
###      __BrightUpscale_WhereOverexposedAppendBright2All__(bright=bright["Full"], bValue=blankBright)
###      __BrightUpscale_WhereOverexposedAppendPxImg2All__(pxImg=pxImgs["Full"], img=imgSets[_bKey]["Full"]["Blank"][_iImg])
###
###      bright["Full"]["Overexposed"].append(False)
###      bright["Full"]["BrightnessFromSS"].append(_bKey)
###    
############################ ^--- Full ---^ #########################
###
############################ v--- Spot ---v #########################
###
###    for _iXY in range(len(_xyKeys)):
###      _xyKey = _xyKeys[_iXY]
###
###      if imgSets[_bKey]["Spot"][_xyKey]["OverexposedMask"][_iImg].max(): # Base-SS-Image has overexposed pixels
###        _dKeys = list(imgSets[_bKey]["Div"].keys())
###        for _iDiv in range(len(_dKeys)):
###          _dKey = _dKeys[_iDiv]
###          try: # to access the xy-key
###            imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey]
###          except: # When it fails, jump over SS an try the next one
###            continue
###
###          if imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey]["OverexposedMask"][_iImg].max(): # Div-SS-Image also overexposed
###            continue                                                               #  -> Search in next div-SS
###
###          else: # Div-SS-Image not overexposed -> Add corresponding upscaled values to brightness-vectors
###            __BrightUpscale_WhereOverexposedAppendDataset__(bright2Append=bright["Spot"][_xyKey], pxImgs2Append=pxImgs["Spot"][_xyKey], scaledAnyBright=scaledAnyBright[_bKey][_dKey]["Spot"][_xyKey], scaledAnyPxImg=scaledAnyPxImgs[_bKey][_dKey]["Spot"][_xyKey], imgIndex=_iImg)
###            bright["Spot"][_xyKey]["Overexposed"].append(False)
###            bright["Spot"][_xyKey]["BrightnessFromSS"].append(_dKey)
###            break
###
###      else: # Base-SS-Image has no overexposed pixels
###        blankBright = brightSets[_bKey]["Spot"][_xyKey]["Blank"][_iImg]
###        __BrightUpscale_WhereOverexposedAppendBright2All__(bright=bright["Spot"][_xyKey], bValue=blankBright)
###        __BrightUpscale_WhereOverexposedAppendPxImg2All__(pxImg=pxImgs["Spot"][_xyKey], img=imgSets[_bKey]["Spot"][_xyKey]["Blank"][_iImg])
###
###        bright["Spot"][_xyKey]["Overexposed"].append(False)
###        bright["Spot"][_xyKey]["BrightnessFromSS"].append(_bKey)
###    
###
###  return bright, pxImgs






###from math import isnan
###import cv2 as cv
###import numpy as np
###import matplotlib.pyplot as plt
###import pickle

from PMPLib.Factors_ImgSets import BuildFactorImgSets
from PMPLib.Factors_ImgData import GetBrightnessSets, GetPxCntSets
from PMPLib.Factors_DivideFactors import GetDivFactorSets
from PMPLib.Factors_CombinedFactors import CalcCombinedFactorSets
from PMPLib.Upscale_Any import UpscaleAny
from PMPLib.Upscale_Overexposed import UpscaleOverexposed

###from misc import bcolors


def DataExtractionAndUpscaling(ssData,
                               ImgKey="uint16",
                               pxSidelen = 12,
                               AddPxSidelen=False,
                               TakeSpotBrightFromAllImgs=True,
                               PxDivTrustband=24,
                               PxDivMinBright=150,
                               #AttachImages=False,
                               MinBright=256,
                               OverexposedValue = 255,
                               ShowImg=False):
  '''Reads out all brighntesses for image and circlearea of all detected spots/circles.
  The results get attached to the circle-structure

  Inputs:
  ----------
  ImgCollection: List of images where the circle-brightness should be readout
  SpotCollection: List of circles detected on each image
  pxTolerance: Tolerance-width and height in [px] (symmetric around circle-center)
  AddPxRadius: False: pxTolerance is fix; True: pxTolerance is added to the circle-radius!

  Returns:
  ----------
  SpotsCollection: (same spot-dict as from input)
  '''

  if pxSidelen == 0:
    print("AttachBrightnessData: pxTolerance must be > 0!")

  halfTol = pxSidelen / 2
  if halfTol % 1 != 0:
    print(str.format("Half tolerance is not integer! Asymetric brightness-detection by 1 pixel", int(halfTol)))

  # imgSets                                                  = __BrightnessFactors_BuildImageSets___(ssData=ssData, ImgKey=ImgKey, pxSidelen=pxSidelen, AddPxSidelen=AddPxSidelen, OverexposedValue=OverexposedValue)
  # brightSets                                               = __BrightnessFactors_GetBrightSets__(imgSets)
  # areaCntSets                                              = __BrightnessFactors_GetPxAreaCnt__(imgSets)
  # divFactors                                               = __BrightnessFactors_BuildDivFactors__(imgSets, brightSets, areaCntSets, PxDivTrustband, PxDivMinBright)
  # combinedFactors                                          = __BrightnessFactors_BuildCombinedFactors__(divFactors)
  # scaledAnyBright, scaledAnyPxImgs                         = __BrightUpscale_Any__(imgSets, brightSets, divFactors, combinedFactors)
  # scaledWhereOverexposedBright, scaledWhereOverexposedImgs = __BrightUpscale_WhereOverexposed__(imgSets, brightSets, scaledAnyBright, scaledAnyPxImgs)


  imgSets                                                  = BuildFactorImgSets(ssData=ssData, ImgKey=ImgKey, pxSidelen=pxSidelen, AddPxSidelen=AddPxSidelen, OverexposedValue=OverexposedValue, TakeSpotBrightFromAllImgs=TakeSpotBrightFromAllImgs)
  brightSets                                               = GetBrightnessSets(imgSets)
  areaCntSets                                              = GetPxCntSets(imgSets, minBright=MinBright)
  divFactors                                               = GetDivFactorSets(imgSets, brightSets, areaCntSets, PxDivTrustband, PxDivMinBright)
  combinedFactors                                          = CalcCombinedFactorSets(divFactors)
  scaledAnyBright, scaledAnyPxImgs                         = UpscaleAny(imgSets, brightSets, divFactors, combinedFactors)
  scaledWhereOverexposedBright, scaledWhereOverexposedImgs = UpscaleOverexposed(imgSets, brightSets, scaledAnyBright, scaledAnyPxImgs)

  return ssData, imgSets, brightSets, areaCntSets, divFactors, combinedFactors, scaledAnyBright, scaledAnyPxImgs, scaledWhereOverexposedBright, scaledWhereOverexposedImgs #, bData#, bImages
