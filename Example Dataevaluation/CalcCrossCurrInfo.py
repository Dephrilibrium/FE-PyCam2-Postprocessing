import pickle
import json
import numpy as np
import matplotlib.pyplot as plt
import FieldEmission as fe
import parse
from os.path import join, basename, dirname













def CalcCrossEmissionInfo(g, l):
    globals().update(l)
    globals().update(g)
    locals().update(g)
    locals().update(l)


    tipNum = parse.parse("{}T{},{}", basename(__file__))[1]


    jsonNames = [
        f"CrossCurrInfo T{tipNum} - Both areas.json",
        f"CrossCurrInfo T{tipNum} - Regulated.json",
        f"CrossCurrInfo T{tipNum} - Unregulated.json",
    ]
    iTipMaxs = [[5e-9, 5e-6], # With regulated Area
               [245e-9, 5e-6], # Only regulated Area
               [5e-9, 245e-9], # Only unregulated Area
    ]


    for _iArea in range(len(iTipMaxs)):
        jsonName = jsonNames[_iArea]
        iTipMax = iTipMaxs[_iArea]

        # Sum and get migrated contribution of the GNDed tips
        crossEmission = {
            "ToI": tipSep["el"][keys[0]]["ITip"], # Current of the emitting tip (Tip of Interest = ToI)
        }
        keepIndicies = np.where((crossEmission["ToI"] >= iTipMax[0]) & (crossEmission["ToI"] <= iTipMax[1]))
        # crossEmission["ToI"][] = np.nan
        crossEmission["ToI"] = crossEmission["ToI"][keepIndicies]

        _gndKeys = keys.copy()
        _gndKeys.pop(0) # ToI was moved to first index!
        for _iGndKey in range(len(_gndKeys)):
            _xy = _gndKeys[_iGndKey]
            _elGndTip = tipSep["el"][_xy]["ITip"][keepIndicies]
            if _iGndKey == 0:
                crossEmission["GNDed"] = _elGndTip
            else:
                crossEmission["GNDed"] = np.add(crossEmission["GNDed"], _elGndTip)
        
        crossEmission["ToI Mean A"] = np.nanmean(crossEmission["ToI"])
        crossEmission["ToI Std A"]  = np.nanstd (crossEmission["ToI"])
        crossEmission["GNDed/ToI"]                                    = np.multiply(100, np.divide(crossEmission["GNDed"], crossEmission["ToI"]))
        crossEmission["GNDed/ToI"][crossEmission["GNDed/ToI"] > 1000] = np.nan
        crossEmission["GNDed/ToI Mean %"]                               = np.nanmean(crossEmission["GNDed/ToI"])
        crossEmission["GNDed/ToI Std %"]                                = np.nanstd (crossEmission["GNDed/ToI"])

        crossEmission["ToI-GNDed"]      = np.subtract(crossEmission["ToI"], crossEmission["GNDed"])
        crossEmission["ToI-GNDed Mean A"] = np.nanmean(crossEmission["ToI-GNDed"])
        crossEmission["ToI-GNDed Std A"]  = np.nanstd (crossEmission["ToI-GNDed"])

        crossEmission.pop("ToI")
        crossEmission.pop("GNDed")
        crossEmission.pop("GNDed/ToI")
        crossEmission.pop("ToI-GNDed")

        with open(f"{jsonName}", "w") as fJSON:
            fJSON.write(json.dumps(crossEmission))

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