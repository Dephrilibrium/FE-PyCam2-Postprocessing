import matplotlib.pyplot as plt
import FieldEmission as fe
import glob

def ColorizeTwinedXWith(twinXList, color):
    twinXList[0][0].spines["right"].set_color(color)
    twinXList[1][0].spines["right"].set_color(color)
    twinXList[1][1].spines["right"].set_color(color)
    twinXList[2][0].spines["right"].set_color(color)
    twinXList[2][1].spines["right"].set_color(color)

    twinXList[0][0].tick_params(colors=color)
    twinXList[1][0].tick_params(colors=color)
    twinXList[1][1].tick_params(colors=color)
    twinXList[2][0].tick_params(colors=color)
    twinXList[2][1].tick_params(colors=color)

    twinXList[0][0].yaxis.label.set_color(color)
    twinXList[1][0].yaxis.label.set_color(color)
    twinXList[1][1].yaxis.label.set_color(color)
    twinXList[2][0].yaxis.label.set_color(color)
    twinXList[2][1].yaxis.label.set_color(color)

    return



def ReadResistorFile(fPath):
    globPaths = glob.glob(fPath)

    f = open(globPaths[0], "r")
    resistor = f.readlines()
    f.close();
    return float(resistor[0])


def ReadElFile(fPath):
    h, d = fe.ReadDataFile(fPath)
    dp = fe.DataProvider(h, d)
    dp.RemoveRows(-1)

    return dp

def ReadSwpFile(fPath):
    globPaths = glob.glob(fPath)

    h, d, dmy = fe.ReadSweepFile(globPaths[0])
    dp = fe.DataProvider(h, d)
    dp.AbsColumn("U7")
    return dp


def ReadCFFile(fPath, resistor:float):
    globPaths = glob.glob(fPath)
    dp = ReadElFile(globPaths[0])

    # Restructuring
    dp.AppendColumn("I", dp.GetColumn("Y"))
    dp.AbsColumn("I")
    dp.RemoveColumns(["Time", "Y", "Dev7"])

    if resistor != None:
        dp.DivideColumn("I", resistor) # Voltage -> Current
    return dp

def ReadUDFile(fPath, swpProvider):
    globPaths = glob.glob(fPath)
    dp = ReadElFile(globPaths[0])

    # Restructuring
    dp.AppendColumn("U", dp.GetColumn("Y"))
    dp.RemoveColumns(["Time", "Dev7", "Y"])

    dp.AbsColumn("U")
    dp.SubtractColumnFrom("U", swpProvider.GetColumn("U7")) # Dropvoltage -> Tipvoltage
    return dp