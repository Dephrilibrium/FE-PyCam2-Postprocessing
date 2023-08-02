import numpy as np
import cv2 as cv
















def __BrightnessOfImgCollection__(ImgCollection):
  """Iterates through the incomming ImgCollection, sums up each pixel-value as total brightness and returns them as a NDArray-vector.

  Args:
      ImgCollection (iterable, image): Image-collection for which the brightnesses should be determined.

  Returns:
      NDArray: NDArray-vector containing the images total brightness
  """
  return np.array([np.sum(img) for img in ImgCollection])











def __BuildBrightSubSet__(ImgSet):
  """Determines the brightenssvector for the incomming ImgSet for Blank (images containing overexposure) and Clean (overexposure removed).

  Args:
      ImgSet (dict, iterable, image): Dictionary with iterable images-vectors with "Blank" and "Clean" keys

  Returns:
      dict: Dictionary with "Blank" and "Clean" keys, containing the brightness-vectors.
  """
  subSet = dict()

  subSet["Blank"] = __BrightnessOfImgCollection__(ImgSet["Blank"])
  # subSet["Clean"] = __BrightnessOfImgCollection__(ImgSet["Clean"])

  return subSet









def GetBrightnessSets(imgSets):
  """Builds the brightness-vectors for an entire set of images

  Args:
      imgSets (dict, iterable, image): Dictionary of iterable image-vectors.

  Returns:
      dict, iterable, int: Dictionary containing the images brightnesses.
  """
  brightSets = dict()

  _bKeys = list(imgSets.keys())
  _nbKeys = len(_bKeys)
  for _iBase in range(_nbKeys):
    _bKey = _bKeys[_iBase]

    brightSets[_bKey] = dict()
    brightSets[_bKey]["Full"] = __BuildBrightSubSet__(imgSets[_bKey]["Full"])
    brightSets[_bKey]["Spot"] = dict()  # Empty dict for "correct" order
    brightSets[_bKey]["Div"] = dict()

    _xyKeys = list(imgSets[_bKey]["Spot"].keys())
    for _iXY in range(len(_xyKeys)):
      _xyKey = _xyKeys[_iXY]
      brightSets[_bKey]["Spot"][_xyKey] = __BuildBrightSubSet__(imgSets[_bKey]["Spot"][_xyKey])


    _dKeys = list(imgSets[_bKey]["Div"].keys())
    _ndKeys = len(_dKeys)
    for _iDiv in range(_ndKeys):
      _dKey = _dKeys[_iDiv]

      brightSets[_bKey]["Div"][_dKey] = dict()
      brightSets[_bKey]["Div"][_dKey]["Full"] = __BuildBrightSubSet__(imgSets[_bKey]["Div"][_dKey]["Full"])
      brightSets[_bKey]["Div"][_dKey]["Spot"] = dict()

      # _xyKeys = list(imgSets[_bKey]["Spot"].keys()) # Already got a bit above!
      for _iXY in range(len(_xyKeys)):
        # _xyKey = _xyKeys[_iXY]
        # brightSets[_bKey]["Spot"][_xyKey] = __BuildBrightSubSet__(imgSets[_bKey]["Spot"][_xyKey])

        try:
          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey] = __BuildBrightSubSet__(imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey])
        except Exception as e:
          imgCnt = len(imgSets[_bKey]["Full"]["Blank"])

          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey] = dict()
          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Blank"] = np.zeros(imgCnt)
          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Clean"] = np.zeros(imgCnt)



  return brightSets









def __GetPxCntOfImgCollection__(ImgCollection, minVal:int):
  """Extracts the amount of contributing pixels (pixel-value > minVal).

  Args:
      ImgCollection (iterable, image): Iterable object containing images.
      minVal (int): Minimum pixelvalue to be counted as contributing pixel.

  Returns:
      NDArray: Vector containing the count of the contributing pixels.
  """
  return [len(np.where(img >= minVal)[0]) for img in ImgCollection]








def __BuildPxCntSubSet__(ImgSet, minVal:int):
  """Builds a subset of the incoming ImgSet for "Blank" and "Clean" Key.

  Args:
      ImgSet (dict, iterable, image): Dictionary containing iterable image-vectors. Keys needed "Blank" and "Clean"
      minVal (int): Minimum pixelvalue to be counted as contributing pixel

  Returns:
      dict, NDArray: Dictionary with the contributing pixel-count for keys "Blank" and "Clean".
  """
  subSet = dict()

  subSet["Blank"] = np.array(__GetPxCntOfImgCollection__(ImgSet["Blank"], minVal=minVal))
  # subSet["Clean"] = np.array(__GetPxCntOfImgCollection__(ImgSet["Clean"], minVal=minVal))
  # subSet["Blank-Clean"] = np.subtract(subSet["Blank"], subSet["Clean"]) # How much pixels are purged in clean-img

  return subSet













def GetPxCntSets(imgSets, minBright:int):
  """Extracts the count of contributing pixels for a full image-set.

  Args:
      ImgSet (dict, iterable, image): Dictionary containing iterable image-vectors. Keys needed "Blank" and "Clean"
      minBright (int): Minimum pixelvalue to be counted as contributing pixel.

  Returns:
      dict, dict, NDArray: Count of contributing pixels for all SS ("Blank" & "Clean" keys).
  """
  pxAreas = dict()

  _bKeys = list(imgSets.keys())
  _nbKeys = len(_bKeys)
  for _iBase in range(_nbKeys):
    _bKey = _bKeys[_iBase]

    pxAreas[_bKey] = dict()
    pxAreas[_bKey]["Full"] = __BuildPxCntSubSet__(imgSets[_bKey]["Full"], minVal=minBright)
    pxAreas[_bKey]["Spot"] = dict()  # Empty dict for "correct" order
    pxAreas[_bKey]["Div"] = dict()

    _xyKeys = list(imgSets[_bKey]["Spot"].keys())
    for _iXY in range(len(_xyKeys)):
      _xyKey = _xyKeys[_iXY]
      pxAreas[_bKey]["Spot"][_xyKey] = __BuildPxCntSubSet__(imgSets[_bKey]["Spot"][_xyKey], minVal=minBright)



    _dKeys = list(imgSets[_bKey]["Div"].keys())
    _ndKeys = len(_dKeys)
    for _iDiv in range(_ndKeys):
      _dKey = _dKeys[_iDiv]

      pxAreas[_bKey]["Div"][_dKey] = dict()
      pxAreas[_bKey]["Div"][_dKey]["Full"] = __BuildPxCntSubSet__(imgSets[_bKey]["Div"][_dKey]["Full"], minVal=minBright)
      pxAreas[_bKey]["Div"][_dKey]["Spot"] = dict()

      # _xyKeys = list(imgSets[_bKey]["Spot"].keys()) # Got already a bit above
      for _iXY in range(len(_xyKeys)):
        _xyKey = _xyKeys[_iXY]

        # pxAreas[_bKey]["Spot"][_xyKey] = __BuildPxCntSubSet__(imgSets[_bKey]["Spot"][_xyKey], minVal=minBright)

        try:
          pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey] = __BuildPxCntSubSet__(imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey], minVal=minBright)
        except Exception as e:
          imgCnt = len(imgSets[_bKey]["Full"]["Blank"])

          pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey] = dict()
          pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Blank"] = np.zeros(imgCnt)
          # pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Clean"] = np.zeros(imgCnt)

  return pxAreas
