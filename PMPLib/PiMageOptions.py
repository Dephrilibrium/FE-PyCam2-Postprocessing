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
    _output += str.format("PiMage_SkipBadSubdirs".ljust(_fill)                  + "={}\n", self.PiMage_SkipBadSubdirs)              # If a parent folder is marked as bad (postfix: _XX) measurement, the subdirectories also skipped!y
    _output += str.format("PiMage_ForceOverride".ljust(_fill)                   + "={}\n", self.PiMage_ForceOverride)               # False = Checks for already processed and skips in case; True = Won't check if a measurement is already processed!

    # Visualization
    _output += str.format("\n[Visualization]\n")
    _output += str.format("ShowImages_Read".ljust(_fill)                        + "={}\n", self.ShowImages_Read)                    # True = show each image (during debugging); False = Silent process
    _output += str.format("ShowImages_Mean".ljust(_fill)                        + "={}\n", self.ShowImages_Mean)                    # True = show each image (during debugging); False = Silent process
    _output += str.format("ShowImages_SpotDetection".ljust(_fill)               + "={}\n", self.ShowImages_SpotDetection)           # True = show each image (during debugging); False = Silent process
    _output += str.format("ShowImages_Draw".ljust(_fill)                        + "={}\n", self.ShowImages_Draw)                    # True = show each image (during debugging); False = Silent process

    # Image processing
    _output += str.format("\n[Image processing]\n")
    _output += str.format("Image_CropWin".ljust(_fill)                          + "={}\n", self.Image_CropWin)                      # None/False: Images not cropped; [x, y, w, h]   -   x, y: left upper corner   -   w, h: size of window
    _output += str.format("Image_bThresh".ljust(_fill)                          + "={}\n", self.Image_bThresh)                      # 8bit brightness Threshold value. It's only used, when the threshold of autodetect-algorithm (Image_ThreshType) is smaller than this one!
    _output += str.format("Image_ThreshType".ljust(_fill)                       + "={}\n", self.Image_ThreshType)                   # cv.THRESH_OTSU:                     Tries otsu
                                                                                                                                    #  cv.ADAPTIVE_THRESH_GAUSSIAN_C:      Adaptive won't work with 16bit
                                                                                                                                    #  cv.ADAPTIVE_THRESH_MEAN_C:          Adaptive won't work with 16bit
                                                                                                                                    #  Other else:                         Uses fixed bThres-Value
    _output += str.format("Image_AutoThresDiv".ljust(_fill)                     + "={}\n", self.Image_AutoThresDiv)                 # When ThreshType is used for auto-thresh, the returend threshold is divided by AutoThreshDiv and used to build the actual threshold (used for fine-tuning of threshhold)
    _output += str.format("Image_UseForMeanNPoints".ljust(_fill)                + "={}\n", self.Image_UseForMeanNPoints)            # <int>: Means together n measurement-points; ".swp": Tryies to find a sweep-file where it can extract the number of n measurement points
    _output += str.format("Image_MeanNPicsPerSS".ljust(_fill)                   + "={}\n", self.Image_MeanNPicsPerSS)               # Means n pics (in row) together
    _output += str.format("Image_OverexposedBrightness".ljust(_fill)            + "={}\n", self.Image_OverexposedBrightness)        # Defines at which 16bit value a pixel counts as overexposed
    _output += str.format("Image_MinBright2CountArea".ljust(_fill)              + "={}\n", self.Image_MinBright2CountArea)          # Defines at which 16bit value a pixel counts as brightness-contributing pixel
 
    # Spot-detection
    _output += str.format("\n[Spot-detection]\n")
    _output += str.format("SpotDetect_Dilate".ljust(_fill)                      + "={}\n", self.SpotDetect_Dilate)                  # Detected image-contours (on thresh-images) are extended by n pixel-rows (entire circumfence) to close small gaps between a splitted spot
    _output += str.format("SpotDetect_Erode".ljust(_fill)                       + "={}\n", self.SpotDetect_Erode)                   # The dilated image-contours are reduced by n pixel-rows (entire circumfence) (if erode=dilate the resulting spot should be the same as initially but whitout missing pixels within)
    _output += str.format("CircleDetect_pxMinRadius".ljust(_fill)               + "={}\n", self.CircleDetect_pxMinRadius)           # Minimum radius for a valid spot: pxMinRadius <= r <= pxMaxRadius; Used to avoid artifacts detected as spots
    _output += str.format("CircleDetect_pxMaxRadius".ljust(_fill)               + "={}\n", self.CircleDetect_pxMaxRadius)           # Maximum radius for a valid spot: pxMinRadius <= r <= pxMaxRadius; Used to avoid the detection of spots bigger than being estimated

    # Spot-Draw on Images
    #  Images with drawed circles are saved for use in papers or for gif-creation
    _output += str.format("\n[Circle-draw]\n")
    _output += str.format("CircleDraw_pxRadius".ljust(_fill)                     + "={}\n", self.CircleDraw_pxRadius)               # Draws a circle using pxRadius to visualize the detected spots on the "circle-draw-images"
    _output += str.format("CircleDraw_AddPxRadius".ljust(_fill)                  + "={}\n", self.CircleDraw_AddPxRadius)            # When enabled, the circles detected spot-radius is added to pxRadius

    # Brightness-Detection
    _output += str.format("\n[Brightness-detection]\n")
    _output += str.format("bDetect_SpotBrightFromAllImgs".ljust(_fill)           + "={}\n", self.bDetect_SpotBrightFromAllImgs)     # When enabled, the brightness is extracted from ALL images based on the xy-key position! (NOTE: This ensures, that all vectors have the same)
    _output += str.format("bDetect_pxSideLen".ljust(_fill)                       + "={}\n", self.bDetect_pxSideLen)                 # Sidelength of a square around the circle center from which the circle-brightness is extracted
    _output += str.format("bDetect_AddPxSideLen".ljust(_fill)                    + "={}\n", self.bDetect_AddPxSideLen)              # When enabled, the circles radius is added to bDetect_pxSideLen

    # XY-Keys
    _output += str.format("\n[XYKeys]\n")
    _output += str.format("XYKeys_pxCollectRadius".ljust(_fill)                  + "={}\n", self.XYKeys_pxCollectRadius)            # Valid radius around a xy-coordinate a detected image-spot is collected under, when located within this area.
    _output += str.format("XYKeys_AddPxCollectRadius".ljust(_fill)               + "={}\n", self.XYKeys_AddPxCollectRadius)         # When enabled, the image-spots radius is added to CircleDetect_pxMaxRadius
    _output += str.format("XYKeys_FollowSpots".ljust(_fill)                      + "={}\n", self.XYKeys_FollowSpots)                # When enabled, the xy-key follows the related circle-centers by meaning them
    _output += str.format("XYKeys_pxCorrectionRadius".ljust(_fill)               + "={}\n", self.XYKeys_pxCorrectionRadius)         # For each SS a set of XY-Key-Pairs can be found. To assign them together, this radius is used as a tolerance and is then re-attached to ssData.

    # XY-Key Sorting
    _output += str.format("\n[XYKey Sorting]\n")
    _output += str.format("XYKeySort_Rowdistance".ljust(_fill)                   + "={}\n", self.XYKeySort_Rowdistance)             # Each leftmost spot of a row does a horizontal raycast to the right. XYKeySort_Rowdistance (in [px]) defines the vertical distance to that ray, in which a spot needs to be located to count as part of the row.

    # Saving
    _output += str.format("\n[Saving]\n")
    _output += str.format("SaveSSImagePkl".ljust(_fill)                          + "={}\n", self.SaveSSImagePkl)                           # Save internal raw ssData structure
    _output += str.format("Save_ImgSets4Brightness".ljust(_fill)                 + "={}\n", self.Save_ImgSets4Brightness)                  # Save "Imageset"                                             for Brightnesses and it's correction as pickle
    _output += str.format("Save_BrightSets4Brightness".ljust(_fill)              + "={}\n", self.Save_BrightSets4Brightness)               # Save "Brightnesses"                                         from Imageset as pickle
    _output += str.format("Save_PxAreaCnts4Brightness".ljust(_fill)              + "={}\n", self.Save_PxAreaCnts4Brightness)               # Save "PixelArea-Counts & -Factors"                          from Imageset as pickle
    _output += str.format("Save_DivFactors4Brightness".ljust(_fill)              + "={}\n", self.Save_DivFactors4Brightness)               # Save "Division-Correction-Factors"                          from BrightSets as pickle
    _output += str.format("Save_ScaledAnyPxImgs".ljust(_fill)                    + "={}\n", self.Save_ScaledAnyPxImgs)                     # Save "Any upscaled pixelcorrected images"                   as pickle (huge!)
    _output += str.format("Save_ScaledAnyBrightnesses".ljust(_fill)              + "={}\n", self.Save_ScaledAnyBrightnesses)               # Save "Any upscaled spotbrightness"                          as pickle
    _output += str.format("Save_ScaledWhereOverexposedPxImgs".ljust(_fill)       + "={}\n", self.Save_ScaledWhereOverexposedPxImgs)        # Save "Any upscaled spotbrightness images"                   as pickle
    _output += str.format("Save_ScaledWhereOverexposedBrightnesses".ljust(_fill) + "={}\n", self.Save_ScaledWhereOverexposedBrightnesses)  # Save "Upscaled spotbrightness where overexposure occured"   as pickle
    _output += str.format("Save_FEMDAQCopies".ljust(_fill)                       + "={}\n", self.Save_FEMDAQCopies)                        # Creates copies of the relevant FEMDAQ-data (if FEMDAQ was used as measurement-tool!)




    f = open(os.path.join(saveDir, fName), "w")
    f.write(_output)
    f.close()
    return
