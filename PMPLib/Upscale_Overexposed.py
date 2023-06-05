# from math import isnan
import numpy as np
# import cv2 as cv








def __GenerateEmptySubSetStructure__():
  """Creates an empty substructure.

  Returns:
      dict: Empty substructure.
  """
  struct = dict()
  struct["xTheory"]                   = list()
  # struct["xSpotDivBlank"]             = list()
  # struct["xSpotDivClean"]             = list()
  # struct["xMeanPxDivBlank"]           = list()
  # struct["xMeanPxDivClean"]           = list()
  # struct["xTheory/BlankArea"]         = list()
  # struct["xTheory/CleanArea"]         = list()
  # struct["xSpot_Mean(Blank,Clean)"]   = list()
  # struct["xMeanPx_Mean(Blank,Clean)"] = list()
  return struct






def __AppendBright2All__(bright, bValue):
  """Appends the given bValue to the given bright.

  Args:
      bright (dict, iterable, int): Iterable object to which bValue gets added.
      bValue (int): Brightnessvalue to add to bright.

  Returns:
      dict, iterable, int: Returns the new dict with bValue appended.
  """
  bright["SpotBright"]["xTheory"]                  .append(bValue)
  # bright["SpotBright"]["xSpotDivBlank"]            .append(bValue)
  # bright["SpotBright"]["xSpotDivClean"]            .append(bValue)
  # bright["SpotBright"]["xMeanPxDivBlank"]          .append(bValue)
  # bright["SpotBright"]["xMeanPxDivClean"]          .append(bValue)
  # bright["SpotBright"]["xTheory/BlankArea"]        .append(bValue)
  # bright["SpotBright"]["xTheory/CleanArea"]        .append(bValue)
  # bright["SpotBright"]["xSpot_Mean(Blank,Clean)"]  .append(bValue)
  # bright["SpotBright"]["xMeanPx_Mean(Blank,Clean)"].append(bValue)

  bright["PxlBright"]["xTheory"]                  .append(bValue)
  # bright["PxlBright"]["xSpotDivBlank"]            .append(bValue)
  # bright["PxlBright"]["xSpotDivClean"]            .append(bValue)
  # bright["PxlBright"]["xMeanPxDivBlank"]          .append(bValue)
  # bright["PxlBright"]["xMeanPxDivClean"]          .append(bValue)
  # bright["PxlBright"]["xTheory/BlankArea"]        .append(bValue)
  # bright["PxlBright"]["xTheory/CleanArea"]        .append(bValue)
  # bright["PxlBright"]["xSpot_Mean(Blank,Clean)"]  .append(bValue)
  # bright["PxlBright"]["xMeanPx_Mean(Blank,Clean)"].append(bValue)
  return bright








def __AppendPxImg2All__(pxImg, img):
  """Appends the given img to the given pxImg.

  Args:
      pxImg (dict, iterable, image): Iterable object to which img is appended.
      img (image): Image which should be appended to pxImg.

  Returns:
      dict, iterable, image: Returns the new dict with img appended.
  """
  pxImg["xTheory"]                  .append(img)
  # pxImg["xSpotDivBlank"]            .append(img)
  # pxImg["xSpotDivClean"]            .append(img)
  # pxImg["xMeanPxDivBlank"]          .append(img)
  # pxImg["xMeanPxDivClean"]          .append(img)
  # pxImg["xTheory/BlankArea"]        .append(img)
  # pxImg["xTheory/CleanArea"]        .append(img)
  # pxImg["xSpot_Mean(Blank,Clean)"]  .append(img)
  # pxImg["xMeanPx_Mean(Blank,Clean)"].append(img)
  return pxImg











def __AppendDataset__(bright2Append, pxImgs2Append, scaledAnyBright, scaledAnyPxImg, imgIndex:int):
  """Appends some data-vectors to the given bright2Append and pxImgs2Append.

  Args:
      bright2Append (dict, iter, _type_): Collection to which a set of data should be appended.
      pxImgs2Append (dict, iter, _type_): Collection to which a set of data should be appended.
      scaledAnyBright (dict, dict, iterable, int): Full set of the any-upscaled brightnesses to append.
      scaledAnyPxImg (dict, dict, iterable, int): Full set of the any-upscaled pixel-brightnesses to append.
      imgIndex (int): Image-index of the data which should be appended.

  Returns:
      dict, iterable, int: Returns a dicitionary containing the appended data.
  """
  bright2Append["SpotBright"]["xTheory"]                  .append(scaledAnyBright["SpotBright"]["Blank"]["xTheory"]                  [imgIndex])
  # bright2Append["SpotBright"]["xSpotDivBlank"]            .append(scaledAnyBright["SpotBright"]["Blank"]["xSpotDivBlank"]            [imgIndex])
  # bright2Append["SpotBright"]["xSpotDivClean"]            .append(scaledAnyBright["SpotBright"]["Blank"]["xSpotDivClean"]            [imgIndex])
  # bright2Append["SpotBright"]["xMeanPxDivBlank"]          .append(scaledAnyBright["SpotBright"]["Blank"]["xMeanPxDivBlank"]          [imgIndex])
  # bright2Append["SpotBright"]["xMeanPxDivClean"]          .append(scaledAnyBright["SpotBright"]["Blank"]["xMeanPxDivClean"]          [imgIndex])
  # bright2Append["SpotBright"]["xTheory/BlankArea"]        .append(scaledAnyBright["SpotBright"]["Blank"]["xTheory/BlankArea"]        [imgIndex])
  # bright2Append["SpotBright"]["xTheory/CleanArea"]        .append(scaledAnyBright["SpotBright"]["Blank"]["xTheory/CleanArea"]        [imgIndex])
  # bright2Append["SpotBright"]["xSpot_Mean(Blank,Clean)"]  .append(scaledAnyBright["SpotBright"]["Blank"]["xSpot_Mean(Blank,Clean)"]  [imgIndex])
  # bright2Append["SpotBright"]["xMeanPx_Mean(Blank,Clean)"].append(scaledAnyBright["SpotBright"]["Blank"]["xMeanPx_Mean(Blank,Clean)"][imgIndex])

  bright2Append["PxlBright"]["xTheory"]                  .append(scaledAnyBright["PxlBright"]["xTheory"]                  [imgIndex])
  # bright2Append["PxlBright"]["xSpotDivBlank"]            .append(scaledAnyBright["PxlBright"]["xSpotDivBlank"]            [imgIndex])
  # bright2Append["PxlBright"]["xSpotDivClean"]            .append(scaledAnyBright["PxlBright"]["xSpotDivClean"]            [imgIndex])
  # bright2Append["PxlBright"]["xMeanPxDivBlank"]          .append(scaledAnyBright["PxlBright"]["xMeanPxDivBlank"]          [imgIndex])
  # bright2Append["PxlBright"]["xMeanPxDivClean"]          .append(scaledAnyBright["PxlBright"]["xMeanPxDivClean"]          [imgIndex])
  # bright2Append["PxlBright"]["xTheory/BlankArea"]        .append(scaledAnyBright["PxlBright"]["xTheory/BlankArea"]        [imgIndex])
  # bright2Append["PxlBright"]["xTheory/CleanArea"]        .append(scaledAnyBright["PxlBright"]["xTheory/CleanArea"]        [imgIndex])
  # bright2Append["PxlBright"]["xSpot_Mean(Blank,Clean)"]  .append(scaledAnyBright["PxlBright"]["xSpot_Mean(Blank,Clean)"]  [imgIndex])
  # bright2Append["PxlBright"]["xMeanPx_Mean(Blank,Clean)"].append(scaledAnyBright["PxlBright"]["xMeanPx_Mean(Blank,Clean)"][imgIndex])

  pxImgs2Append["xTheory"]                  .append(scaledAnyPxImg["xTheory"]                  [imgIndex])
  # pxImgs2Append["xSpotDivBlank"]            .append(scaledAnyPxImg["xSpotDivBlank"]            [imgIndex])
  # pxImgs2Append["xSpotDivClean"]            .append(scaledAnyPxImg["xSpotDivClean"]            [imgIndex])
  # pxImgs2Append["xMeanPxDivBlank"]          .append(scaledAnyPxImg["xMeanPxDivBlank"]          [imgIndex])
  # pxImgs2Append["xMeanPxDivClean"]          .append(scaledAnyPxImg["xMeanPxDivClean"]          [imgIndex])
  # pxImgs2Append["xTheory/BlankArea"]        .append(scaledAnyPxImg["xTheory/BlankArea"]        [imgIndex])
  # pxImgs2Append["xTheory/CleanArea"]        .append(scaledAnyPxImg["xTheory/CleanArea"]        [imgIndex])
  # pxImgs2Append["xSpot_Mean(Blank,Clean)"]  .append(scaledAnyPxImg["xSpot_Mean(Blank,Clean)"]  [imgIndex])
  # pxImgs2Append["xMeanPx_Mean(Blank,Clean)"].append(scaledAnyPxImg["xMeanPx_Mean(Blank,Clean)"][imgIndex])
  return bright2Append, pxImgs2Append





















def UpscaleOverexposed(imgSets, brightSets, scaledAnyBright, scaledAnyPxImgs):
  """Creates brightness-vectors where only overexposed spots/pixels are upscaled.

  Args:
      imgSets (dict, dict, iterable, images): A full set of images (SS, Blank/Clean, etc...)
      brightSets (dict, dict, iterable, int): A full set of brightnesses.
      scaledAnyBright (dict, dict, iterable, int): A full set of any-upscaled spot-brightnesses.
      scaledAnyPxImgs (dict, dict, iterable, int): A full set of any-upscaled pixel-brightnesses.

  Returns:
      dict, dict: A full brightness-collection. A full pixelimage-collection.
  """

  # Prepare for full-data
  bright = dict()
  bright["Full"] = dict()
  bright["Full"]["SpotBright"] = __GenerateEmptySubSetStructure__()
  bright["Full"]["PxlBright"] = __GenerateEmptySubSetStructure__()
  bright["Full"]["Overexposed"] = list()
  bright["Full"]["BrightnessFromSS"] = list()

  pxImgs = dict()
  pxImgs["Full"] = __GenerateEmptySubSetStructure__()

  _bKeys = list(brightSets.keys())
  _bKey = _bKeys[0] # To grab _xyKeys

  # Prepare for spot-data
  bright["Spot"] = dict()
  pxImgs["Spot"] = dict()

  _xyKeys = list(imgSets[_bKey]["Spot"].keys())
  for _iXY in range(len(_xyKeys)):
    _xyKey = _xyKeys[_iXY]

    bright["Spot"][_xyKey] = dict()
    bright["Spot"][_xyKey]["SpotBright"] = __GenerateEmptySubSetStructure__()
    bright["Spot"][_xyKey]["PxlBright"] = __GenerateEmptySubSetStructure__()
    bright["Spot"][_xyKey]["Overexposed"] = list()
    bright["Spot"][_xyKey]["BrightnessFromSS"] = list()

    # pxImgs["Spot"] = dict()
    pxImgs["Spot"][_xyKey] = __GenerateEmptySubSetStructure__()


  for _iImg in range(len(imgSets[_bKey]["Full"]["Blank"])):

    if imgSets[_bKey]["Full"]["OverexposedMask"][_iImg].max(): # Base-SS-Image has overexposed pixels

      _dKeys = list(imgSets[_bKey]["Div"].keys())
      for _iDiv in range(len(_dKeys)):
        _dKey = _dKeys[_iDiv]
        if imgSets[_bKey]["Div"][_dKey]["Full"]["OverexposedMask"][_iImg].max() and _dKey != _dKeys[-1]: # Div-SS-Image also overexposed and it is not already the last shutterspeed
          continue                                                               #  -> Search in next div-SS

        else: # Div-SS-Image not overexposed -> Add corresponding upscaled values to brightness-vectors
          __AppendDataset__(bright2Append=bright["Full"], pxImgs2Append=pxImgs["Full"], scaledAnyBright=scaledAnyBright[_bKey][_dKey]["Full"], scaledAnyPxImg=scaledAnyPxImgs[_bKey][_dKey]["Full"], imgIndex=_iImg)
          bright["Full"]["Overexposed"].append(False)
          bright["Full"]["BrightnessFromSS"].append(_dKey)
          break

      else: # No unoverexposed (or no matching) Div-SS-Image has been found
        __AppendBright2All__(bright=bright["Full"], bValue=0)
        __AppendPxImg2All__(pxImg=pxImgs["Full"], img=imgSets[_bKey]["Full"]["Blank"][_iImg]) # Add original Image by default, but imply that:
        bright["Full"]["Overexposed"].append(True)                                                                          #  by marking as overexposed
        bright["Full"]["BrightnessFromSS"].append(-1)                                                                       #  and use -1 as "origin"-SS


    else: # Base-SS-Image has no overexposed pixels
      blankBright = brightSets[_bKey]["Full"]["Blank"][_iImg]
      __AppendBright2All__(bright=bright["Full"], bValue=blankBright)
      __AppendPxImg2All__(pxImg=pxImgs["Full"], img=imgSets[_bKey]["Full"]["Blank"][_iImg])

      bright["Full"]["Overexposed"].append(False)
      bright["Full"]["BrightnessFromSS"].append(_bKey)
    
######################### ^--- Full ---^ #########################

######################### v--- Spot ---v #########################

    for _iXY in range(len(_xyKeys)):
      _xyKey = _xyKeys[_iXY]

      oeMask = imgSets[_bKey]["Spot"][_xyKey]["OverexposedMask"][_iImg]
      if oeMask.size > 0:
        oeMax = oeMask.max() # True or False
      else:
        oeMax = False

      # if imgSets[_bKey]["Spot"][_xyKey]["OverexposedMask"][_iImg].max(): # Base-SS-Image has overexposed pixels
      if oeMax: # Base-SS-Image has overexposed pixels
        _dKeys = list(imgSets[_bKey]["Div"].keys())
        for _iDiv in range(len(_dKeys)):
          _dKey = _dKeys[_iDiv]
          try: # to access the xy-key
            imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey]
          except: # When it fails, jump over SS an try the next one
            continue

          # if imgSets[_bKey]["Div"][_dKey]["Spot"][_xyKey]["OverexposedMask"][_iImg].max() and _dKey != _dKeys[-1]: # Div-SS-Image also overexposed and it is not already the last shutterspeed
          if oeMax and _dKey != _dKeys[-1]: # Div-SS-Image also overexposed and it is not already the last shutterspeed
            continue                                                               #  -> Search in next div-SS

          else: # Div-SS-Image not overexposed -> Add corresponding upscaled values to brightness-vectors
            __AppendDataset__(bright2Append=bright["Spot"][_xyKey], pxImgs2Append=pxImgs["Spot"][_xyKey], scaledAnyBright=scaledAnyBright[_bKey][_dKey]["Spot"][_xyKey], scaledAnyPxImg=scaledAnyPxImgs[_bKey][_dKey]["Spot"][_xyKey], imgIndex=_iImg)
            bright["Spot"][_xyKey]["Overexposed"].append(False)
            bright["Spot"][_xyKey]["BrightnessFromSS"].append(_dKey)
            break

      else: # Base-SS-Image has no overexposed pixels
        blankBright = brightSets[_bKey]["Spot"][_xyKey]["Blank"][_iImg]
        __AppendBright2All__(bright=bright["Spot"][_xyKey], bValue=blankBright)
        __AppendPxImg2All__(pxImg=pxImgs["Spot"][_xyKey], img=imgSets[_bKey]["Spot"][_xyKey]["Blank"][_iImg])

        bright["Spot"][_xyKey]["Overexposed"].append(False)
        bright["Spot"][_xyKey]["BrightnessFromSS"].append(_bKey)
    

  return bright, pxImgs