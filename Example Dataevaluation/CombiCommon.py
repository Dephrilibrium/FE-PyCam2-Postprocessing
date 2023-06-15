import sys
import os
from os.path import join, dirname, basename, abspath, splitext
sys.path.append(dirname(dirname(abspath(__file__))))

from lib import SplitAndMean, ReadElAsDP, ReadSwpAsDP, ReadSwpAsDPFromFolder, ReadPkl, ReadResistor, ReadResistorFromFolder
from lib import GetQuadrantOfSpot, CombinePlots, Twinx2D_2x2, Twinx2D_3x2, SameXYLimitsOnAxisColl, SameXYLimitsOnLRSubplots, SaveFigList
from lib import PlotSupTitleAndLegend, PlotLegend, ShowMajorMinorY

# from CombiCommon import Build_CF_UD_DP, Build_IC_DP, AbsAllDPColumns
# from CombiCommon import DataPreparation, DataPlot, FNDataPreparation, FNDataPlot

import glob
import FieldEmission as fe
import numpy as np
import matplotlib.pyplot as plt
import parse
import json

from misc import PlotSupTitleAndLegend, SaveFigList, AdjustFigSize, PlotLegendOnly, SetTexFont




def Build_CF_UD_DP(cf:fe.DataProvider, ud:fe.DataProvider, uVec, resistor, dTime):

    rows = cf.Rows
    time = np.linspace(start=0, stop=dTime*rows, num=rows, endpoint=True)
    cfud = fe.DataProvider(["Time"], time)

    cfud["ITip"] = cf["Y"]
    cfud["UDrp"] = ud["Y"]
    cfud["UTip"] = ud["Y"]
    cfud["USply"] = uVec.copy()

    cfud["ITip"] = np.divide  (cfud["ITip"] , resistor)
    cfud["UTip"] = np.subtract(abs(cfud["USply"]), abs(cfud["UTip"]))
    return cfud


def AbsAllDPColumns(dp:fe.DataProvider):
    for _iCol in range(dp.Columns):
        dp.AbsColumn(_iCol)
    return dp



def __SearchUp__(iVec, iStart):
    _iTake = iStart
    for _iIter in range(len(iVec)):
        if not iVec.__contains__(_iTake):
            break
        _iTake += 1

    success = False
    if _iIter < len(iVec):
        success = True

    return _iTake, success


def __SearchDown__(iVec, iStart):
    _iTake = iStart
    for _iIter in range(iStart):
        if not iVec.__contains__(_iTake):
            break
        _iTake -= 1

    success = False
    if _iIter < len(iVec):
        success = True

    return _iTake, success


def Build_IC_DP(cf:fe.DataProvider, uVec, dTime):

    rows = cf.Rows
    time = np.linspace(start=0, stop=dTime*rows, num=rows, endpoint=True)
    cfud = fe.DataProvider(["Time"], time)

    curr = cf["Y"]
    currInfPositions = np.where(curr > 1e37)[0]
    for _iOvr in currInfPositions:
        if _iOvr == 0:
            pass
        else:
            _iTake = _iOvr - 1

        curr[_iOvr] = curr[_iTake]



    cfud["ISum"] = abs(cf["Y"])
    cfud["USply"] = abs(uVec.copy())
    return cfud



def DataPreparation(callerGlobals, callerLocals):
    globals().update(callerLocals)
    globals().update(callerGlobals)
    locals().update(callerGlobals)
    locals().update(callerLocals)

    del callerLocals, callerGlobals

    # Grab brightness
    brPath = abspath(join(folder, brPaths[_i]))
    brDat = ReadPkl(brPath)
    keys = list(brDat["Spot"].keys())
    for _iKeyPopout in XY_Popout:
        keys.pop(_iKeyPopout)

    # Grab el data and collect XY wise in dictionaries
    elDat = dict()
    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        x, y = GetQuadrantOfSpot(spotCoord=_xy, imgWH=imgWH)
        _iEl = 2*y + x

        cfPath = abspath(join(folder, cfPaths[tipNum_2_XYiPos[_iEl]]))
        udPath = abspath(join(folder, udPaths[tipNum_2_XYiPos[_iEl]]))
        icPath = abspath(join(folder, icPaths[tipNum_2_XYiPos[_iEl]]))

        # Read and manage el. data
        cfDat = ReadElAsDP(cfPath)
        udDat = ReadElAsDP(udPath)
        icDat = ReadElAsDP(icPath)
        swDat = ReadSwpAsDPFromFolder(folder)
        reVal = ReadResistorFromFolder(folder)

        cfDat.RemoveRows(-1)
        udDat.RemoveRows(-1)
        icDat.RemoveRows(-1)
        elDat = Build_CF_UD_DP(cf=cfDat, ud=udDat, uVec=swDat["U7"], resistor=reVal, dTime=6)
        elDat = AbsAllDPColumns(elDat)
        icDat = Build_IC_DP(icDat, swDat["U7"], dTime=6)
        icDat = AbsAllDPColumns(icDat)

        # Collect separately
        tipSep["el"][_xy] = elDat


        #Divide bright by U to remove U-dependency (!!!Forgot firstly!!! --> Brightnesscurrent differed in regulation!)
        # tipSep["br"][_xy] = np.array(brDat["Spot"][_xy]["SpotBright"]["xTheory"])
        _tipSepTmp = np.array(brDat["Spot"][_xy]["SpotBright"]["xTheory"])
        _elUTipTmp = elDat["UTip"]
        tipSep["br"][_xy] = np.divide(_tipSepTmp, _elUTipTmp**4)
        # tipSep["br"][_xy] = _tipSepTmp

        

        # Build brightness-sum (100%)
        if _iXY == 0:
            tipSum["el"] = np.array(tipSep["el"][_xy]["ITip"].copy())
            tipSum["br"] = np.array(tipSep["br"][_xy].copy())
        else:
            tipSum["el"] = np.add(tipSum["el"], tipSep["el"][_xy]["ITip"])
            tipSum["br"] = np.add(tipSum["br"], tipSep["br"][_xy])

    # Build the contribution factors
    contrib["Sum"] = np.nan_to_num(np.divide(tipSum["br"], tipSum["br"]), copy=False, nan=0, posinf=0, neginf=0)
    contrib["SumCheck"] = []
    contrib["SumSub"] = []
    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        x, y = GetQuadrantOfSpot(spotCoord=_xy, imgWH=imgWH)
        _iEl = 2*y + x

        contrib[_xy] = np.nan_to_num(np.divide(tipSep["br"][_xy], tipSum["br"]), copy=True, nan=0, posinf=0, neginf=0)
        if _iXY == 0:
            contrib["SumCheck"] = contrib[_xy].copy()
        else:
            contrib["SumCheck"] = np.add(contrib["SumCheck"], contrib[_xy].copy())

    contrib["SumSub"] = np.subtract(contrib["Sum"], contrib["SumCheck"])

    # brCurr["Sum"] = np.multiply(tipSum["el"], contrib["Sum"])
    brCurr["Sum"] = np.multiply(icDat["ISum"], contrib["Sum"])
    brCurr["Tips"] = dict()
    curDiv["Sum"] = []
    curDiv["Tips"] = dict()
    # curDiv["Sum"] = np.nan_to_num(np.divide(brCurr["Sum"], tipSum["el"]), copy=True, nan=0, posinf=0, neginf=0)
    curDiv["Sum"] = np.nan_to_num(np.divide(brCurr["Sum"], icDat["ISum"]), copy=True, nan=0, posinf=0, neginf=0)
    curDiv["Tips"] = dict()
    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        # brCurr["Tips"][_xy] = np.multiply(tipSum["el"], contrib[_xy])
        brCurr["Tips"][_xy] = np.multiply(icDat["ISum"], contrib[_xy])
        curDiv["Tips"][_xy] = np.nan_to_num(np.divide(brCurr["Tips"][_xy], tipSep["el"][_xy]["ITip"]), copy=True, nan=0, posinf=0, neginf=0)

    return globals(), locals()



def DataPlot(callerGlobals, callerLocals):
    globals().update(callerLocals)
    globals().update(callerGlobals)
    locals().update(callerGlobals)
    locals().update(callerLocals)


    SetTexFont(13)

    fig, axL = plt.subplots(nrows=3, ncols=2)
    fig.set_size_inches(w=14, h=10)
    CombinePlots(fig, axL[0, 0:])

    axR = Twinx2D_3x2(fig, axL)
    figs.append(fig)
    axLs.append(axL)
    axRs.append(axR)

    # Plot
    # # axL[0,0].semilogy(elDat["Time"], tipSum["el"] , "o-.", markersize=6, linewidth=1.5, color="#000000", label="Int. Current")
    axL[0,0].semilogy(elDat["Time"], icDat["ISum"], "x", markersize=10, linewidth=1.5, color="#000000", label="el. Current")
    axL[0,0].semilogy(elDat["Time"], brCurr["Sum"], "1"  , markersize=12, linewidth=1.5, color="#808080", label="br. Current")
    # axR[0,0].plot    (elDat["Time"], curDiv["Sum"], "+"  , markersize=8, linewidth=1.5, color="#FF00FF", label="el./br. Current")
    axR[0,0].plot    (elDat["Time"], icDat["USply"], "+"  , markersize=8, linewidth=1.5, color="#FF00FF", label="Supply/Tip Voltage")
    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        x, y = GetQuadrantOfSpot(spotCoord=_xy, imgWH=imgWH)
        _iEl = 2*y + x
        y += 1
        elTip = tipSep["el"][_xy]
        brTip = brDat["Spot"][_xy]["SpotBright"]["xTheory"]
        brCur = brCurr["Tips"][_xy]
        cDiv = curDiv["Tips"][_xy]

        axL[y, x].semilogy(elDat["USply"], elTip["ITip"], "x", markersize=10, linewidth=1.5, color=plotCol["el"]  [_iEl], label="el. Current")
        # axL[0, 0].semilogy(elDat["Time"] , elTip["ITip"], "x", markersize=6, linewidth=1.5, color=plotCol["el"]  [_iEl], label="Tip-Current")

        axL[y, x].semilogy(elDat["USply"], brCur        , "1", markersize=12, linewidth=1.5, color=plotCol["brEl"][_iEl], label="br. Current")
        # axL[0, 0].semilogy(elDat["Time"] , brCur        , "1", markersize=12, linewidth=1.5, color=plotCol["brEl"][_iEl], label="Tip-BrCurrent")

        # axR[y, x].plot    (elDat["USply"], curDiv["Tips"][_xy], "+", markersize=8, linewidth=1.5, color=plotCol["contrib"][_iEl], label="el./br. Current")
        axR[y, x].plot    (elDat["USply"], elTip["UTip"], "+", markersize=8, linewidth=1.5, color=plotCol["contrib"][_iEl], label="Supply/Tip Voltage")

        # axR[y, x].plot(elDat["USply"], cDiv         , "3-.", markersize=3, linewidth=1.5, color=plotCol["br"][_iEl], label="Tip-BrCurrent")
        # axR[0, 0].plot(elDat["Time"] , cDiv         , "3-.", markersize=3, linewidth=1.5, color=plotCol["br"][_iEl], label="Tip-BrCurrent")

        # axR[y, x].semilogy(elDat["USply"], brTip        , "1-.", markersize=2, linewidth=1.5, color=plotCol["br"]  [_iEl], label="Tip-Brightness")
        # axL[y, x].semilogy(elDat["USply"] , brCur        , "1-.", markersize=2, linewidth=1.5, color=plotCol["brEl"][_iEl], label="Tip-BrCurrent")
        # axR[0, 0].semilogy(elDat["Time"] , brTip        , "1-.", markersize=2, linewidth=1.5, color=plotCol["br"]  [_iEl], label="Tip-Brightness")

    return globals(), locals()










def FNDataPreparation(callerGlobals, callerLocals):
    globals().update(callerLocals)
    globals().update(callerGlobals)
    locals().update(callerGlobals)
    locals().update(callerLocals)

    nanXReplace = 10
    nanYReplace = -25

    icFN = fe.FowlerNordheim(DatMgr=icDat, ColumnU="USply", ColumnI="ISum", distance_µm=50)
    icFN["FNx"] = np.nan_to_num(icFN["FNx"], copy=False, nan=nanXReplace, posinf=nanXReplace, neginf=nanXReplace)
    icFN["FNy"] = np.nan_to_num(icFN["FNy"], copy=False, nan=nanYReplace, posinf=nanYReplace, neginf=nanYReplace)

    tipSumDP = fe.DataProvider("USply", icDat["USply"])
    # tipSumDP["ISum"] = tipSum["br"]
    tipSumDP["ISum"] = brCurr["Sum"]
    tipSumFN = fe.FowlerNordheim(DatMgr=tipSumDP, ColumnU="USply", ColumnI="ISum", distance_µm=50)
    del tipSumDP

    tipSumFNDiv = np.nan_to_num(np.divide(icFN["FNy"], tipSumFN["FNy"]), copy=True, nan=0, posinf=0, neginf=0)
    # tipSumFNDivCut = fe.DataProvider(tipSumFNDiv.HeaderColumn, tipSumFNDiv.data)
    # tipSumFNDivMeanAndStd = {
    #     "Mean": np.nanmean(tipSumFNDiv[])
    # }

    tipSepFN = dict()
    tipSepFN["elFN"] = dict()
    tipSepFN["brFN"] = dict()
    tipSepFNDiv = dict()
    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        # Electrical
        _tipDP = tipSep["el"][_xy]
        _fn = fe.FowlerNordheim(DatMgr=_tipDP, ColumnU="USply", ColumnI="ITip", distance_µm=50)
        tipSepFN["elFN"][_xy] = _fn

        # Virtual brightnesscurrent
        tipSepDP = fe.DataProvider("USply", _tipDP["USply"])
        # tipSepDP["ITip"] = tipSum["br"]
        tipSepDP["ITip"] = brCurr["Tips"][_xy]
        _fn = fe.FowlerNordheim(DatMgr=tipSepDP, ColumnU="USply", ColumnI="ITip", distance_µm=50)
        _fn["FNx"] = np.nan_to_num(_fn["FNx"], copy=False, nan=nanXReplace, posinf=nanXReplace, neginf=nanXReplace)
        _fn["FNy"] = np.nan_to_num(_fn["FNy"], copy=False, nan=nanYReplace, posinf=nanYReplace, neginf=nanYReplace)

        # fe.FowlerNordheimParameters(DatMgr=)

        tipSepFN["brFN"][_xy] = _fn

        tipSepFNDiv[_xy] = np.nan_to_num(np.divide(tipSepFN["elFN"][_xy]["FNy"], tipSepFN["brFN"][_xy]["FNy"]), copy=True, nan=0, posinf=0, neginf=0)

    del tipSepDP

    return globals(), locals()




def FNDataPlot(callerGlobals, callerLocals):
    globals().update(callerLocals)
    globals().update(callerGlobals)
    locals().update(callerGlobals)
    locals().update(callerLocals)


    SetTexFont(13)
    fig, axL = plt.subplots(nrows=3, ncols=2)
    fig.set_size_inches(w=14, h=10)
    CombinePlots(fig, axL[0, 0:])

    axR = Twinx2D_3x2(fig, axL)
    figs.append(fig)
    axLs.append(axL)
    axRs.append(axR)

    # Plot
    # # axL[0,0].semilogy(elDat["Time"], tipSum["el"] , "o-.", markersize=6, linewidth=1.5, color="#000000", label="Int. Current")
    axL[0,0].plot(icFN    ["FNx"], icFN    ["FNy"], "x", markersize=10, linewidth=1.5, color="#000000", label="el. Current")
    axL[0,0].plot(tipSumFN["FNx"], tipSumFN["FNy"], "1"  , markersize=12, linewidth=1.5, color="#808080", label="br. Current")
    axR[0,0].plot(icFN    ["FNx"], tipSumFNDiv    , "+"  , markersize=8, linewidth=1.5, color="#FF00FF", label="el./br. Current")
    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        x, y = GetQuadrantOfSpot(spotCoord=_xy, imgWH=imgWH)
        _iEl = 2*y + x
        y += 1
        elTip = tipSep["el"][_xy]
        brTip = brDat["Spot"][_xy]["SpotBright"]["xTheory"]
        brCur = brCurr["Tips"][_xy]
        cDiv = curDiv["Tips"][_xy]

        axL[y, x].plot(tipSepFN["elFN"][_xy]["FNx"], tipSepFN["elFN"][_xy]["FNy"], "x", markersize=10, linewidth=1.5, color=plotCol["el"]  [_iEl], label="el. Current")
        # axL[0, 0].semilogy(elDat["Time"] , elTip["ITip"], "x", markersize=6, linewidth=1.5, color=plotCol["el"]  [_iEl], label="Tip-Current")

        axL[y, x].plot(tipSepFN["brFN"][_xy]["FNx"], tipSepFN["brFN"][_xy]["FNy"], "1", markersize=12, linewidth=1.5, color=plotCol["brEl"][_iEl], label="br. Current")
        # axL[0, 0].semilogy(elDat["Time"] , brCur        , "1", markersize=12, linewidth=1.5, color=plotCol["brEl"][_iEl], label="Tip-BrCurrent")

        axR[y, x].plot(tipSepFN["elFN"][_xy]["FNx"], tipSepFNDiv[_xy]       , "+", markersize=8, linewidth=1.5, color=plotCol["contrib"][_iEl], label="el./br. Current")

        # axR[y, x].plot(elDat["USply"], cDiv         , "3-.", markersize=3, linewidth=1.5, color=plotCol["br"][_iEl], label="Tip-BrCurrent")
        # axR[0, 0].plot(elDat["Time"] , cDiv         , "3-.", markersize=3, linewidth=1.5, color=plotCol["br"][_iEl], label="Tip-BrCurrent")

        # axR[y, x].semilogy(elDat["USply"], brTip        , "1-.", markersize=2, linewidth=1.5, color=plotCol["br"]  [_iEl], label="Tip-Brightness")
        # axL[y, x].semilogy(elDat["USply"] , brCur        , "1-.", markersize=2, linewidth=1.5, color=plotCol["brEl"][_iEl], label="Tip-BrCurrent")
        # axR[0, 0].semilogy(elDat["Time"] , brTip        , "1-.", markersize=2, linewidth=1.5, color=plotCol["br"]  [_iEl], label="Tip-Brightness")

    return globals(), locals()











def DataBuildPotentials(callerGlobals, callerLocals):
    globals().update(callerLocals)
    globals().update(callerGlobals)
    locals().update(callerGlobals)
    locals().update(callerLocals)

    potentials = dict()
    potentials["USply"] = icDat["USply"]
    potentials["PSply"] = abs(icDat["USply"])
    potentials["UTips"] = dict()
    potentials["PTips"] = dict()

    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        _tip = tipSep["el"][_xy]
        potentials["UTips"][_xy] = abs(_tip["UTip"])
        # potentials["PTips"] [_xy] = abs(np.subtract(abs(_tip["USply"]), abs(_tip["UDrp"])))
        potentials["PTips"] [_xy] = abs(_tip["UDrp"])

    return globals(), locals()





def DataPlotPotentials(callerGlobals, callerLocals):
    globals().update(callerLocals)
    globals().update(callerGlobals)
    locals().update(callerGlobals)
    locals().update(callerLocals)

    # Plot
    SetTexFont(13)

    fig, axL = plt.subplots(nrows=2, ncols=1)
    fig.set_size_inches(w=14, h=10)

    # axR = Twinx2D_3x2(fig, axL)
    figs.append(fig)
    axLs.append(axL)
    # axRs.append(axR)

    axLs[-1][0].plot(potentials["USply"], potentials["USply"], "o", markersize=7, linewidth=1.5, color="#000000", label="$U_{Supply}$")
    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        x, y = GetQuadrantOfSpot(spotCoord=_xy, imgWH=imgWH)
        _iEl = 2*y + x
        axLs[-1][0].plot(potentials["USply"], potentials["UTips"][_xy], "x", markersize=9, linewidth=1.5, color=plotCol["el"]  [_iEl], label=legendStrs[_iXY])

    axLs[-1][1].plot(potentials["USply"], potentials["PSply"], "o", markersize=7, linewidth=1.5, color="#000000", label="$U_{Supply}$")
    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        x, y = GetQuadrantOfSpot(spotCoord=_xy, imgWH=imgWH)
        _iEl = 2*y + x
        axLs[-1][1].plot(potentials["USply"], potentials["PTips"][_xy], "x", markersize=9, linewidth=1.5, color=plotCol["el"]  [_iEl], label=legendStrs[_iXY])

    return globals(), locals()












def FN_And_CurrDeviation(callerGlobals, callerLocals):
    globals().update(callerLocals)
    globals().update(callerGlobals)
    locals().update(callerGlobals)
    locals().update(callerLocals)


    for _iArea in range(len(iTipMaxs)):
        jsonName = jsonNames[_iArea]
        iTipMax  = iTipMaxs [_iArea]

        _fnKeys = list(tipSep["el"].keys())
        uiMean      = []
        uiStd       = []
        fnDivMnFac  = []
        fnDivStdFac = []
        fnDivMn     = []
        fnDivStd    = []
        fnPrms = {}
        for _iFnK in range(len(_fnKeys)):
            _fnK = _fnKeys[_iFnK]
            msk = np.where((tipSep['el'][_fnK]["ITip"] >= iTipMax[_iFnK][0]) & (tipSep['el'][_fnK]["ITip"] <= iTipMax[_iFnK][1]))

            UIElDat = tipSep['el'][_fnK]["ITip"][msk]
            uiMean.append(np.mean(UIElDat))
            uiStd .append(np.std (UIElDat))

            FNDivDat = tipSepFNDiv[_fnK][msk]
            fnDivMnFac .append(np.mean(FNDivDat))
            fnDivStdFac.append(np.std (FNDivDat))

            _fnx = tipSep['el'][_fnK]["FNx"][msk]
            _fny = tipSep['el'][_fnK]["FNy"][msk]
            _cleanFN = fe.DataProvider(["FNx", "FNy"], [_fnx, _fny])

            if (_iArea == 2): # Definition uses index 3 for unregulated data-clipping
                if (_cleanFN.Rows < 2): # Vector to short for interpolation -> Add dummy-row and insert dummy-data resulting in nonsense parameters
                    _cleanFN.AppendRow([0, 0])
                    _cleanFN["FNx"] = [0.1, 0.2]
                    _cleanFN["FNy"] = [0,   0  ]

                _fnParams = fe.FowlerNordheimParameters(DatMgr=_cleanFN, ColumnFnX="FNx", ColumnFnY="FNy", xFitRegion=[0, 0.5], distance_μm=50, phiMaterial=4.8)
                fnPrms[_fnK] = _fnParams

                with open(f"{jsonFNName}", "w") as fJSON:
                    fJSON.write(json.dumps(fnDivDat))

                with open(f"{jsonFNName}", "r+") as fJSON:
                    fc = fJSON.read()
                    fc = fc.replace(",", "\n")
                    fc = fc.replace("{", "\n")
                    fc = fc.replace("}", "")
                    fc = fc.replace("]", "\n]\n")
                    fc = fc.replace("[", "\n[\n")
                    fc = fc.replace("\n ", "\n")
                    fJSON.seek(0)
                    fJSON.write(fc)


        fnDivMn  = fnDivMnFac .copy() # Copy: Factors -> Percent
        fnDivStd = fnDivStdFac.copy() # Copy: Factors -> Percent
        fnDivMn  = np.multiply(fnDivMn , 100) # -> %
        fnDivStd = np.multiply(fnDivStd, 100) # -> %
        fnDivDat =     {
            "FN Div Fac": {
                "Mean": np.mean(fnDivMnFac ),
                "Std" : np.std (fnDivStdFac),
                "TipMean": fnDivMnFac ,
                "TipStd" : fnDivStdFac,
            },
            "FN Div %": {
                "Mean": np.mean(fnDivMn),
                "Std": np.mean(fnDivStd),
                "TipMean": fnDivMn .tolist(),
                "TipStd" : fnDivStd.tolist(),
            },
            "UI": {
                "Mean": np.mean(uiMean),
                "Std" : np.mean(uiStd ),
                "TipMean": uiMean,
                "TipStd" : uiStd ,
            }
        }
        # with open('FNCurrDiv - Both Areas.csv', 'w') as f:  # You will need 'wb' mode in Python 2.x
        #     writer = csv.writer(f)
        #     for key, value in fnDivDat.items():
        #         writer.writerow([key, value])

        with open(f"{jsonName}", "w") as fJSON:
            fJSON.write(json.dumps(fnDivDat))

        with open(f"{jsonName}", "r+") as fJSON:
            fc = fJSON.read()
            fc = fc.replace(",", "\n")
            fc = fc.replace("{", "\n")
            fc = fc.replace("}", "")
            fc = fc.replace("]", "\n]\n")
            fc = fc.replace("[", "\n[\n")
            fc = fc.replace("\n ", "\n")
            fJSON.seek(0)
            fJSON.write(fc)

    return globals(), locals()








def FNDeviDataPlot(callerGlobals, callerLocals):
    globals().update(callerLocals)
    globals().update(callerGlobals)
    locals().update(callerGlobals)
    locals().update(callerLocals)


    testErrors = [
        5.410445109405955e-08,
        8.876179886749666e-08,
        9.459228128216161e-08,
        6.997487279154668e-08,
    ]


    SetTexFont(13)

    fig, axL = plt.subplots(nrows=3, ncols=2)
    fig.set_size_inches(w=14, h=10)
    CombinePlots(fig, axL[0, 0:])

    axR = Twinx2D_3x2(fig, axL)
    figs.append(fig)
    axLs.append(axL)
    axRs.append(axR)

    # Plot
    # # axL[0,0].semilogy(elDat["Time"], tipSum["el"] , "o-.", markersize=6, linewidth=1.5, color="#000000", label="Int. Current")
    axL[0,0].semilogy(elDat["Time"], icDat["ISum"], "x", markersize=10, linewidth=1.5, color="#000000", label="el. Current")
    axL[0,0].semilogy(elDat["Time"], brCurr["Sum"], "1"  , markersize=12, linewidth=1.5, color="#808080", label="br. Current")
    # axR[0,0].plot    (elDat["Time"], curDiv["Sum"], "+"  , markersize=8, linewidth=1.5, color="#FF00FF", label="el./br. Current")
    axR[0,0].plot    (elDat["Time"], icDat["USply"], "+"  , markersize=8, linewidth=1.5, color="#FF00FF", label="Supply/Tip Voltage")
    for _iXY in range(len(keys)):
        _xy = keys[_iXY]
        x, y = GetQuadrantOfSpot(spotCoord=_xy, imgWH=imgWH)
        _iEl = 2*y + x
        y += 1
        elTip = tipSep["el"][_xy]
        brTip = brDat["Spot"][_xy]["SpotBright"]["xTheory"]
        brCur = brCurr["Tips"][_xy]
        cDiv = curDiv["Tips"][_xy]


        # error = fnDivDat["UI"]["TipStd"][_iXY]
        error = testErrors[_iXY]
        axL[y, x].semilogy(elDat["USply"], elTip["ITip"], "x", markersize=10, linewidth=1.5, color=plotCol["el"]  [_iEl], label="el. Current")
        
        # axL[y, x].semilogy(elDat["USply"], brCur        , "1", markersize=12, linewidth=1.5, color=plotCol["brEl"][_iEl], label="br. Current")
        axL[y, x].errorbar(x=elDat["USply"], y=brCur, yerr=error, fmt="1", markersize=12, linewidth=1.5, color=plotCol["brEl"][_iEl], label="br. Current")

        axR[y, x].plot    (elDat["USply"], elTip["UTip"], "+", markersize=8, linewidth=1.5, color=plotCol["contrib"][_iEl], label="Supply/Tip Voltage")

    return globals(), locals()