from os.path import join, basename, dirname
import pickle
import numpy as np
import FieldEmission as fe


import matplotlib.pyplot as plt


from misc import GrabPklFile
from misc import PlotSupTitleAndLegend
from misc import GetQuadrantOfSpot
from misc import SaveFigList

from _alt.Check_GradeOfOverexposement import __twinx2D___
from _alt.Check_GradeOfOverexposement import __SameXYLimitsOnLRSubplots__
from _alt.Check_GradeOfOverexposement import __SameXYLabelsOnLRSubplots__
from Paper2x2_misc import ColorizeTwinedXWith
from Paper2x2_misc import ReadResistorFile
from Paper2x2_misc import ReadSwpFile
from Paper2x2_misc import ReadCFFile
from Paper2x2_misc import ReadUDFile








bPath = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\03 Sample-Sweeps\230307_124953 1kV IMax500nA"
# bPath = r"D:\05 PiCam\230215 HQCam 150nm Cu SOI2x2_0006 (libcamera)\Auswertung\02 Alle Zusammen\230306_140339 1kV 250nA #2"
# Read Image-Data
PMP_OE_Bright = GrabPklFile(join(bPath, "PMP_ScaledWhereOverexposedBrightnesses.pkl"))
PMP_PixlAreas = GrabPklFile(join(bPath, "PMP_PxAreaCnts4Brightness.pkl"))
imgWH = [700, 700]

XY = list(PMP_OE_Bright["Spot"].keys())
ssKeys = list(PMP_PixlAreas.keys())
yKeys = list(PMP_OE_Bright["Full"]["SpotBright"].keys())

PMP_PixlAreas = PMP_PixlAreas[ssKeys[0]]










# Read and sort el. data
res = ReadResistorFile(join(bPath, "*.resistor"))

swp = ReadSwpFile(join(bPath, "*.swp"))
swp.AppendColumn("Time", np.linspace(0, swp.Rows * 6, swp.Rows, endpoint=True))

ig = ReadCFFile(join(bPath, "Dev7_ISum.dat"             ), None)
i0 = ReadCFFile(join(bPath, "Dev100_FEAR16v2(Ch0CF).dat"), res)
i1 = ReadCFFile(join(bPath, "Dev100_FEAR16v2(Ch1CF).dat"), res)
i2 = ReadCFFile(join(bPath, "Dev100_FEAR16v2(Ch2CF).dat"), res)
i3 = ReadCFFile(join(bPath, "Dev100_FEAR16v2(Ch3CF).dat"), res)
elCurr = {
    "Full": ig,
     XY[0]: i1,
     XY[1]: i2,
     XY[2]: i0,
     XY[3]: i3,
}
del i0, i1, i2, i3


# UDrop
u0 = ReadUDFile(join(bPath, "Dev100_FEAR16v2(Ch0UD).dat"), swpProvider=swp)
u1 = ReadUDFile(join(bPath, "Dev100_FEAR16v2(Ch1UD).dat"), swpProvider=swp)
u2 = ReadUDFile(join(bPath, "Dev100_FEAR16v2(Ch2UD).dat"), swpProvider=swp)
u3 = ReadUDFile(join(bPath, "Dev100_FEAR16v2(Ch3UD).dat"), swpProvider=swp)
elVolt = {
    "Full": swp,
     XY[0]: u1,
     XY[1]: u2,
     XY[2]: u0,
     XY[3]: u3,
}
del u0, u1, u2, u3





# Build ImageData (collection of Brightness and ShutterSpeed)
idDataSet = "SpotBright"
# idDataSet = "SpotBright"
idSubSet = yKeys[0]
logLoVal = 1e-10

imBrgt = dict()
imBrgt["Full"] = fe.DataProvider("Br",           np.abs(PMP_OE_Bright["Full"][idDataSet][idSubSet])    )    # Just grab theoretical upscale
imBrgt["Full"]     .AppendColumn("SS", np.divide(np.abs(PMP_OE_Bright["Full"]["BrightnessFromSS"]), 1000))  # µs / 1000 = ms
# id["Full"]     .AppendColumn("Ar", np.power (np.abs(PMP_PixlAreas["Full"]["Blank"]), 2))                # PxCnt

pxArr = np.abs(PMP_PixlAreas["Full"]["Blank"])
pxArr[pxArr < 1] = 1 # To avoid /0
imBrgt["Full"]     .AppendColumn("Ar", pxArr)                    # PxCnt
imBrgt["Full"]     .AppendColumn("B/A", np.divide(imBrgt["Full"].GetColumn("Br"), imBrgt["Full"].GetColumn("Ar")))

for _xy in XY:
    imBrgt[_xy] = fe.DataProvider("Br",          np.abs(          PMP_OE_Bright["Spot"][_xy][idDataSet][idSubSet]    ))     # Just grab theoretical upscale
    imBrgt[_xy]     .AppendColumn("SS",          np.abs(np.divide(PMP_OE_Bright["Spot"][_xy]["BrightnessFromSS"], 1000)))   # µs / 1000 = ms
    pxArr = np.abs(PMP_PixlAreas["Spot"][_xy]["Blank"])
    pxArr[pxArr < 1] = 1
    imBrgt[_xy]     .AppendColumn("Ar", pxArr)                               # PxCnt





###### Calculate all dependency combinations ######
### Raw
# 00.) B

### Separate division
# 01.) B / (A)
# 02.) B / (U)
# 03.) B / (U^2)
# 04.) B / (sqrt(U))

### Separate multiplication
# 05.) B * (A)
# 06.) B * (U)
# 07.) B * (U^2)
# 08.) B * (sqrt(U))

### Combi division
# 09.) B / (A * U)
# 10.) B / (A * U^2
# 11.) B / (A * sqrt(U))

### Combi multiplication
# 12.) B * (A * U)
# 13.) B * (A * U^2
# 14.) B * (A * sqrt(U))

### Combi mixed up
# 15.) B * (U       / A)
# 16.) B * (U^2     / A)
# 16.) B * (sqrt(U) / A)

# 17.) B * (A / U      )
# 18.) B * (A / U^2    )
# 19.) B * (A / sqrt(U))

def CalcDepSet(B, A, U):
    bLen = len(B)

    U2  = np.power(U, 2)
    U05 = np.power(U, 0.5)

    _bright = dict()

    _bright["B"                ] = B
    _bright["B / (A)"          ] = np.divide(B, A  )
    _bright["B / (U)"          ] = np.divide(B, U  )
    _bright["B / (U^2)"        ] = np.divide(B, U2 )
    _bright["B / (sqrt(U))"    ] = np.divide(B, U05)

    _bright["B * (A)"          ] = np.multiply(B, A  )
    _bright["B * (U)"          ] = np.multiply(B, U  )
    _bright["B * (U^2)"        ] = np.multiply(B, U2 )
    _bright["B * (sqrt(U))"    ] = np.multiply(B, U05)

    _bright["B / (A * U)"      ] = np.divide(B, np.multiply(A, U  ))
    _bright["B / (A * U^2"     ] = np.divide(B, np.multiply(A, U2 ))
    _bright["B / (A * sqrt(U))"] = np.divide(B, np.multiply(A, U05))

    _bright["B * (A * U)"      ] = np.multiply(B, np.multiply(A, U  ))
    _bright["B * (A * U^2"     ] = np.multiply(B, np.multiply(A, U2 ))
    _bright["B * (A * sqrt(U))"] = np.multiply(B, np.multiply(A, U05))

    _bright["B * (U       / A)"] = np.multiply(B, np.divide(U  , A))
    _bright["B * (U^2     / A)"] = np.multiply(B, np.divide(U2 , A))
    _bright["B * (sqrt(U) / A)"] = np.multiply(B, np.divide(U05, A))

    _bright["B * (A / U      )"] = np.multiply(B, np.divide(A, U  ))
    _bright["B * (A / U^2    )"] = np.multiply(B, np.divide(A, U2 ))
    _bright["B * (A / sqrt(U))"] = np.multiply(B, np.divide(A, U05))

    return _bright


cmbFac = dict()
brCmbi = dict()
for _iXY in range(len(XY)):
    _xy = XY[_iXY]

    _B = np.abs(imBrgt[_xy].GetColumn("Br"))
    _A = np.abs(imBrgt[_xy].GetColumn("Ar"))
    _U = np.abs(elVolt[_xy].GetColumn("U"))

    brCmbi[_xy] = CalcDepSet(_B, _A, _U)




# Preparation
figs = list()
subL = list()
subR = list()


# Plot Brightness and 
fig, lAxis = plt.subplots(nrows=3, ncols=2)#, sharex=True, sharey=True)
figs.append(fig)
subL.append(lAxis)
subR.append(__twinx2D___(fig, lAxis))



_x = np.array(list(range(len(imBrgt[XY[0]].GetColumn("Br")))))
subL[-1][0][0].semilogy(_x, imBrgt["Full"].GetColumn("Br"), "d--", markersize=4, linewidth=1  , color="#FF0000", label="Sum(Brightness)")
# subR[-1][0][0].plot    (_x, imBrgt["Full"].GetColumn("SS"), "1--", markersize=2, linewidth=0.5, color="#666666", label="From Shutterspeed")
subR[-1][0][0].plot    (_x, imBrgt["Full"].GetColumn("Ar"), "1--", markersize=2, linewidth=0.5, color="#666666", label="PxCnt")

for _xy in XY:
    _iY, _iX = GetQuadrantOfSpot(_xy, imgWH)
    _iY += 1 # Add the y-Offset
    subL[-1][_iY][_iX].semilogy(_x, imBrgt[_xy].GetColumn("Br"), "d--", markersize=4, linewidth=1  , color="#FF0000", label="Sum(Brightness)")
    # subR[-1][_iY][_iX].plot    (_x, imBrgt[_xy].GetColumn("SS"), "1--", markersize=2, linewidth=0.5, color="#666666", label="From Shutterspeed")
    # subR[-1][_iY][_iX].plot    (_x, imBrgt[_xy].GetColumn("Ar"), "1--", markersize=2, linewidth=0.5, color="#666666", label="PxCnt")

    cmbKeys = list(brCmbi[_xy].keys())
    for _iCmbKey in range(len(cmbKeys)): #[1,2,4,9,10,11]:
        _cmbKey = cmbKeys[_iCmbKey]
        subR[-1][_iY][_iX].semilogy(_x, brCmbi[_xy][_cmbKey], "1--", markersize=2, linewidth=0.5, label=_cmbKey)


    subL[-1][0][0].semilogy(_x, imBrgt[_xy].GetColumn("Br"), "d--", markersize=2, linewidth=0.5, label=f"B@{_xy}")
    subR[-1][0][0].plot    (_x, imBrgt[_xy].GetColumn("Ar"), "1--", markersize=2, linewidth=0.5, label="PxCnt@{_xy}")

PlotSupTitleAndLegend(figs[-1], "F01 - Brightness & Shutterspeed")
# __SameXYLimitsOnLRSubplots__(subL[-1], [1e0, 1e9], subR[-1], [-100, 6100], None)
ColorizeTwinedXWith(subR[-1], "#666666")
subL[-1][0][0].set_ylabel("Brightness")
subL[-1][1][0].set_ylabel("Brightness")
subL[-1][2][0].set_ylabel("Brightness")
subR[-1][0][1].set_ylabel("Shutterspeed")
subR[-1][1][1].set_ylabel("Shutterspeed")
subR[-1][2][1].set_ylabel("Shutterspeed")








SaveFigList(figList=figs, saveFolder=sPaths[0], figSize=(15,12), dpi=300)




print("Finished")