import os
import pickle
import FieldEmission as fe
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import numpy as np
import json

from os.path import join, dirname, basename, abspath, splitext

from _lib import SplitAndMean, ReadElAsDP, ReadSwpAsDP, ReadSwpAsDPFromFolder, ReadPkl, ReadResistor, ReadResistorFromFolder
from _lib import GetQuadrantOfSpot, CombinePlots, Twinx2D_2x2, Twinx2D_3x2, SameXYLimitsOnAxisColl, SameXYLimitsOnLRSubplots, SaveFigList
from _lib import PlotSupTitleAndLegend, PlotLegend, ShowMajorMinorY

from _misc import SetTexFont

from _findMethods import FindXYKeysAboveMinValInMSSCurrents


showImgs = True
plotFN2EstimateFitRange = False # Not necessary anymore, as below the voltages can be given directly to auto-calculate the FN-coordinate range

folders = [
r"230727_171103 700V IMax1V",
]

legLocs = [ # LegendLocations
    (0.43, 0.1175), # Sweep 700V
]

USigMin = [ # U where the IV-Characteristic "starts"
    310, # Sweep 700V
]


USigMax = [ # U where the IV-Characteristics is not in regulation/Saturation
    450, # Sweep 700V
]

d_um = [ # distance in µm between tips and Camera
    60, # Sweep 700V
]


replace4thOne = [
    # (529, 2182),    # Sweep 700V    (can be used to replace the 4th tip, specified here!)
    None,           # Sweep 700V -> No risk for discussion!
]















fnFitRegion = [
    [d_um[0] / USigMax[0], d_um[0] / USigMin[0]], # Sweep     700V
]














os.chdir(dirname(__file__))

for _iFolder in range(len(folders)):
    folder = folders[_iFolder]

    # Lumi
    mss = ReadPkl(join(folder, r"PMP_mssContainer.pkl"))
    ses = ReadPkl(join(folder, r"PMP_sesContainer.pkl"))


    # Sweep
    swp = ReadSwpAsDPFromFolder(folder)

    # CurrentFlow
    resistor = ReadResistorFromFolder(folder)
    cf = ReadElAsDP(join(folder, r"Dev100_FEAR16v2(Ch0CF).dat"))
    cf.RemoveRows(0) # Remove initial datapoint

    # VoltageDrop
    ud = ReadElAsDP(join(folder, r"Dev100_FEAR16v2(Ch0UD).dat"))
    ud.RemoveRows(0) # Remove initial datapoint







    #### Prepare electrical data
    # CF
    cf["IAll"] = np.divide(cf["Y"], resistor)
    cf.RemoveColumns(["Y", "Dev7", "Time"])
    cf.AbsColumn("IAll")

    # UD
    ud["UExt"] = np.subtract(abs(swp["U7"]), abs(ud["Y"]))
    ud.RemoveColumns(["Y", "Time", "Dev7"])
    ud.AbsColumn("UExt")






    #### Get iteration values
    _nImgs = len(mss["MergedSensorSignal"])
    _xyKeys = list(mss["XYKeys"].keys())
    _nxyKeys = len(_xyKeys)

    # Build empty share-factor dictionary
    mssShares = {}
    mssShares["mss/U"]    = {}
    mssShares["ShareFac"] = {}
    mssShares["Sum"]      = []


    # Build lumiSpot/U
    for _iKey in range(_nxyKeys):
        _xyKey = _xyKeys[_iKey]
        mssShares["mss/U"][_xyKey] = []
        mssSpot = mss["XYKeys"][_xyKey]["MergedSensorSignal"]
        uSply = [1] * ud["UExt"].__len__() # Voltage for division = 1 --> When all tips emit at the same voltage, the division creates on all signals the same reduction --> Cancels out of the equation
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
        mssU = mssShares["mss/U"][_xyKey]
        mssShares["ShareFac"][_xyKey] = np.divide(mssU, mssShares["Sum"])

        mssShares["ShareFac"][_xyKey] = np.array(mssShares["ShareFac"][_xyKey])
        mssCurrent[_xyKey] = np.multiply(cf["IAll"], mssShares["ShareFac"][_xyKey])

        fnProvider = fe.DataProvider(["U", "I"], [ud["UExt"], mssCurrent[_xyKey]])
        fn = fe.FowlerNordheim(DatMgr=fnProvider, ColumnU="U", ColumnI="I", distance_μm=60)

        __ssK = list(ses.keys())[0]
        __xyK = replace4thOne[_iFolder]
        if __xyK != None: # If some XY Key is given, replace the 4th tip with it
            __min = np.array(mss["XYKeys"][__xyK]["MergedSensorSignal"][0])
            __vec = np.array(mss["XYKeys"][__xyK]["MergedSensorSignal"])
            __all = np.array(mss["MergedSensorSignal"])
            __dmgRelSpot = np.divide(__min, __vec)
            __dmgRelSpotPerc = np.multiply(__dmgRelSpot, 100)
            __dmgRelAll = np.divide(__min, __all)
            __dmgRelAllPerc = np.multiply(__dmgRelAll, 100)

            _iOff = int(USigMin[_iFolder] / 6 + 1) # Clip away when supply voltage < min-voltage to see only points with enough signal/current!
            _dmgRelAppPercNoNoise = __dmgRelAllPerc[_iOff:-_iOff]
            __meanDmgOnAll = np.mean(_dmgRelAppPercNoNoise)
            __stdDmgOnAll = np.std(_dmgRelAppPercNoNoise)


    _xyKeysHiNoise = FindXYKeysAboveMinValInMSSCurrents(mssCurrentContainer=mssCurrent, minVal=1e-9, onIndicies=range(-6, -1))
    print(f"High-noise tips in {folder}")
    print(str(_xyKeysHiNoise))










    # Plot all I vs. time
    SetTexFont(24)
    fig, axL = plt.subplots(nrows=1, ncols=1)
    axR = axL.twinx()
    fig.set_size_inches(w=14, h=10)
    if showImgs:
        plt.show(block=False)

    u = ud["UExt"]
    i = cf["IAll"]

    tDelta = 6.0
    t = np.linspace(start=0, stop=tDelta * (len(u)-1), num=len(u), endpoint=True)
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
    axL.set_xlim([t.min()-25, t.max()+25])
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
    fig.text(x=0.65, y=0.125, s="$n_{Active\ Tips} = $" + f"${_nxyKeys}$")

    fig.suptitle("Currents and voltages\nof the 21x21 cathode")
    axL.set_xlabel("Time [s]")
    axL.set_ylabel("Emissionsstrom [A]")
    axR.set_ylabel("Voltage [V]")










    #### Prepare Plot ITotal + 4 tip-quadrants
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

    if replace4thOne[_iFolder] != None:
        del _highestxyKeys[-1]          # Delete last key to append the one slightly damaged one!
        del _highestxyKeyCurrents[-1]   # Delete last key to append the one slightly damaged one!
        dmgKeyInfo = replace4thOne[_iFolder]
        _highestxyKeys.append(dmgKeyInfo)
        _highestxyKeyCurrents.append(mssCurrent[dmgKeyInfo].max())


    # Plot Total and 4 quadrants
    SetTexFont(24)
    fig4, axL4 = plt.subplots(nrows=3, ncols=2)
    CombinePlots(fig4, axL4[0, 0:])
    axR4 = Twinx2D_3x2(fig=fig4, lAxis=axL4)
    fig4.set_size_inches(w=14, h=10)
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
    
    cmap = get_cmap('Dark2')
    if plotFN2EstimateFitRange:
        axL4[1,0].plot(dpArr[0]["FNx"], dpArr[0]["FNy"], "1"  , markersize=12, linewidth=1.5, color=cmap.colors[0], label="$I_{opt.}$")
        axL4[1,1].plot(dpArr[1]["FNx"], dpArr[1]["FNy"], "1"  , markersize=12, linewidth=1.5, color=cmap.colors[1], label="$I_{opt.}$")
        axL4[2,0].plot(dpArr[2]["FNx"], dpArr[2]["FNy"], "1"  , markersize=12, linewidth=1.5, color=cmap.colors[2], label="$I_{opt.}$")
        axL4[2,1].plot(dpArr[3]["FNx"], dpArr[3]["FNy"], "1"  , markersize=12, linewidth=1.5, color=cmap.colors[3], label="$I_{opt.}$")

        axL4[1,0].plot(fit[0]["interpolatedFN"]["fnx"], fit[0]["interpolatedFN"]["fny"], "--"  , markersize=12, linewidth=1.5, color="#606060", label="$Fitted$")
        axL4[1,1].plot(fit[1]["interpolatedFN"]["fnx"], fit[1]["interpolatedFN"]["fny"], "--"  , markersize=12, linewidth=1.5, color="#606060", label="$Fitted$")
        axL4[2,0].plot(fit[2]["interpolatedFN"]["fnx"], fit[2]["interpolatedFN"]["fny"], "--"  , markersize=12, linewidth=1.5, color="#606060", label="$Fitted$")
        axL4[2,1].plot(fit[3]["interpolatedFN"]["fnx"], fit[3]["interpolatedFN"]["fny"], "--"  , markersize=12, linewidth=1.5, color="#606060", label="$Fitted$")
    else:
        axL4[0,0].semilogy(dpArr[4]["USply"], dpArr[4]["ITotal"], "1"  , markersize=12, linewidth=1.5, color="#000000", label=r"$I_{Total}$")
        axL4[1,0].semilogy(dpArr[0]["USply"], dpArr[0]["ITip"], "1"  , markersize=12, linewidth=1.5, color=cmap.colors[0], label=r"$I_{OMap.}$")
        axL4[1,1].semilogy(dpArr[1]["USply"], dpArr[1]["ITip"], "1"  , markersize=12, linewidth=1.5, color=cmap.colors[1], label=r"$I_{OMap.}$")
        axL4[2,0].semilogy(dpArr[2]["USply"], dpArr[2]["ITip"], "1"  , markersize=12, linewidth=1.5, color=cmap.colors[2], label=r"$I_{OMap.}$")
        axL4[2,1].semilogy(dpArr[3]["USply"], dpArr[3]["ITip"], "1"  , markersize=12, linewidth=1.5, color=cmap.colors[3], label=r"$I_{OMap.}$")

        axL4[0,0].semilogy(fit[4]["interpolatedUI"]["U"], fit[4]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#606060", label=r"$Fit$")

        axL4[1,0].semilogy(fit[0]["interpolatedUI"]["U"], fit[0]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#606060", label=r"$Fit$")
        axL4[1,1].semilogy(fit[1]["interpolatedUI"]["U"], fit[1]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#606060", label=r"$Fit$")
        axL4[2,0].semilogy(fit[2]["interpolatedUI"]["U"], fit[2]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#606060", label=r"$Fit$")
        axL4[2,1].semilogy(fit[3]["interpolatedUI"]["U"], fit[3]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#606060", label=r"$Fit$")

        # axL4[0,0].semilogy(dpArr[4]["UExt"], dpArr[4]["ITotal"], "x--"  , markersize=10, linewidth=1.5, color="#000000", label="$I_{Total}$")
        # axL4[0,1].semilogy(dpArr[4]["UExt"], dpArr[4]["ITotal"], "x--"  , markersize=10, linewidth=1.5, color="#000000", label="$I_{Total}$")
        # axL4[1,0].semilogy(dpArr[4]["UExt"], dpArr[4]["ITotal"], "x--"  , markersize=10, linewidth=1.5, color="#000000", label="$I_{Total}$")
        # axL4[1,1].semilogy(dpArr[4]["UExt"], dpArr[4]["ITotal"], "x--"  , markersize=10, linewidth=1.5, color="#000000", label="$I_{Total}$")

        # axL4[0,0].semilogy(fit[4]["interpolatedUI"]["U"], fit[4]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#808080", label="$Fit_{FN}$")
        # axL4[0,1].semilogy(fit[4]["interpolatedUI"]["U"], fit[4]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#808080", label="$Fit_{FN}$")
        # axL4[1,0].semilogy(fit[4]["interpolatedUI"]["U"], fit[4]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#808080", label="$Fit_{FN}$")
        # axL4[1,1].semilogy(fit[4]["interpolatedUI"]["U"], fit[4]["interpolatedUI"]["I"], "--"  , markersize=12, linewidth=1.5, color="#808080", label="$Fit_{FN}$")

        # axR4[0,0].plot(dpArr[4]["UExt"], dpArr[0]["Share"], ".--"  , markersize=7, linewidth=1.5, color="#000000", alpha=0.3, label=r"$S_{Total}$")

        axR4[1,0].plot(dpArr[0]["USply"], dpArr[0]["Share"], ".--"  , markersize=7, linewidth=1.5, color=cmap.colors[0], alpha=0.4, label=r"$F_{OMap.}$")
        axR4[1,1].plot(dpArr[1]["USply"], dpArr[1]["Share"], ".--"  , markersize=7, linewidth=1.5, color=cmap.colors[1], alpha=0.4, label=r"$F_{OMap.}$")
        axR4[2,0].plot(dpArr[2]["USply"], dpArr[2]["Share"], ".--"  , markersize=7, linewidth=1.5, color=cmap.colors[2], alpha=0.4, label=r"$F_{OMap.}$")
        axR4[2,1].plot(dpArr[3]["USply"], dpArr[3]["Share"], ".--"  , markersize=7, linewidth=1.5, color=cmap.colors[3], alpha=0.4, label=r"$F_{OMap.}$")



    fig4.text(x=0.130, y=0.8450, s="$Total$", color="#000000")
    fig4.text(x=0.130, y=0.5000, s="$Tip (x,y)$\n" + f"$({_highestxyKeys[0][0]},{_highestxyKeys[0][1]})$", color=cmap.colors[0])
    fig4.text(x=0.550, y=0.5000, s="$Tip (x,y)$\n" + f"$({_highestxyKeys[1][0]},{_highestxyKeys[1][1]})$", color=cmap.colors[1])
    fig4.text(x=0.130, y=0.2275, s="$Tip (x,y)$\n" + f"$({_highestxyKeys[2][0]},{_highestxyKeys[2][1]})$", color=cmap.colors[2])
    fig4.text(x=0.550, y=0.2275, s="$Tip (x,y)$\n" + f"$({_highestxyKeys[3][0]},{_highestxyKeys[3][1]})$", color=cmap.colors[3])


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


    if plotFN2EstimateFitRange:
        ShowMajorMinorY(axL4.flatten(), useLogLocator=False)
    else:
        ShowMajorMinorY(axL4.flatten(), useLogLocator=True)

    axL4[0, 0].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=True , labelleft=True , labelright=False)
    axR4[0, 0].tick_params(which="both", bottom=False, left=False, right=False, labelbottom=False, labelleft=False, labelright=False)

    axL4[1, 0].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=False, labelleft=True , labelright=False)
    axR4[1, 0].tick_params(which="both", bottom=False, left=False, right=True , labelbottom=False, labelleft=False, labelright=False)

    axL4[1, 1].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=False, labelleft=False, labelright=False)
    axR4[1, 1].tick_params(which="both", bottom=False, left=False, right=True , labelbottom=False, labelleft=False, labelright=True )

    axL4[2, 0].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=True , labelleft=True,  labelright=False)
    axR4[2, 0].tick_params(which="both", bottom=False, left=False, right=True , labelbottom=False, labelleft=False, labelright=False)

    axL4[2, 1].tick_params(which="both", bottom=True , left=True , right=False, labelbottom=True , labelleft=False, labelright=False)
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
    ]
    lLbls = [
        axL4[1,0].lines[0]._label,
        axR4[1,0].lines[0]._label,
        axL4[1,0].lines[1]._label,
    ]
    PlotLegend(fig4, lHandles=lHndls, lLabels=lLbls, loc=(0.125, 0.885), ncol=3, LabelColor="#000000")











    # Just a plot, being able to extract the turn-on voltage (before the inner vectors removed from json dump)
    SetTexFont(24)
    figTotal, axLTotal = plt.subplots(nrows=1, ncols=1)
    figTotal.set_size_inches(w=14, h=10)
    if showImgs:
        plt.show(block=False)

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

        # Only single tips
        if _iFitKey < 4:
            _hiKey = _highestxyKeys[_iFitKey]
            jsonFitOut[_fitKey]["MaxCurrent"] = _highestxyKeyCurrents[_iFitKey]
            _indexOfIMax = np.where(mssCurrent[_hiKey] == jsonFitOut[_fitKey]["MaxCurrent"])[0][0]
            jsonFitOut[_fitKey]["MaxShare"] = mssShares["ShareFac"][_hiKey][_indexOfIMax]
            jsonFitOut[_fitKey]["MaxSharePerc"] = jsonFitOut[_fitKey]["MaxShare"] * 100

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
    fig4.savefig(join(savepath, "IV-Characteristic of the 4 strongest tips.png"), dpi=300)
    fig .savefig(join(savepath, "I vs t with total and all tip currents.png"), dpi=300)
    plt.close("all")



print("EOS")