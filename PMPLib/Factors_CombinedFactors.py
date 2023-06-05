from math import isnan
import numpy as np
import cv2 as cv








def __CalcCombinedFactorSubSet__(divFactorSet):
  """Obsolet function: Subfunction to build up the combinated factors

  Args:
      divFactorSet (_type_): _description_

  Returns:
      _type_: _description_
  """
  subSet = dict()

  subSet["SpotDiv"] = dict()
  subSet["SpotDiv"]["Blank"] = dict()
  subSet["SpotDiv"]["Clean"] = dict()
  subSet["SpotDiv"]["Blank&Clean"] = dict()
  subSet["SpotDiv"]["Blank"]["xAreaBlank"]       = np.multiply(divFactorSet["SpotDiv"]["Blank"], divFactorSet["PxAreaDiv"]["Blank"])
  subSet["SpotDiv"]["Blank"]["xAreaClean"]       = np.multiply(divFactorSet["SpotDiv"]["Blank"], divFactorSet["PxAreaDiv"]["Clean"])
  subSet["SpotDiv"]["Clean"]["xAreaBlank"]       = np.multiply(divFactorSet["SpotDiv"]["Clean"], divFactorSet["PxAreaDiv"]["Blank"])
  subSet["SpotDiv"]["Clean"]["xAreaClean"]       = np.multiply(divFactorSet["SpotDiv"]["Clean"], divFactorSet["PxAreaDiv"]["Clean"])
  subSet["SpotDiv"]["Blank&Clean"]["Mean"]       = np.mean([divFactorSet["SpotDiv"]["Blank"], divFactorSet["SpotDiv"]["Clean"]], axis=0)
  subSet["SpotDiv"]["Blank&Clean"]["xAreaBlank"] = np.multiply(subSet["SpotDiv"]["Blank&Clean"]["Mean"], divFactorSet["PxAreaDiv"]["Blank"])
  subSet["SpotDiv"]["Blank&Clean"]["xAreaClean"] = np.multiply(subSet["SpotDiv"]["Blank&Clean"]["Mean"], divFactorSet["PxAreaDiv"]["Clean"])
  

  subSet["MeanPxDiv"] = dict()
  subSet["MeanPxDiv"]["Blank"] = dict()
  subSet["MeanPxDiv"]["Clean"] = dict()
  subSet["MeanPxDiv"]["Blank&Clean"] = dict()
  subSet["MeanPxDiv"]["Blank"]["xAreaBlank"]       = np.multiply(divFactorSet["MeanPxDiv"]["Blank"], divFactorSet["PxAreaDiv"]["Blank"])
  subSet["MeanPxDiv"]["Blank"]["xAreaClean"]       = np.multiply(divFactorSet["MeanPxDiv"]["Blank"], divFactorSet["PxAreaDiv"]["Clean"])
  subSet["MeanPxDiv"]["Clean"]["xAreaBlank"]       = np.multiply(divFactorSet["MeanPxDiv"]["Clean"], divFactorSet["PxAreaDiv"]["Blank"])
  subSet["MeanPxDiv"]["Clean"]["xAreaClean"]       = np.multiply(divFactorSet["MeanPxDiv"]["Clean"], divFactorSet["PxAreaDiv"]["Clean"])
  subSet["MeanPxDiv"]["Blank&Clean"]["Mean"]       = np.mean([divFactorSet["MeanPxDiv"]["Blank"], divFactorSet["MeanPxDiv"]["Clean"]], axis=0)
  subSet["MeanPxDiv"]["Blank&Clean"]["xAreaBlank"] = np.multiply(subSet["MeanPxDiv"]["Blank&Clean"]["Mean"], divFactorSet["PxAreaDiv"]["Blank"])
  subSet["MeanPxDiv"]["Blank&Clean"]["xAreaClean"] = np.multiply(subSet["MeanPxDiv"]["Blank&Clean"]["Mean"], divFactorSet["PxAreaDiv"]["Clean"])

  return subSet














def CalcCombinedFactorSets(divFactorSets):
  """Obsolet function: which builded different combinations of upscale factors during the beginnings of the measurement-method (try-outs to develop some feeling for the matter)

  Args:
      divFactorSets (_type_): _description_

  Returns:
      _type_: _description_
  """
  cmbFactors = dict()

  # _bKeys = list(divFactorSets.keys())
  # for _iBase in range(len(_bKeys)):
  #   _bKey = _bKeys[_iBase]

  #   cmbFactors[_bKey] = dict()

  #   _dKeys = list(divFactorSets[_bKey].keys())
  #   for _iDiv in range(len(_dKeys)):
  #     _dKey = _dKeys[_iDiv]

  #     cmbFactors[_bKey][_dKey] = dict()
  #     cmbFactors[_bKey][_dKey]["Full"] = __CalcCombinedFactorSubSet__(divFactorSets[_bKey][_dKey]["Full"])
  #     cmbFactors[_bKey][_dKey]["Full"]["Theory"] = dict()
  #     cmbFactors[_bKey][_dKey]["Full"]["Theory"]["/BlankArea"] = np.divide(divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Full"]["PxAreaDiv"]["Blank"])
  #     np.nan_to_num(cmbFactors[_bKey][_dKey]["Full"]["Theory"]["/BlankArea"], copy=False, nan=0, posinf=0, neginf=0)
  #     cmbFactors[_bKey][_dKey]["Full"]["Theory"]["/CleanArea"] = np.divide(divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Full"]["PxAreaDiv"]["Clean"])
  #     np.nan_to_num(cmbFactors[_bKey][_dKey]["Full"]["Theory"]["/CleanArea"], copy=False, nan=0, posinf=0, neginf=0)


  #     cmbFactors[_bKey][_dKey]["Spot"] = dict()
  #     _xyKeys = list(divFactorSets[_bKey][_dKey]["Spot"].keys())
  #     for _iXY in range(len(_xyKeys)):
  #       _xyKey = _xyKeys[_iXY]

  #       cmbFactors[_bKey][_dKey]["Spot"][_xyKey] = __CalcCombinedFactorSubSet__(divFactorSets[_bKey][_dKey]["Spot"][_xyKey])
  #       cmbFactors[_bKey][_dKey]["Spot"][_xyKey]["Theory"] = dict()
  #       cmbFactors[_bKey][_dKey]["Spot"][_xyKey]["Theory"]["/BlankArea"] = np.divide(divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"]["Blank"])
  #       np.nan_to_num(cmbFactors[_bKey][_dKey]["Spot"][_xyKey]["Theory"]["/BlankArea"], copy=False, nan=0, posinf=0, neginf=0)
  #       cmbFactors[_bKey][_dKey]["Spot"][_xyKey]["Theory"]["/CleanArea"] = np.divide(divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Spot"][_xyKey]["PxAreaDiv"]["Clean"])
  #       np.nan_to_num(cmbFactors[_bKey][_dKey]["Spot"][_xyKey]["Theory"]["/CleanArea"], copy=False, nan=0, posinf=0, neginf=0)


  return cmbFactors









