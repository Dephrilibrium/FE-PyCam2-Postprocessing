# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 10:51:05 2022

@author: asc
"""

"""
Created on Tue Apr 26 10:48:07 2022

@author: asc
"""


from detect_points import centroid_activeSpots, replaceOverexposedPointsSTDproPunkt, plotResultsMEANLT,saveDictSTDproPunkt,addVItoDictwithMEAN,detectPoints, PointPositionReferenceImage, CopyCDLFiles
from extract_tar import extract_tar
import glob,os
import shutil
import natsort


# measurement dir

# directory = '//fs-01/KETEK-NET/Prozess/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam/'
# directory = '//fs-01/KETEK-NET/Prozess/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam_LTT/'
directory = '//fs-01/KETEK-NET/Prozess/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam_LT_Vsweep/'


#detektierte Punkte und Plots speichern unter: 
savedir = '/'.join(['/'.join(directory.split('/')[:-2]),directory.split('/')[-2]+'_Ausw'])+'/' # =dir + _Ausw
if not os.path.exists(savedir):
    os.makedirs(savedir)
#savedir = '//fs-01/KETEK-NET/Prozess/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam_LTT_Ausw/'


# Folder to evaluate

# automatisch
ffs_meas = os.listdir(directory)
ffs_ausw = os.listdir(savedir)
ffs=[meas for meas in ffs_meas if meas not in ffs_ausw] # nur unausgewertete

ffs = ['2022-07-12_220329_W1_V1_nM24'] # manuell

# Measurement
save = True                #Save results and figures?
width_point = 4            #width for sum of pixels (effetive pixel diameter approx. 12.4 um)
limitBrightness = 1         #limit grey value for detection of points
numberImagesPerVoltage = 3  #how many images per voltage were taken?
radiusOfCircles = width_point        #circles around detected points

numberMeasurementsPerVoltage=2
SingleLT=True
LifeTimeTest=False
median=1

filename = 'AuswParams.txt'

# tar noch nicht entpackt??
extract_tar(ffs, path = directory, LTT=LifeTimeTest) 

for folder in ffs:
    
    path = directory+folder+'/'
    if not os.path.exists(savedir+folder+'/'):
        os.makedirs(savedir+folder+'/')
        
    if LifeTimeTest:
        currents = os.listdir(path) 
    else:
        currents=['']
    AuswParams = open(savedir+folder+'/'+filename, 'w')
    AuswParams.write(f' width_point =\t\t\t {width_point}\n limitBrightness =\t\t {limitBrightness} \n numberImagesPerVoltage =\t {numberImagesPerVoltage} \n radiusOfCircles =\t\t {radiusOfCircles} \n numberMeasurementsPerVoltage =  {numberMeasurementsPerVoltage} \n SingleLT =\t\t\t {SingleLT} \n LifeTimeTest =\t\t\t {LifeTimeTest} \n median =\t\t\t {median}')
    AuswParams.close()

    for curr in currents:
        if LifeTimeTest:
            currpath = path + curr + '/'
            saveunder = savedir+folder+'/'+curr+'/'
        else:
            currpath = path
            saveunder = savedir+folder+'/'
        if not os.path.exists(saveunder):
            os.makedirs(saveunder)
        
        # IV File und tars einlesen
        measfile = glob.glob(currpath+'*.txt')
        tars = glob.glob(currpath+'*.tar.gz')
        if (len(measfile)<3 or len(tars)<3) and (LifeTimeTest or SingleLT):
            continue # Abbruch wenn Messung nicht durchgelaufen
        elif '_XX' in curr:
            continue
        try:
            img0_nr= int(glob.glob(currpath+'*.jpg')[0][-29:-21].lstrip('0')) # definiert das erste jpg pro Ordner als Dunkelbild
        except ValueError:
            img0_nr=0
        
        
        # Ermittlung der verwendeten ShutterSpeeds:
        UsedShutterSpeeds=[]
        for file in glob.glob(currpath+'*.jpg'):
            UsedShutterSpeeds.append(int(file[-17:-8].lstrip('0')))
        UsedShutterSpeeds=list(dict.fromkeys(UsedShutterSpeeds))

        # call functions:
        for shutterSpeed in UsedShutterSpeeds:
            print('Measurement: '+currpath.split('/')[-3] +'\n'+'current: '+ currpath.split('/')[-2]+f'   ss={shutterSpeed:09.0f}')
            saveundernew, locationPointsPerFile, filenames = detectPoints(currpath, saveunder, shutterSpeed, save, width_point, limitBrightness, numberImagesPerVoltage, numberMeasurementsPerVoltage, radiusOfCircles, img0_nr, median=median, LTT=LifeTimeTest)
            
            saveDictSTDproPunkt(saveundernew, locationPointsPerFile, limitBrightness=limitBrightness)
            for file in measfile:
                locationPointsPerFile = addVItoDictwithMEAN(file, locationPointsPerFile, LT=SingleLT, LTT=LifeTimeTest)

            plotPoints = plotResultsMEANLT(locationPointsPerFile, saveundernew, save=save, width_point=width_point)
            if type(plotPoints) == str: # if measurement was interrupted, a string is returned
                print(plotPoints)
            # centroid_activeSpots(locationPointsPerFile, saveundernew, LT=SingleLT, LTT=LifeTimeTest)

        
        locationPointsPerFile = replaceOverexposedPointsSTDproPunkt(saveunder, currpath, ss=UsedShutterSpeeds, numberImagesPerVoltage=numberImagesPerVoltage, numberMeasurementsPerVoltage=numberMeasurementsPerVoltage, LT=SingleLT, img0_nr = img0_nr, LTT=LifeTimeTest)
        UsedShutterSpeeds=natsort.os_sorted(UsedShutterSpeeds)
        saveDictSTDproPunkt(saveunder+f'{str(natsort.os_sorted(UsedShutterSpeeds)[-1])[:-3]}ersetzt/', locationPointsPerFile, limitBrightness=limitBrightness)
        plotPoints = plotResultsMEANLT(locationPointsPerFile, saveunder+f'{str(natsort.os_sorted(UsedShutterSpeeds)[-1])[:-3]}ersetzt/', save=save, width_point=width_point)
        PointPositionReferenceImage(locationPointsPerFile, folder , saveunder+f'{str(natsort.os_sorted(UsedShutterSpeeds)[-1])[:-3]}ersetzt/',current=curr, MaxSS=f'{str(natsort.os_sorted(UsedShutterSpeeds)[-1])[:-3]}ersetzt', rawdir=directory, save=True, width_point=width_point, LT=SingleLT, LTT=LifeTimeTest)
        if type(plotPoints) == str: # if measurement was interrupted, a string is returned
                print(plotPoints)
                continue
        #centroid_activeSpots(locationPointsPerFile, saveunder+f'{str(natsort.os_sorted(UsedShutterSpeeds)[-1])[:-3]}ersetzt/', LT = SingleLT, LTT=LifeTimeTest) 
        
        UsedShutterSpeeds=natsort.os_sorted(UsedShutterSpeeds)[:-1]
        
        locationPointsPerFile = replaceOverexposedPointsSTDproPunkt(saveunder, currpath, ss=UsedShutterSpeeds, numberImagesPerVoltage=numberImagesPerVoltage, numberMeasurementsPerVoltage=numberMeasurementsPerVoltage, LT=SingleLT, img0_nr = img0_nr, LTT=LifeTimeTest)
        UsedShutterSpeeds=natsort.os_sorted(UsedShutterSpeeds)
        saveDictSTDproPunkt(saveunder+f'{str(natsort.natsort.os_sorted(UsedShutterSpeeds)[-1])[:-3]}ersetzt/', locationPointsPerFile, limitBrightness=limitBrightness)
        plotPoints = plotResultsMEANLT(locationPointsPerFile, saveunder+f'{str(natsort.os_sorted(UsedShutterSpeeds)[-1])[:-3]}ersetzt/', save=save, width_point=width_point)
        PointPositionReferenceImage(locationPointsPerFile, folder, saveunder+f'{str(natsort.os_sorted(UsedShutterSpeeds)[-1])[:-3]}ersetzt/',current=curr, MaxSS=f'{str(natsort.os_sorted(UsedShutterSpeeds)[-1])[:-3]}ersetzt',rawdir=directory, save=True, width_point=width_point, LT=SingleLT, LTT=LifeTimeTest)
        if type(plotPoints) == str: # if measurement was interrupted, a string is returned
                print(plotPoints)
                continue           
        #centroid_activeSpots(locationPointsPerFile, saveunder+f'{str(natsort.os_sorted(UsedShutterSpeeds)[-1])[:-3]}ersetzt/', LT = SingleLT, LTT=LifeTimeTest) 
        
        #Messdaten in Auswertungs-Odner kopieren
        for file in measfile:
            shutil.copy2(file, saveunder)
        
        if SingleLT:    
            # txt Files für CDL Auswertung kopieren -> nur bei LT oder LTT
            CopyCDLFiles(savedir+folder, curr, numberMeasurementsPerVoltage)
            