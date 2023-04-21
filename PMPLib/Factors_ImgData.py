import numpy as np
import cv2 as cv
















def __BrightnessOfImgCollection__(ImgCollection):
  return np.array([np.sum(img) for img in ImgCollection])











def __BuildBrightSubSet__(ImgSet):
  subSet = dict()

  subSet["Blank"] = __BrightnessOfImgCollection__(ImgSet["Blank"])
  subSet["Clean"] = __BrightnessOfImgCollection__(ImgSet["Clean"])

  return subSet









def GetBrightnessSets(imgSets):
  brightSets = dict()

  _bKeys = list(imgSets.keys())
  for _iBase in range(len(_bKeys)):
    _bKey = _bKeys[_iBase]

    brightSets[_bKey] = dict()
    brightSets[_bKey]["Full"] = __BuildBrightSubSet__(imgSets[_bKey]["Full"])
    brightSets[_bKey]["Spot"] = dict()  # Empty dict for "correct" order
    brightSets[_bKey]["Div"] = dict()


    _dKeys = list(imgSets[_bKey]["Div"].keys())
    for _iDiv in range(len(_dKeys)):
      _dKey = _dKeys[_iDiv]

      brightSets[_bKey]["Div"][_dKey] = dict()
      brightSets[_bKey]["Div"][_dKey]["Full"] = __BuildBrightSubSet__(imgSets[_bKey]["Div"][_dKey]["Full"])
      brightSets[_bKey]["Div"][_dKey]["Spot"] = dict()

      _xyKeys = list(imgSets[_bKey]["Spot"].keys())
      for _iXY in range(len(_xyKeys)):
        _xyKey = _xyKeys[_iXY]
        brightSets[_bKey]["Spot"][_xyKey] = __BuildBrightSubSet__(imgSets[_bKey]["Spot"][_xyKey])

        try:
          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey] = __BuildBrightSubSet__(imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey])
        except Exception as e:
          imgCnt = len(imgSets[_bKey]["Full"]["Blank"])

          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey] = dict()
          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Blank"] = np.zeros(imgCnt)
          brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Clean"] = np.zeros(imgCnt)



  return brightSets









def __GetPxCntOfImgCollection__(ImgCollection, minVal:int):
  # return [cv.countNonZero(img) for img in ImgCollection]
  return [len(np.where(img >= minVal)[0]) for img in ImgCollection]








def __BuildPxCntSubSet__(ImgSet, minVal:int):
  subSet = dict()

  subSet["Blank"] = np.array(__GetPxCntOfImgCollection__(ImgSet["Blank"], minVal=minVal))
  subSet["Clean"] = np.array(__GetPxCntOfImgCollection__(ImgSet["Clean"], minVal=minVal))
  subSet["Blank-Clean"] = np.subtract(subSet["Blank"], subSet["Clean"]) # How much pixels are purged in clean-img

  return subSet













def GetPxCntSets(imgSets, minBright:int):
  pxAreas = dict()

  _bKeys = list(imgSets.keys())
  for _iBase in range(len(_bKeys)):
    _bKey = _bKeys[_iBase]

    pxAreas[_bKey] = dict()
    pxAreas[_bKey]["Full"] = __BuildPxCntSubSet__(imgSets[_bKey]["Full"], minVal=minBright)
    pxAreas[_bKey]["Spot"] = dict()  # Empty dict for "correct" order
    pxAreas[_bKey]["Div"] = dict()


    _dKeys = list(imgSets[_bKey]["Div"].keys())
    for _iDiv in range(len(_dKeys)):
      _dKey = _dKeys[_iDiv]

      pxAreas[_bKey]["Div"][_dKey] = dict()
      pxAreas[_bKey]["Div"][_dKey]["Full"] = __BuildPxCntSubSet__(imgSets[_bKey]["Div"][_dKey]["Full"], minVal=minBright)
      pxAreas[_bKey]["Div"][_dKey]["Spot"] = dict()

      _xyKeys = list(imgSets[_bKey]["Spot"].keys())
      for _iXY in range(len(_xyKeys)):
        _xyKey = _xyKeys[_iXY]

        pxAreas[_bKey]["Spot"][_xyKey] = __BuildPxCntSubSet__(imgSets[_bKey]["Spot"][_xyKey], minVal=minBright)
        try:
          pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey] = __BuildPxCntSubSet__(imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey], minVal=minBright)
        except Exception as e:
          imgCnt = len(imgSets[_bKey]["Full"]["Blank"])

          pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey] = dict()
          pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Blank"] = np.zeros(imgCnt)
          pxAreas[_bKey]["Div"][_dKey]["Spot"][_xyKey]["Clean"] = np.zeros(imgCnt)

  return pxAreas
