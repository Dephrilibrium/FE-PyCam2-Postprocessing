import os

class PiMageOptions():
  """Creates the object containing all PiMagePro (DataExtraction script) configurations. The class is used to provide a simple "store"-method on save.
  """

  def Save(self, saveDir:str, fName:str):
    """Saves the implemented option to the given save-directory using the given filename.

    Args:
        saveDir (str): Target folderpath
        fName (str, optional): Target filename (incl. extension). Defaults to "PiMageOptions.opt".
    """
    _output = ""

    _output += str.format("# PiMagePro settings\n")


    

    # Processing
    _fill = 25
    _output += str.format("\n[PiMage sequence]\n")
    _output += str.format("PiMage_SkipBadSubdirs"                           .ljust(_fill) + "={}\n", self.PiMage_SkipBadSubdirs)                        # If a parent folder is marked as bad (postfix: _XX) measurement, the subdirectories also skipped!y



    _output += str.format("\n[PiMage-sequence]\n")
    _output += str.format("opt.PiMage_SkipBadSubdirs"                       .ljust(_fill) + "={}\n", self.PiMage_SkipBadSubdirs )                       # If a parent folder is marked as bad (postfix: _XX) measurement, the subdirectories also skipped!y
    _output += str.format("opt.PiMage_ForceOverride"                        .ljust(_fill) + "={}\n", self.PiMage_ForceOverride  )                       # False = Checks for already processed and skips in case; True = Won't check if a measurement is already processed!



    _output += str.format("\n[Visualization]\n")
    _output += str.format("opt.ShowImages_Read"                             .ljust(_fill) + "={}", self.ShowImages_Read               )                       # True = show each image (during debugging); False = Silent process
    _output += str.format("opt.ShowImages_Mean"                             .ljust(_fill) + "={}", self.ShowImages_Mean               )                       # True = show each image (during debugging); False = Silent process
    _output += str.format("opt.ShowImages_SpotDetection"                    .ljust(_fill) + "={}", self.ShowImages_SpotDetection      )                       # True = show each image (during debugging); False = Silent process
    _output += str.format("opt.ShowImages_Draw"                             .ljust(_fill) + "={}", self.ShowImages_Draw               )                       # True = show each image (during debugging); False = Silent process



    _output += str.format("\n[SS Autodetection]\n")
    _output += str.format("opt.DetectSS_AllowedPercentDeviation"            .ljust(_fill) + "={}", self.DetectSS_AllowedPercentDeviation)               # Is the detected SS within the range of an already known SS its counted as the same SS


    _output += str.format("\n[Image processing]\n")
    _output += str.format("opt.Image_CropWin"                               .ljust(_fill) + "={}", self.Image_CropWin              )                    # None/False: Images not cropped; [x, y, w, h]   -   x, y: left upper corner   -   w, h: size of window
    _output += str.format("opt.Image_bThresh"                               .ljust(_fill) + "={}", self.Image_bThresh              )                    # 16bit brightness Threshold value. It's only used, when the threshold of autodetect-algorithm (Image_ThreshType) is smaller than this one!
    _output += str.format("opt.Image_ThreshType"                            .ljust(_fill) + "={}", self.Image_ThreshType           )                    # cv.THRESH_OTSU:                     Tries otsu
                                                                                                                                                        # cv.ADAPTIVE_THRESH_GAUSSIAN_C:      Adaptive won't work with 16bit
                                                                                                                                                        # cv.ADAPTIVE_THRESH_MEAN_C:          Adaptive won't work with 16bit
                                                                                                                                                        # Other else:                         Uses fixed bThres-Value
    _output += str.format("opt.Image_AutoThresDiv"                          .ljust(_fill) + "={}", self.Image_AutoThresDiv         )                    # When ThrehType is used for auto-thresh, the returend threshold is divided by AutoThreshDiv and used to build the actual threshold (used for fine-tuning of threshhold)
    _output += str.format("opt.Image_UseForMeanNPoints"                     .ljust(_fill) + "={}", self.Image_UseForMeanNPoints    )                    # <int>: Means together n measurement-points; ".swp": Tryies to find a sweep-file where it can extract the number of n measurement points
    _output += str.format("opt.Image_MeanNPicsPerSS"                        .ljust(_fill) + "={}", self.Image_MeanNPicsPerSS       )                    # Means n pics (in row) together
    _output += str.format("opt.Image_OverexposedBrightness"                 .ljust(_fill) + "={}", self.Image_OverexposedBrightness)                    # Defines at which 16bit value a pixel counts as overexposed
    _output += str.format("opt.Image_MinBright2CountArea"                   .ljust(_fill) + "={}", self.Image_MinBright2CountArea  )                    # Defines at which 16bit value a pixel counts as brightness-contributing pixel



    _output += str.format("\n[Spot-detection]\n")
    _output += str.format("opt.SpotDetect_Dilate"                           .ljust(_fill) + "={}", self.SpotDetect_Dilate     )                         # Detected image-contours (on thresh-images) are extended by n pixel-rows (entire circumfence) to close small gaps between a splitted spot
    _output += str.format("opt.SpotDetect_Erode"                            .ljust(_fill) + "={}", self.SpotDetect_Erode      )                         # The dilated image-contours are reduced by n pixel-rows (entire circumfence) (if erode=dilate the resulting spot should be the same as initially but whitout missing pixels within)
    _output += str.format("opt.SpotDetect_pxMinRadius"                      .ljust(_fill) + "={}", self.SpotDetect_pxMinRadius)                         # Minimum radius for a valid spot: pxMinRadius <= r <= pxMaxRadius; Used to avoid artifacts detected as spots
    _output += str.format("opt.SpotDetect_pxMaxRadius"                      .ljust(_fill) + "={}", self.SpotDetect_pxMaxRadius)                         # Maximum radius for a valid spot: pxMinRadius <= r <= pxMaxRadius; Used to avoid the detection of spots bigger than being estimated



    _output += str.format("\n[Spot-Draw on Images]\n")
    _output += str.format("opt.CircleDraw_pxRadius"                         .ljust(_fill) + "={}", self.CircleDraw_pxRadius   )                         # Draws a circle using pxRadius to visualize the detected spots on the "circle-draw-images"
    _output += str.format("opt.CircleDraw_AddPxRadius"                      .ljust(_fill) + "={}", self.CircleDraw_AddPxRadius)                         # When enabled, the circles detected spot-radius is added to pxRadius
    _output += str.format("opt.CircleDraw_pxThickness"                      .ljust(_fill) + "={}", self.CircleDraw_pxThickness)                         # Determine the line-thickness of the drawn circles around of each spot respectively each xyKey in [px]


    _output += str.format("\n[Brightness-Extraction]\n")
    _output += str.format("opt.SesExtraction_pxSideLen"                     .ljust(_fill) + "={}", self.SesExtraction_pxSideLen   )                     # Sidelength of a square around the circle center from which the circle-brightness is extracted
    _output += str.format("opt.SesExtraction_AddPxSideLen"                  .ljust(_fill) + "={}", self.SesExtraction_AddPxSideLen)                     # When enabled, the circles radius is added to bDetect_pxSideLen



    _output += str.format("\n[XY-Keys]\n")
    _output += str.format("opt.XYKeys_pxCollectRadius"                      .ljust(_fill) + "={}", self.XYKeys_pxCollectRadius   )                      # Valid radius around a xy-coordinate a detected image-spot is collected under, when located within this area.
    _output += str.format("opt.XYKeys_AddPxCollectRadius"                   .ljust(_fill) + "={}", self.XYKeys_AddPxCollectRadius)                      # When enabled, the image-spots radius is added to SpotDetect_pxMaxRadius
    _output += str.format("opt.XYKeys_FollowSpots"                          .ljust(_fill) + "={}", self.XYKeys_FollowSpots       )                      # When enabled, the xy-key follows the related circle-centers by meaning them
    _output += str.format("opt.XYKeys_pxCorrectionRadius"                   .ljust(_fill) + "={}", self.XYKeys_pxCorrectionRadius)                      # For each SS a set of XY-Key-Pairs can be found. To assign them together, this radius is used as a tolerance and is then re-attached to ssData.
    _output += str.format("opt.XYKeys_CrossCheckKeys"                       .ljust(_fill) + "={}", self.XYKeys_CrossCheckKeys)                          # This option defines if the XYKeys are iterated again and combined if they are in range of each other (range = opt.XYKeys_pxCorrectionRadius)



    _output += str.format("\n[XY-Key Sorting]\n")
    _output += str.format("opt.XYKeySort_Rowdistance"                       .ljust(_fill) + "={}", self.XYKeySort_Rowdistance)                          # Each leftmost spot of a row does a horizontal raycast to the right. XYKeySort_Rowdistance (in [px]) defines the vertical distance to that ray, in which a spot needs to be located to count as part of the row.



    _output += str.format("\n[Dump, Save & Datacopy]\n")
    _output += str.format("opt.PngDump_16bitGrayScale"                      .ljust(_fill) + "={}", self.PngDump_16bitGrayScale                   )      # Dump imagecollection of the raw 16-bit images as PNGs                                                   (highest SS only)
    _output += str.format("opt.PngDump_8bitThreshhold"                      .ljust(_fill) + "={}", self.PngDump_8bitThreshhold                   )      # Dump imagecollection of the raw threshhold images as PNGs                                               (highest SS only)
    _output += str.format("opt.PngDump_8bitCircleDetect"                    .ljust(_fill) + "={}", self.PngDump_8bitCircleDetect                 )      # Dump imagecollection of the dilated and eroded threshhold images, used for the circle-detection as PNGs (highest SS only)
    _output += str.format("opt.PngDump_8bitCircleDrawAroundEachDetection"   .ljust(_fill) + "={}", self.PngDump_8bitCircleDrawAroundEachDetection)      # Dump imagecollection of the 8-bit images with cirlces drawn around each detected spot as PNGs           (highest SS only)
    _output += str.format("opt.PngDump_8bitXYKeyDrawAroundEachXYKey"        .ljust(_fill) + "={}", self.PngDump_8bitXYKeyDrawAroundEachXYKey     )      # Dump imagecollection of the 8-bit images with cirlces drawn around each XYKey as PNGs                   (highest SS only)

    _output += str.format("opt.PklDump_imgContainer"                        .ljust(_fill) + "={}", self.PklDump_imgContainer                     )      # Dump the entire image-container as pickle-binary (all images incl. subarea-images -> HUGE filesize)
    _output += str.format("opt.PklDump_cirContainer"                        .ljust(_fill) + "={}", self.PklDump_cirContainer                     )      # Dump the circle-container as pickle-binary (all circle data)
    _output += str.format("opt.PklDump_pcoContainer"                        .ljust(_fill) + "={}", self.PklDump_pcoContainer                     )      # Dump the PixelCount- and Overexposureinfo-container as pickle-binary
    _output += str.format("opt.PklDump_sesContainer"                        .ljust(_fill) + "={}", self.PklDump_sesContainer                     )      # Dump the SEnsorSignal-container as pickle-binary
    _output += str.format("opt.PklDump_mssContainer"                        .ljust(_fill) + "={}", self.PklDump_mssContainer                     )      # Dump the MergedSensorSignal-container as pickle-binary (combination of the sensor signals on the different SS-images)

    _output += str.format("opt.Copy_FEMDAQData"                       .ljust(_fill) + "={}", self.Copy_FEMDAQData         )           # Creates copies of the relevant FEMDAQ-data (if FEMDAQ was used as measurement-tool!)



    f = open(os.path.join(saveDir, fName), "w")
    f.write(_output)
    f.close()
    return
