from PMPLib.Factors_ImgSets import BuildFactorImgSets
from PMPLib.Factors_ImgData import GetBrightnessSets, GetPxCntSets
from PMPLib.Factors_DivideFactors import GetDivFactorSets
from PMPLib.Factors_CombinedFactors import CalcCombinedFactorSets
from PMPLib.Upscale_Any import UpscaleAny
from PMPLib.Upscale_Overexposed import UpscaleOverexposed

###from misc import bcolors
import numpy as np


# def DataExtractionAndUpscaling(ssData,
#                                ImgKey="uint16",
#                                pxSidelen = 12,
#                                AddPxSidelen=False,
#                                TakeSpotBrightFromAllImgs=True,
#                                MinBright=256,
#                                OverexposedValue = 255,
#                                ):
#     """Takes the collected ssData, and uses the images from ImgKey to determine necessary img-sets and extract brightess data, area (count of the active pixels), factors, any upscaled brightness (ignoring overexposure) as well as the upscaled brightness only, where overexposure occured

#     Args:
#         ssData (iterable): Iterable object of ssData images
#         ImgKey (str, optional): Dictionary key of the image-set which should be used for data extraction. Defaults to "uint16".
#         pxSidelen (int, optional): Sidelength of a sqaure which is determined around a spots center to read out the spots brightness. Defaults to 12.
#         AddPxSidelen (bool, optional): If true, pxSideLen is added to the spots radius. Defaults to False.
#         TakeSpotBrightFromAllImgs (bool, optional): If true, a brightness value on each image for the detected spots are extraced (all brightness-vectors have the same length!). Defaults to True.
#         MinBright (int, optional): Used as a minimal value. When a pixel-value > MinBright, it counts as active pixel. Defaults to 256.
#         OverexposedValue (int, optional): Defines the pixelvalue at whicha pixel counts as overexposed. Defaults to 255.

#     Returns:
#         _type_: _description_
#     """

#     if pxSidelen == 0:
#         print("AttachBrightnessData: pxTolerance must be > 0!")

#     halfTol = pxSidelen / 2
#     if halfTol % 1 != 0:
#         print(str.format("Half tolerance is not integer! Asymetric brightness-detection by 1 pixel", int(halfTol)))


#     imgSets                                                  = BuildFactorImgSets(ssData=ssData, ImgKey=ImgKey, pxSidelen=pxSidelen, AddPxSidelen=AddPxSidelen, OverexposedValue=OverexposedValue, TakeSpotBrightFromAllImgs=TakeSpotBrightFromAllImgs)
#     brightSets                                               = GetBrightnessSets(imgSets)
#     areaCntSets                                              = GetPxCntSets(imgSets, minBright=MinBright)
#     divFactors                                               = GetDivFactorSets(imgSets) #, brightSets, areaCntSets, PxDivTrustband, PxDivMinBright)
#     # combinedFactors                                          = CalcCombinedFactorSets(divFactors) # Not used anymore since signal-linearity was proven! -> Factors = Div-Factors
#     # scaledAnyBright, scaledAnyPxImgs                         = UpscaleAny(imgSets, brightSets, divFactors) #, combinedFactors)
#     scaledAnyBright                                          = UpscaleAny(imgSets, brightSets, divFactors) #, combinedFactors)
#     # scaledWhereOverexposedBright, scaledWhereOverexposedImgs = UpscaleOverexposed(imgSets, brightSets, scaledAnyBright, scaledAnyPxImgs)
#     scaledWhereOverexposedBright                             = UpscaleOverexposed(imgSets, brightSets, scaledAnyBright, None)

#     # return ssData, imgSets, brightSets, areaCntSets, divFactors, scaledAnyBright, scaledAnyPxImgs, scaledWhereOverexposedBright#, scaledWhereOverexposedImgs #combinedFactors, , bData#, bImages
#     return ssData, imgSets, brightSets, areaCntSets, divFactors, scaledAnyBright, None, scaledWhereOverexposedBright#, scaledWhereOverexposedImgs #combinedFactors, , bData#, bImages





def SubareaImagesAndSensorsignalInfo(cirContainer, pxSidelen:int, addSidelen:bool, imgContainer, imgKey:str):
    """This subroutine determines the spots subarea-image as a referenced part of the corresponding full image. Afterwards all raw sensor signals are determined and collected in a separate collection. This is done by carrying out following steps:
    1.) The circle-center coordinate is extracted from the XY-Keys
    2.) pxSidelength is equally distributed around the center to obtain a quadratic area around the circle-center defining the spots subimage.
    3.) The spots area-corners are used to obtain the spots subimage-area as reference from the full image
    4.) When all subarea-

    Args:
        cirContainer (_type_): _description_
        imgContainer (_type_): _description_
        imgKey (str, optional): _description_. Defaults to None.
    """
    _ssKeys = list(imgContainer.keys())                         # Grab SS-Keys
    _xyKeys = list(cirContainer[_ssKeys[0]]["XYKeys"].keys())   # Grab XY-Keys
    
    # Guard clauses
    _imKeys = list(imgContainer[_ssKeys[0]].keys())             # Grab the different image keys
    if not _imKeys.__contains__(imgKey):                        # Auto-use first image-key, if not specified!
        raise Exception(f"Non-existing image-key. Allowed: {str(_imKeys)}")
    del _imKeys

    _nssKeys = len(_ssKeys)
    _nxyKeys = len(_xyKeys)
    _nImgCnt = len(imgContainer[_ssKeys[0]][imgKey])
    _imSize = imgContainer[_ssKeys[0]][imgKey][0].shape
    xMax = _imSize[1]
    yMax = _imSize[0]

    _halfSidelen = (pxSidelen) // 2 # Create half sidelengt, but ensure that the value is integer! (indicies cant have .5 values!)

    sesContainer = {}   # Empty raw sensor signal container
    for _issKey in range(_nssKeys):             # Iterate through all SS
        _ssKey = _ssKeys[_issKey]
        imgContainer[_ssKey]["XYKeys"]        = dict() # Create empty XY-Dict for subarea-images

        sesContainer[_ssKey] = dict()
        sesContainer[_ssKey] = {
            "SumOfImage"   : np.array([np.sum(fImg) for fImg in imgContainer[_ssKey][imgKey]]),  # Append list containing the sum of the entire image
            "SumOfSubareas": [],                                                                 # Append empty list for the sum of subarea-sensor signals
            "XYKeys"       : {},                                                                 # Prepare an empty dict for the subarea-image sensor signals
        }

        # Only subarea-images
        for _ixyKey in range(_nxyKeys):         # Then through all XY-Keys
            _xyKey = _xyKeys[_ixyKey]
            _xyInfo = cirContainer[_ssKeys[0]]["XYKeys"][_xyKey] # Use always the entire set of XYKeys -> Use longest SS with the most detections!

            imgContainer[_ssKey]["XYKeys"][_xyKey]        = { # Create empty list for referenced subimage-area
                "SubareaCoord": [],
                "SubareaImage": [],
                }

            # Determin the left upper (x1,y1) and right lower (x2,y2) corner of the referenced subimage-area
            #  and ensure, that the coordinates always stays inbound of the image width & height
            r = 0 if not addSidelen else _xyInfo["radius"]
            x1 = (_xyInfo["x"] - _halfSidelen - r)
            if (x1 <     0): x1 = 0

            x2 = (_xyInfo["x"] + _halfSidelen + r)
            if (x2 >= xMax): x2 = xMax - 1

            y1 = (_xyInfo["y"] - _halfSidelen - r)
            if (y1 <     0): y1 = 0

            y2 = (_xyInfo["y"] + _halfSidelen + r)
            if (y2 >= yMax): y2 = yMax - 1

            imgContainer[_ssKey]["XYKeys"][_xyKey]["SubareaCoord"] = (x1, y1, x2, y2) # Static for each XYKey/Spot. Store left upper (x1,y1) and right lower (x2,y2) corner as 4-member tuple

            sesContainer[_ssKey]["XYKeys"][_xyKey] = {}
            sesContainer[_ssKey]["XYKeys"][_xyKey]["SumOfSubarea"] = []
            for _iImg in range(_nImgCnt):       # As well as all images!
                # Grab full image and subarea
                _rawimg = imgContainer[_ssKey][imgKey][_iImg]      # Get full image
                _subimg = _rawimg[y1:y2, x1:x2]                    # Parse out the xy-area as reference

                # Append the subarea to the collection
                imgContainer[_ssKey]["XYKeys"][_xyKey]["SubareaImage"].append(_subimg)  # Grab a reference of the full image

                # Determine the brighntesses
                sesContainer[_ssKey]["XYKeys"][_xyKey]["SumOfSubarea"].append(np.sum(_subimg))                        # Sensor signal of the subarea-image

        # Only full image!
        # If all subarea-images are appended, determine the sum of subarea-Sensor signal for each XYKey
                                 # Sensor signal of the full image
        for _iImg in range(_nImgCnt):
            _imSum = 0

            for _ixyKey in range(_nxyKeys):
                _xyKey = _xyKeys[_ixyKey]
                _imSum += sesContainer[_ssKey]["XYKeys"][_xyKey]["SumOfSubarea"][_iImg]
            sesContainer[_ssKey]["SumOfSubareas"].append(_imSum)

    return sesContainer












def PixelcountAndOverexposureInfo(cirContainer, imgContainer, imgKey:str, valueOfOverexposement:int, valueOfAreacount:int):
    # PixelCount and Overexposementinfo
    pcoContainer = {}

    # Grab neccessary base-info
    _ssKeys = list(imgContainer.keys())                         # Grab SS-Keys
    _xyKeys = list(cirContainer[_ssKeys[0]]["XYKeys"].keys())   # Grab XY-Keys
    
    # Guard clauses
    _imKeys = list(imgContainer[_ssKeys[0]].keys())             # Grab the different image keys
    if not _imKeys.__contains__(imgKey):                        # Auto-use first image-key, if not specified!
        raise Exception(f"Non-existing image-key. Allowed: {str(_imKeys)}")
    del _imKeys

    if valueOfOverexposement > 0xFFFF or valueOfOverexposement < 0:                          # Auto-use first image-key, if not specified!
        raise Exception(f"Invalid valueOfOverexposement. Must be: 0 <= valueOfOverexposement ({valueOfOverexposement}) <= 0xFFFF")
    
    if valueOfAreacount > 0xFFFF or valueOfAreacount < 0:                          # Auto-use first image-key, if not specified!
        raise Exception(f"Invalid valueOfAreacount. Must be: 0 <= valueOfAreacount ({valueOfAreacount}) <= 0xFFFF")
    
    _nssKeys = len(_ssKeys)
    _nxyKeys = len(_xyKeys)
    _nImgCnt = len(imgContainer[_ssKeys[0]][imgKey])
    # _imSize = imgContainer[_ssKeys[0]][_imKey][0].shape
    # xMax = _imSize[1]
    # yMax = _imSize[0]
    for _issKey in range(_nssKeys):             # Iterate through all SS
        _ssKey = _ssKeys[_issKey]
        
        pcoContainer[_ssKey] = {
            "CountOfAllPixels"         : [], # Amount of all pixels
            "CountOfContributingPixels": [], # Amount of pixels >= valueOfContribution
            "CountOfOverexposedPixels" : [], # Amount of pixels >= valueOfOverexposement
            "BoolOfOverexposure"       : [], # True if "CountOfOverexposedPixels" > 0
            "XYKeys"                   : {}, # Subcollection for the XY-Keys
        }

        # Only subarea-images!
        for _ixyKey in range(_nxyKeys):         # Then through all XY-Keys
            _xyKey = _xyKeys[_ixyKey]
            pcoContainer[_ssKey]["XYKeys"][_xyKey] = {
                "CountOfAllPixels"         : [], # Amount of all pixels
                "CountOfContributingPixels": [], # Amount of pixels >= valueOfContribution
                "CountOfOverexposedPixels" : [], # Amount of pixels >= valueOfOverexposement
                "BoolOfOverexposure"       : [], # True if "CountOfOverexposedPixels" > 0
            }

            for _iImg in range(_nImgCnt):       # As well as all images!
                _subareaimg = imgContainer[_ssKey]["XYKeys"][_xyKey]["SubareaImage"][_iImg]
                _nAllPixels = _subareaimg.shape[0] * _subareaimg.shape[1]
                _nContributingPixels = np.where(_subareaimg >= valueOfAreacount)[0].__len__()
                _nOverexposedPixels = np.where(_subareaimg >= valueOfOverexposement)[0].__len__()

                pcoContainer[_ssKey]["XYKeys"][_xyKey]["CountOfAllPixels"]         .append(_nAllPixels)
                pcoContainer[_ssKey]["XYKeys"][_xyKey]["CountOfContributingPixels"].append(_nContributingPixels)
                pcoContainer[_ssKey]["XYKeys"][_xyKey]["CountOfOverexposedPixels"] .append(_nOverexposedPixels)
                pcoContainer[_ssKey]["XYKeys"][_xyKey]["BoolOfOverexposure"]       .append(True if (_nOverexposedPixels > 0) else False)


        # Only full image!
        for _iImg in range(_nImgCnt):       # As well as all images!
            _fullimg = imgContainer[_ssKey][imgKey][_iImg]
            _nAllPixels = _fullimg.shape[0] * _fullimg.shape[1]
            _nContributingPixels = np.where(_fullimg >= valueOfAreacount)[0].__len__()
            _nOverexposedPixels = np.where(_fullimg >= valueOfOverexposement)[0].__len__()

            pcoContainer[_ssKey]["CountOfAllPixels"]         .append(_nAllPixels)
            pcoContainer[_ssKey]["CountOfContributingPixels"].append(_nContributingPixels)
            pcoContainer[_ssKey]["CountOfOverexposedPixels"] .append(_nOverexposedPixels)
            pcoContainer[_ssKey]["BoolOfOverexposure"]       .append(True if (_nOverexposedPixels > 0) else False)
            
    return pcoContainer








def MergeSensorsignalVectors(sesContainer, pcoContainer):
    # Grab neccessary base-info
    _ssKeys = list(sesContainer.keys())                         # Grab SS-Keys
    _xyKeys = list(sesContainer[_ssKeys[0]]["XYKeys"].keys())   # Grab XY-Keys
    
    _nssKeys = len(_ssKeys)
    _nxyKeys = len(_xyKeys)
    _nImgCnt = len(sesContainer[_ssKeys[0]]["SumOfImage"])   # Amount of measured images

    # Merged Sensor Signal vectors
    mssContainer = {
        "MergedSensorSignal"  : [],
        "BoolOfOverexposure"  : [],
        "ContainsOverexposure": None,           # Use a default-dummy, so that it can be seen, when its set at the end of the function!
        "ReferenceSS"         : _ssKeys[0],
        "UpscaledFromSS"      : [],
        "XYKeys": {}
    }

    # Only Subarea-images
    for _ixyKey in range(_nxyKeys):         # Then through all XY-Keys
        _xyKey = _xyKeys[_ixyKey]

        mssContainer["XYKeys"][_xyKey] = {}
        mssContainer["XYKeys"][_xyKey]["MergedSensorSignal"]   = []
        mssContainer["XYKeys"][_xyKey]["BoolOfOverexposure"]   = []
        mssContainer["XYKeys"][_xyKey]["ContainsOverexposure"] = False,
        mssContainer["XYKeys"][_xyKey]["ReferenceSS"]          = _ssKeys[0]
        mssContainer["XYKeys"][_xyKey]["UpscaledFromSS"]       = []

        for _iImg in range(_nImgCnt):       # As well as all images!
            for _issKey in range(_nssKeys):                                              #  Scan SSs for an unoverexposed sensor signal value
                _ssKey = _ssKeys[_issKey]
                _sesVec = sesContainer[_ssKey]["XYKeys"][_xyKey]["SumOfSubarea"]
                _boeVec = pcoContainer[_ssKey]["XYKeys"][_xyKey]["BoolOfOverexposure"]
                _upScl = _ssKeys[0] / _ssKey


                if (   (_boeVec[_iImg] == True) and (_ssKey == _ssKeys[-1])         # Reached shortest SS, but still overexposed! -> Still the best value we have -> Upscale this one and add BoolOfOverexposure = True
                    or (_boeVec[_iImg] == False)):                                  # Value is not overexposed                                                    -> Upscale this one and add BoolOfOverexposure = False
                    mssContainer["XYKeys"][_xyKey]["MergedSensorSignal"].append(_sesVec[_iImg] * _upScl)    #  -> Append upscaled SEnsor Signal value
                    mssContainer["XYKeys"][_xyKey]["BoolOfOverexposure"].append(_boeVec[_iImg])             #  -> Append if the value contains overexposure
                    mssContainer["XYKeys"][_xyKey]["UpscaledFromSS"]    .append(_ssKey)                     #  -> Append from which 
                    break                                                                                   # Image finished -> Next one!
        
        
        _containsBOE = mssContainer["XYKeys"][_xyKey]["BoolOfOverexposure"].__contains__(True)
        mssContainer["XYKeys"][_xyKey]["ContainsOverexposure"] = _containsBOE

    # Only Full images
    for _iImg in range(_nImgCnt):               # Iterate through all images
        _sesSum = 0
        _sesBOE = False
        _sesFromSS = _ssKeys[0]

        for _ixyKey in range(_nxyKeys):         # Then through all XY-Keys
            _xyKey = _xyKeys[_ixyKey]
            _xyInfo = mssContainer["XYKeys"][_xyKey]

            _sesSum += _xyInfo["MergedSensorSignal"][_iImg]     # Summarize the subarea SEnsor Signals
            _boeTemp  = _xyInfo["BoolOfOverexposure"][_iImg]    # Grab its BoolOfOverexposure
            if _boeTemp == True:                                #  -> when BOE is True
                _sesBOE = True                                     #     mark the entire sesSum as "contains overexposure"
            
            _fromSSTemp  = _xyInfo["UpscaledFromSS"]    [_iImg] # Grab the SS from which this SEnsor Signal was upscaled from
            if _fromSSTemp < _sesFromSS:                        #  -> When the overall "_fromSS" > than the actual "_fromSSTemp"
                _sesFromSS = _fromSSTemp                        #     override "_fromSS" with "_fromSSTemp"
                                                                # NOTE: For the overall "_sesFromSS" is always the shortest SS appended, which contributes to "_sesSum"


        # Append the values for the current image
        mssContainer["MergedSensorSignal"]  .append(_sesSum)
        mssContainer["BoolOfOverexposure"]  .append(_sesBOE)
        mssContainer["UpscaledFromSS"]      .append(_sesFromSS)

    try:
        mssContainer["ContainsOverexposure"] = mssContainer["XYKeys"][_xyKey]["BoolOfOverexposure"].__contains__(True) # If there is at least one overexposed value in the merged vector, make that visible by a simple bool
    except:
        pass

    return mssContainer