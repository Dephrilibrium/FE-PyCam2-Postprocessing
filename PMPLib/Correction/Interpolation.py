import matplotlib.pyplot as plt
from pylab import get_current_fig_manager
import numpy as np
from scipy.optimize import curve_fit
import math
import numpy as np

from misc import PlotSupTitleAndLegend




def __default_CapFunc__(pxlX, bAdj, A):
  # if type(pxlX) != np.ndarray:
  #   pxlX = [pxlX]

  # sqrt = [-math.sqrt(x/A) for x in pxlX]

  # y = (255 * bAdj) * (1 - np.exp(sqrt * eAdj))
  y = (255 * bAdj) * (1 - np.exp(-pxlX/A))
  return y


def __default_Gauss__(pxlX, bAdj, x0, sigma):
#def __default_Gauss(pxlX, bAdj, A):
  y = (255 * bAdj) * np.exp(-(pxlX-x0)**2/(2*sigma**2))
  return y





def __findSlopeIndexOver__(bVec, minSlope, keepBorder):
  iMin = 0
  iMax = len(bVec) - 1

  bMin = 5

  deri1 = np.gradient(bVec)  # Slope
  deri2 = np.gradient(deri1) # Curvature
  deri3 = np.gradient(deri2) # Curvature Slope
  deri4 = np.gradient(deri3) # Curvature Slope Curvature
  deri5 = np.gradient(deri4) # Curvature Slope Curvature Slope

  f1 = plt.figure()
  plt.plot(bVec, label="Bright")
  plt.plot(deri1, label="Derivation 1")
  plt.plot(deri2, label="Derivation 2")
  plt.plot(deri3, label="Derivation 3")
  plt.plot(deri4, label="Derivation 4")
  plt.plot(deri5, label="Derivation 5")
  plt.legend()

  # iMin = np.where(deri2 == deri2.max())[0][0]
  # iMax = np.where(deri2 == deri2.min())[0][0]

  for _iGrad in range(len(deri1)):
    bright = bVec[_iGrad]
    deriVal1 = deri1[_iGrad]
    deriVal4 = deri4[_iGrad]
    if bright >= bMin and deriVal1 >= minSlope and deriVal4 <= 0:
      iMin = _iGrad
      break

  # for _iGrad in range(len(deri1)):
  #   bright = bVec[-1 -_iGrad]
  #   deriVal1 = deri1[-1 -_iGrad]
  #   deriVal4 = deri4[-1 -_iGrad]
  #   if bright >= bMin and deriVal1 >= minSlope and deriVal4 <= 0:
  #     iMax = len(deri1) -1 - _iGrad
  #     break
  iMax = np.where(bVec == bVec.max())[0][0]
  
  if keepBorder:
    # if iMin > 0:
    #   iMin -= 1
    if iMax < (len(bVec) -1):
      iMax += 1
  
  plt.plot([iMin, iMin], [0, 255], "r--", label="left border")
  plt.plot([iMax, iMax], [0, 255], "r--", label="left border")

  return (iMin, iMax)



def InterpolateLuminosityVector(bVec, bAdj, sMin, bMax, func=lambda pxlX, bAdj, A: __default_CapFunc__(pxlX, bAdj, A)):
  
  ipVec = dict()
  ipVec["x"] = bVec["x"]
  ipVec["y"] = bVec["y"].copy().astype(np.uint16)

  replace = (bVec["y"] >= bMax)
  if replace.max() == False: # Nothing to do! return a uint16-copy
    return ipVec

  # Otherwise grab overexposed x-indicies,
  rplcX = bVec["x"][replace] 

  # Build Slope for bMin and bMax
  # bGrad = np.gradient(bVec["y"])
  (iKMinL, iKMaxL) = __findSlopeIndexOver__(bVec["y"], sMin, keepBorder=False)
  (iKMinR, iKMaxR) = __findSlopeIndexOver__(np.flip(bVec["y"]), sMin, keepBorder=False)

  # grab interpolationd ata
  # ipKeep = (bVec["y"] >= bMin) & (bVec["y"] <= bMax)
  # ipX = bVec["x"][ipKeep]
  # ipXSub = ipX.min()
  # ipX -= ipXSub
  # ipY = bVec["y"][ipKeep]

  ipXL = bVec["x"].copy()[iKMinL:iKMaxL]
  ipXR = np.flip(np.flip(bVec["x"].copy())[iKMinR:iKMaxR])
  ipXLR = np.concatenate((ipXL, ipXR))
  ipXSub = int((ipXLR[0] + ipXLR[-1]) / 2)
  ipXLR -= ipXSub

  ipYL = bVec["y"].copy()[iKMinL:iKMaxL]
  ipYR = np.flip(np.flip(bVec["y"].copy())[iKMinR:iKMaxR])
  ipYLR = np.concatenate((ipYL, ipYR))
  # popt, pcov = curve_fit(f=lambda pxX, A: func(pxX, bAdj, A), xdata=ipX, ydata=ipY, p0=[1.0]) # __default_Cap__
  # popt, pcov = curve_fit(f=lambda pxX, x0, sigma: __default_Gauss__(pxX, bAdj, x0, sigma), xdata=ipX, ydata=ipY, p0=[1.0, 1.0]) # __default_Gauss__
  popt, pcov = curve_fit(lambda x, adj, x0, sig: __default_Gauss__(x, adj, x0, sig), xdata=ipXLR, ydata=ipYLR) # __default_Gauss__

  # and replace the overexposed data via interpolation fit-function!
  for _iX in range(len(rplcX)):
    x = rplcX[_iX]
    _iXReal =  np.where(bVec["x"] == x)[0][0]
    ipVec["y"][_iXReal] = (int(__default_Gauss__(x, popt[0], popt[1], popt[2]))) # __default_Gauss__
    # ipVec["y"][rplcX[_iX]] = (int(__default_Gauss__(x, bAdj, popt[0], popt[1]))) # __default_Gauss__
    # ipVec["y"][rplcX[_iX]] = (int(func(x, bAdj, popt[0]))) # __default_Cap__
    # ipVec["y"][rplcX[_iX]] += bVec["y"][iKMin]


  ipXSmooth = np.linspace(bVec["x"][0], bVec["x"][-1], 250)
  # ipYSmooth = [__default_CapFunc__(xs, bAdj, popt[0]) for xs in ipXSmooth] # __default_Cap__
  # ipYSmooth = [__default_Gauss__(xs, bAdj, popt[0], popt[1]) for xs in ipXSmooth] # __default_Gauss__
  ipYSmooth = [__default_Gauss__(xs, popt[0], popt[1], popt[2]) for xs in ipXSmooth] # __default_Gauss__

  # ipYSmooth += bVec["y"][iKMin]
  # plt.close()
  f1 = plt.figure(figsize=(12,6), dpi=200)
  plt.plot(bVec["x"]         , bVec["y"] , "x"  , markersize=7, label="Ori Brightness")
  # plt.plot(bVec["x"][1:]-0.5 , np.diff(bVec["y"].astype(np.int16))     , "d-."  , markersize=5, label="Ori Diff")
  plt.plot(bVec["x"]         , np.gradient(bVec["y"].astype(np.int16)) , "s-."  , markersize=5, label="Ori Grad")
  plt.plot(bVec["x"]         , np.gradient(np.gradient(bVec["y"]).astype(np.int16)) , "s-."  , markersize=5, label="Ori Curvature")
  plt.plot(bVec["x"]         , np.gradient(np.gradient(np.gradient(bVec["y"])).astype(np.int16)) , "s-."  , markersize=5, label="Ori Curvature Slope")
  plt.plot(ipXLR               , ipYLR       , "*"  , markersize=3, label="interpolation XY kep")
  plt.plot(ipXSmooth         , ipYSmooth , "d"  , markersize=3, label="interpolation smooth")
  plt.plot(ipXSmooth + ipXSub, ipYSmooth , "-"  , markersize=3, label="interpolation smooth (backshifted)")
  plt.plot(ipVec["x"]        , ipVec["y"], "o--", markersize=3, label="XY with interpolation")
  plt.plot([ipXL[0] ] * 2    , [0, 255]  , "r--", markersize=3, label="interpol-pnt")
  plt.plot([ipXL[-1]] * 2    , [0, 255]  , "r--", markersize=3, label="interpol-pnt")
  plt.plot([ipXR[0] ] * 2    , [0, 255]  , "r--", markersize=3, label="interpol-pnt")
  plt.plot([ipXR[-1]] * 2    , [0, 255]  , "r--", markersize=3, label="interpol-pnt")
  # plt.legend()
  PlotSupTitleAndLegend(f1, "Interpolation via Gauss")
  

  # ipVec["y"] = np.array(ipVec["y"])
  return ipVec