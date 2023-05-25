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

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230417_171941 850V T1-4=2.5",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230417_174418 700V T1-4=1",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_02 Performance-Check\230418_085317 850V T1-4=2.5",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_094854 450V T1=2.5, T2,3,4=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_101154 450V T1=5, T2,3,4=gnd",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_104503 850V T2=2.5, T1,3,4=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_112114 950V T2=5, T1,3,4=gnd",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_115301 750V T3=2.5, T1,2,4=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_121938 750V T3=5, T1,2,4=gnd",

r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_124726 650V T4=2.5, T1,2,3=gnd",
r"D:\05 PiCam\230404 HQCam SOI2x2_0014\Messungen\09_03 Messungen tips einzeln, Rest grounded\230418_131423 650V T4=5, T1,2,3=gnd",
]

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
sensBlackLevel = 0




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
                blackMean = int(np.mean(blckImgs) + 1)
                blackStd = int(np.std(blckImgs) * 6 + 1) # 6 sigma
                sensBlackLevel = blackMean + blackStd
                print(f"Using mean of dark-image: ", end="")
            else:
                print(f"Using fix value: ", end="")
            print(f"if(pixelbright < {sensBlackLevel:.2f}) = 0")
            
                
            blckImgs = SubtractFromImgCollection(blckImgs, sensBlackLevel)
            measImgs = SubtractFromImgCollection(measImgs, sensBlackLevel)
            measImgs = StretchBrightness(measImgs, blackLevel=sensBlackLevel, whiteLevel=0xFFF) # 12bit max


        # print(f"Subtracting Darkfield- from Measurement-Images...")
        # measImgs = SubtractFromImgCollection(ImgCollection=measImgs, ImgOrBlacklevel=blckImgs[0], ShowImg=False) # MeasImgs - Darkfield


        # #### Paper-Examples 12-bit -> 16-bit)
        # paper12Bit = np.array([
        #     measImgs[805],
        #     measImgs[806],
        #     measImgs[807],
        # ])
        # paths12Bit = [
        #     r"C:\Users\ham38517\Downloads\save\805 12bit_0000.png",
        #     r"C:\Users\ham38517\Downloads\save\806 12bit_0000.png",
        #     r"C:\Users\ham38517\Downloads\save\807 12bit_0000.png",
        # ]
        # paths16Bit = [
        #     r"C:\Users\ham38517\Downloads\save\805 16bit_0000.png",
        #     r"C:\Users\ham38517\Downloads\save\806 16bit_0000.png",
        #     r"C:\Users\ham38517\Downloads\save\807 16bit_0000.png",
        # ]


        # savPath = DumpCollectionAs16BitPNG(paper12Bit, paths12Bit)
        # paper16Bit = ConvertBitsPerPixel(ImgCollection=paper12Bit, originBPP=12, targetBPP=16)    
        # savPath = DumpCollectionAs16BitPNG(paper16Bit, paths16Bit)

        
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
        print(f"PNG-Dump of Measurement images took: {(time()-start):.3f}s")

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