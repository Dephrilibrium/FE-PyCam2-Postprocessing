##################################################################################
# This script converts raw bayer data into 16 bit grayscale images and means     #
# nPicsPerSS * nMeasPnts = nPicsToMean together.                                 #
# E.g.:                                                                          #
#  nPicsPerSS = 3, nMeasPnts = 1: [mean(imgs[0:3]), mean(imgs[3:6]), etc...]     #
#  nPicsPerSS = 3, nMeasPnts = 2: [mean(imgs[0:6]), mean(imgs[6:12]), etc...]    #
#                                                                                #
# The PyCam2-Server already supports this conversion, but its implemented as an  #
# option which can be deactivated, as the conversion consumes much time which    #
# can be avoided by converting the images via post-processing.                   #
#                                                                                #
# As PNGs further compress the images, the resulting image-folder only have a    #
# datasize of a view tens of MB.                                                 #
#                                                                                #
# How to use (variable explanation):                                             #
# wds:              List of folders which are  scanned recursevly for raw bayer- #
#                    data
# bayerType:        Extension-filter string to search for the bayer-data-files.  #
# demosaicType:     Extension in which the files should be stored.               #
# nPicsPerSS:       Defines how much images are meaned together pixel by pixel.  #
# nMeasPnts:        Defines how much measurement points were carried out in a    #
#                    row.                                                        #
# sensBlackLevel:   Is used to subtract the black-level (see options below!)     #
#                                                                                #
# 2023 © haum (OTH-Regensburg)                                                   #
##################################################################################

import os
from os.path import join, basename, dirname, isdir, exists, isfile
import numpy as np
import numpngw as npng
from PIL import Image
import matplotlib.pyplot as plt
import pickle
import glob
import natsort
import parse

from colorama import Fore, Style
from time import time

from PIL import Image
import cv2 as cv

from PMPLib.ImgFileHandling import GrabSSFromFilenames, ReadImageFilepaths, ReadImagesFromPaths, ReadImages, BlackFormat, ImageFormat
from PMPLib.ImgManipulation import MeanImages, SubtractFromImgCollection, DemosaicBayer, ConvertBitsPerPixel, StretchBrightness
from misc import DurationOfLambda





def DumpCollectionAs16BitPNG(ImgCollection, PathCollection):
    """Saves the iterable ImgCollection as 16 bit grayscale PNGs with the names of PathCollection. Normally the mean images are stored with this function.

    Args:
        ImgCollection (iterable image data): Iterable object of 16bit images
        PathCollection (iterable strings): Iterable object containing the filenames (including folder) of the "0000" images (first image of a measurement-point)

    Returns:
        iterable strings: Iterable object containing the actual filenames the images were saved as.
    """
    savePaths = []
    saveState = True
    for _i in range(len(ImgCollection)): # Iterate through images
        img = ImgCollection[_i]                                                         # Grab image
        path = PathCollection[_i]                                                       # Grab corresponding path
        savePaths.append(path.replace("_0000." + bayerType, "_mean." + demosaicType))   # Replace to target-path

        # Save 16bit PNG
        _saved = cv.imwrite(savePaths[-1], img)
        if _saved:
            print(f"Wrote {basename(savePaths[-1])}", end="\r")                                                # Log for how far it's already gone
        else:
            print(f"{Fore.RED}Couldn't write {basename(savePaths[-1])}{Fore.RESET}")                                                # Log for how far it's already gone
            print(f"{Fore.RED}Check your path for illegal characters (opencv don't like \"µ\" for instance){Fore.RESET}")                                                # Log for how far it's already gone
            saveState = False
    
    if _saved: # When last image was a success, add a new line
        print("")
    return savePaths, saveState


def DumpCollectionIntoPNG8(ImgCollection, PathCollection):
    """Saves the iterable ImgCollection as 8 bit grayscale PNGs with the names of PathCollection. Normally the mean images are stored with this function.

    Args:
        ImgCollection (iterable image data): Iterable object of 8bit images
        PathCollection (iterable strings): Iterable object containing the filenames (including folder) of the "0000" images (first image of a measurement-point)

    Returns:
        iterable strings: Iterable object containing the actual filenames the images were saved as.
    """
    savePaths = []

    png8Target = "PNG8"
    fPath = dirname(PathCollection[0])
    fPath = fPath.replace("Pics", png8Target)
    if not exists(fPath):
        os.mkdir(fPath)

    for _i in range(len(ImgCollection)):
        img = ImgCollection[_i]                                                         # Grab image
        # img = np.right_shift(img, 4).astype(np.uint8)
        path = PathCollection[_i]                                                       # Grab corresponding path
        path = path.replace("_0000." + bayerType, "_mean." + demosaicType)
        path = path.replace("Pics", png8Target)
        savePaths.append(path)   # Replace to target-path

        # Save 16bit PNG
        # npng.write_png(savePaths[-1], img)
        cv.imwrite(savePaths[-1], img)
        # plt.imsave(savePaths[-1], img, cmap="gray")
        # pilim = Image.fromarray(img.astype(np.uint32))
        # pilim.save(savePaths[-1])
        print(f"Wrote {basename(savePaths[-1])}", end="\r")                                                # Log for how far it's already gone
    print("")
    return savePaths



def DumpCollectionAsGray(ImgCollection, PathCollection):
    """Saves the iterable ImgCollection binary pickle-files (.gray extension) with the names of PathCollection. Normally the mean images are stored with this function.

    Args:
        ImgCollection (iterable image data): Iterable object of images
        PathCollection (iterable strings): Iterable object containing the filenames (including folder) of the "0000" images (first image of a measurement-point)

    Returns:
        iterable strings: Iterable object containing the actual filenames the images were saved as.
    """
    savePaths = []
    for _i in range(len(ImgCollection)):
        img = ImgCollection[_i]                                     # Grab image
        path = PathCollection[_i]                                   # Grab corresponding path
        savePaths.append(path.replace("_0000." + bayerType, "_mean.gray"))   # Replace to target-path

        # Save Img
        fGray = open(savePaths[-1], "wb")
        pickle.dump(img, fGray)
        fGray.close()
        print(f"Wrote {basename(savePaths[-1])}", end="\r")                            # Log for how far it's already gone
    print("")
    return savePaths




def DeleteFiles(FilepathCollection):
    """Deletes all files from the iterable filepath-collection.

    Args:
        FilepathCollection (iterable): Iterable object of filepaths (strings) which should be deleted.
    """
    for _path in FilepathCollection:
        os.remove(_path)
    return






















###### USER AREA ######
wds = [
# 21x21
r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_171103 700V IMax1V",
r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_173431 500V IMax1V - 15m (full unsat.)",
r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_175303 700V IMax1V",
r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_181207 700V IMax1V - 15m (start was sat.)",
r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_183133 700V IMax1V",
r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_185401 1000V IMax1V - 15m (fully sat.)",
r"D:\05 PiCam\230719 HQCam SOI21x21_0003 150nm Cu-Cam\Messungen\08_01 10k, SSList\230727_193006 700V IMax1V",
]



dumpBlackImgs = False           # True: BlackSubtraction Image is dumped as PNG too
deleteRawAfter = True           # True: Unpacked RAW-files from .tars are removed after conversion!
bayerType = "raw"               # raw bayer
demosaicType = "png"            # gs for gray-scale
nPicsPerSS = 3                  # Images taken per SS
nMeasPnts = 1                   # Amount of measurements were taken per line (Rpts of sweep per line)

ConvertImageByImage = True      # Big size images can cause a "out of RAM" exception, when all images
                                #  loaded simultaneously into RAM.
                                #  This option splits up all measurement-image paths into blocks which 
                                #  converts exactly one mean image for the steps:
                                #  1.) Loading nPicsPerSS images from hard-disk into RAM
                                #  2.) Demosaicking each
                                #  3.) Subtracting the blacklevel
                                #  4.) Converting from 12bit to 16bit range
                                #  4.) Dumping 16bit PNG and
                                #  6.) Removing the old raw-images from hard-disk

# https://www.strollswithmydog.com/pi-hq-cam-sensor-performance/
# Black-Level typically 256 .. 257.3 depending on gain; For Gain=1 typically 256.3DN
# zeroPxlsBelow < 0: No zeroing
# zeroPxlsBelow = 0: Use Darkimage-Mean + Darkimage-Std
# zeroPxlsBelow > 0: Set "pxls < Value = 0"
# sensBlackLevel = 256 + 12   # Mean + Std
sensBlackLevel = 0











###### DO NOT TOUCH AREA ######
for _fold in wds: # Iterate working directories

    for root, dirs, files in os.walk(_fold): # Iterate current wd recurively

        print(f"Postprocessing: {root}")
        files = glob.glob(join(root, "*." + bayerType))
        # files = natsort.os_sorted(files)
        if len(files) <= 0:
            print(f"Couldn't find any {bayerType}-Files. Continuing to next folder")
            continue


        # Darkfield images
        print(f"Reading Darkfield-Images...")
        blckImgs, blckPaths = ReadImages(FolderPath=root, Format=str.format(BlackFormat, "*", "*", "*", "raw")     , CropWindow=None, IgnorePathVector=None, ShowImg=False)

        # We need the entire blackPaths before they are modfied by the mean,
        #   which is why we need to grab the filenames here already, but use
        #   them at for _nImgIteration... etc... below
        _imgFilepaths = ReadImageFilepaths(FolderPath=root, Format=str.format(ImageFormat, "*", "*", "*", "*", "raw"), IgnorePathVector=blckPaths)

        # Determine the amount of conversation iterations
        #  nConversions = nSS * nMeasPnts * nImgsPerSS
        #  with: 
        #   -> nMeasPnts = How much measurement points were taken per target-value (e.g. a specific extraction voltage)
        #   -> nSS = Amount of Shutterspeeds at which images were captured
        #   -> nImgsPerSS = Amount of images captured per Shutterspeed
        if ConvertImageByImage == True:
            _nConversions = len(_imgFilepaths) // (nPicsPerSS * nMeasPnts)
        else:
            _nConversions = 1

        # Measurement image reading and meaning!
        for _nConvIteration in range(_nConversions):
            if _nConversions > 1:
                _iFilestart = _nConvIteration * (nPicsPerSS * nMeasPnts)
                _iFilestop  = _iFilestart + (nPicsPerSS * nMeasPnts)
                measPaths = _imgFilepaths[_iFilestart:_iFilestop]
            else:
                measPaths = _imgFilepaths

            print(f"Reading Measurement-Images...")
            measImgs = ReadImagesFromPaths(Filepaths=measPaths, cvFlags=cv.IMREAD_ANYDEPTH | cv.IMREAD_GRAYSCALE, CropWindow=None, ShowImg=False)
            # measImgs, measPaths = ReadImages(FolderPath=root, Format=str.format(ImageFormat, "*", "*", "*", "*", "raw"), CropWindow=None, IgnorePathVector=blckPaths, ShowImg=None)

            if _nConvIteration == 0: # Blackimage only on first cycle
                print(f"Demosaic Darkfield-Bayer 2 Grayscale...")
                blckImgs = DemosaicBayer(blckImgs)
            print(f"Demosaic Measurement-Bayer 2 Grayscale...")
            measImgs = DemosaicBayer(measImgs)

            # Meaning nPicsPerSS
            blckClipPaths = blckPaths.copy() # If nPicsPerSS == 1 && nMeasPnts == 1 --> measClipPath = measPaths
            measClipPaths = measPaths.copy() # If nPicsPerSS == 1 && nMeasPnts == 1 --> measClipPath = measPaths
            if nPicsPerSS > 1:
                if _nConvIteration == 0: # BlackImages only on first cycle
                    print(f"Meaning Darkfield-Images (nPicsPerSS)...")
                    blckImgs = MeanImages(ImgCollection=blckImgs, ImgsPerMean=nPicsPerSS, ShowImg=False)        # Meaning nPicsPerSS
                    blckClipPaths = blckClipPaths[::nPicsPerSS]

                print(f"Meaning Measurement-Images (nPicsPerSS)...")
                measImgs = MeanImages(ImgCollection=measImgs, ImgsPerMean=nPicsPerSS, ShowImg=False)        # Meaning nPicsPerSS
                measClipPaths = measClipPaths[::nPicsPerSS]

            # Meaning nMeasPnts
            if nMeasPnts > 1:
                if _nConvIteration == 0: # BlackImages only on first cycle
                    print(f"Meaning Darkfield-Images (nMeasPnts)...")
                    blckImgs = MeanImages(ImgCollection=blckImgs, ImgsPerMean=nMeasPnts, ShowImg=False)     # Meaning nMeasPnts
                    blckClipPaths = blckClipPaths[::nMeasPnts]

            # Dump also BlackImages if requested!
            if dumpBlackImgs == True:
                if _nConvIteration == 0:
                    print(f"12Bit BlackSubtraction-Images -> 16Bit Images...")
                    blkImgs4Save = ConvertBitsPerPixel(ImgCollection=blckImgs.copy(), originBPP=12, targetBPP=16)
                    print(f"Dumping BlackSubtraction-Images...")
                    DumpCollectionAs16BitPNG(blkImgs4Save, blckClipPaths)
                    del blkImgs4Save # Free RAM after use


                print(f"Meaning Measurement-Images (nMeasPnts)...")
                measImgs = MeanImages(ImgCollection=measImgs, ImgsPerMean=nMeasPnts, ShowImg=False)     # Meaning nMeasPnts
                measClipPaths = measClipPaths[::nMeasPnts]

            # Subtract blacklevel
            if sensBlackLevel >= 0:
                if _nConvIteration == 0:
                    print(f"Determining 12bit blacklevel from blackimages...")
                    if sensBlackLevel == 0:
                        blackMean = int(np.mean(blckImgs))
                        if blackMean == 0:
                            blackMean = 1
                        blackStd = int(np.std(blckImgs) * 3) # +- 3 Sigma = 6 Sigma
                        if blackStd == 0:
                            blackStd = 1
                        if blackStd < blackMean:
                            print(f"6 sigma < mean; Using mean + 3 sigma of dark-image: ", end="")
                            sensBlackLevel = blackMean + blackStd
                        else:
                            print(f"6 sigma > mean; Using mean of dark-image: ", end="")
                            sensBlackLevel = blackMean
                    else:
                        print(f"Using fix value: ", end="")
                    print(f"Determined Blacklevel-value: {sensBlackLevel:.2f}")

                    if sensBlackLevel > 0x0FFF: # 12bit maximum value!
                        print(f"{Fore.RED}!!! ERROR !!!")
                        print(f"{Fore.RED}Blacklevel-value > 12bit-maximum-value --> {sensBlackLevel} > {4095}")
                        print(f"{Fore.RED}The process will continue, but you will receive only complete black images!{Fore.RESET}")
                    if sensBlackLevel > 310:    # Normal is 250-300
                        print(f"{Fore.YELLOW}!!! WARNING !!!")
                        print(f"{Fore.YELLOW}Blacklevel-value is abnormal high --> {sensBlackLevel} > {310}")
                        print(f"{Fore.YELLOW}The process will continue, but check your data manually!{Fore.RESET}")


                print(f"Subtracting black-level from 12Bit Images...")
                print(f"Condition: if(pixelbright < {sensBlackLevel:.2f}) = 0")             # Moved up so that the blacklevel is only determined once
                if _nConvIteration == (_nConversions-1):                                    # Run it on black images only at the last cycle (just for checking if all pixels become nearly 0)
                    blckImgs = SubtractFromImgCollection(blckImgs, sensBlackLevel)
                measImgs = SubtractFromImgCollection(measImgs, sensBlackLevel)
                measImgs = StretchBrightness(measImgs, blackLevel=sensBlackLevel, whiteLevel=0xFFF) # 12bit max


            # 12 bit -> 16 bit shift (values pixelwise << 4)
            print(f"12Bit Measurement-Images -> 16Bit Images...")
            measImgs = ConvertBitsPerPixel(ImgCollection=measImgs, originBPP=12, targetBPP=16)

            # Saving 16bit PNGs
            print("Dumping Measurement-Images as 16bit-PNGs for PiMagePro...")
            start = time()
            # pklPaths = DumpCollectionAsGray(measImgs, measClipPaths)
            png16Paths, saveOk = DumpCollectionAs16BitPNG(measImgs, measClipPaths)
            print(f"PNG-Dump of Measurement images took: {(time()-start):.3f}s")


            # Remove the original bayer data files
            if deleteRawAfter == True:
                if saveOk:
                    print("Deleting obsolet .raw-files...")
                    if _nConvIteration == (_nConversions-1):
                        DeleteFiles(blckPaths)
                    DeleteFiles(measPaths)
                else:
                    print("Skip deleting .raw-files, as there was images which couldn't be written!")

print("Finished")