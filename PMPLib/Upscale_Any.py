# from math import isnan
import numpy as np
# import cv2 as cv










def __UpscaleAnySpot__(brightSet, theoryFactors): #, divFactors, combiFactors):
  """Subroutine to upscale any detected spotbrightness, ignoring if it contains overexposed pixels.

  Args:
      brightSet (_type_): Set of all extracted brightness-vectors.
      divFactors (_type_): Set of division
      combiFactors (_type_): _description_

  Returns:
      dict: Dictionary containing all upscaled spot brightnesses.
  """
  upscaledSpotAny = dict()

  upscaledSpotAny = dict()
  upscaledSpotAny["Blank"] = dict()
  upscaledSpotAny["Clean"] = dict()

  upscaledSpotAny["Blank"]["xTheory"] = np.multiply(brightSet["Blank"], theoryFactors)

  # upscaledSpotAny["Blank"]["xTheory"] = np.multiply(brightSet["Blank"], theoryFactors)

  # upscaledSpotAny["Blank"]["xSpotDivBlank"] = np.multiply(brightSet["Blank"], divFactors["SpotDiv"]["Blank"])
  # upscaledSpotAny["Blank"]["xSpotDivClean"] = np.multiply(brightSet["Blank"], divFactors["SpotDiv"]["Clean"])

  # upscaledSpotAny["Blank"]["xMeanPxDivBlank"] = np.multiply(brightSet["Blank"], divFactors["MeanPxDiv"]["Blank"])
  # upscaledSpotAny["Blank"]["xMeanPxDivClean"] = np.multiply(brightSet["Blank"], divFactors["MeanPxDiv"]["Clean"])

  # upscaledSpotAny["Blank"]["xTheory/BlankArea"] = np.multiply(brightSet["Blank"], combiFactors["Theory"]["/BlankArea"])
  # upscaledSpotAny["Blank"]["xTheory/CleanArea"] = np.multiply(brightSet["Blank"], combiFactors["Theory"]["/CleanArea"])

  # upscaledSpotAny["Blank"]["xSpot_Mean(Blank,Clean)"]   = np.multiply(brightSet["Blank"], combiFactors["SpotDiv"]["Blank&Clean"]["Mean"])
  # upscaledSpotAny["Blank"]["xMeanPx_Mean(Blank,Clean)"] = np.multiply(brightSet["Blank"], combiFactors["MeanPxDiv"]["Blank&Clean"]["Mean"])


  upscaledSpotAny["Clean"]["xTheory"] = np.multiply(brightSet["Clean"], theoryFactors)
  # upscaledSpotAny["Clean"]["xTheory"] = np.multiply(brightSet["Clean"], theoryFactors)

  # upscaledSpotAny["Clean"]["xSpotDivBlank"] = np.multiply(brightSet["Clean"], divFactors["SpotDiv"]["Blank"])
  # upscaledSpotAny["Clean"]["xSpotDivClean"] = np.multiply(brightSet["Clean"], divFactors["SpotDiv"]["Clean"])

  # upscaledSpotAny["Clean"]["xMeanPxDivBlank"] = np.multiply(brightSet["Clean"], divFactors["MeanPxDiv"]["Blank"])
  # upscaledSpotAny["Clean"]["xMeanPxDivClean"] = np.multiply(brightSet["Clean"], divFactors["MeanPxDiv"]["Clean"])

  # upscaledSpotAny["Clean"]["xTheory/BlankArea"] = np.multiply(brightSet["Clean"], combiFactors["Theory"]["/BlankArea"])
  # upscaledSpotAny["Clean"]["xTheory/CleanArea"] = np.multiply(brightSet["Clean"], combiFactors["Theory"]["/CleanArea"])

  # upscaledSpotAny["Clean"]["xSpot_Mean(Blank,Clean)"]   = np.multiply(brightSet["Blank"], combiFactors["SpotDiv"]["Blank&Clean"]["Mean"])
  # upscaledSpotAny["Clean"]["xMeanPx_Mean(Blank,Clean)"] = np.multiply(brightSet["Blank"], combiFactors["MeanPxDiv"]["Blank&Clean"]["Mean"])

  return upscaledSpotAny








def __CalculateUpscaleAnyPxImg__(hiSSImg, loSSImg, factor:float, mask):
  """Subroutine to upscale any pixel-values, ignoring if it contains overexposed pixels. The mask is a 2d-boolean mask, containing overexposed pixels (mask to clear overexposed loSSImg-pixels, in which the unoverexposed hiSSImg pixels are inserted).

  Args:
      hiSSImg (image): Image with longer shutterspeed.
      loSSImg (image): Image with shorter shutterspeed.
      factor (float): Upscalefactor for the shorter shutterspeed.
      mask (2d-matrix, boolean): Boolean mask. False-Values are set to 0!

  Returns:
      int, int, image: sum of loSSImg upscaled brightness, sum and image of hiSSImg containing upscaled loSSImg pixels
  """
  scaledPxlImg = np.multiply(loSSImg, factor, dtype=np.float32) # Try to save RAM by using half size Float   #, where=mask)
  # scaledPxlImg[scaledPxlImg < 1] = 0.0
  scaledLo = np.sum(scaledPxlImg)
  scaledPxlImg[mask == False] = 0 # correct resolution errors from int -> float conversion

  upscaledImg = np.add(hiSSImg, scaledPxlImg, dtype=np.float32)  #np.float64)
  upscaledImg[upscaledImg < 1] = 0 # correct resolution errors from int -> float conversion
  scaledOnOverexpose = np.sum(upscaledImg)

  return scaledLo, scaledOnOverexpose, scaledPxlImg







def __BuildUpscaleAnyPxSubSet__(hiSSImgSet, loSSImgSet, theoryFactors): #, divFactors, combiFactors):
  """Builds a full subset of pixel-upscale brightness and images.

  Args:
      hiSSImgSet (image): Image with longer shutterspeed.
      loSSImgSet (image): Image with shorter shutterspeed.
      theoryFactors (iterable, int): Iterable object (same lenght as image-vectors) containing the upscaling factors.

  Returns:
      iterable int, iterable image: List of brightness-values, List of upscaled images
  """
  upscaledAnyPxBright = dict()
  # upscaledAnyPxBright = dict() # No Full-Upscale of loSS-Image saved -> But it's implemented. See "scldLo" variable below!
  upscaledAnyPxBright["xTheory"]                    = list()
  # upscaledAnyPxBright["xSpotDivBlank"]              = list()
  # upscaledAnyPxBright["xSpotDivClean"]              = list()
  # upscaledAnyPxBright["xMeanPxDivBlank"]            = list()
  # upscaledAnyPxBright["xMeanPxDivClean"]            = list()
  # upscaledAnyPxBright["xTheory/BlankArea"]          = list()
  # upscaledAnyPxBright["xTheory/CleanArea"]          = list()
  # upscaledAnyPxBright["xSpot_Mean(Blank,Clean)"]    = list()
  # upscaledAnyPxBright["xMeanPx_Mean(Blank,Clean)"]  = list()

  upscaledAnyPxlImgs = dict()
  # upscaledAnyPxlImgs = dict()
  upscaledAnyPxlImgs["xTheory"]                   = list()
  # upscaledAnyPxlImgs["xSpotDivBlank"]             = list()
  # upscaledAnyPxlImgs["xSpotDivClean"]             = list()
  # upscaledAnyPxlImgs["xMeanPxDivBlank"]           = list()
  # upscaledAnyPxlImgs["xMeanPxDivClean"]           = list()
  # upscaledAnyPxlImgs["xTheory/BlankArea"]         = list()
  # upscaledAnyPxlImgs["xTheory/CleanArea"]         = list()
  # upscaledAnyPxlImgs["xSpot_Mean(Blank,Clean)"]   = list()
  # upscaledAnyPxlImgs["xMeanPx_Mean(Blank,Clean)"] = list()

  # dummy = list()
  for _iImg in range(len(hiSSImgSet["Blank"])):
    # Upscaling overexposed pixels!

    #  * theory value (hiSS / loSS)
    scldLo, scldOvrexpsd, scldImg = __CalculateUpscaleAnyPxImg__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], theoryFactors[_iImg], hiSSImgSet["OverexposedMask"][_iImg])
    upscaledAnyPxBright["xTheory"].append(scldOvrexpsd)
    upscaledAnyPxlImgs ["xTheory"].append(scldImg)

    # # Blank SpotDiv
    # scldLo, scldOvrexpsd, scldImg = __CalculateUpscaleAnyPxImg__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], divFactors["SpotDiv"]["Blank"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
    # upscaledAnyPxBright["xSpotDivBlank"].append(scldOvrexpsd)
    # upscaledAnyPxlImgs ["xSpotDivBlank"].append(scldImg)

    # # Cleaned SpotDiv
    # scldLo, scldOvrexpsd, scldImg = __CalculateUpscaleAnyPxImg__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], divFactors["SpotDiv"]["Clean"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
    # upscaledAnyPxBright["xSpotDivClean"].append(scldOvrexpsd)
    # upscaledAnyPxlImgs ["xSpotDivClean"].append(scldImg)

    # # Blank MeanPxDiv in trustband!
    # scldLo, scldOvrexpsd, scldImg = __CalculateUpscaleAnyPxImg__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], divFactors["MeanPxDiv"]["Blank"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
    # upscaledAnyPxBright["xMeanPxDivBlank"].append(scldOvrexpsd)
    # upscaledAnyPxlImgs ["xMeanPxDivBlank"].append(scldImg)

    # # Cleaned MeanPxDiv in trustband
    # scldLo, scldOvrexpsd, scldImg = __CalculateUpscaleAnyPxImg__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], divFactors["MeanPxDiv"]["Clean"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
    # upscaledAnyPxBright["xMeanPxDivClean"].append(scldOvrexpsd)
    # upscaledAnyPxlImgs ["xMeanPxDivClean"].append(scldImg)

    # # Theory / AreaDivBlank
    # scldLo, scldOvrexpsd, scldImg = __CalculateUpscaleAnyPxImg__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], combiFactors["Theory"]["/BlankArea"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
    # upscaledAnyPxBright["xTheory/BlankArea"].append(scldOvrexpsd)
    # upscaledAnyPxlImgs ["xTheory/BlankArea"].append(scldImg)

    # # Theory / AreaDivClean
    # scldLo, scldOvrexpsd, scldImg = __CalculateUpscaleAnyPxImg__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], combiFactors["Theory"]["/CleanArea"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
    # upscaledAnyPxBright["xTheory/CleanArea"].append(scldOvrexpsd)
    # upscaledAnyPxlImgs ["xTheory/CleanArea"].append(scldImg)

    # # Mean(SpotDivBlank, SpotDivClean)
    # scldLo, scldOvrexpsd, scldImg = __CalculateUpscaleAnyPxImg__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], combiFactors["SpotDiv"]["Blank&Clean"]["Mean"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
    # upscaledAnyPxBright["xSpot_Mean(Blank,Clean)"].append(scldOvrexpsd)
    # upscaledAnyPxlImgs ["xSpot_Mean(Blank,Clean)"].append(scldImg)

    # # Mean(MeanPxDivBlank, MeanPxDivClean)
    # scldLo, scldOvrexpsd, scldImg = __CalculateUpscaleAnyPxImg__(hiSSImgSet["Clean"][_iImg], loSSImgSet["Blank"][_iImg], combiFactors["MeanPxDiv"]["Blank&Clean"]["Mean"][_iImg], hiSSImgSet["OverexposedMask"][_iImg])
    # upscaledAnyPxBright["xMeanPx_Mean(Blank,Clean)"].append(scldOvrexpsd)
    # upscaledAnyPxlImgs ["xMeanPx_Mean(Blank,Clean)"].append(scldImg)

  return upscaledAnyPxBright, upscaledAnyPxlImgs










def UpscaleAny(imgSets, brightSets, divFactorSets): #, combinedFactorSets):
  """Upscales any brightnesses (spot and pixelwise).

  Args:
      imgSets (_type_): A full set of images (SS, Full/Blank, et...)
      combinedFactorSets (_type_): Corresponding upscale-factors for the image-set.

  Returns:
      _type_: A full set of upscaled spot-brightness and upscaled pixel-images.
  """
  upscaledBright = dict()
  upscaledPxImgs = dict()
  # upscaled["Full"] = __BrightUpscale_AnySubSet__()

  _bKeys = list(brightSets.keys())
  _nbKeys = len(_bKeys)
  for _iBase in range(_nbKeys):
    _bKey = _bKeys[_iBase]

    upscaledBright[_bKey] = dict()
    upscaledPxImgs[_bKey] = dict()

    _dKeys = list(brightSets[_bKey]["Div"].keys())
    _ndKeys = len(_dKeys)
    for _iDiv in range(_ndKeys):
      _dKey = _dKeys[_iDiv]

      upscaledBright[_bKey][_dKey] = dict()
      upscaledBright[_bKey][_dKey]["Full"] = dict()

      upscaledPxImgs[_bKey][_dKey] = dict()
      upscaledPxImgs[_bKey][_dKey]["Full"] = dict()

      # Spotwise upscaling for full image
      # upscaledBright[_bKey][_dKey]["Full"]["SpotBright"] = __UpscaleAnySpot__(brightSets[_bKey]["Div"][_dKey]["Full"], divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Full"], combinedFactorSets[_bKey][_dKey]["Full"])
      upscaledBright[_bKey][_dKey]["Full"]["SpotBright"] = __UpscaleAnySpot__(brightSets[_bKey]["Div"][_dKey]["Full"], divFactorSets[_bKey][_dKey]["Theory"]) #, None, None)

      # Pxwise upscaling for full image
      # pxBright, pxImgs = __BuildUpscaleAnyPxSubSet__(imgSets[_bKey]["Full"], imgSets[_bKey]["Div"][_dKey]["Full"], divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Full"], combinedFactorSets[_bKey][_dKey]["Full"])
      pxBright, pxImgs = __BuildUpscaleAnyPxSubSet__(imgSets[_bKey]["Full"], imgSets[_bKey]["Div"][_dKey]["Full"], divFactorSets[_bKey][_dKey]["Theory"]) #, None, None)
      upscaledBright[_bKey][_dKey]["Full"]["PxlBright"] = pxBright
      upscaledPxImgs[_bKey][_dKey]["Full"] = pxImgs

      upscaledBright[_bKey][_dKey]["Spot"] = dict()
      upscaledPxImgs[_bKey][_dKey]["Spot"] = dict()
      _xyKeys = list(brightSets[_bKey]["Div"][_dKey]["Spot"].keys())
      for _iXY in range(len(_xyKeys)):
        _xyKey = _xyKeys[_iXY]

        upscaledBright[_bKey][_dKey]["Spot"][_xyKey] = dict()
        upscaledPxImgs[_bKey][_dKey]["Spot"][_xyKey] = dict()

        # Spotwise upscaling for separate spots
        # upscaledBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"] = __UpscaleAnySpot__(brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey], divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Spot"][_xyKey], combinedFactorSets[_bKey][_dKey]["Spot"][_xyKey])
        upscaledBright[_bKey][_dKey]["Spot"][_xyKey]["SpotBright"] = __UpscaleAnySpot__(brightSets[_bKey]["Div"][_dKey]["Spot"][_xyKey], divFactorSets[_bKey][_dKey]["Theory"]) #, None, None)

        # Pxwise upscaling for separate spots
        try:
          # pxBright, pxImgs = __BuildUpscaleAnyPxSubSet__(imgSets[_bKey]["Spot"][_xyKey], imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey], divFactorSets[_bKey][_dKey]["Theory"], divFactorSets[_bKey][_dKey]["Spot"][_xyKey], combinedFactorSets[_bKey][_dKey]["Spot"][_xyKey])
          pxBright, pxImgs = __BuildUpscaleAnyPxSubSet__(imgSets[_bKey]["Spot"][_xyKey], imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey], divFactorSets[_bKey][_dKey]["Theory"]) #, None, None)
          upscaledBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"] = pxBright
          upscaledPxImgs[_bKey][_dKey]["Spot"][_xyKey] = pxImgs
        except Exception as e:
          imgCnt = len(imgSets[_bKey]["Spot"][_xyKey]["Blank"])
          imgShape = imgSets[_bKey]["Spot"][_xyKey]["Blank"][0].shape
          upscaledBright[_bKey][_dKey]["Spot"][_xyKey]["PxlBright"] = [0] * imgCnt
          upscaledPxImgs[_bKey][_dKey]["Spot"][_xyKey] = [np.zeros(imgShape)] * imgCnt

  return upscaledBright, upscaledPxImgs