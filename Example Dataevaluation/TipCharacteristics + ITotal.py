import pickle
import FieldEmission as fe
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.patches import Circle
from matplotlib.cm import get_cmap
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import LogLocator
import numpy as np
import json

import os
from os.path import join, dirname, basename, abspath, splitext


import sys

from lib import SplitAndMean, ReadElAsDP, ReadSwpAsDP, ReadSwpAsDPFromFolder, ReadPkl, ReadResistor, ReadResistorFromFolder
from lib import GetQuadrantOfSpot, CombinePlots, Twinx2D_2x2, Twinx2D_3x2, SameXYLimitsOnAxisColl, SameXYLimitsOnLRSubplots, SaveFigList
from lib import PlotSupTitleAndLegend, PlotLegend, ShowMajorMinorY

from misc import SetTexFont

from findMethods import FindXYKeysAboveMinValInMSSCurrents






showImgs = True
plotFN2EstimateFitRange = False # Not necessary anymore, as below the voltages can be given directly to auto-calculate the FN-coordinate range




folders = [
r".\230727_171103 700V IMax1V"
]

legLocs = [ # LegendLocations
    (0.43, 0.1175), # Sweep 700V
    (0.43, 0.1175), # 15m 500V
    (0.43, 0.1175), # Sweep 700V
    (0.43, 0.1175), # 15m 700V
    (0.43, 0.1175), # Sweep 700V
    (0.43, 0.1175), # 15m 1000V
    (0.43, 0.1175), # Sweep 700V
]

USigMin = [ # U where the IV-Characteristic "starts"
    290, # Sweep 700V
    310, # 15m 500V
    310, # Sweep 700V
    310, # 15m 700V
    310, # Sweep 700V
    310, # 15m 1000V
    310, # Sweep 700V
]


USigMax = [ # U where the IV-Characteristics is not in regulation/Saturation
    400, # Sweep 700V
    500, # 15m 500V
    500, # Sweep 700V
    500, # 15m 700V
    500, # Sweep 700V
    500, # 15m 1000V
    500, # Sweep 700V
]

d_um = [ # distance in µm between tips and Camera
    60, # Sweep 700V
    60, # 15m 500V
    60, # Sweep 700V
    60, # 15m 700V
    60, # Sweep 700V
    60, # 15m 1000V
    60, # Sweep 700V
]


replace4thOne = [
    # (529, 2182),    # Sweep 700V    (replace with damaged one for paper-discussion)
    None,           # Sweep 700V -> No risk for discussion!
    None,           # 15m 500V
    None,           # Sweep 700V
    None,           # 15m 700V
    None,           # Sweep 700V
    None,           # 15m 1000V
    None,           # Sweep 700V
]
minCurrent4ProperSignal = 20e-9  # Only active if replace4thOne is != None! (search for: _xyK)














fnFitRegion = [
    [d_um[0] / USigMax[0], d_um[0] / USigMin[0]], # Sweep     700V
    [d_um[1] / USigMax[1], d_um[1] / USigMin[1]], # 15m       500V
    [d_um[2] / USigMax[2], d_um[2] / USigMin[2]], # Sweep     700V
    [d_um[3] / USigMax[3], d_um[3] / USigMin[3]], # 15m       700V
    [d_um[4] / USigMax[4], d_um[4] / USigMin[4]], # Sweep     700V
    [d_um[5] / USigMax[5], d_um[5] / USigMin[5]], # 15m       1000V
    [d_um[6] / USigMax[6], d_um[6] / USigMin[6]], # Sweep     700V
]
















for _iFolder in range(len(folders)):
    folder = folders[_iFolder]

    # Lumi
    mss = ReadPkl(join(dirname(__file__), folder, r"PMP_mssContainer.pkl"))
    ses = ReadPkl(join(dirname(__file__), folder, r"PMP_sesContainer.pkl"))


    # Sweep
    swp = ReadSwpAsDPFromFolder(folder)

    # ITotal 6517
    iTotal = ReadElAsDP(join(dirname(__file__), folder, r"Dev7_ISum.dat"))
    iTotal.RemoveRows(0)

    # CurrentFlow
    resistor = ReadResistorFromFolder(folder)
    cf = ReadElAsDP(join(dirname(__file__), folder, r"Dev100_FEAR16v2(Ch0CF).dat"))
    cf.RemoveRows(0)

    # VoltageDrop
    ud = ReadElAsDP(join(dirname(__file__), folder, r"Dev100_FEAR16v2(Ch0UD).dat"))
    ud.RemoveRows(0) # Remove initial datapoint







    #### Prepare electrical data
    # CF
    cf["IAll"] = np.divide(cf["Y"], resistor)
    cf.RemoveColumns(["Y", "Dev7", "Time"])
    cf.AbsColumn("IAll")
    cf["ITotal6517"] = iTotal["Y"]

    # UD
    ud["UExt"] = np.subtract(abs(swp["U7"]), abs(ud["Y"]))
    ud.RemoveColumns(["Y", "Time", "Dev7"])
    ud.AbsColumn("UExt")






    #### Prepare lumiData
    _nImgs = len(mss["MergedSensorSignal"])

    # len(lumiData["Spot"][(274, 125)]["SpotBright"]["xTheory"])
    # len(lumiData["Spot"][(274, 125)]["PxlBright"]["xTheory"])
    # len(lumiData["Spot"][(274, 125)]["Overexposed"])
    # len(lumiData["Spot"][(274, 125)]["BrightnessFromSS"])


    _xyKeys = list(mss["XYKeys"].keys())
    _nxyKeys = len(_xyKeys)

    # Build empty share-factor dictionary
    mssShares = {}
    mssShares["mss/U"]    = {}
    mssShares["ShareFac"] = {}
    mssShares["Sum"]      = []


    # lenOfLumiVecs = dict()
    # for _iKey in range(_nxyKeys):
    #     _xyKey = _xyKeys[_iKey]
    #     lenOfLumiVecs[_xyKey] = len(mss["Spot"][_xyKey]["SpotBright"]["xTheory"])


    # Build lumiSpot/U
    for _iKey in range(_nxyKeys):
        _xyKey = _xyKeys[_iKey]
        mssShares["mss/U"][_xyKey] = []
        # for _iImg in range(_nImgs):
            # mssSpot = mss["XYKeys"][_xyKey]["MergedSensorSignal"][_iImg]
            # uSply = ud["UExt"][_iImg]
        mssSpot = mss["XYKeys"][_xyKey]["MergedSensorSignal"]
        uSply = [1] * ud["UExt"].__len__()
        mssShares["mss/U"][_xyKey] = np.divide(mssSpot, uSply)

    # Build lumiSum
    for _iImg in range(_nImgs):
        mssShares["Sum"].append(0)
        for _iKey in range(_nxyKeys):
            _xyKey = _xyKeys[_iKey]
            mssShares["Sum"][-1] += mssShares["mss/U"][_xyKey][_iImg]
    mssShares["Sum"] = np.array(mssShares["Sum"])

    # Build empty luminiscent-current dictionary
    mssCurrent = dict()

    # Build actual lumiShares and lumiCurrents
    for _iKey in range(_nxyKeys):
        _xyKey = _xyKeys[_iKey]
        mssShares["ShareFac"][_xyKey] = []
        mssCurrent[_xyKey] = []
        # for _iImg in range(_nImgs):
            # mssU = mss["XYKeys"][_xyKey]["MergedSensorSignal"][_iImg]
            # mssShares["ShareFac"][_xyKey].append(np.divide(mssU, mssShares["Sum"]))
        mssU = mssShares["mss/U"][_xyKey]
        mssShares["ShareFac"][_xyKey] = np.divide(mssU, mssShares["Sum"])

        mssShares["ShareFac"][_xyKey] = np.array(mssShares["ShareFac"][_xyKey])
        mssCurrent[_xyKey] = np.multiply(cf["IAll"], mssShares["ShareFac"][_xyKey])

        fnProvider = fe.DataProvider(["U", "I"], [ud["UExt"], mssCurrent[_xyKey]])
        fn = fe.FowlerNordheim(DatMgr=fnProvider, ColumnU="U", ColumnI="I", distance_μm=60)


        
        # Search for percentage influence of the damaged spot (black level)
        __ssK = list(ses.keys())[0]
        __xyK = replace4thOne[_iFolder]
        if __xyK != None:
            _iKeep = np.where(cf["ITotal6517"] >= minCurrent4ProperSignal)[0]
            __min = np.array(mss["XYKeys"][__xyK]["MergedSensorSignal"][0])
            __vec = np.array(mss["XYKeys"][__xyK]["MergedSensorSignal"][_iKeep[0]:_iKeep[-1]])
            __all = np.array(mss["MergedSensorSignal"]                 [_iKeep[0]:_iKeep[-1]])

            __dmgRelSpot = np.divide(__min, __vec)
            __dmgRelSpotPerc = np.multiply(__dmgRelSpot, 100)
            __dmgRelAll = np.divide(__min, __all)
            __dmgRelAllPerc = np.multiply(__dmgRelAll, 100)

            # Clipping is now done by min-current instead of voltages!
            # _iKeep = int(USigMin[_iFolder] / 6 + 1) # Clip away when supply voltage < min-voltage to see some correct signal!
            # _dmgRelAppPercNoNoise = __dmgRelAllPerc[_iKeep:-_iKeep]
            _dmgRelAppPercNoNoise = __dmgRelAllPerc

            __meanDmgOnAll = np.mean(_dmgRelAppPercNoNoise)
            __stdDmgOnAll = np.std(_dmgRelAppPercNoNoise)



    # _dLen = mssCurrent[_xyKeys[0]].size
    # _xyKeysHiNoise = FindXYKeysAboveMinValInMSSCurrents(mssCurrentContainer=mssCurrent, minVal=1e-9, onIndicies=range(_dLen-5, _dLen))
    _xyKeysHiNoise = FindXYKeysAboveMinValInMSSCurrents(mssCurrentContainer=mssCurrent, minVal=1e-9, onIndicies=range(-6, -1))
    print(f"High-noise tips in {folder}")
    print(str(_xyKeysHiNoise))











    SetTexFont(24)
    fig, axL = plt.subplots(nrows=1, ncols=1)
    axR = axL.twinx()
    fig.set_size_inches(w=14, h=10)
    if showImgs:
        plt.show(block=False)

    u = ud["UExt"]
    i = cf["IAll"]
    # i = cf["ITotal6517"]

    tDelta = 6.0
    tScale = 60 # sec -> min
    t = np.divide(np.linspace(start=0, stop=tDelta * (len(u)-1), num=len(u), endpoint=True), tScale)
    # axL.semilogy(u, i, "x--", markersize=10, linewidth=1.5, color="#000000", label="$I_{el.}$")
    axL.semilogy(t, i, "x--", markersize=10, linewidth=1.5, color="#000000", label="$I_{el.}$")
    axR.plot(t, abs(swp["U7"]), "+--", markersize=10, linewidth=1.5, color="#FF00FF", label="$U_{Supply}$")
    axR.plot(t, u, "+--", markersize=10, linewidth=1.5, color="#FF00FF", alpha=0.35, label="$U_{Extr.}$")
    for _iKey in range(_nxyKeys):
        _xyKey = _xyKeys[_iKey]

        # axL.semilogy(u, mssCurrent[_xyKey], "1--"  , markersize=12, linewidth=0.5, alpha=0.5, label="$I_{opt.}$")
        axL.semilogy(t, mssCurrent[_xyKey], "1--"  , markersize=12, linewidth=0.35, alpha=0.5, label="$Share_{opt.}$")

    ShowMajorMinorY(axis=[axL], useLogLocator=True)
    ShowMajorMinorY(axis=[axR], useLogLocator=False)
    # axL.set_xlim([t.min()-15, t.max()+15])
    axL.set_xlim([t.min(), t.max()])
    axL.set_ylim([1e-13, 2e-4])
    axR.set_ylim([-50, 2550])

    # axL.set_xticks([250, 300, 350, 400, 450, 500, 550])
    axL.set_yticks([1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4])
    axR.set_yticks([0, 250,500,750,1000])


    lHndls = [
        tuple([axL.lines[0]
    ]),
        tuple(axL.lines[1:]
    ),
        tuple([axR.lines[0]
    ]),
        tuple([axR.lines[1],
    ]),
    ]
    lLbls = [
        axL.lines[0]._label,
        axL.lines[1]._label,
        axR.lines[0]._label,
        axR.lines[1]._label,
    ]
    PlotLegend(fig, lHandles=lHndls, lLabels=lLbls, loc=legLocs[_iFolder], ncol=1, LabelColor="#000000")
    fig.text(x=0.6, y=0.125, s="$n_{Active\ Tips} = $" + f"${_nxyKeys}$")

    fig.suptitle("Currents and voltages\nof the 21x21 cathode")
    axL.set_xlabel("Time [s]")
    axL.set_ylabel("Emissionsstrom [A]")
    axR.set_ylabel("Voltage [V]")

    # Set y-Scales explicit






    # Building 2D-Histogram Plot data for Hist over Time
    mssCurrList = np.array([mssCurrent[_xy] for _xy in mssCurrent]).T
    mssCurrFlat = mssCurrList.flatten()
    

    mssCurrTLen = len(mssCurrList[0])
    mssCurrLen = len(mssCurrList)
    
    _singleHistIndex = 108 #mssCurrLen // 2

    tFlat = np.array([[t[_i]] * mssCurrTLen for _i in range(mssCurrLen)]).flatten()

    iKeep = np.where(mssCurrFlat > 1e-9)[0]
    mssCurrFlat = mssCurrFlat[iKeep]
    tFlat = tFlat[iKeep]

    # Plot Histogram2D of all tips over time
    mssFig, mssAxL = plt.subplots(nrows=1, ncols=1)
    mssAxR = mssAxL.twinx()
    mssFig.set_size_inches(w=16, h=10)
    if showImgs:
        plt.show(block=False)


    mssInsAxL = mssAxL.inset_axes([0.25, 0.11, 0.45, 0.25])
    mssInsAxL.spines['bottom']  .set_color('red')
    mssInsAxL.spines['top']     .set_color('red')
    mssInsAxL.spines['right']   .set_color('red')
    mssInsAxL.spines['left']    .set_color('red')
    mssInsAxL.spines['bottom']  .set_linewidth(5)
    mssInsAxL.spines['top']     .set_linewidth(5)
    mssInsAxL.spines['right']   .set_linewidth(5)
    mssInsAxL.spines['left']    .set_linewidth(5)
    mssInsAxL.spines['bottom']  .set_linestyle("--")
    mssInsAxL.spines['top']     .set_linestyle("--")
    mssInsAxL.spines['right']   .set_linestyle("--")
    mssInsAxL.spines['left']    .set_linestyle("--")
    mssInsAxL.tick_params(axis='both', colors='white')

    # matrix, *opt = np.histogram2d(tFlat, mssCurrFlat)
    # img = plt.imshow(matrix, norm = colors.LogNorm(), #cmap = matplotlib.cm.gray, 
    #              interpolation="None")
    
    xBins = np.linspace(0, t[-1], 171, endpoint=True)
    yBins = np.logspace(np.log10(1e-9), np.log10(150e-6), 81)
    # for _i in range(ssCurrLen):
    #     pass

    # mssAxL.scatter(tFlat, mssCurrFlat)
    
    h = mssAxL.hist2d(tFlat, mssCurrFlat, bins=[xBins, yBins], norm=plt.Normalize(vmin=0, clip=True), cmap="afmhot", linewidth=0, edgecolors="black", rasterized=True)
    hVertLine = mssAxL.semilogy([t[_singleHistIndex]] * 2, [1e-10, 150e-6], "r--", linewidth=5)
    mssAxL.semilogy(t, i, "-", color="#00FF00", alpha=0.75, linewidth=5)

    mssAxR.plot(t, abs(swp["U7"]), "-", color="#FF00FF", alpha=0.5, linewidth=5)
    mssAxR.plot(t, abs(u), "-", color="#FF00FF", alpha=1, linewidth=5)

    # mssInsAxL.hist(mssCurrList[_singleHistIndex], bins=np.logspace(np.log10(1e-10), np.log10(15e-6), 51), color="#ac2d00", edgecolor="black")
    mssInsAxL.hist(mssCurrList[_singleHistIndex], bins=yBins, color="#ac2d00", edgecolor="black")


    ### HBar on top (Size: 14x10)
    # hbarPos = mssFig.add_axes([0.1, 0.875, 0.8, 0.035])
    # hbar = mssFig.colorbar(h[3], cax=hbarPos, ax=mssAxL, orientation="horizontal", location="top")#, label="$n_{Tips}$")
    ### HBar at right side (Size: 16x10)
    hbarPos = mssFig.add_axes([0.915, 0.085, 0.02, 0.865])
    hbar = mssFig.colorbar(h[3], cax=hbarPos, ax=mssAxL, orientation="vertical", location="right")#, label="$n_{Tips}$")
    
    # mssAxL.set_xscale("log")
    mssAxL.set_yscale("log")
    hbar.formatter = ScalarFormatter()
    hbar.set_ticks([1,2,3,4,5,6,7,8, 9, 10, 11, 12])
    hbar.set_label("$n_{Tips}$", labelpad=10)
    hbar.update_ticks()

    mssInsAxL.set_xscale("log")
    


    # Make the plot it beatuiful :)
    # Mainplot
    # mssAxL.grid(visible=True, which="both", axis="both", color="#CCCCCC", linestyle="-", linewidth=0.5)
    # ShowMajorMinorY(axis=[mssAxL], useLogLocator=True, which="both") # Is shown correctly, but not saved correctly!

    mssAxL.set_xlim([t.min(), t.max()])
    mssAxL.set_ylim([1e-9, 150e-6])
    mssAxR.set_ylim([0, 724])

    mssAxL.set_xticks([0, 2, 4, 6, 8, 10, 12, 14, 16])
    mssAxL.set_yticks([1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4])

    # Legend and Labeling
    # PlotLegend(fig, lHandles=lHndls, lLabels=lLbls, loc=legLocs[_iFolder], ncol=1, LabelColor="#000000")
    # mssFig.text(x=0.1, y=0.83, s="$n_{contributing\ Tips} = $" + f"${_nxyKeys}$") # For vertical HBar above the plot
    mssFig.text(x=0.1, y=0.965, s="$n_{contributing\ Tips} = $" + f"${_nxyKeys}$") # For vertical HBar right of plot 

    specialFont = {"weight": "bold", "size": 35}
    mssAxL.text(x= 110/tScale, y=50e-6, s="$I_{Total}$", color="#00FF00", alpha=1, rotation=0, fontdict=specialFont)

    mssAxR.text(x=290/tScale, y=570, s="$U_{Supply}$", color="#FF00FF", alpha=0.5, rotation=37, fontdict=specialFont)
    mssAxR.text(x=450/tScale, y=575, s="$U_{Extr.}$", color="#FF00FF", alpha=1, rotation=0, fontdict=specialFont)


    # fig.suptitle("Histogram of current over time (colorized by count of tip in bin-range)")
    mssAxL.set_xlabel("Time [min]")
    mssAxL.set_ylabel("Current [A]")
    mssAxR.set_ylabel("Voltage [V]")
    # mssFig.subplots_adjust(left=0.1, right=0.91, top=0.82, bottom=0.085, wspace=0.25, hspace=0.2) # For vertical HBar above the plot (Size: 14x10)
    mssFig.subplots_adjust(left=0.085, right=0.825, top=0.95, bottom=0.085, wspace=0.25, hspace=0.2) # For vertical HBar right of plot (Size: 16x10)


    # Inset
    mssInsAxL.set_xlim([0.5e-9, 20e-6])
    mssInsAxL.set_ylim([0, 12.5])

    # mssInsAxL.set_xticks([1e-9, 1e-8, 1e-7, 1e-6, 1e-5])
    mssInsAxL.set_xticks([1e-9, 1e-8, 1e-7, 1e-6, 1e-5])
    mssInsAxL.set_yticks([0, 2, 4, 6, 8, 10, 12])


    ### Inset-Beatifulization x)
    # mssInsAxL.text  (x=0.7e-9, y=7.25, s=f"1D Histogram #{_singleHistIndex}\n(red dashed line)")
    mssInsAxL.text(x=0.7e-9, y=7, s="1D-histogram\n(dashed red line)")
    mssInsAxL.set_xlabel("Emission current [A]", color="white")
    mssInsAxL.set_ylabel("$n_{tips}$", color="white")






    #### Plot 4 tips
    _nTipsInSeparateQuadrantPlot = 4            # The n tips with the hightes currents are plotted in a separate plot window

    tipKeys = []
    _xyKeysCopy = _xyKeys.copy() # Make indipendent list from where keys can be taken out without affecting the original xyKeys!
    _highestxyKeys = []
    _highestxyKeyCurrents = []
    for _i in range(_nTipsInSeparateQuadrantPlot):
        _nkeycopy = len(_xyKeysCopy)

        _maxCurr = 0
        _maxCurrKey = (-1, -1)

        for _ixyKeyCopy in range(_nkeycopy):
            _xyKeyCopy = _xyKeysCopy[_ixyKeyCopy]
            _mssMaxCurr = mssCurrent[_xyKeyCopy].max()
            if _mssMaxCurr > _maxCurr:
                _maxCurr = _mssMaxCurr
                _maxCurrKey = _xyKeyCopy
        

        _xyKeysCopy.remove(_maxCurrKey)
        _nkeycopy = len(_xyKeysCopy)

        _highestxyKeys.append(_maxCurrKey)
        _highestxyKeyCurrents.append(_maxCurr)

    # Replace exemplarely for the first 700V sweep
    #  the last highest current with the damaged
    #  spot for paper (discussion of damaged area of coated cam)
    if replace4thOne[_iFolder] != None:
        del _highestxyKeys[-1]          # Delete last key to append the one slightly damaged one!
        del _highestxyKeyCurrents[-1]   # Delete last key to append the one slightly damaged one!
        dmgKeyInfo = replace4thOne[_iFolder]
        _highestxyKeys.append(dmgKeyInfo)
        _highestxyKeyCurrents.append(mssCurrent[dmgKeyInfo].max())

    SetTexFont(24)
    fig4, axL4 = plt.subplots(nrows=3, ncols=2)
    CombinePlots(fig4, axL4[0, 0:])
    axR4 = Twinx2D_3x2(fig=fig4, lAxis=axL4)
    # axR4 = Twinx2D_2x2(fig=fig4, lAxis=axL4)
    fig4.set_size_inches(w=14, h=12)
    fig4.subplots_adjust(left=0.11, right=0.92, top=0.92, bottom=0.1, wspace=0.4, hspace=0.3)

    if showImgs:
        plt.show(block=False)


    swpU = abs(swp["U7"])
    dpArr = [
        fe.DataProvider(ColumnHeaderKeysOrDict=["Time", "USply", "UExt", "ITip"  , "Share"], NumpyArray=np.transpose(np.vstack([t, swpU, u, mssCurrent[_highestxyKeys[0]], mssShares["ShareFac"][_highestxyKeys[0]] * 100  ]))), # Share in %
        fe.DataProvider(ColumnHeaderKeysOrDict=["Time", "USply", "UExt", "ITip"  , "Share"], NumpyArray=np.transpose(np.vstack([t, swpU, u, mssCurrent[_highestxyKeys[1]], mssShares["ShareFac"][_highestxyKeys[1]] * 100  ]))), # Share in %
        fe.DataProvider(ColumnHeaderKeysOrDict=["Time", "USply", "UExt", "ITip"  , "Share"], NumpyArray=np.transpose(np.vstack([t, swpU, u, mssCurrent[_highestxyKeys[2]], mssShares["ShareFac"][_highestxyKeys[2]] * 100  ]))), # Share in %
        fe.DataProvider(ColumnHeaderKeysOrDict=["Time", "USply", "UExt", "ITip"  , "Share"], NumpyArray=np.transpose(np.vstack([t, swpU, u, mssCurrent[_highestxyKeys[3]], mssShares["ShareFac"][_highestxyKeys[3]] * 100  ]))), # Share in %
        fe.DataProvider(ColumnHeaderKeysOrDict=["Time", "USply", "UExt", "ITotal", "Share"], NumpyArray=np.transpose(np.vstack([t, swpU, u, cf        ["IAll"]           , [100] * cf.Rows                     ]))), # Entire cathode
    ]
    _keepRange = np.where((swpU < swpU.max()) & (swpU >= 1))[0]
    _keepOffset = _keepRange[0] # Get shift-index before overriding
    _keepRange = np.array(range(_keepRange.size // 2 + 1)) # Append the first max-Supply Voltage point to the dataset
    _keepRange += _keepOffset 
    dpArr[0].KeepRows(_keepRange)
    dpArr[1].KeepRows(_keepRange)
    dpArr[2].KeepRows(_keepRange)
    dpArr[3].KeepRows(_keepRange)
    dpArr[4].KeepRows(_keepRange)


    fe.FowlerNordheim(DatMgr=dpArr[0], ColumnU="UExt", ColumnI="ITip"  , distance_μm=60)
    fe.FowlerNordheim(DatMgr=dpArr[1], ColumnU="UExt", ColumnI="ITip"  , distance_μm=60)
    fe.FowlerNordheim(DatMgr=dpArr[2], ColumnU="UExt", ColumnI="ITip"  , distance_μm=60)
    fe.FowlerNordheim(DatMgr=dpArr[3], ColumnU="UExt", ColumnI="ITip"  , distance_μm=60)
    fe.FowlerNordheim(DatMgr=dpArr[4], ColumnU="UExt", ColumnI="ITotal", distance_μm=60)

    fit = [
        fe.FowlerNordheimParameters(DatMgr=dpArr[0], ColumnFnX="FNx", ColumnFnY="FNy", xFitRegion=fnFitRegion[_iFolder], distance_μm=60, nInterpolPnts=1000),
        fe.FowlerNordheimParameters(DatMgr=dpArr[1], ColumnFnX="FNx", ColumnFnY="FNy", xFitRegion=fnFitRegion[_iFolder], distance_μm=60, nInterpolPnts=1000),
        fe.FowlerNordheimParameters(DatMgr=dpArr[2], ColumnFnX="FNx", ColumnFnY="FNy", xFitRegion=fnFitRegion[_iFolder], distance_μm=60, nInterpolPnts=1000),
        fe.FowlerNordheimParameters(DatMgr=dpArr[3], ColumnFnX="FNx", ColumnFnY="FNy", xFitRegion=fnFitRegion[_iFolder], distance_μm=60, nInterpolPnts=1000),
        fe.FowlerNordheimParameters(DatMgr=dpArr[4], ColumnFnX="FNx", ColumnFnY="FNy", xFitRegion=fnFitRegion[_iFolder], distance_μm=60, nInterpolPnts=1000),
    ]
    fit[0]["interpolatedUI"].ClipData(ColumnKeyOrIndex="U", RemoveAtValue=150, ClipFlag=fe.ClipFlags.Below)
    fit[1]["interpolatedUI"].ClipData(ColumnKeyOrIndex="U", RemoveAtValue=150, ClipFlag=fe.ClipFlags.Below)
    fit[2]["interpolatedUI"].ClipData(ColumnKeyOrIndex="U", RemoveAtValue=150, ClipFlag=fe.ClipFlags.Below)
    fit[3]["interpolatedUI"].ClipData(ColumnKeyOrIndex="U", RemoveAtValue=150, ClipFlag=fe.ClipFlags.Below)
    fit[4]["interpolatedUI"].ClipData(ColumnKeyOrIndex="U", RemoveAtValue=150, ClipFlag=fe.ClipFlags.Below)
    
    dark2   = get_cmap('Dark2')
    tab10   = get_cmap('tab10')
    tab20b  = get_cmap('tab20b')
    tab20c  = get_cmap('tab20c')
    accent  = get_cmap("Accent")
    set2    = get_cmap("Set2")
    
    cmap = [                    # Mapping proper colors with contrast to black and white
        tab10   .colors[ 0],
        tab10   .colors[ 1],
        tab10   .colors[ 2],
        tab10   .colors[ 3],
    ]
    if plotFN2EstimateFitRange:
        axL4[1,0].plot(dpArr[0]["FNx"], dpArr[0]["FNy"], "o--"  , markersize=7, linewidth=2.5, color=cmap[0], label="$I_{opt.}$")
        axL4[1,1].plot(dpArr[1]["FNx"], dpArr[1]["FNy"], "o--"  , markersize=7, linewidth=2.5, color=cmap[1], label="$I_{opt.}$")
        axL4[2,0].plot(dpArr[2]["FNx"], dpArr[2]["FNy"], "o--"  , markersize=7, linewidth=2.5, color=cmap[2], label="$I_{opt.}$")
        axL4[2,1].plot(dpArr[3]["FNx"], dpArr[3]["FNy"], "o--"  , markersize=7, linewidth=2.5, color=cmap[3], label="$I_{opt.}$")

        axL4[1,0].plot(fit[0]["interpolatedFN"]["fnx"], fit[0]["interpolatedFN"]["fny"], "--"  , markersize=12, linewidth=1.5, color="#606060", label="$Fitted$")
        axL4[1,1].plot(fit[1]["interpolatedFN"]["fnx"], fit[1]["interpolatedFN"]["fny"], "--"  , markersize=12, linewidth=1.5, color="#606060", label="$Fitted$")
        axL4[2,0].plot(fit[2]["interpolatedFN"]["fnx"], fit[2]["interpolatedFN"]["fny"], "--"  , markersize=12, linewidth=1.5, color="#606060", label="$Fitted$")
        axL4[2,1].plot(fit[3]["interpolatedFN"]["fnx"], fit[3]["interpolatedFN"]["fny"], "--"  , markersize=12, linewidth=1.5, color="#606060", label="$Fitted$")
    else:
        axL4[0,0].semilogy(dpArr[4]["USply"], dpArr[4]["ITotal"], "o--"  , markersize=7, linewidth=2.5, color="#000000", label=r"$I_{Total}$")
        axL4[1,0].semilogy(dpArr[0]["USply"], dpArr[0]["ITip"]  , "o--"  , markersize=7, linewidth=2.5, color=cmap[0], label=r"$I_{OMap.}$")
        axL4[1,1].semilogy(dpArr[1]["USply"], dpArr[1]["ITip"]  , "o--"  , markersize=7, linewidth=2.5, color=cmap[1], label=r"$I_{OMap.}$")
        axL4[2,0].semilogy(dpArr[2]["USply"], dpArr[2]["ITip"]  , "o--"  , markersize=7, linewidth=2.5, color=cmap[2], label=r"$I_{OMap.}$")
        axL4[2,1].semilogy(dpArr[3]["USply"], dpArr[3]["ITip"]  , "o--"  , markersize=7, linewidth=2.5, color=cmap[3], label=r"$I_{OMap.}$")

        axL4[0,0].semilogy(fit[4]["interpolatedUI"]["U"], fit[4]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=2.5, color="#606060", label=r"$Fit$")

        axL4[1,0].semilogy(fit[0]["interpolatedUI"]["U"], fit[0]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=2.5, color="#606060", label=r"$Fit$")
        axL4[1,1].semilogy(fit[1]["interpolatedUI"]["U"], fit[1]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=2.5, color="#606060", label=r"$Fit$")
        axL4[2,0].semilogy(fit[2]["interpolatedUI"]["U"], fit[2]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=2.5, color="#606060", label=r"$Fit$")
        axL4[2,1].semilogy(fit[3]["interpolatedUI"]["U"], fit[3]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=2.5, color="#606060", label=r"$Fit$")

        # axL4[0,0].semilogy(dpArr[4]["UExt"], dpArr[4]["ITotal"], "x--"  , markersize=10, linewidth=1.5, color="#000000", label="$I_{Total}$")
        # axL4[0,1].semilogy(dpArr[4]["UExt"], dpArr[4]["ITotal"], "x--"  , markersize=10, linewidth=1.5, color="#000000", label="$I_{Total}$")
        # axL4[1,0].semilogy(dpArr[4]["UExt"], dpArr[4]["ITotal"], "x--"  , markersize=10, linewidth=1.5, color="#000000", label="$I_{Total}$")
        # axL4[1,1].semilogy(dpArr[4]["UExt"], dpArr[4]["ITotal"], "x--"  , markersize=10, linewidth=1.5, color="#000000", label="$I_{Total}$")

        # axL4[0,0].semilogy(fit[4]["interpolatedUI"]["U"], fit[4]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#808080", label="$Fit_{FN}$")
        # axL4[0,1].semilogy(fit[4]["interpolatedUI"]["U"], fit[4]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#808080", label="$Fit_{FN}$")
        # axL4[1,0].semilogy(fit[4]["interpolatedUI"]["U"], fit[4]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#808080", label="$Fit_{FN}$")
        # axL4[1,1].semilogy(fit[4]["interpolatedUI"]["U"], fit[4]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#808080", label="$Fit_{FN}$")

        # axR4[0,0].plot(dpArr[4]["UExt"], dpArr[0]["Share"], ".--"  , markersize=7, linewidth=1.5, color="#000000", alpha=0.3, label=r"$S_{Total}$")

        axR4[1,0].plot(dpArr[0]["USply"], dpArr[0]["Share"], ".--"  , markersize=12, linewidth=2.5, color=cmap[0], alpha=0.25, label=r"$F_{OMap.}$")
        axR4[1,1].plot(dpArr[1]["USply"], dpArr[1]["Share"], ".--"  , markersize=12, linewidth=2.5, color=cmap[1], alpha=0.25, label=r"$F_{OMap.}$")
        axR4[2,0].plot(dpArr[2]["USply"], dpArr[2]["Share"], ".--"  , markersize=12, linewidth=2.5, color=cmap[2], alpha=0.25, label=r"$F_{OMap.}$")
        axR4[2,1].plot(dpArr[3]["USply"], dpArr[3]["Share"], ".--"  , markersize=12, linewidth=2.5, color=cmap[3], alpha=0.25, label=r"$F_{OMap.}$")



    axL4[0,0].text(x=160, y=7e-5, fontsize=36, s="$Total$", color="#000000")
    # axL4[1,0].text(x=155, y=1e-6, fontsize=36, s=f"$({_highestxyKeys[0][0]},{_highestxyKeys[0][1]})$" + "\n$(x,y)$", color=cmap[0])
    # axL4[1,1].text(x=155, y=1e-6, fontsize=36, s=f"$({_highestxyKeys[1][0]},{_highestxyKeys[1][1]})$" + "\n$(x,y)$", color=cmap[1])
    # axL4[2,0].text(x=155, y=1e-6, fontsize=36, s=f"$({_highestxyKeys[2][0]},{_highestxyKeys[2][1]})$" + "\n$(x,y)$", color=cmap[2])
    # axL4[2,1].text(x=155, y=1e-6, fontsize=36, s=f"$({_highestxyKeys[3][0]},{_highestxyKeys[3][1]})$" + "\n$(x,y)$", color=cmap[3])
    axL4[1,0].text(x=160, y=50e-6, fontsize=36, s=r"$E_{FEA, 1}$", color=cmap[0])
    axL4[1,1].text(x=160, y=50e-6, fontsize=36, s=r"$E_{FEA, 2}$", color=cmap[1])
    axL4[2,0].text(x=160, y=50e-6, fontsize=36, s=r"$E_{FEA, 3}$", color=cmap[2])
    axL4[2,1].text(x=160, y=50e-6, fontsize=36, s=r"$E_{FEA, 4}$", color=cmap[3])


    # fig4.suptitle("Optical derived currents and shares of the 4 most contributing tips")
    axL4[0, 0].set_ylabel("$Current\ [A]$")
    axL4[1, 0].set_ylabel("$Current\ [A]$")
    axL4[2, 0].set_ylabel("$Current\ [A]$")

    axR4[1, 1].set_ylabel("$Share\ [\%]$")
    axR4[2, 1].set_ylabel("$Share\ [\%]$")

    axR4[1, 1].yaxis.set_label_coords(1.14, 0.35)
    axR4[2, 1].yaxis.set_label_coords(1.14, 0.35)

    axL4[0, 0].set_xlabel("$U_{Supply}\ [V]$")
    axL4[2, 0].set_xlabel("$U_{Supply}\ [V]$")
    axL4[2, 1].set_xlabel("$U_{Supply}\ [V]$")

    axL4[0, 0].xaxis.set_label_coords(0.5, -0.15)
    # axL4[2, 0].xaxis.set_label_coords(1.18, 0.3) # not used!!!
    # axL4[2, 1].xaxis.set_label_coords(1.18, 0.3) # not used!!!


    if plotFN2EstimateFitRange:
        ShowMajorMinorY(axL4.flatten(), useLogLocator=False)
    else:
        ShowMajorMinorY(axL4.flatten(), useLogLocator=True)

    axL4[0, 0].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=True , labelleft=True , labelright=False)
    axR4[0, 0].tick_params(which="both", bottom=False, left=False, right=False, labelbottom=False, labelleft=False, labelright=False)

    axL4[1, 0].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=True , labelleft=True , labelright=False)
    axR4[1, 0].tick_params(which="both", bottom=False, left=False, right=True , labelbottom=False, labelleft=False, labelright=True )

    axL4[1, 1].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=True , labelleft=True , labelright=False)
    axR4[1, 1].tick_params(which="both", bottom=False, left=False, right=True , labelbottom=False, labelleft=False, labelright=True )

    axL4[2, 0].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=True , labelleft=True,  labelright=False)
    axR4[2, 0].tick_params(which="both", bottom=False, left=False, right=True , labelbottom=False, labelleft=False, labelright=True )

    axL4[2, 1].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=True , labelleft=True , labelright=False)
    axR4[2, 1].tick_params(which="both", bottom=False, left=False, right=True , labelbottom=False, labelleft=False, labelright=True )



    if plotFN2EstimateFitRange:
        SameXYLimitsOnAxisColl(axL4, [-35, -5], [0, 0.5])
    else:
        SameXYLimitsOnAxisColl(axL4, [1e-11, 1e-3], [150, 750])
        SameXYLimitsOnAxisColl(axR4, [-2, 25], None)

    axL4[0, 0].set_ylim([1e-8, 1e-3])

    axL4[0, 0].set_yticks([1e-8, 1e-6, 1e-4])
    axL4[1, 0].set_yticks([1e-10, 1e-8, 1e-6, 1e-4])
    axL4[1, 1].set_yticks([1e-10, 1e-8, 1e-6, 1e-4])
    axL4[2, 0].set_yticks([1e-10, 1e-8, 1e-6, 1e-4])
    axL4[2, 1].set_yticks([1e-10, 1e-8, 1e-6, 1e-4])

    # axR4[0, 0].set_yticks([0, 25, 50, 75, 100])
    axR4[1, 0].set_yticks([0, 5, 10, 15])
    axR4[1, 1].set_yticks([0, 5, 10, 15])
    axR4[2, 0].set_yticks([0, 5, 10, 15])
    axR4[2, 1].set_yticks([0, 5, 10, 15])

    axL4[0, 0].set_xticks([200,300,400,500,600,700])
    axL4[1, 0].set_xticks([200,300,400,500,600,700])
    axL4[1, 1].set_xticks([200,300,400,500,600,700])
    axL4[2, 0].set_xticks([200,300,400,500,600,700])
    axL4[2, 1].set_xticks([200,300,400,500,600,700])


    lHndls = [
        tuple([axL4[0,0].lines[0],          # Left axis Current
               axL4[1,0].lines[0],
               axL4[1,1].lines[0],
               axL4[2,0].lines[0],
               axL4[2,1].lines[0],
    ]),
        tuple([axR4[1,0].lines[0],          # Right axis share
               axR4[1,1].lines[0],
               axR4[2,0].lines[0],
               axR4[2,1].lines[0],
    ]),
        tuple([axL4[1,0].lines[1],          # Left axis fit
               axL4[1,1].lines[1],
               axL4[2,0].lines[1],
               axL4[2,1].lines[1],
    ]),
    #     tuple([axL4[0,0].lines[2]
    # ]),
    ]
    lLbls = [
        axL4[1,0].lines[0]._label,
        axR4[1,0].lines[0]._label,
        # axR4[0,0].lines[0]._label,
        # axL4[0,0].lines[2]._label,
        axL4[1,0].lines[1]._label,
    ]
    PlotLegend(fig4, lHandles=lHndls, lLabels=lLbls, loc=(0.12, 0.93), ncol=3, LabelColor="#000000")











    # Just a plot, being able to extract the turn-on voltage (before the inner vectors removed from json dump)
    SetTexFont(24) 
    figTotal, axLTotal = plt.subplots(nrows=1, ncols=1)
    # axR = axL.twinx()
    figTotal.set_size_inches(w=14, h=10)
    if showImgs:
        plt.show(block=False)

    # u = ud["UExt"]
    # i = cf["IAll"]
    dpTotalUI = dpArr[4]
    fitTotalUI = fit[4]["interpolatedUI"]
    axLTotal.semilogy(dpTotalUI ["UExt"], dpTotalUI ["ITotal"], "x--", color="#FF0000", label="ITotal")
    axLTotal.semilogy(fitTotalUI["U"], fitTotalUI["I"], "x--", color="#000000", label="ITotal")


    ShowMajorMinorY([axLTotal], useLogLocator=True)
    axLTotal.set_ylim([1e-13, 1e-3])
    axLTotal.set_xlim([200, 750])









    fPrefix = basename(folder).split(" ")[0] + " "
    savepath = dirname(folder)

    ### save FN Data
    jsonFitOut = {
        str(_highestxyKeys[0]): fit[0],
        str(_highestxyKeys[1]): fit[1],
        str(_highestxyKeys[2]): fit[2],
        str(_highestxyKeys[3]): fit[3],
        "(Cathode)"           : fit[4],
    }
    jsonKeys = list(jsonFitOut.keys())
    for _iFitKey in range(len(jsonKeys)):

        # For all
        _fitKey = jsonKeys[_iFitKey]
        del jsonFitOut[_fitKey]["fitFunc1D"]
        del jsonFitOut[_fitKey]["interpolatedFN"]
        del jsonFitOut[_fitKey]["interpolatedUI"]

        # dpArr[_iFitKey].ClipData("UExt", RemoveAtValue=dpArr)
        # jsonFitOut[_fitKey]["MeanShare"] = 

        # Only single tips
        if _iFitKey < 4:
            _hiKey = _highestxyKeys[_iFitKey]
            jsonFitOut[_fitKey]["MaxCurrent"] = _highestxyKeyCurrents[_iFitKey]
            _indexOfIMax = np.where(mssCurrent[_hiKey] == jsonFitOut[_fitKey]["MaxCurrent"])[0][0]
            jsonFitOut[_fitKey]["MaxShare"] = mssShares["ShareFac"][_hiKey][_indexOfIMax]
            jsonFitOut[_fitKey]["MaxSharePerc"] = jsonFitOut[_fitKey]["MaxShare"] * 100


        jsonFitOut["(Cathode)"]["MaxCurrent"] = np.max(cf["IAll"])
        _indexOfIMax = np.where(cf["IAll"] == np.max(cf["IAll"]))[0][0]
        jsonFitOut["(Cathode)"]["MaxShare"] = 1.0
        jsonFitOut["(Cathode)"]["MaxSharePerc"] = jsonFitOut["(Cathode)"]["MaxShare"] * 100

        

    jsonFName = join(savepath, f"{fPrefix} FNParams, 4x IOpt.json")
    with open(jsonFName, "w") as fJSON:
        fJSON.write(json.dumps(jsonFitOut))
    
    
    with open(f"{jsonFName}", "r+") as fJSON: # Postformatting
        fc = fJSON.read()
        fc = fc.replace(",", "\n")
        fc = fc.replace("{", "\n")
        fc = fc.replace("}", "")
        fc = fc.replace("]", "\n]\n")
        fc = fc.replace("[", "\n[\n")
        fc = fc.replace("\"(", "\n\n\"(")
        fc = fc.replace("\n ", "\n")
        fJSON.seek(0)
        fJSON.write(fc)






    # Save high-noise keys
    jsonFName = join(savepath, f"{fPrefix} High noise XYKeys.json")
    with open(jsonFName, "w") as fJSON:

        fJSON.write(json.dumps(_xyKeysHiNoise))
    
    
    with open(f"{jsonFName}", "r+") as fJSON: # Postformatting
        fc = fJSON.read()
        fc = fc.replace(",", "\n")
        fc = fc.replace("{", "\n")
        fc = fc.replace("}", "")
        fc = fc.replace("]", "\n]\n")
        fc = fc.replace("[", "\n[\n")
        fc = fc.replace("\"(", "\n\n\"(")
        fc = fc.replace("\n ", "\n")
        fJSON.seek(0)
        fJSON.write(fc)


    ### Save plots
    fig4   .savefig(join(savepath, "IV-Characteristic of the 4 strongest tips.svg"), dpi=900)
    fig    .savefig(join(savepath, "I vs t with total and all tip currents.svg"), dpi=900)
    mssFig .savefig(join(savepath, "Hist2D over time with single Hist1D as inset.svg"), dpi=900)
    mssFig2.savefig(join(savepath, "Hist2D over ITotal with single Hist1D as inset.svg"), dpi=900)
    # SaveFigList(figList=[fig], saveFolder=savepath, prefix=fPrefix, figSize=(14,10), dpi=300, ClearSaved=False)
    plt.close("all")



print("EOS")