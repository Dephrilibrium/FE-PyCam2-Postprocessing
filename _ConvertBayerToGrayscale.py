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


bayerType = "raw"           # raw bayer
demosaicType = "png"        # gs for gray-scale
nPicsPerSS = 3              # Images taken per SS
nMeasPnts = 1               # Amount of measurements were taken per line (Rpts of sweep per line)

# https://www.strollswithmydog.com/pi-hq-cam-sensor-performance/
# Black-Level typically 256 .. 257.3 depending on gain; For Gain=1 typically 256.3DN
# zeroPxlsBelow < 0: No zeroing
# zeroPxlsBelow = 0: Use Darkimage-Mean + Darkimage-Std
# zeroPxlsBelow > 0: Set "pxls < Value = 0"
# sensBlackLevel = 256 + 12
sensBlackLevel = -1







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
    for _i in range(len(ImgCollection)): # Iterate through images
        img = ImgCollection[_i]                                                         # Grab image
        path = PathCollection[_i]                                                       # Grab corresponding path
        savePaths.append(path.replace("_0000." + bayerType, "_mean." + demosaicType))   # Replace to target-path

        # Save 16bit PNG
        cv.imwrite(savePaths[-1], img)
        print(f"Wrote {basename(savePaths[-1])}", end="\r")                                                # Log for how far it's already gone
    print("")
    return savePaths


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




wds = [
# ### Before Cam-Change!
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_185118 Tip Ch1",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_193753 Tip Ch2",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230406_202712 Tip Ch3",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\02_02 Einzel BurnIn (1kV@IMax250nA)\230408_114847 Tip Ch4",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_131817 Tip1-4 1kV 250nA (Reg. for Tip-Quality)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_143425 Tip1, 3 700V (Sat)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_150043 Tip1, 3 600V (UnSat)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_152323 Tip2, 4 400V (Sat)",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\03_02 Unreg Kombis (IMax5V)\230408_154730 Tip1, 4 400V (UnSat)",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_112532 800V T1-4=2.5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_120802 800V T1-4=0",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_124826 800V T1,4=2.5, T2,3=0",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_133017 800V T1,3=2.5, T2,4=0",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_152121 300V T1-4=5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\04_02 Messungen\230411_153855 500V T1-4=5",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230411_161431 850V T1=2.5, T2-4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230411_170007 600V T1=5, T2-4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230411_173651 850V T2=2.5, T1,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_095047 300V T2=2.5, T1,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_104129 850V T3=2.5, T1,2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_112600 550V T3=2.5, T1,2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_120205 850V T4=2.5, T1,2,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\05_02 Messungen Tips einzeln, Rest floatend\230412_121044 275V T4=2.5, T1,2,3=f",

# ### After Cam-Change
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230414_142228 850V T1=2.5, T2,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230414_162436 850V T2=2.5, T1,3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230414_171309 1kV T3=2.5, T1,2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_02 Reaktivierungsversuche\230416_113420 1kV T4=2.5, T1,2,3=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_124224 850V T1-4=2.5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_130710 650V T1-4=2.5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_132804 600V T1-4=2.5",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_140248 850V T2,3,4=2.5, T1=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_143702 650V T2,3,4=5, T1=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_151519 850V T2,4=2.5, T1,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_153805 650V T2,4=5, T1,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_155756 575V T2,4=5, T1,3=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230416_164211 850V T2,3=2.5, T1,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_091311 650V T2,3=5, T1,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_093726 650V T2,3=5, T1,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_100014 650V T2,3=5, T1,4=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_103529 850V T3,4=2.5, T1,2=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_111937 600V T3,4=5, T1,2=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_120247 850V T1,2=2.5, T3,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_124704 650V T1,2=5, T3,4=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_132015 850V T1,3=2.5, T2,4=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_140546 550V T1,3=5, T2,4=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_154117 550V T1,4=2.5, T2,3=f",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\08_03 Kombis\230417_163540 550V T1,4=2.5, T2,3=f",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230417_171941 850V T1-4=2.5",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230417_174418 700V T1-4=1",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230418_085317 850V T1-4=2.5",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_094854 450V T1=2.5, T2,3,4=gnd",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_101154 450V T1=5, T2,3,4=gnd",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_104503 850V T2=2.5, T1,3,4=gnd",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_112114 950V T2=5, T1,3,4=gnd",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_115301 750V T3=2.5, T1,2,4=gnd",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_121938 750V T3=5, T1,2,4=gnd",

# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_124726 650V T4=2.5, T1,2,3=gnd",
# r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_131423 650V T4=5, T1,2,3=gnd",


# 21x21
# r"D:\05 PiCam\Jachym-Compress\Jachym",
r"D:\05 PiCam\230612 HQCam SOI21x21_0003",
# r"D:\05 PiCam\230612 HQCam SOI21x21_0001\Messungen\02_02 Some Sweeps\230614_090038 550V (regulated)",
]

dumpBlackSub = True             # True: BlackSubtraction Image is dumped as PNG too
bayerType = "raw"               # raw bayer
demosaicType = "png"            # gs for gray-scale
nPicsPerSS = 3                  # Images taken per SS
nMeasPnts = 1                   # Amount of measurements were taken per line (Rpts of sweep per line)

ConvertImageByImage = True     # Big size images can cause a "out of RAM" exception, when all images
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
            if nPicsPerSS > 1:
                if _nConvIteration == 0: # BlackImages only on first cycle
                    print(f"Meaning Darkfield-Images (nPicsPerSS)...")
                    blckImgs = MeanImages(ImgCollection=blckImgs, ImgsPerMean=nPicsPerSS, ShowImg=False)        # Meaning nPicsPerSS
                    blckClipPaths = blckPaths[::nPicsPerSS]

                print(f"Meaning Measurement-Images (nPicsPerSS)...")
                measImgs = MeanImages(ImgCollection=measImgs, ImgsPerMean=nPicsPerSS, ShowImg=False)        # Meaning nPicsPerSS
                measClipPaths = measPaths[::nPicsPerSS]

            # Meaning nMeasPnts
            if nMeasPnts > 1:
                if _nConvIteration == 0: # BlackImages only on first cycle
                    print(f"Meaning Darkfield-Images (nMeasPnts)...")
                    blckImgs = MeanImages(ImgCollection=blckImgs, ImgsPerMean=nMeasPnts, ShowImg=False)     # Meaning nMeasPnts
                    blckClipPaths = blckClipPaths[::nMeasPnts]

            # Dump also BlackImages if requested!
            if dumpBlackSub == True:
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
                        blackStd = int(np.std(blckImgs) * 6) # 6 Sigma
                        if blackStd == 0:
                            blackStd = 1
                        if blackStd < blackMean:
                            print(f"6 sigma < mean; Using mean + 6 sigma of dark-image: ", end="")
                            sensBlackLevel = blackMean + blackStd
                        else:
                            print(f"6 sigma > mean; Using mean of dark-image: ", end="")
                            sensBlackLevel = blackMean
                    else:
                        print(f"Using fix value: ", end="")
                    print(f"Determined Blacklevel-value: {sensBlackLevel:.2f}")


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
            png16Paths = DumpCollectionAs16BitPNG(measImgs, measClipPaths)
            print(f"PNG-Dump of Measurement images took: {(time()-start):.3f}s")


            # Remove the original bayer data files
            print("Deleting obsolet .raw-files...")
            # if _nConvIteration == (_nConversions-1):
            #     DeleteFiles(blckPaths)
            # DeleteFiles(measPaths)


print("Finished")