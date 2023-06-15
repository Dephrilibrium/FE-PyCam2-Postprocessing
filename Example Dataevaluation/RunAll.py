import subprocess
import glob
import os
from os.path import join, basename, dirname, splitext


targetFolders = [
# r"P:\MIKRO\Mikrosensorik\Mitarbeiter\Hausladen\Veröffentlichung, Vorträge, etc\230403 IEEE PyCam2\Measurements\00 Kurzschlusstests",
# r"P:\MIKRO\Mikrosensorik\Mitarbeiter\Hausladen\Veröffentlichung, Vorträge, etc\230403 IEEE PyCam2\Measurements\02_02 Einzel BurnIn (1kV@IMax250nA)",
r"P:\MIKRO\Mikrosensorik\Mitarbeiter\Hausladen\Veröffentlichung, Vorträge, etc\230403 IEEE PyCam2\Measurements\03_02 Unreg Kombis (IMax5V)",
r"P:\MIKRO\Mikrosensorik\Mitarbeiter\Hausladen\Veröffentlichung, Vorträge, etc\230403 IEEE PyCam2\Measurements\04_02 Weitere Kombis",
r"P:\MIKRO\Mikrosensorik\Mitarbeiter\Hausladen\Veröffentlichung, Vorträge, etc\230403 IEEE PyCam2\Measurements\05_02 Tips einzeln, Rest floatend",
r"P:\MIKRO\Mikrosensorik\Mitarbeiter\Hausladen\Veröffentlichung, Vorträge, etc\230403 IEEE PyCam2\Measurements\08_02 Reaktivierungsversuche",
r"P:\MIKRO\Mikrosensorik\Mitarbeiter\Hausladen\Veröffentlichung, Vorträge, etc\230403 IEEE PyCam2\Measurements\08_03 Kombis",
r"P:\MIKRO\Mikrosensorik\Mitarbeiter\Hausladen\Veröffentlichung, Vorträge, etc\230403 IEEE PyCam2\Measurements\09_02 Performance-Check",
r"P:\MIKRO\Mikrosensorik\Mitarbeiter\Hausladen\Veröffentlichung, Vorträge, etc\230403 IEEE PyCam2\Measurements\09_03 Auswertung tips einzeln, Rest grounded",
]


for targetFolder in targetFolders:
    for root, dir, files in os.walk(targetFolder):
        pyFiles = glob.glob(join(root, "*.py"))

        for pyFile in pyFiles:
            cmd = f"python {pyFile}"
            subprocess.run(["python", join(root, pyFile)])


print("Runned all scripts in a row")