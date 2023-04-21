import matplotlib.pyplot as plt
import numpy as np






def FourierOnLuminosityVector(bVec):
  plt.close()
  f = plt.figure()
  a = f.subplots(ncols=2)
  a[0].plot(list(range(len(bVec["y"]))), bVec["y"], label="bVec")

  dFourier = np.fft.ifft(np.fft.fft(bVec["y"], n=100)) 
  a[0].plot(list(range(len(dFourier))), dFourier, label="ifft(fft)")

  fourier = np.fft.fft(bVec["y"], n=100)
  four = list()
  for _iF in range(len(fourier)):
    # if (_iF % 2) == 0 and _iF >= 1:
    if _iF >= 2:
      four.append(0)
      continue
    four.append(fourier[_iF])
  # four = four[0:10]

  a[1].plot(list(range(len(fourier))), fourier, label="fft")
  a[1].plot(list(range(len(four))), four, label="fftClipped")


  iFourier = np.fft.ifft(four, n=len(fourier))
  a[0].plot(np.linspace(0, len(iFourier), len(iFourier)), iFourier, label="ifft")


  a[0].legend()
  a[1].legend()
  return