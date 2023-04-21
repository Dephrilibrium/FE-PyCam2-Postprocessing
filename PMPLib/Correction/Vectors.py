from math import pi
import numpy as np
from PMPLib.Correction.Convert import cart2pol_deg, pol2cart_deg
import matplotlib.pyplot as plt
import cv2 as cv



def __FindShortestPxLen2Border__(tImg, center):
  h, w = tImg.shape[0], tImg.shape[1]
  x2, y2 = center[0], center[1]

  l0 = w-x2
  l90 = y2
  l180 = x2
  l270 = h-y2
  polarLen = [l0, l90, l180, l270]

  iMin = 0
  for nLen in range(1, len(polarLen)):
    if polarLen[iMin] > polarLen[nLen]:
      iMin = nLen

  return polarLen[iMin], 90*iMin






def GrabLuminosityVector4Coord(tImg, center, coord, overlap, flip=True, showImg=False):
  '''Extracts n brightness-vectors (dark to bright-center) of the given tImg'''

  vLen, dir = __FindShortestPxLen2Border__(tImg=tImg, center=center)
  coord2center = (center[0] - coord[0], center[1] - coord[1])
  (d, a) = cart2pol_deg(coord2center[0], coord2center[1])
  # (d, a) = cart2pol_deg(coord[0], coord[1])
  if(overlap < 0):
    overlap = vLen - 1 # Symmetric in both directions

  iCoord = 0 # Starting with overexposed pixel!
  bVec = dict()
  bVec["x"] = list()
  bVec["y"] = list()

  if showImg:
    iVec = dict()

  vecLen = vLen + overlap
  for iLen in range(vecLen):
    r = iLen - overlap
    (x,y) = pol2cart_deg(r, a)
    x = int(round(center[0] + x))
    y = int(round(center[1] + y))
    if ((x,y) == coord):
      iCoord = bVec["y"].__len__()

    bVec["x"].append(int(r))
    bVec["y"].append(tImg[y, x])

    if showImg:
      # Going from center to px-coordinate -> inverse direction!
      if iLen == 0:
        iVec["stop"] = (x, y)
        iVec["stopInverted"] = (y, x)
      # if (y,x) == coord:
      if iLen == (vecLen - 1):
        iVec["start"] = (x, y)
        iVec["startInverted"] = (y, x)


  # Reverse if requested
  if flip :
    # bVec["x"].reverse()
    bVec["y"].reverse()
    iCoord = len(bVec["y"]) - 1 - iCoord

  # Convert to ndarray
  bVec["x"] = np.array(bVec["x"])
  bVec["y"] = np.array(bVec["y"])

  if showImg:
    figImg = plt.figure()
    drawImg = tImg.copy()
    drawImg[iVec["startInverted"]] = 0
    drawImg[iVec["stopInverted"]] = 0
    plt.imshow(cv.arrowedLine(img=drawImg, pt1=iVec["start"], pt2=iVec["stop"], color=(128,0,0), thickness=1, tipLength=0.1))

  return bVec, iCoord - np.where(bVec["x"] == 0)[0][0]




