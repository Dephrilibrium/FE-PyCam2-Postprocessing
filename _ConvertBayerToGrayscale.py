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

from PMPLib.ImgFileHandling import ReadImages, OTH_BlkFormat, OTH_ImgFormat
from PMPLib.ImgManipulation import MeanImages, SubtractFromImgCollection, DemosaicBayer, ConvertBitsPerPixel, StretchBrightness
from misc import DurationOfLambda





def DumpCollectionAs16BitPNG(ImgCollection, PathCollection):
    savePaths = []
    for _i in range(len(ImgCollection)):
        img = ImgCollection[_i]                                                         # Grab image
        path = PathCollection[_i]                                                       # Grab corresponding path
        savePaths.append(path.replace("_0000." + bayerType, "_mean." + demosaicType))   # Replace to target-path

        # Save 16bit PNG
        # npng.write_png(savePaths[-1], img)
        cv.imwrite(savePaths[-1], img)
        # plt.imsave(savePaths[-1], img, cmap="gray")
        # pilim = Image.fromarray(img.astype(np.uint32))
        # pilim.save(savePaths[-1])
        print(f"Wrote {basename(savePaths[-1])}", end="\r")                                                # Log for how far it's already gone
    print("")
    return savePaths


def DumpCollectionIntoPNG8(ImgCollection, PathCollection):
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
    for _path in FilepathCollection:
        os.remove(_path)
    return




folders = [
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\01 Aktivierung IMax1V\230221_115432 Tip Ch1 (aktiviert, 6517)",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\01 Aktivierung IMax1V\230221_124600 Tip Ch2 (aktiviert)",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\01 Aktivierung IMax1V\230222_095249 Tip Ch3 (aktiviert)",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\01 Aktivierung IMax1V\230222_103240 Tip Ch4 (aktiviert)",

# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\02 Alle Zusammen\230222_160417 1kV 100nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\02 Alle Zusammen\230223_084426 1kV 250nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\02 Alle Zusammen\230306_124505 1kV 250nA #1",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\02 Alle Zusammen\230306_140339 1kV 250nA #2",

r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\03 Sample-Sweeps\230307_124953 1kV IMax500nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\03 Sample-Sweeps\230308_085027 1kV IMax 250nA",

# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\04 USwp für bessere Charakteristik\230308_133039",

# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_143559 USwp 1kV, IMax250nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_151018 ZickZack 1by1 linStps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_154416 ZickZack 1by1 linStps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_164837 USwp 1kV, IMax250nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_172255 ZickZack 1by1 log10Stps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_175658 ZickZack 1by1 log10Stps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\05 ZigZag 1b1\230308_190251 USwp 1kV, IMax250nA",

# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_200641 USwp 1kV, IMax250nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_202958 ZickZack 1while1 linStps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_205330 ZickZack 1while1 linStps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_215722 USwp 1kV, IMax250nA",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_222134 ZickZack 1by1 log10Stps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_224524 ZickZack 1by1 log10Stps",
# r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Messungen\06 ZigZag 1w1\230308_234915 USwp 1kV, IMax250nA",
]

bayerType = "raw"           # raw bayer
demosaicType = "png"        # gs for gray-scale
nPicsPerSS = 3              # Images taken per SS
nMeasPnts = 1               # Amount of measurements were taken per line (Rpts of sweep per line)

# https://www.strollswithmydog.com/pi-hq-cam-sensor-performance/
# Black-Level typically 256 .. 257.3 depending on gain; For Gain=1 typically 256.3DN
# zeroPxlsBelow < 0: No zeroing
# zeroPxlsBelow = 0: Use Darkimage-Mean
# zeroPxlsBelow > 0: Set "pxls < Value = 0"
sensBlackLevel = 256 + 12




for _fold in folders:

    for root, dirs, files in os.walk(_fold):

        print(f"Postprocessing: {root}")
        files = glob.glob(join(root, "*." + bayerType))
        # files = natsort.os_sorted(files)
        if len(files) <= 0:
            print(f"Couldn't find any {bayerType}-Files. Continuing to next folder")
            continue

        print(f"Reading Darkfield-Images...")
        blckImgs, blckPaths = ReadImages(fPaths=root, Format=str.format(OTH_BlkFormat, "*", "*", "*", "raw")     , CropWindow=None, IgnorePathVector=None, ShowImg=False)

        print(f"Reading Measurement-Images...")
        measImgs, measPaths = ReadImages(fPaths=root, Format=str.format(OTH_ImgFormat, "*", "*", "*", "*", "raw"), CropWindow=None, IgnorePathVector=blckPaths, ShowImg=None)

        print(f"Demosaic Darkfield-Bayer 2 Grayscale...")
        blckImgs = DemosaicBayer(blckImgs)
        print(f"Demosaic Measurement-Bayer 2 Grayscale...")
        measImgs = DemosaicBayer(measImgs)
        
        if nPicsPerSS > 1:
            print(f"Meaning Darkfield-Images (nPicsPerSS)...")
            blckImgs = MeanImages(ImgCollection=blckImgs, ImgsPerMean=nPicsPerSS, ShowImg=False)        # Meaning nPicsPerSS
            blckClipPaths = blckPaths[::nPicsPerSS]

            print(f"Meaning Measurement-Images (nPicsPerSS)...")
            measImgs = MeanImages(ImgCollection=measImgs, ImgsPerMean=nPicsPerSS, ShowImg=False)        # Meaning nPicsPerSS
            measClipPaths = measPaths[::nPicsPerSS]

        if nMeasPnts > 1:
            print(f"Meaning Darkfield-Images (nMeasPnts)...")
            blckImgs = MeanImages(ImgCollection=blckImgs, ImgsPerMean=nMeasPnts, ShowImg=False)     # Meaning nMeasPnts
            blckPaths = blckPaths[::nMeasPnts]

            print(f"Meaning Measurement-Images (nMeasPnts)...")
            measImgs = MeanImages(ImgCollection=measImgs, ImgsPerMean=nMeasPnts, ShowImg=False)     # Meaning nMeasPnts
            measPaths = measPaths[::nMeasPnts]

        if sensBlackLevel >= 0:
            print(f"Subtracting black-level from 12Bit Images...")
            if sensBlackLevel == 0:
                sensBlackLevel = int(np.mean(blckImgs) + 1)
                print(f"Using mean of dark-image: ", end="")
            else:
                print(f"Using fix value: ", end="")
            print(f"if(pixelbright < {sensBlackLevel:.2f}) = 0")
                
            blckImgs = SubtractFromImgCollection(blckImgs, sensBlackLevel)
            measImgs = SubtractFromImgCollection(measImgs, sensBlackLevel)
            measImgs = StretchBrightness(measImgs, blackLevel=sensBlackLevel, whiteLevel=0xFFF) # 12bit max


        # print(f"Subtracting Darkfield- from Measurement-Images...")
        # measImgs = SubtractFromImgCollection(ImgCollection=measImgs, ImgOrBlacklevel=blckImgs[0], ShowImg=False) # MeasImgs - Darkfield
        
        print(f"12Bit Measurement-Images -> 16Bit Images...")
        measImgs = ConvertBitsPerPixel(ImgCollection=measImgs, originBPP=12, targetBPP=16)    



        # print("Starting black images PNG Dump...")
        # start = time()
        # pngPaths = DumpCollectionAs16BitPNG(blckImgs, blckClipPaths)
        # print(f"PNG-Dump of Black images took: {(time()-start):.3f}s")

        # print("Starting measurement images PNG8 Dump...")
        # start = time()
        # pngPaths = DumpCollectionAs8BitPNG(blckImgs, blckClipPaths)
        # print(f"PNG8-Dump of Measurement images took: {(time()-start):.3f}s")


        # print("Starting black images PKL Dump...")
        # start = time()
        # pklPaths = DumpCollectionAsGray(blckImgs, blckClipPaths)
        # print(f"PKL-Dump of Black images took: {(time()-start):.3f}s")




        # blckSubImgs = []
        # blckSubImgMinMax = []
        # fPng, aPng = plt.subplots()
        # fPkl, aPkl = plt.subplots()
        # for _iPath in range(len(pngPaths)):
        #     # Grab pkl-image again
        #     pklPath = pklPaths[_iPath]
        #     fTest_Pkl = open(pklPath, "rb")
        #     imgPkl = pickle.load(fTest_Pkl)
        #     fTest_Pkl.close()

        #     # Grab 16bit png again
        #     pngPath = pngPaths[_iPath]
        #     imgPng = cv.imread(pngPath, cv.IMREAD_ANYDEPTH)

        #     blckSubImgs.append(np.subtract(imgPkl, imgPng))
        #     blckSubImgMinMax.append({"min": np.min(blckSubImgs[-1]), "max": np.max(blckSubImgs[-1])})

        #     aPkl.cla()
        #     aPng.cla()
        #     aPkl.imshow(imgPkl)
        #     aPng.imshow(imgPng)

        # print("Starting measurement images PNG Dump...")
        # start = time()
        # pngPaths = DumpCollectionAs16BitPNG(measImgs, measClipPaths)
        # print(f"PNG-Dump of Measurement images took: {(time()-start):.3f}s")

        # print("Dumping Measurement-Images as PNG8 for ocular observance...")
        # start = time()
        # png8Imgs = ConvertBitsPerPixel(OriImgCollection=measImgs, originBPP=16, targetBPP=8)
        # png8Imgs = png8Imgs.astype(np.uint8)
        # png8Paths = DumpCollectionIntoPNG8(png8Imgs.astype(np.uint8), measClipPaths)
        # print(f"PNG8-Dump of Measurement images took: {(time()-start):.3f}s")

        print("Dumping Measurement-Images as 16bit-PNGs for PiMagePro...")
        start = time()
        # pklPaths = DumpCollectionAsGray(measImgs, measClipPaths)
        png16Paths = DumpCollectionAs16BitPNG(measImgs, measClipPaths)
        print(f"PKL-Dump of Measurement images took: {(time()-start):.3f}s")

        # measSubImgs = []
        # measSubImgMinMax = []
        # for _iPath in range(len(pngPaths)):
        #     # Grab pkl-image again
        #     pklPath = pklPaths[_iPath]
        #     fTest_Pkl = open(pklPath, "rb")
        #     imgPkl = pickle.load(fTest_Pkl)
        #     fTest_Pkl.close()

        #     # Grab 16bit png again
        #     pngPath = pngPaths[_iPath]
        #     imgPng = cv.imread(pngPath, cv.IMREAD_ANYDEPTH)

        #     measSubImgs.append(np.subtract(imgPkl, imgPng))
        #     measSubImgMinMax.append({"min": np.min(measSubImgs[-1]), "max": np.max(measSubImgs[-1])})

        #     aPkl.cla()
        #     aPng.cla()
        #     aPkl.imshow(imgPkl)
        #     aPng.imshow(imgPng)


        print("Deleting obsolet .raw-files...")
        DeleteFiles(blckPaths)
        DeleteFiles(measPaths)

    
print("Finished")