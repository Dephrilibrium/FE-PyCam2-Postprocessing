from math import isnan
import numpy as np
import cv2 as cv

















def __CalcSpotDivFactorSubSet__(bVec, dVec):
  subSet = dict()
  subSet["Blank"] = np.divide(bVec["Blank"], dVec["Blank"])
  subSet["Clean"] = np.divide(bVec["Clean"], dVec["Clean"])
  np.nan_to_num(subSet["Blank"], copy=False, nan=0, posinf=0, neginf=0)
  np.nan_to_num(subSet["Clean"], copy=False, nan=0, posinf=0, neginf=0)
  return subSet












def __CalcPxDivFactor__(bImg, dImg, trustband, loMinBright):

  if bImg.dtype.name == "uint8":
    _bMaxBright = 0xFF
  elif bImg.dtype.name == "uint16":
    _bMaxBright = 0xFFFF
  else:
    _bMaxBright = 0xFFFFFFFF
  _bMinBright = 0

  lower = trustband[0]
  if lower < _bMinBright:
    lower = _bMinBright

  upper = trustband[1]
  if upper > _bMaxBright:
    upper = _bMaxBright

  if lower > upper:
    raise Exception("lower trusted brightness > higher trusted brightness")

  # Remove non-trusted pixels
  trustMask = (bImg < lower) | (bImg > upper)
  minLoMask = dImg < loMinBright
  bImg = bImg.copy()
  # dImg = dImg.copy() # Not neccessary to manipulate divider-image -> Save RAM
  bImg[trustMask] = 0
  bImg[minLoMask] = 0
  # dImg[mask] = 0

  divImg = np.divide(bImg, dImg)
  np.nan_to_num(divImg, copy=False, nan=np.nan, posinf=np.nan, neginf=np.nan)
  meanDiv = np.nanmean(divImg)
  if isnan(meanDiv):
    meanDiv = 0
  np.nan_to_num(divImg, copy=False, nan=0, posinf=0, neginf=0)
  return meanDiv, divImg









def __CalcPxDivFactorSubSet__(bImgs, dImgs, trustband, loMinBright):
  subSet = dict()
  subSet["Blank"] = list()
  subSet["Clean"] = list()

  for _iImg in range(len(bImgs["Blank"])):
    meanDiv, divImg = __CalcPxDivFactor__(bImgs["Blank"][_iImg], dImgs["Blank"][_iImg], trustband, loMinBright)
    subSet["Blank"].append(meanDiv)
    meanDiv, divImg = __CalcPxDivFactor__(bImgs["Clean"][_iImg], dImgs["Clean"][_iImg], trustband, loMinBright)
    subSet["Clean"].append(meanDiv)

  np.nan_to_num(subSet["Blank"], copy=False, nan=0, posinf=0, neginf=0)
  np.nan_to_num(subSet["Clean"], copy=False, nan=0, posinf=0, neginf=0)
  return subSet

def __BrightnessFactors_BuildPxAreaCntDivFactorSubSet__(bAreaCntSet, dAreaCntSet):
  subSet = dict()
  subSet["Blank"] = np.divide(bAreaCntSet["Blank"], dAreaCntSet["Blank"])
  subSet["Clean"] = np.divide(bAreaCntSet["Clean"], dAreaCntSet["Clean"])

  np.nan_to_num(subSet["Blank"], copy=False, nan=0, posinf=0, neginf=0)
  np.nan_to_num(subSet["Clean"], copy=False, nan=0, posinf=0, neginf=0)
  return subSet











def GetDivFactorSets(imgSets): #, brightSets, pxAreaCntSets, PxDivTrustband, PxDivMinBright):
  factors = dict()

  _bKeys = list(imgSets.keys())
  for _iBase in range(len(_bKeys)):
    _bKey = _bKeys[_iBase]

    factors[_bKey] = dict()

    _dKeys = list(imgSets[_bKey]["Div"].keys())
    for _iDiv in range(len(_dKeys)):
      _dKey = _dKeys[_iDiv]

      factors[_bKey][_dKey] = dict()
      factors[_bKey][_dKey]["Theory"] = [_bKey / _dKey] * len(imgSets[_bKey]["Full"]["Blank"])
      # factors[_bKey][_dKey]["Full"] = dict()
      # factors[_bKey][_dKey]["Spot"] = dict()


      # factors[_bKey][_dKey]["Full"]["SpotDiv"] = __CalcSpotDivFactorSubSet__(brightSets[_bKey]["Full"], brightSets[_bKey]["Div"][_dKey]["Full"])
      # # factors[_bKey][_dKey]["Spot"]["SpotDiv"] = dict()

      # factors[_bKey][_dKey]["Full"]["MeanPxDiv"] = __CalcPxDivFactorSubSet__(imgSets[_bKey]["Full"], imgSets[_bKey]["Div"][_dKey]["Full"], PxDivTrustband, PxDivMinBright)
      # # factors[_bKey][_dKey]["Spot"]["MeanPxDiv"] = dict()

      # factors[_bKey][_dKey]["Full"]["PxAreaDiv"] = __BrightnessFactors_BuildPxAreaCntDivFactorSubSet__(pxAreaCntSets[_bKey]["Full"], pxAreaCntSets[_bKey]["Div"][_dKey]["Full"])
      # # factors[_bKey][_dKey]["Spot"]["PxAreaDiv"] = dict()

      # _xyKeys = list(imgSets[_bKey]["Spot"].keys())
      # for _iXY in range(len(_xyKeys)):
      #   _xyKey = _xyKeys[_iXY]

      #   factors[_bKey][_dKey]["Spot"][_xyKey] = dict()
      #   factors[_bKey][_dKey]["Spot"][_xyKey]["SpotDiv"] = __CalcSpotDivFactorSubSet__(brightSets[_bKey]["Spot"][_xyKey], brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey])
      #   try:
      #     factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"] = __CalcPxDivFactorSubSet__(imgSets[_bKey]["Spot"][_xyKey], imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey], PxDivTrustband, PxDivMinBright)
      #   except Exception as e:
      #     factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"] = dict()
      #     factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Blank"] = np.zeros(len(imgSets[_bKey]["Full"]["Blank"]))
      #     factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Clean"] = factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Blank"] # Because all 0 -> Reuse!

      #   try:
      #     factors[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"] = __BrightnessFactors_BuildPxAreaCntDivFactorSubSet__(pxAreaCntSets[_bKey]["Spot"][_xyKey], pxAreaCntSets[_bKey]["Div"][_dKey]["Spot"][_xyKey])
      #   except Exception as e:
      #     factors[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"] = dict()
      #     factors[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"]["Blank"] = np.zeros(len(imgSets[_bKey]["Full"]["Blank"]))
      #     factors[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"]["Clean"] = factors[_bKey][_dKey]["Spot"][_xyKey]["MeanPxDiv"]["Blank"] # Because all 0 -> Reuse!

  return factors