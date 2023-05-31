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
                               #PxDivTrustband=[24, 250],          # PxDivTrustband (list, optional): Not used anymore, but was used to determine a trustband for pixelwise division factors. Defaults to [24. 250].
                               #PxDivMinBright=150,                # PxDivMinBright (int, optional): Not used anymore, but was used to determin a minimal pixelwise brightness (ensures enough signal 2 noise ratio). Defaults to 150.
                               #AttachImages=False,                # AttachImages (bool, optional): Not used anymore, since the linearity was proven and no image-manupulation had to be done anymore.
                               MinBright=256,
                               OverexposedValue = 255,
                               ShowImg=False                       # ShowImg (bool, optional): Not used anymore. If true, the images are plotted when debugging the script. Defaults to False.
                               ):
    """Takes the collected ssData, and uses the images from ImgKey to determine necessary img-sets and extract brightess data, area (count of the active pixels), factors, any upscaled brightness (ignoring overexposure) as well as the upscaled brightness only, where overexposure occured

    Args:
        ssData (iterable): Iterable object of ssData images
        ImgKey (str, optional): Dictionary key of the image-set which should be used for data extraction. Defaults to "uint16".
        pxSidelen (int, optional): Sidelength of a sqaure which is determined around a spots center to read out the spots brightness. Defaults to 12.
        AddPxSidelen (bool, optional): If true, pxSideLen is added to the spots radius. Defaults to False.
        TakeSpotBrightFromAllImgs (bool, optional): If true, a brightness value on each image for the detected spots are extraced (all brightness-vectors have the same length!). Defaults to True.
        MinBright (int, optional): Used as a minimal value. When a pixel-value > MinBright, it counts as active pixel. Defaults to 256.
        OverexposedValue (int, optional): Defines the pixelvalue at whicha pixel counts as overexposed. Defaults to 255.

    Returns:
        _type_: _description_
    """

    if pxSidelen == 0:
        print("AttachBrightnessData: pxTolerance must be > 0!")

    halfTol = pxSidelen / 2
    if halfTol % 1 != 0:
        print(str.format("Half tolerance is not integer! Asymetric brightness-detection by 1 pixel", int(halfTol)))


    imgSets                                                  = BuildFactorImgSets(ssData=ssData, ImgKey=ImgKey, pxSidelen=pxSidelen, AddPxSidelen=AddPxSidelen, OverexposedValue=OverexposedValue, TakeSpotBrightFromAllImgs=TakeSpotBrightFromAllImgs)
    brightSets                                               = GetBrightnessSets(imgSets)
    areaCntSets                                              = GetPxCntSets(imgSets, minBright=MinBright)
    divFactors                                               = GetDivFactorSets(imgSets) #, brightSets, areaCntSets, PxDivTrustband, PxDivMinBright)
    # combinedFactors                                          = CalcCombinedFactorSets(divFactors) # Not used anymore since signal-linearity was proven! -> Factors = Div-Factors
    scaledAnyBright, scaledAnyPxImgs                         = UpscaleAny(imgSets, brightSets, divFactors) #, combinedFactors)
    scaledWhereOverexposedBright, scaledWhereOverexposedImgs = UpscaleOverexposed(imgSets, brightSets, scaledAnyBright, scaledAnyPxImgs)

    return ssData, imgSets, brightSets, areaCntSets, divFactors, scaledAnyBright, scaledAnyPxImgs, scaledWhereOverexposedBright, scaledWhereOverexposedImgs #combinedFactors, , bData#, bImages
