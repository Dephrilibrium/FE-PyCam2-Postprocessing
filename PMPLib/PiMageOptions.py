import os

class PiMageOptions():

  # def __init__():
  #   This class has no constructor and collects 
  #    the variables which are added from outside
  #    to save them in a given folder.
  #   return

  def Save(self, saveDir, fName="PiMageOptions.opt"):
    _output = ""

    _output += str.format("# PiMagePro settings\n")

    # Processing
    _fill = 25
    _output += str.format("\n[PiMage sequence]\n")
    _output += str.format("PiMage_SkipBadSubdirs".ljust(_fill)                   + "={}\n", self.PiMage_SkipBadSubdirs)
    _output += str.format("PiMage_ForceOverride".ljust(_fill)                    + "={}\n", self.PiMage_ForceOverride)

    # Visualization
    _output += str.format("\n[Visualization]\n")
    _output += str.format("ShowImages_Read".ljust(_fill)                         + "={}\n", self.ShowImages_Read)
    _output += str.format("ShowImages_Mean".ljust(_fill)                         + "={}\n", self.ShowImages_Mean)
    _output += str.format("ShowImages_Subtract".ljust(_fill)                     + "={}\n", self.ShowImages_Subtract)
    _output += str.format("ShowImages_SpotDetection".ljust(_fill)                + "={}\n", self.ShowImages_SpotDetection)
    _output += str.format("ShowImages_Draw".ljust(_fill)                         + "={}\n", self.ShowImages_Draw)
    _output += str.format("ShowImages_BrightnessExtraction".ljust(_fill)         + "={}\n", self.ShowImages_BrightnessExtraction)

    # Image processing
    _output += str.format("\n[Image processing]\n")
    _output += str.format("Image_CropWin".ljust(_fill)                           + "={}\n", self.Image_CropWin)
    _output += str.format("Image_bThresh".ljust(_fill)                           + "={}\n", self.Image_bThresh)
    _output += str.format("Image_TryOtsu".ljust(_fill)                           + "={}\n", self.Image_TryOtsu)
    _output += str.format("Image_UseForMeanNPoints".ljust(_fill)                 + "={}\n", self.Image_UseForMeanNPoints)
    _output += str.format("Image_MeanNPoints".ljust(_fill)                       + "={}\n", self.Image_MeanNPoints)
    _output += str.format("Image_MeanNPicsPerSS".ljust(_fill)                    + "={}\n", self.Image_MeanNPicsPerSS)
    _output += str.format("Image_OverexposedBrightness".ljust(_fill)             + "={}\n", self.Image_OverexposedBrightness)

    # Spot-detection
    _output += str.format("\n[Spot-detection]\n")
    _output += str.format("SpotDetect_Dilate".ljust(_fill)                       + "={}\n", self.SpotDetect_Dilate)
    _output += str.format("SpotDetect_Erode".ljust(_fill)                        + "={}\n", self.SpotDetect_Erode)
    _output += str.format("CircleDetect_pxMinRadius".ljust(_fill)                + "={}\n", self.CircleDetect_pxMinRadius)
    _output += str.format("CircleDetect_pxMaxRadius".ljust(_fill)                + "={}\n", self.CircleDetect_pxMaxRadius)
    _output += str.format("CircleDetect_AddPxRadius".ljust(_fill)                + "={}\n", self.CircleDetect_AddPxRadius)
    _output += str.format("XYKeys_FollowSpots".ljust(_fill)                      + "={}\n", self.XYKeys_FollowSpots)

    # Spot-Draw on Images
    #  Images with drawed circles are saved for use in papers or for gif-creation
    _output += str.format("\n[Circle-draw]\n")
    _output += str.format("CircleDraw_pxRadius".ljust(_fill)                     + "={}\n", self.CircleDraw_pxRadius)
    _output += str.format("CircleDraw_AddPxRadius".ljust(_fill)                  + "={}\n", self.CircleDraw_AddPxRadius)

    # Brightness-Detection
    _output += str.format("\n[Brightness-detection]\n")
    _output += str.format("bDetect_pxSideLen".ljust(_fill)                       + "={}\n", self.bDetect_pxSideLen)
    _output += str.format("bDetect_AddPxSideLen".ljust(_fill)                    + "={}\n", self.bDetect_AddPxSideLen)
    _output += str.format("bDetect_Trustband".ljust(_fill)                       + "={}\n", self.bDetect_Trustband)
    _output += str.format("bDetect_MinTrust".ljust(_fill)                        + "={}\n", self.bDetect_MinTrust)
    # _output += str.format("bDetect_SaveImages".ljust(_fill)                     + "={}\n", self.bDetect_SaveImages)

    # XY-Keys
    _output += str.format("\n[XYKeys]\n")
    _output += str.format("XYKeys_pxCollectRadius".ljust(_fill)                  + "={}\n", self.XYKeys_pxCollectRadius)
    _output += str.format("XYKeys_AddPxCollectRadius".ljust(_fill)               + "={}\n", self.XYKeys_AddPxCollectRadius)
    _output += str.format("XYKeys_pxCorrectionRadius".ljust(_fill)               + "={}\n", self.XYKeys_pxCorrectionRadius)

    # XY-Key Sorting
    _output += str.format("\n[XYKey Sorting]\n")
    _output += str.format("XYKeySort_Rowdistance".ljust(_fill)                   + "={}\n", self.XYKeySort_Rowdistance)

    # Saving
    _output += str.format("\n[Saving]\n")
    _output += str.format("SaveSSImagePkl".ljust(_fill)                          + "={}\n", self.SaveSSImagePkl)
    # _output += str.format("SaveValidImagePkl".ljust(_fill)                       + "={}\n", self.SaveValidImagePkl)
    # _output += str.format("SaveBrightnessFactors".ljust(_fill)                   + "={}\n", self.SaveBrightnessFactors)
    _output += str.format("Save_ImgSets4Brightness".ljust(_fill)                 + "={}\n", self.Save_ImgSets4Brightness)
    _output += str.format("Save_BrightSets4Brightness".ljust(_fill)              + "={}\n", self.Save_BrightSets4Brightness)
    _output += str.format("Save_PxAreaCnts4Brightness".ljust(_fill)              + "={}\n", self.Save_PxAreaCnts4Brightness)
    _output += str.format("Save_DivFactors4Brightness".ljust(_fill)              + "={}\n", self.Save_DivFactors4Brightness)
    _output += str.format("Save_CombinedFactors4Brightness".ljust(_fill)         + "={}\n", self.Save_CombinedFactors4Brightness)
    _output += str.format("Save_ScaledAnyPxImgs".ljust(_fill)                    + "={}\n", self.Save_ScaledAnyPxImgs)
    _output += str.format("Save_ScaledAnyBrightnesses".ljust(_fill)              + "={}\n", self.Save_ScaledAnyBrightnesses)
    _output += str.format("Save_ScaledWhereOverexposedPxImgs".ljust(_fill)       + "={}\n", self.Save_ScaledWhereOverexposedPxImgs)
    _output += str.format("Save_ScaledWhereOverexposedBrightnesses".ljust(_fill) + "={}\n", self.Save_ScaledWhereOverexposedBrightnesses)

    f = open(os.path.join(saveDir, fName), "w")
    f.write(_output)
    f.close()
    return
