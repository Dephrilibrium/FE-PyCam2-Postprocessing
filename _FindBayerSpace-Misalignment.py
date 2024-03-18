##################################################################################
# Currently in development state:                                                #
# Visualizes what happens, if a odd clipwindow for the images was used (already  #
# fixed in the latest PyCam2-Server). The determined x-shift can be used by      #
# "PreClipImagesOrRaw.py" to restore the correct alignment of cost of a few      #
# pixels in the iamges width.
# 2023 © haum (OTH-Regensburg)                                                   #
##################################################################################





import pickle
import matplotlib.pyplot as plt
import numpy as np
from time import sleep




x = 0
y = 0
w = 100
h = 100


cx = int(x * 1.5)
cy = y
cw = int((x+w) * 1.5)
ch = h


# One direct RAW-image path goes here
imgPath = r"<Drive>\<Input Pics folderpath here>\01_01 Activation\Pics\FirstImage.raw", # Topmost Parent --> Scans the child-folders iteratively













fImg = open(imgPath, "rb")
img = pickle.load(fImg)
fImg.close()

for iIter in range(1000):


    cutImg = img[cy:ch, cx:cw].copy()
    imShow = np.empty( (w, h) )
    for byte in range(2):
      imShow[:, byte::2] = ( (cutImg[:, byte::3] << 4) | ((cutImg[:, 2::3] >> (byte * 4)) & 0b1111) )
    
    plt.clf()
    plt.imshow(imShow)
    plt.colorbar()
    plt.clim([0, 4095])
    plt.xlabel("x-Coordinate")
    plt.ylabel("y-Coordinate")
    plt.title("Demosaicking: Index-Shift in Bayer-Space")
    plt.text(5, 10, f"x-Shift: {iIter}", fontsize="large", color="black", backgroundcolor="white")
    plt.pause(0.5)

    ### Adjust clip
    cx = cx + 1
    cw = cw + 1
    # cy = cy + 1
    # ch = ch + 1
    # sleep(0.5)

print("EOS")