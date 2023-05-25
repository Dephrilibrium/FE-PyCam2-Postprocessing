import numpy as np
import pickle

from PMPLib.ImgAreas import GetCircleArea_XYX2Y2
from PMPLib.ImgAreas import GetXYArea_XYX2Y2













def __BuildImgSubSet__(ImgCollection, XYCollection, pxSidelen, AddPxSidelen, OverexposedBright, CleanMask, TakeSpotBrightFromAllImgs):
  subSet = dict()
  subSet["Full"] = dict()
  subSet["Full"]["Blank"] = list()
  subSet["Full"]["Clean"] = list()
  subSet["Full"]["OverexposedMask"] = list()
  subSet["Full"]["CleanMask"] = list()

  subSet["Spot"] = dict()
  # subSet["Spot"]["Blank"] = dict()
  # subSet["Spot"]["Clean"] = dict()
  # subSet["Spot"]["OverexposedMask"] = list()


  for _iImg in range(len(ImgCollection)):
    subSet["Full"]["Blank"].append(ImgCollection[_iImg])
    cleanImg = subSet["Full"]["Blank"][-1].copy()
    overexposedMask = cleanImg >= OverexposedBright
    subSet["Full"]["OverexposedMask"].append(overexposedMask)

    if CleanMask == None:
      subSet["Full"]["CleanMask"].append(subSet["Full"]["OverexposedMask"][-1]) # Overexpose == Clean -> Img is base-SS
    else:
      subSet["Full"]["CleanMask"].append(CleanMask[_iImg])   # Use cleanMask vom given base to indicate which pixels are purged

    cleanImg[subSet["Full"]["CleanMask"][-1]] = 0     # subSet["Full"]["CleanMask"][-1] = OverexposedMasks
    subSet["Full"]["Clean"].append(cleanImg)

  _xyKeys = list(XYCollection.keys())
  # _imgShape = ImgCollection[0].shape;
  _imgShape = (pxSidelen, pxSidelen) # Size of an spot!
  for _iXY in range(len(_xyKeys)):
    _xyKey = _xyKeys[_iXY]
    subSet["Spot"][_xyKey] = dict()
    subSet["Spot"][_xyKey]["Blank"] = list()
    subSet["Spot"][_xyKey]["Clean"] = list()
    subSet["Spot"][_xyKey]["OverexposedMask"] = list()
    subSet["Spot"][_xyKey]["CleanMask"] = list()
    subSet["Spot"][_xyKey]["Area"] = list()

    # Block 1: Take spot-brightness from each picture!
    # Only one XY-Coordinate available -> Radius can't be taken into account (no AddPxRadius option)
    if TakeSpotBrightFromAllImgs: # When active the spot-position is based on the XY-coordinates -> Only needs to be calculated once!
      x1, y1, x2, y2 = GetXYArea_XYX2Y2(XYTuple=_xyKey, pxHeight=pxSidelen, pxWidth=pxSidelen)
      for _iImg in range(len(ImgCollection)):
          subSet["Spot"][_xyKey]["Blank"].append(subSet["Full"]["Blank"][_iImg][y1:y2, x1:x2])                      # Add references to full-dataset
          subSet["Spot"][_xyKey]["Clean"].append(subSet["Full"]["Clean"][_iImg][y1:y2, x1:x2])                      # Add references to full-dataset
          subSet["Spot"][_xyKey]["OverexposedMask"].append(subSet["Full"]["OverexposedMask"][_iImg][y1:y2, x1:x2])  # Add references to full-dataset
          subSet["Spot"][_xyKey]["CleanMask"].append(subSet["Full"]["CleanMask"][_iImg][y1:y2, x1:x2])              # Add references to full-dataset
          subSet["Spot"][_xyKey]["Area"].append([x1, y1, x2, y2])

    # Block 2: Take spot-brightness only from images circles were detected!
    # Each circle has its own center and radius -> AddPx can be used!
    else:
      for _iImg in range(len(ImgCollection)):
        try:
          _iIndex = XYCollection[_xyKey]["ImageIndex"].index(_iImg)
          _circle = XYCollection[_xyKey]["ImgCircles"][_iIndex]

          x1, y1, x2, y2 = GetCircleArea_XYX2Y2(Circle=_circle, pxTolerance=pxSidelen, AddPxTolerance=AddPxSidelen)
          subSet["Spot"][_xyKey]["Blank"].append(subSet["Full"]["Blank"][_iImg][y1:y2, x1:x2])                      # Add references to full-dataset
          subSet["Spot"][_xyKey]["Clean"].append(subSet["Full"]["Clean"][_iImg][y1:y2, x1:x2])                      # Add references to full-dataset
          subSet["Spot"][_xyKey]["OverexposedMask"].append(subSet["Full"]["OverexposedMask"][_iImg][y1:y2, x1:x2])  # Add references to full-dataset
          subSet["Spot"][_xyKey]["CleanMask"].append(subSet["Full"]["CleanMask"][_iImg][y1:y2, x1:x2])              # Add references to full-dataset
          subSet["Spot"][_xyKey]["Area"].append([x1, y1, x2, y2])
        except Exception as e:
          subSet["Spot"][_xyKey]["Blank"].append(np.zeros(_imgShape))
          subSet["Spot"][_xyKey]["Clean"].append(np.zeros(_imgShape))
          subSet["Spot"][_xyKey]["OverexposedMask"].append(np.zeros(_imgShape, dtype=bool))
          subSet["Spot"][_xyKey]["CleanMask"].append(subSet["Spot"][_xyKey]["OverexposedMask"][-1])
          subSet["Spot"][_xyKey]["Area"].append([0, 0, 0, 0])

  return subSet













def BuildFactorImgSets(ssData, ImgKey, pxSidelen, AddPxSidelen, OverexposedValue, TakeSpotBrightFromAllImgs):

  _ssKeys = list(ssData.keys())

  bImgs = dict()

  for _iBase in range(len(_ssKeys) -1):
    _bKey = _ssKeys[_iBase]

    # Prepare dict for full base-images
    bImgs[_bKey] = __BuildImgSubSet__(ImgCollection=pickle.loads(pickle.dumps(ssData[_bKey]["Images"][ImgKey])), XYCollection=ssData[_bKey]["Circles"]["XYKeys"], pxSidelen=pxSidelen, AddPxSidelen=AddPxSidelen, OverexposedBright=OverexposedValue, CleanMask=None, TakeSpotBrightFromAllImgs=TakeSpotBrightFromAllImgs)
    bImgs[_bKey]["Div"] = dict()


    #######################      ^--- Appends Base Images ---^     #######################
    ######################################################################################
    #######################      v--- Appends Div-Images  ---v     #######################
    for _iDiv in range(_iBase + 1, len(_ssKeys)):
      _dKey = _ssKeys[_iDiv]

      # Prepare dict for div
      # bImgs[_bKey]["Div"][_dKey] = __BuildImgSubSet__(ImgCollection=pickle.loads(pickle.dumps(ssData[_dKey]["Images"][ImgKey])), XYCollection=ssData[_dKey]["Circles"]["XYKeys"], pxSidelen=pxSidelen, AddPxSidelen=AddPxSidelen, OverexposedBright=OverexposedValue, CleanMask=bImgs[_bKey]["Full"]["OverexposedMask"], TakeSpotBrightFromAllImgs=TakeSpotBrightFromAllImgs)
      bImgs[_bKey]["Div"][_dKey] = __BuildImgSubSet__(ImgCollection=pickle.loads(pickle.dumps(ssData[_dKey]["Images"][ImgKey])), XYCollection=ssData[_bKey]["Circles"]["XYKeys"], pxSidelen=pxSidelen, AddPxSidelen=AddPxSidelen, OverexposedBright=OverexposedValue, CleanMask=bImgs[_bKey]["Full"]["OverexposedMask"], TakeSpotBrightFromAllImgs=TakeSpotBrightFromAllImgs)

  return bImgs