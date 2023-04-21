# -*- coding: utf-8 -*-
"""
Created on Tue May 25 11:16:56 2021

@author: dar

"""


#%% import important stuff

import os
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import glob
from extract_tar import extract_tar
import natsort
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from matplotlib.colors import LogNorm
import math

#%% Progess Bar definition
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


#%% sweeps

def sweeps(V_set,delta=0.5):
    """
    Die Funktion sweeps() übergibt V_set um die Umschlagpunkte der 
    Spannungssweeps zu ermitteln. Dabei wird ein Digitaler Filter verwendet, 
    der die obere und unter Grenze von der Set-Spannung ermittelt und in einem
    Array speichert. t muss eventuell verändert werden.
    V_set: Array
    return:Array(Grenzen), Array(Anzahl sweeps)
    """
    import importlib.util
    
    V_set = np.array(V_set)
    
    spec = importlib.util.spec_from_file_location("", "//fs-01/KETEK-NET/Prozess/Produktentwicklung/3.2.12_XRAYSOURCE/Auswertung/Python/mib_neu/peakdetect.py")
    peakdetect = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(peakdetect)
    grenzen=peakdetect.peakdet(V_set,delta)
    #print(grenzen)
    
    if (grenzen[0].size == 0) and (grenzen[1].size == 0):
        grenzen = [0]
    elif (grenzen[0].size == 0):
        grenzen = grenzen[1][:,0]
    elif (grenzen[1].size ==0):
        grenzen = grenzen[0][:,0]
    else:
        grenzen = np.append(grenzen[0][:,0],grenzen[1][:,0])
    
    grenzen = np.sort(grenzen)
    grenzen = np.append(np.append([0],grenzen),[V_set.size-1])
    sw = np.ones(len(grenzen)-1)
    
    return grenzen.astype(int), sw


#%% Detection of Points Definition 

def detectPoints(path, saveunder, shutterSpeed=False, save=True, \
                  width_point=5, limitBrightness=5, numberImagesPerVoltage=3, \
                numberMeasurementsPerVoltage=2, radiusOfCircles=10, img0_nr = 0, \
                    ladebalken = False, mesh=True, treshadjust=True, median=3, LTT=False):
    '''
    call function to detect points in PiCam images
    for images with multiple shutter speeds please call function for every 
    shutter speed (it can only handle one)

    Parameters
    ----------
    REQUIRED:
    path : path of measurement data and images
    saveunder : path for saving the results
    shutterSpeed : shutter speed of images, set to False if only one shutter
                    speed was used
    OPTIONAL:
    save : True for saving results including plots and edited images with 
            marked points
    width_point : area around one point, eg 10 = 10 pixels in every direction 
                around detected center (pixel diameter approx 1.55 um; 8x8 Pixels binned -> effectively 12.4 um )
    limitBrightness : limit for the brightness of one pixel for detection
    numberImagesPerVoltage : number of images per ShutterSpeed and voltage 
    numberMeasurementsPerVoltage : number of measurements per V_set 
    radiusOfCircles = radius of circles in point detection image
    img0_nr: Number of dark image
    ladebalken: Ladebalken?
    mesh: use mesh (8x8 only)
    treshadjust: use treshold adjustment for anti-blooming?
    

    Returns
    -------
    locationPointsPerFile : dictionary (key = filename) consisting of:
        SumLoc/SumAll: 
        SumPixelsLoc: brightness of all detected points
        SumPixelsAll: brightness of whole image
        coordinates: if points were detected: coordinates
        brightness: if points were detected: brightness at coordinates
        fehler_coordinates: if points were detected: error of brightness at coordinates 

    '''


    if saveunder[-1] != '/':
        saveunder = saveunder+'/'
    if not os.path.exists(saveunder):
        os.makedirs(saveunder)
    
    locationPointsPerFile = dict() #dict for saving detected points for each file
    img0_mean_images = list() #list of img0
    img0_mean_images_std = list() #and their errors
    img_mean_images = list() #list of img
    img_mean_images_std = list() #and their errors
    img_List = []
    
    if shutterSpeed == False:
        filenames = glob.glob(path+'*.jpg')
    else:
        filenames = glob.glob(path+f'*ss={shutterSpeed:09.0f}*.jpg')
        if len(filenames) == 0:
            return 'break', 'break', 'break'
        saveunder = saveunder + f'ss={shutterSpeed}/'
        if not os.path.exists(saveunder):
            os.makedirs(saveunder)
    progress = 0
    img0_file = True # Parameter zum Überspringen von Punktdetektion bei Dunkelbild
    
    if LTT==True: # Bei ungerader Anzahl Messungen in LT-Mess wird der letzte Messwert (mehrere Bilder) ignoriert -> sonst schmarrn beim Mitteln
        if (len(filenames)/numberImagesPerVoltage)%numberMeasurementsPerVoltage != 0: 
            LT_filenames = [x for x in filenames if 'LT' in x[-31:]]
            LT_filenames = [x for x in filenames if x[-29:-21] == LT_filenames[-1][-29:-21]]
            filenames = [x for x in filenames if x not in LT_filenames]
    
    for file in filenames:
        # print(file[-29:])
        sumOfPixels = dict()
        locationPoints = dict()
        
        # read pictures and append to list
        # first read img0 (Dunkelbild), get mean and std
        
        if img0_file == True:
            for j in range(numberMeasurementsPerVoltage):
                if file[-29:-21] == f'{img0_nr+j:08.0f}': # einmal img0_nr, dann img0_nr+1 für 2 Messungen pro Spannung
                    for i in range(numberImagesPerVoltage): # 0 bis 2 bei 3 Bilder Pro Messung
                        if file[-7:-4] == '000': #erstes von numberImagesPerVoltage
                            img0_List = []
                            img0_List.append(cv.imread(file,0).astype(np.float64)) # read image as np-array (380x507), 0 means grayscale
                            if not LTT:
                                break
                        elif file[-7:-4] == f'{i:03.0f}':
                            img0_List.append(cv.imread(file,0).astype(np.float64))
                            if file[-7:-4] == f'{numberImagesPerVoltage-1:03.0f}': # falls letztes -> Mitteln
                                img0 = np.mean(img0_List, axis = 0)
                                img0_std = np.std(img0_List, axis = 0)
                                img0_mean_images.append(img0) # mean images -> 2 normal
                                
            if file[-29:-21] == f'{img0_nr+numberMeasurementsPerVoltage-1:08.0f}': # falls letzte Wiederholng vom Messroutine
                if file[-7:-4] == f'{numberImagesPerVoltage-1:03.0f}': # und falls letztes von den 3 pro Spannung
                    # Mittelwerte der Dunkelbilder (img0) bilden ..
                    img0 = np.mean(img0_mean_images, axis = 0).astype(np.uint8)
                    # und Fehler bestimmen .. fehlerfortpflanzung!
                    img0_std = np.sqrt(sum([kk**2 for kk in img0_mean_images_std])).astype(np.uint8)
                    img0_file = False # alle Dunkelbilder eingelesen 
                    plt.imshow(img0, cmap = 'gray')
                    plt.title(f'files: {int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f} (img0)')
                    if save == True:
                        if 'upSwp' in file[-34:]:
                            plt.savefig(f'{saveunder}{int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f}_widthPoint_{width_point}_upSwp_img0.png', dpi = 200)
                        elif 'LT' in file[-31:]:
                            plt.savefig(f'{saveunder}{int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f}_widthPoint_{width_point}_LT_img0.png', dpi = 200)
                        elif 'downSwp' in file[-36:]:
                            plt.savefig(f'{saveunder}{int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f}_widthPoint_{width_point}_downSwp_img0.png', dpi = 200)
                        else:
                            plt.savefig(f'{saveunder}{int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f}_widthPoint_{width_point}_img0.png', dpi = 200)           
                    if not LTT:
                        continue
                
        #keine Punktedetektion für Dunkelbilder, außer bei LTT -> sonst falsche Mittelung!
        if (LTT == False) and (img0_file == True):
            continue
        
        #then read in other images, append to list
        img_not_ready = True 

        for i in range(numberImagesPerVoltage):
            if file[-7:-4] == '000':
                img_List = []
                try:
                    img_List.append(cv.imread(file,0).astype(np.float64))
                except AttributeError as e:
                    print(e)
                
            elif file[-7:-4] == f'{i:03.0f}': 
                try:
                    img_List.append(cv.imread(file,0).astype(np.float64))
                except AttributeError as e:
                    print(e)
                
        # Mittelwert bilden und zu Liste hinzufügen
        if file[-7:-4] == f'{numberImagesPerVoltage-1:03.0f}':
            img_mean = np.mean(img_List, axis = 0)
            img_mean_std = np.std(img_List, axis = 0)
            img_mean_images.append(img_mean)
            img_mean_images_std.append(img_mean_std)
            
            #if np.amax(img_mean) == 255:
            #    print('Warnung: min. ein Pixel == 255 --> evtl. Überbelichtung')
        
            
        # Bilder für gleichen Vset-Wert mitteln + Fehler
        if len(img_mean_images) == numberMeasurementsPerVoltage:
            img_mean = np.mean(img_mean_images, axis = 0).astype(np.uint8)
            img_mean_std = np.sqrt(sum([kk**2 for kk in img_mean_images_std])).astype(np.uint8)
            img_not_ready = False
            #zurücksetzen der img-Listen
            img_mean_images = list()
            img_mean_images_std = list()
            
        if img_not_ready == True: #mean is not ready yet, continue with next image
            continue
        
        # Dunkelbild abziehen
        try:
            #img = cv.subtract(img,img0)      
            img = np.subtract(img_mean,img0) 
            for ix,iy in zip(np.where(img>img_mean)[0],np.where(img>img_mean)[1]): # Werte < 0  werden sonst 255
                   img[ix,iy]=0
            img_std = np.sqrt(img0_std**2 + img_mean_std**2).astype(np.uint8)  # gausssche fehlerfortpflanzung sqrt(fehler1**2 + fehler2**2 + ...)
        except NameError:
            print('img0 not defined, continue without subtracting')
        except cv.error as e:
            print(e)
            print('image reading failed, continue with next images..')
            continue
        # Ränder schwärzen
        for ix,iy in zip(np.where(img>0)[0],np.where(img>0)[1]): 
            if ix<=75 or ix>=325 or iy<=100 or iy>=400:
                img[ix,iy]=0
            else:
                pass
                    
            
        #median filter
        img = cv.medianBlur(img, median)
        
        # neue Detektion ab 14.12.2021 mit mesh
        
        # neu ab 03.02.2022: finde optimalen thresh durch Breite der Punkte:
        # start mit OTSU, danach in 5-er Schritten thresh erhöhen
        ret1,img_thresh1 = cv.threshold(img,1,255,cv.THRESH_BINARY+cv.THRESH_OTSU)#cv.THRESH_BINARY)
        if ret1 < limitBrightness:
            # wenn threshold kleiner als limitBrightness ist, threshold auf limitBrightness setzen
            ret1,img_thresh1 = cv.threshold(img,limitBrightness,255,cv.THRESH_BINARY)
        contours1_new=[]
        contours1, hierarchy1 = cv.findContours(img_thresh1,1,2)
        if treshadjust == True:
            breakvalue = False
            newthresh = False
            for j in range(len(contours1)):
                    # in contours1 sind alle Koordinaten, pro Punkt müssen die Koordinaten der Konturen
                    # gemittelt werden, um auf Mittelpunkt des detektierten Punktes zu kommen
                    xcontours1, ycontours1 = list(), list()
                    for i in contours1[j]:
                        xcontours1.append(i[0][0])
                        ycontours1.append(i[0][1])
                    # wenn diese Konturen breiter oder höher sind als die vorgegebene Breite des Punktes (width_point),
                    # wird threshold-Wert erhöht, um ein Verlaufen der Punkte zu vermeiden
                    if max(ycontours1)-min(ycontours1)>width_point or max(xcontours1)-min(xcontours1)>width_point:
                        newthresh = True
                        break
                        
                    # wenn erster thresh-Wert schon passend war (und if Bedingung nicht zutrifft), müssen auch hier die 
                    # Koordinaten gemittelt werden:
                    else: 
                        for j in range(len(contours1)):
                            xcontours1, ycontours1 = list(), list()
                            for i in contours1[j]:
                                xcontours1.append(i[0][0])
                                ycontours1.append(i[0][1])
                            # nur hinzufügen, wenn nicht schon in contours1_new vorhanden:
                            alreadySaved = False
                            for coord in contours1_new:
                                if abs(coord[0]-int(np.mean(xcontours1))) <= width_point:
                                    if abs(coord[1]-int(np.mean(ycontours1))) <= width_point:
                                        alreadySaved = True
                                        break
                            if alreadySaved == False:
                                contours1_new.append((int(np.mean(xcontours1)), int(np.mean(ycontours1))))
                            elif alreadySaved == True:
                                sum_new = cv.sumElems(img[int(np.mean(ycontours1))-5:int(np.mean(ycontours1))+5, int(np.mean(xcontours1))-5:int(np.mean(xcontours1))+5])[0]
                                sum_old = cv.sumElems(img[coord[1]-5:coord[1]+5, coord[0]-5:coord[0]+5])[0]
                                if sum_new > sum_old:
                                    contours1_new[contours1_new.index(coord)] = (int(np.mean(xcontours1)), int(np.mean(ycontours1)))
                        
            while newthresh:
                ret1 += 5
                ret1,img_thresh1 = cv.threshold(img,ret1,255,cv.THRESH_BINARY)
                contours1, hierarchy1 = cv.findContours(img_thresh1,1,2)
                for j in range(len(contours1)):
                    xcontours1, ycontours1 = list(), list()
                    for i in contours1[j]:
                        xcontours1.append(i[0][0])
                        ycontours1.append(i[0][1])
                    if max(ycontours1)-min(ycontours1)>width_point or max(xcontours1)-min(xcontours1)>width_point:
                        breakvalue = True
                        break
                if breakvalue == True:
                    breakvalue = False
                    continue
                # wenn Schleife durchlaufen ist und if-Bedingung nie zutraf, ist der optimale threshold wert gefunden 
                # und die while Schleife kann abgebrochen werden
                newthresh = False
            
            #Treshhold adjusted!
                
            
            #Mittelwerte aus finalen contours1 werden in Liste contours1_new gespeichert:
            for j in range(len(contours1)):
                xcontours1, ycontours1 = list(), list()
                for i in contours1[j]:
                    xcontours1.append(i[0][0])
                    ycontours1.append(i[0][1])
                # nur hinzufügen, wenn nicht schon in contours1_new vorhanden:
                alreadySaved = False
                for coord in contours1_new:
                    if abs(coord[0]-int(np.mean(xcontours1))) <= width_point:
                        if abs(coord[1]-int(np.mean(ycontours1))) <= width_point:
                            alreadySaved = True
                            break
                if alreadySaved == False:
                    contours1_new.append((int(np.mean(xcontours1)), int(np.mean(ycontours1))))
                elif alreadySaved == True:
                    sum_new = cv.sumElems(img[int(np.mean(ycontours1))-width_point:int(np.mean(ycontours1))+width_point, int(np.mean(xcontours1))-width_point:int(np.mean(xcontours1))+width_point])[0]
                    sum_old = cv.sumElems(img[coord[1]-width_point:coord[1]+width_point, coord[0]-width_point:coord[0]+width_point])[0]
                    if sum_new > sum_old:
                        # der hellere Punkt wird übernommen
                        contours1_new[contours1_new.index(coord)] = (int(np.mean(xcontours1)), int(np.mean(ycontours1)))
        
        # Erstellen des Mesh aus den vorher detektierten Punkten (nur sehr helle Punkte wurden detektiert -- dh Artefakte
        # können Mesh nicht verfälschen)
        
        # neu ab 08.03.2022: mesh deaktivierbar (mit mesh=False)
        
        if mesh == True:
            # 8x8 array: 8 x und 8 y werte gesucht -- erstelle dictionary mit x und y-Koordinaten
            xycoord = dict()
    
            for loc in contours1_new: 
                #check x Koordinate
                i = 1
                while True:
                    try: 
                        if abs(loc[0] - xycoord[f'x{i}'])<= width_point: 
                            #x Koordinate schon gespeichert
                            break
                        
                    except KeyError:
                        xycoord[f'x{i}'] = loc[0] #speicher x-Koordinate
                        break
                    i += 1
                i = 1
                while True:
                    #check y Koordinate
                    try:
                        if abs(loc[1] - xycoord[f'y{i}'])<= width_point:
                            #y Koordinate schon gespeichert
                            break
                    except KeyError:
                        xycoord[f'y{i}'] = loc[1] #speichere y-Koordinate
                        break
                    i += 1
                
            # wenn im dictionary weniger als 16 Koordinaten (je 8 x- und 8 y-Koordinaten)
            # gespeichert wurden, müssen die fehlenden gefunden werden..
            if len(xycoord) < 16:
                x = list()
                y = list()
                i = 1
                while True:
                    try:
                        x.append(xycoord[f'x{i}'])
                    except KeyError:
                        break
                    i += 1
                i = 1
                while True:
                    try:
                        y.append(xycoord[f'y{i}'])
                    except KeyError:
                        break
                    i += 1
                # dafür werden die Koordinaten erstmal der Größe nach sortiert..
                x.sort()
                y.sort()
                
                if len(x) == 0:
                    # keine Koordinaten für x gefunden --> 8 x-Koordinaten 
                    # erstellen durch Mitte des Bildes
                    for i in range(1,9):
                        #resolution in x: 507 pixels, width array: 140 pixels
                        xycoord[f'x{i}'] = int(507/2)-70-20+i*20
                        x.append(int(507/2)-70-20+i*20)
                        
                elif len(x) == 1:
                    # nur eine Koordinate gefunden --> je nach Lage werden links 
                    # und rechts davon Koordinaten erstellt
                    for i in range(1,9):
                        if int(507/2)-70-20+i*20-10 <=x[0] <= int(507/2)-70-20+i*20+10:
                            #detected point at i th position
                            for j in range(1,i): #fill up from 1st until i th pos
                                k = 1
                                while True:
                                    try: 
                                        xycoord[f'x{k}']
                                    except KeyError:
                                        xycoord[f'x{k}'] = x[0]-(i-j)*20
                                        x.append(x[0]-(i-j)*20)
                                        break
                                    k+=1
                            for j in range(i+1,9): #fill up from i th until 8th pos
                                k = 1
                                while True:
                                    try: 
                                        xycoord[f'x{k}']
                                    except KeyError:
                                        xycoord[f'x{k}'] = x[0]+(j-i)*20
                                        x.append(x[0]+(j-i)*20)
                                        break
                                    k+=1
                            break
                        
                if len(y) == 0:
                    # keine Koordinaten für y gefunden --> 8 y-Koordinaten 
                    # erstellen durch Mitte des Bildes
                    for i in range(1,9):
                        #resolution in y: 380 pixels, width array: 140 pixels
                        xycoord[f'y{i}'] = int(380/2)-70-20+i*20
                        y.append(int(380/2)-70-20+i*20)
                
                        
                elif len(y) == 1:
                    # nur eine Koordinate gefunden --> je nach Lage werden links 
                    # und rechts davon Koordinaten erstellt
                    for i in range(1,9):
                        if int(380/2)-70-20+i*20-10 <=y[0] <= int(380/2)-70-20+i*20+10:
                            #detected point at i th position
                            for j in range(1,i): #fill up from 1st until i th pos
                                k = 1
                                while True:
                                    try: 
                                        xycoord[f'y{k}']
                                    except KeyError:
                                        xycoord[f'y{k}'] = y[0]-(i-j)*20
                                        y.append(y[0]-(i-j)*20)
                                        break
                                    k+=1
                            for j in range(i+1,9): #fill up from i th until 8th pos
                                k = 1
                                while True:
                                    try: 
                                        xycoord[f'y{k}']
                                    except KeyError:
                                        xycoord[f'y{k}'] = y[0]+(j-i)*20
                                        y.append(y[0]+(j-i)*20)
                                        break
                                    k+=1
                            break
                
                #erneutes Sortieren der Koordinaten
                x.sort()
                y.sort()
                
                # Untergrenze und Obergrenze x und y hinzufuegen (falls diese fehlt)
                if int(507/2)-70+10 < min(x): #Obergrenze Minimum
                    # erste Reihe fehlt
                    i = 1
                    while True:
                        try:
                            xycoord[f'x{i}']
                        except KeyError:
                            xycoord[f'x{i}'] = int(507/2)-70 
                            x.append(int(507/2)-70)
                            break
                        i += 1
                    
                if max(x) < int(507/2)+70-10: #Untergrenze Maximum
                    # letzte Reihe fehlt
                    i = 1
                    while True:
                        try:
                            xycoord[f'x{i}']
                        except KeyError:
                            xycoord[f'x{i}'] = int(507/2)+70
                            x.append(int(507/2)+70)
                            break
                        i += 1
                    
                if int(380/2)-70+10 < min(y): #Obergrenze Minimum
                    # erste Spalte fehlt
                    i = 1
                    while True:
                        try:
                            xycoord[f'y{i}']
                        except KeyError:
                            xycoord[f'y{i}'] = int(380/2)-70 
                            y.append(int(380/2)-70)
                            break
                        i += 1
                    
                if max(y) < int(380/2)+70-10: #Untergrenze Maximum
                    # letzte Spalte fehlt
                    i = 1
                    while True:
                        try:
                            xycoord[f'y{i}']
                        except KeyError:
                            xycoord[f'y{i}'] = int(380/2)+70 
                            y.append(int(380/2)+70)
                            break
                        i += 1
                
                # erneutes Sortieren...
                x.sort()
                y.sort()
                
                # Abstände zwischen Koordinaten ausrechnen..
                deltax, deltay = list(), list()
                for i in range(0, len(x)-1):
                    deltax.append(x[i+1]-x[i])
                for j in range(0, len(y)-1):
                    deltay.append(y[j+1]-y[j])
                
                # je nach Größe der Abstände (deltax und deltay), werden 
                # Koordinaten in den Zwischenräumen eingefügt..
                for dx in deltax:
                    if 10<=dx<=29:
                        continue
                    elif 30<=dx<=49:
                        #one point missing in between
                        xindex = deltax.index(dx)
                        newx = (x[xindex]+x[xindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'x{i}']
                            except KeyError:
                                xycoord[f'x{i}'] = int(newx)
                                break
                            i+=1
                    elif 50<=dx<=69:
                        #two points missing in between
                        xindex = deltax.index(dx)
                        newx = (x[xindex]+x[xindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'x{i}']
                            except KeyError:
                                xycoord[f'x{i}'] = int(newx-10)
                                xycoord[f'x{i+1}'] = int(newx+10)
                                break
                            i+=1
                    elif 70<=dx<=89:
                        #three points missing in between
                        xindex = deltax.index(dx)
                        newx = (x[xindex]+x[xindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'x{i}']
                            except KeyError:
                                xycoord[f'x{i}'] = int(newx-20)
                                xycoord[f'x{i+1}'] = int(newx)
                                xycoord[f'x{i+2}'] = int(newx+20)
                                break
                            i+=1
                    elif 90<=dx<=109:
                        #four points missing in between
                        xindex = deltax.index(dx)
                        newx = (x[xindex]+x[xindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'x{i}']
                            except KeyError:
                                xycoord[f'x{i}'] = int(newx-30)
                                xycoord[f'x{i+1}'] = int(newx-10)
                                xycoord[f'x{i+2}'] = int(newx+10)
                                xycoord[f'x{i+3}'] = int(newx+30)
                                break
                            i+=1
                    elif 110<=dx<=129:
                        #five points missing in between
                        xindex = deltax.index(dx)
                        newx = (x[xindex]+x[xindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'x{i}']
                            except KeyError:
                                xycoord[f'x{i}'] = int(newx-40)
                                xycoord[f'x{i+1}'] = int(newx-20)
                                xycoord[f'x{i+2}'] = int(newx)
                                xycoord[f'x{i+3}'] = int(newx+20)
                                xycoord[f'x{i+4}'] = int(newx+40)
                                break
                            i+=1
                    elif 130<=dx<=149:
                        #six points missing in between
                        xindex = deltax.index(dx)
                        newx = (x[xindex]+x[xindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'x{i}']
                            except KeyError:
                                xycoord[f'x{i}'] = int(newx-50)
                                xycoord[f'x{i+1}'] = int(newx-30)
                                xycoord[f'x{i+2}'] = int(newx-10)
                                xycoord[f'x{i+3}'] = int(newx+10)
                                xycoord[f'x{i+4}'] = int(newx+30)
                                xycoord[f'x{i+5}'] = int(newx+50)
                                break
                            i+=1
                            
                #fill up y coordinates
                for dy in deltay:
                    if 10<=dy<=29:
                        continue
                    elif 30<=dy<=49:
                        #one point missing in between
                        yindex = deltay.index(dy)
                        newy = (y[yindex]+y[yindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'y{i}']
                            except KeyError:
                                xycoord[f'y{i}'] = int(newy)
                                break
                            i+=1
                    elif 50<=dy<=69:
                        #two points missing in between
                        yindex = deltay.index(dy)
                        newy = (y[yindex]+y[yindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'y{i}']
                            except KeyError:
                                xycoord[f'y{i}'] = int(newy-10)
                                xycoord[f'y{i+1}'] = int(newy+10)
                                break
                            i+=1
                    elif 70<=dy<=89:
                        #three points missing in between
                        yindex = deltay.index(dy)
                        newy = (y[yindex]+y[yindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'y{i}']
                            except KeyError:
                                xycoord[f'y{i}'] = int(newy-20)
                                xycoord[f'y{i+1}'] = int(newy)
                                xycoord[f'y{i+2}'] = int(newy+20)
                                break
                            i+=1
                    elif 90<=dy<=109:
                        #four points missing in between
                        yindex = deltay.index(dy)
                        newy = (y[yindex]+y[yindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'y{i}']
                            except KeyError:
                                xycoord[f'y{i}'] = int(newy-30)
                                xycoord[f'y{i+1}'] = int(newy-10)
                                xycoord[f'y{i+2}'] = int(newy+10)
                                xycoord[f'y{i+3}'] = int(newy+30)
                                break
                            i+=1
                    elif 110<=dy<=129:
                        #five points missing in between
                        yindex = deltay.index(dy)
                        newy = (y[yindex]+y[yindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'y{i}']
                            except KeyError:
                                xycoord[f'y{i}'] = int(newy-40)
                                xycoord[f'y{i+1}'] = int(newy-20)
                                xycoord[f'y{i+2}'] = int(newy)
                                xycoord[f'y{i+3}'] = int(newy+20)
                                xycoord[f'y{i+4}'] = int(newy+40)
                                break
                            i+=1
                    elif 130<=dy<=149:
                        #six points missing in between
                        yindex = deltay.index(dy)
                        newy = (y[yindex]+y[yindex+1])/2
                        i = 1
                        while True:
                            try: 
                                xycoord[f'y{i}']
                            except KeyError:
                                xycoord[f'y{i}'] = int(newy-50)
                                xycoord[f'y{i+1}'] = int(newy-30)
                                xycoord[f'y{i+2}'] = int(newy-10)
                                xycoord[f'y{i+3}'] = int(newy+10)
                                xycoord[f'y{i+4}'] = int(newy+30)
                                xycoord[f'y{i+5}'] = int(newy+50)
                                break
                            i+=1
            # Mesh erstellt!
        
        
        #finde dunklere Punkte und überprüfe, ob Punkte in Muster des Arrays passen und wenn ja, füge zu contours1 hinzu..
        contours2_new = list()

        # neu: for Schleife durch alle möglichen threshold values
        for thresh in range(limitBrightness,255,5):
            ret2,img_thresh2 = cv.threshold(img,thresh,255,cv.THRESH_BINARY)
            contours2, hierarchy2 = cv.findContours(img_thresh2,1,2)
            
            # wieder Mittelwerte der gefundenen Konturen berechnen
            for j in range(len(contours2)):
                xcontours2, ycontours2 = list(), list()
                for i in contours2[j]:
                    xcontours2.append(i[0][0])
                    ycontours2.append(i[0][1])
                # nur wenn die Breite der Punkte kleiner ist als width_point, 
                # werden Koordinaten gespeichert
                if max(ycontours2)-min(ycontours2)<width_point or max(xcontours2)-min(xcontours2)<width_point:
                    if img_thresh2[int(np.mean(ycontours2)), int(np.mean(xcontours2))] > 0:
                        # Ausschließen, dass dunkle Punkte (= Artefakte) erkannt wurden
                        contours2_new.append((int(np.mean(xcontours2)), int(np.mean(ycontours2))))
        
        if mesh == True:
            # neue Koordinaten nur zu contours1_new hinzufügen, wenn diese zu Koordinaten
            # des Mesh passt und wenn Koordinaten nicht schon gespeichert sind
            for loc in contours2_new: 
                #check x Koordinate
                for i in range(1,9):
                    try:
                        if abs(loc[0] - xycoord[f'x{i}'])<= width_point: 
                            #x Koordinate vorhanden
                            for j in range(1,9):
                                #check y Koordinate
                                if abs(loc[1] - xycoord[f'y{j}'])<= width_point:
                                    #y Koordinate vorhanden
                                    alreadySaved = False
                                    for coord in contours1_new:
                                        if abs(coord[0]-loc[0]) <= width_point:
                                            if abs(coord[1]-loc[1]) <= width_point:
                                                alreadySaved = True
                                                break
                                    if alreadySaved == False:
                                        contours1_new.append(loc)
                                    elif alreadySaved == True:
                                        # wenn der neue Punkt heller ist, wird die alte Koordinate überschrieben
                                        sum_new = cv.sumElems(img[loc[1]-5:loc[1]+5, loc[0]-5:loc[0]+5])[0]
                                        sum_old = cv.sumElems(img[coord[1]-5:coord[1]+5, coord[0]-5:coord[0]+5])[0]
                                        if sum_new > sum_old:
                                            contours1_new[contours1_new.index(coord)] = (loc[0],loc[1])
                    except KeyError:
                        pass
        
        # ohne mesh nur Doppeldetektionen vermeiden:
        elif mesh == False:
            for loc in contours2_new: 
                #check x Koordinate
                alreadySaved = False
                for coord in contours1_new:
                    if abs(coord[0]-loc[0]) <= width_point:
                        if abs(coord[1]-loc[1]) <= width_point:
                            alreadySaved = True
                            break
                if alreadySaved == False:
                    contours1_new.append(loc)
                elif alreadySaved == True:
                    # wenn der neue Punkt heller ist, wird die alte Koordinate überschrieben
                    sum_new = cv.sumElems(img[loc[1]-width_point:loc[1]+width_point, loc[0]-width_point:loc[0]+width_point])[0]
                    sum_old = cv.sumElems(img[coord[1]-width_point:coord[1]+width_point, coord[0]-width_point:coord[0]+width_point])[0]
                    if sum_new > sum_old:
                        contours1_new[contours1_new.index(coord)] = (loc[0],loc[1])
    

        img_subdraw = np.copy(img)
        if np.amax(img_subdraw) > 0:
            color = int(np.amax(img_subdraw))
        else:
            color = 10

        #detektierte Punkte einzeichnen und Bild speichern
        for xy in contours1_new:
            cv.circle(img_subdraw, xy, radiusOfCircles, (color, 0, 0))
        
        plt.imshow(img_subdraw, cmap = 'gray')
        plt.title(f'files: {int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f}')
        if save == True:
            if 'upSwp' in file[-34:]:
                plt.savefig(f'{saveunder}{int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f}_widthPoint_{width_point}_upSwp.png', dpi = 200)
            elif 'LT' in file[-31:]:
                plt.savefig(f'{saveunder}{int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f}_widthPoint_{width_point}_LT.png', dpi = 200)
            elif 'downSwp' in file[-36:]:
                plt.savefig(f'{saveunder}{int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f}_widthPoint_{width_point}_downSwp.png', dpi = 200)
            else:
                plt.savefig(f'{saveunder}{int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f}_widthPoint_{width_point}.png', dpi = 200)
        
        #sum up intensities
        SumPixelsAll = cv.sumElems(img)[0]
        SumPixelsLoc = 0
        SumPixelsLoc_std = 0
        
        for loc in contours1_new:
            #Bilden der Summe der Pixelhelligkeiten um detektierten Punkt
            sumPx = (cv.sumElems(img[(loc[1]-width_point):(loc[1]+width_point), (loc[0]-width_point):(loc[0]+width_point)])[0])
            #mit Fehler (Fehlerfortpflanzung!!)
            sumPx_fehler = np.sqrt(cv.sumElems(img_std[(loc[1]-width_point):(loc[1]+width_point), (loc[0]-width_point):(loc[0]+width_point)]**2)[0])
            sumOfPixels[(loc[0],loc[1])] = sumPx
            locationPoints[(loc[0],loc[1])] = sumPx
            locationPoints[f'fehler_{(loc[0],loc[1])}'] = sumPx_fehler
            SumPixelsLoc += sumPx
            SumPixelsLoc_std += sumPx_fehler**2 

        # Kennwerte dem dictionary hinzufügen
        locationPoints['SumPixelsAll_std'] = cv.sumElems(img_std)[0]
        locationPoints['SumPixelsAll'] = SumPixelsAll
        locationPoints['SumPixelsLoc_std'] = np.sqrt(SumPixelsLoc_std)
        locationPoints['SumPixelsLoc'] = SumPixelsLoc
        if SumPixelsAll > 0:
            locationPoints['SumLoc/SumAll'] = SumPixelsLoc/SumPixelsAll
        else:
            locationPoints['SumLoc/SumAll'] = 0
        
        # dictionary des einzelnen Bildes zu großem dictionary des gesamten Ordners hinzufügen
        locationPointsPerFile[f'{int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f}.jpg'] = locationPoints

        progress += numberMeasurementsPerVoltage
        # Ladebalken
        printProgressBar(progress, len(filenames)/numberImagesPerVoltage, length=60)
        
        #output for ipynb
        if ladebalken is not False:
            try:
                ladebalken.value=progress/(len(filenames)/numberImagesPerVoltage)*100
            except OSError:
                pass
        
        plt.close('all')

    return saveunder, locationPointsPerFile, filenames


#%% finde überbelichtete Pixel und speichere Koordinaten in dict

def findOverexposureMEAN(path, numberImagesPerVoltage=3, numberMeasurementsPerVoltage=2, shutterSpeed = False, files = False, img0_nr = 0, LTT=False):
    resultsPerFile = dict()
    
    if path[-1] != '/':
        path = path+'/'
    
    if files == False:
        if shutterSpeed == False:
            filenames = glob.glob(path+'*.jpg')
        else: # normalerweise wird shutterspeed übergeben
            filenames = glob.glob(path+f'*ss={shutterSpeed:09.0f}*.jpg')
    else: 
        filenames = []
        if shutterSpeed == False:
            for i in files:
                names = glob.glob(path+f'*Array{i[:-4]}*.jpg')
                for j in names:
                    filenames.append(j)
        else:
            for i in files:
                names = glob.glob(path+f'*{i[:-4]}*ss={shutterSpeed:09.0f}*.jpg')
                for j in names:
                    filenames.append(j)
    img0_file = True
    img0_mean_images = list() #list of img0
    #img0_mean_images_std = list() #and their errors
    img_mean_images = list() #list of img
    img_mean_images_std = list() #and their errors
    img_List = []
    
    if LTT==True: # Bei ungerader Anzahl Messungen in LT-Mess wird der letzte Messwert (mehrere Bilder) ignoriert -> sonst schmarrn beim Mitteln
        if (len(filenames)/numberImagesPerVoltage)%numberMeasurementsPerVoltage != 0: 
            LT_filenames = [x for x in filenames if 'LT' in x[-31:]]
            LT_filenames = [x for x in filenames if x[-29:-21] == LT_filenames[-1][-29:-21]]
            filenames = [x for x in filenames if x not in LT_filenames]
    
    for file in filenames:
        results = dict()
        
        if img0_file == True:
            for j in range(numberMeasurementsPerVoltage):
                if file[-29:-21] == f'{img0_nr+j:08.0f}': # einmal img0_nr, dann img0_nr+1 für 2 Messungen pro Spannung
                    for i in range(numberImagesPerVoltage): # 0 bis 2 bei 3 Bilder Pro Messung
                        if file[-7:-4] == '000': #erstes von numberImagesPerVoltage
                            img0_List = []
                            img0_List.append(cv.imread(file,0).astype(np.float64)) # read image as np-array (380x507), 0 means grayscale
                            if not LTT:
                                break
                        elif file[-7:-4] == f'{i:03.0f}':
                            img0_List.append(cv.imread(file,0).astype(np.float64))
                            if file[-7:-4] == f'{numberImagesPerVoltage-1:03.0f}': # falls letztes -> Mitteln
                                img0 = np.mean(img0_List, axis = 0)
                                #img0_std = np.std(img0_List, axis = 0)
                                img0_mean_images.append(img0) # mean images -> 2 normal
                                
            if file[-29:-21] == f'{img0_nr+numberMeasurementsPerVoltage-1:08.0f}': # falls letzte Wiederholng vom Messroutine
                if file[-7:-4] == f'{numberImagesPerVoltage-1:03.0f}': # und falls letztes von den 3 pro Spannung
                    # Mittelwerte der Dunkelbilder (img0) bilden ..
                    img0 = np.mean(img0_mean_images, axis = 0).astype(np.uint8)
                    # und Fehler bestimmen .. fehlerfortpflanzung!
                    #img0_std = np.sqrt(sum([kk**2 for kk in img0_mean_images_std])).astype(np.uint8)
                    img0_file = False # alle Dunkelbilder eingelesen 
                    plt.imshow(img0, cmap = 'gray')
                    if not LTT:
                        continue
                
        #keine Punktedetektion für Dunkelbilder, außer bei LTT -> sonst falsche Mittelung!
        if (LTT == False) and (img0_file == True):
            continue
        
        #then read in other images, append to list
        img_not_ready = True 

        for i in range(numberImagesPerVoltage):
            if file[-7:-4] == '000':
                img_List = []
                try:
                    img_List.append(cv.imread(file,0).astype(np.float64))
                except AttributeError as e:
                    print(e)
                
            elif file[-7:-4] == f'{i:03.0f}': 
                try:
                    img_List.append(cv.imread(file,0).astype(np.float64))
                except AttributeError as e:
                    print(e)
                
        # Mittelwert bilden und zu Liste hinzufügen
        if file[-7:-4] == f'{numberImagesPerVoltage-1:03.0f}':
            img_mean = np.mean(img_List, axis = 0)
            img_mean_std = np.std(img_List, axis = 0)
            img_mean_images.append(img_mean)
            img_mean_images_std.append(img_mean_std)
            
            #if np.amax(img_mean) == 255:
            #    print('Warnung: min. ein Pixel == 255 --> evtl. Überbelichtung')
        
            
        # Bilder für gleichen Vset-Wert mitteln + Fehler
        if len(img_mean_images) == numberMeasurementsPerVoltage:
            img_mean = np.mean(img_mean_images, axis = 0).astype(np.uint8)
            img_mean_std = np.sqrt(sum([kk**2 for kk in img_mean_images_std])).astype(np.uint8)
            img_not_ready = False
            #zurücksetzen der img-Listen
            img_mean_images = list()
            img_mean_images_std = list()
            
        if img_not_ready == True: #mean is not ready yet, continue with next image
            continue
        
        # Dunkelbild abziehen
        try:
            #img = cv.subtract(img,img0)      
            img = np.subtract(img_mean,img0) 
            for ix,iy in zip(np.where(img>img_mean)[0],np.where(img>img_mean)[1]): # Werte < 0  werden sonst 255
                   img[ix,iy]=0
            #img_std = np.sqrt(img0_std**2 + img_mean_std**2).astype(np.uint8)  # gausssche fehlerfortpflanzung sqrt(fehler1**2 + fehler2**2 + ...)
        except NameError:
            print('img0 not defined, continue without subtracting')
        except cv.error as e:
            print(e)
            print('image reading failed, continue with next images..')
            continue
        # Ränder schwärzen
        for ix,iy in zip(np.where(img>0)[0],np.where(img>0)[1]): 
            if ix<=75 or ix>=325 or iy<=100 or iy>=400:
                img[ix,iy]=0
            else:
                pass
        
        x,y = np.where(img == 255)
        for i, j in zip(x,y):
            results[(i,j)] = img[i][j]
        resultsPerFile[f'{int(file[-29:-21])-numberMeasurementsPerVoltage+1:05.0f}-{int(file[-29:-21]):05.0f}.jpg'] = results
        
    return resultsPerFile

#%% plot results out of dictionary

def plotResultsMEAN(locationPointsPerFile, saveunder, save, width_point=5, limitBrightness=5):
        '''
        generates and saves (if save == True) plots of results(=locationPointsPerFile)
        from detectPoints()
    
        Parameters
        ----------
        locationPointsPerFile : dict returned from detectPoints()
        path : path of measurement data
        saveunder : path for saving plots
        save : True for saving figures, False for only showing figures
    
        Returns
        -------
        plotPoints : dict() with all points
    
        '''    
        
        if saveunder[-1] == '/':
            pass
        else:
            saveunder = saveunder+'/'
        
        if not os.path.exists(saveunder):
            os.makedirs(saveunder)
        
        #  Plot brightness of all pixels for each photo
        sumPxs = []
        sumPxs_std = []
        sumLoc = []
        sumLoc_std = []
        #sumError = []
        VoltSet = []
        VoltEmi = []
        emissionI = []
        VoltSet_std = []
        VoltEmi_std = []
        emissionI_std = []
        fotonummer = []
        try:
            for key in locationPointsPerFile:
                fotonummer.append(np.mean([float(key[:-4].split('-')[1]),float(key[:-4].split('-')[0])]))
                sumPxs.append( locationPointsPerFile[key]['SumPixelsAll'])
                sumPxs_std.append( locationPointsPerFile[key]['SumPixelsAll_std'])
                sumLoc.append(locationPointsPerFile[key]['SumPixelsLoc'])
                sumLoc_std.append(locationPointsPerFile[key]['SumPixelsLoc_std'])
                VoltSet.append(locationPointsPerFile[key]['VoltSet'])
                VoltSet_std.append( locationPointsPerFile[key]['VoltSet_std'])
                VoltEmi.append( locationPointsPerFile[key]['VoltEmi'])
                VoltEmi_std.append( locationPointsPerFile[key]['VoltEmi_std'])
                emissionI.append( locationPointsPerFile[key]['IEmi'])
                emissionI_std.append( locationPointsPerFile[key]['IEmi_std'])
                
        except TypeError as e:
            print(e)
            return 'break because no data in dict'
            
        
        fig, ax = plt.subplots()
        try:
            ax.errorbar(fotonummer, sumPxs, yerr = sumPxs_std, capsize = 1,\
                    ecolor = 'orange', elinewidth = 0.1)
        except ValueError:
            ax.plot(np.arange(len(sumPxs)), sumPxs)
        ax.set_ylabel('Pixelhelligkeit')
        ax.set_yscale('log')
        ax.set_xlabel('Fotonummer')
        if save == True:
            plt.savefig(f'{saveunder}FullPlot_Fotonr_brightnessPixelsAll_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100)
        
        #plot all sweeps in one graph
        fig, ax = plt.subplots()
        ax.errorbar(VoltSet, sumPxs, yerr = sumPxs_std, capsize = 1,\
                    ecolor = 'cornflowerblue', elinewidth = 0.1)
        ax.set_ylabel('Pixelhelligkeit')
        ax.set_yscale('log')
        ax.set_xlabel('V_set [V]')
        
        ax2 = ax.twinx()
        ax2.errorbar(VoltSet, emissionI, yerr = emissionI_std, capsize = 1, \
                    color = 'red', ecolor = 'lightcoral', elinewidth = 0.1)
        ax2.set_ylabel('I_emi [A]')
        ax2.set_yscale('log')
        if save == True:
            plt.savefig(f'{saveunder}FullPlot_Vset_Iemi_brightnessPixelsAll_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100)
        
        # number sweeps to cut plots
        grenzen, nrsweeps = sweeps(VoltSet)
        print(f'grenzen: {grenzen}')
        
        sw = 1
        plotPoints = dict()
        
        # Änderung am 04.02.2022: dict wird außerhalb der for-Schleife über grenzen erstellt + fehler behoben..
        # 24.04.2022 : Funktion von PlotDictMean verwendet, sonst redundant
        plotPoints=plotDictMEAN(locationPointsPerFile, width_point = 5)
        
        for i in range(0, len(grenzen)-1, 2):
            #debug print
            try:
                print(f'grenzen[i] : {grenzen[i]} und grenzen [i+2] : {grenzen[i+2]}')
                print(f'VoltEmi[i] : {VoltEmi[grenzen[i]]} und VoltEmi [i+2] : {VoltEmi[grenzen[i+2]]}')
                print(f'fotonummer[i] : {fotonummer[grenzen[i]]} und fotonummer [i+2] : {fotonummer[grenzen[i+2]]}')
            except IndexError as e:
                print(e)
                'stop plotting'
                break
            
            #wenn dict für plot points leer ist, schleife abbrechen
            try:
                if bool(plotPoints['x1']) == False:
                    print('no points detected --> break')
                    break
            except KeyError:
                break
            
            fig, ax1 = plt.subplots()
            ax1.errorbar(VoltSet[grenzen[i]:grenzen[i+2]], emissionI[grenzen[i]:grenzen[i+2]], fmt = 'r', yerr=emissionI_std[grenzen[i]:grenzen[i+2]], label='Emissionsstrom [A]')
            ax1.set_ylabel('Emissionsstrom [A]')
            ax1.set_yscale('log')
            ax1.set_xlabel('Spannung [V]')
            ax1.legend(loc='upper left')
            ax2 = ax1.twinx()
            try:
                ax2.errorbar(VoltSet[grenzen[i]:grenzen[i+2]], sumPxs[grenzen[i]:grenzen[i+2]], yerr = sumPxs_std[grenzen[i]:grenzen[i+2]], label='Pixelhelligkeit')
            except ValueError as e:
                print(e)
            ax2.set_yscale('log')
            ax2.set_ylabel('Pixelhelligkeit')
            ax2.yaxis.set_label_position("right")
            ax2.legend(loc = 'center left')

            if save == True:
                plt.savefig(f'{saveunder}sw_{sw}_Plot_Vset_emissionCurrent_brightnessPixelsAll_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100, bbox_inches="tight")
            
            ax3 = ax1.twinx()
            ax3.spines['right'].set_position(("axes", 1.2))
            try:
                ax3.errorbar(VoltSet[grenzen[i]:grenzen[i+2]], VoltEmi[grenzen[i]:grenzen[i+2]], fmt = 'black', yerr = VoltEmi_std[grenzen[i]:grenzen[i+2]], label='VoltEmi')
            except ValueError as e:
                print(e)
            ax3.set_ylabel('VoltEmi [V]')
            ax3.set_yscale('log')
            ax3.legend(loc = 'lower left')
            
            if save == True:
                plt.savefig(f'{saveunder}sw_{sw}_Plot_Vset_Vemi_emissionCurrent_brightnessPixelsAll_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100, bbox_inches="tight")
                
            # Plot Brightness of each Point
            fig, ax1 = plt.subplots()
            
            k = 0            
            while True:
                try:
                    if len(plotPoints[f'x{k}']) > 0:
                        xk, pointk, pointfehlerk = list(), list(), list()
                        for fotonr in plotPoints[f'xFoto{k}']:
                            if fotonummer[grenzen[i]] <= fotonr <= fotonummer[grenzen[i+2]]:
                                index = plotPoints[f'xFoto{k}'].index(fotonr)  
                                xk.append(plotPoints[f'x{k}'][index])
                                pointk.append(plotPoints[f'point{k}'][index])
                                pointfehlerk.append(plotPoints[f'point_fehler{k}'][index])
                        ax1.errorbar(xk, pointk, yerr = pointfehlerk, label = f'point{k}')
                    
                    k+=1
                except KeyError:
                    break
                               
            
            try: 
                ax1.errorbar(VoltSet[grenzen[i]:grenzen[i+2]], sumLoc[grenzen[i]:grenzen[i+2]], yerr = sumLoc_std[grenzen[i]:grenzen[i+2]], label='alle Punkte')
            except ValueError as e:
                print(e)

            ax1.legend(bbox_to_anchor=(1.2,1), loc = 'upper left')
            ax1.set_ylabel('Pixelhelligkeit')
            ax1.set_xlabel('Spannung [V]')
            ax1.set_yscale('log')

            ax2 = ax1.twinx()
            try:
                ax2.errorbar(VoltSet[grenzen[i]:grenzen[i+2]], emissionI[grenzen[i]:grenzen[i+2]], yerr = emissionI_std[grenzen[i]:grenzen[i+2]], label='Emissionsstrom', color = 'red')
            except ValueError as e:
                print(e)
            ax2.set_yscale('log')
            ax2.set_ylabel('Emissionsstrom [A]')
            ax2.legend(loc='upper left')
            
            if save == True:
                try:
                    plt.savefig(f'{saveunder}sw_{sw}_Plot_Vset_Iemi_brightnessPixelsLoc_allPixels_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100, bbox_inches="tight")
                except OSError as e:
                    print(e)
                    plt.show()
                    
            # more plots
            ax3 = ax1.twinx()
            ax3.spines['right'].set_position(("axes", 1.2))
            ax3.errorbar(VoltSet[grenzen[i]:grenzen[i+2]], VoltEmi[grenzen[i]:grenzen[i+2]], fmt = 'black', yerr = VoltEmi_std[grenzen[i]:grenzen[i+2]], label='VoltEmi')
            ax3.set_ylabel('VoltEmi [V]')
            ax3.set_yscale('log')
            ax3.legend(loc = 'center left')
            ax1.legend(bbox_to_anchor=(1.4,1), loc = 'upper left')
            
            if save == True:
                try:
                    plt.savefig(f'{saveunder}sw_{sw}_Plot_Vset_Vemi_Iemi_brightnessPixelsLoc_allPixels_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100, bbox_inches="tight")
                except OSError as e:
                    print(e)
                    plt.show()

            fig, ax1 = plt.subplots()
            
            k = 0            
            while True:
                try:
                    if len(plotPoints[f'x{k}']) > 0:
                        xk, pointk, pointfehlerk = list(), list(), list()
                        for fotonr in plotPoints[f'xFoto{k}']:
                            if grenzen[i] <= fotonr <= grenzen[i+2]:
                                index = plotPoints[f'xFoto{k}'].index(fotonr)  
                                xk.append(plotPoints[f'x{k}'][index])
                                pointk.append(plotPoints[f'point{k}'][index])
                                pointfehlerk.append(plotPoints[f'point_fehler{k}'][index])
                        ax1.errorbar(xk, pointk, yerr = pointfehlerk, label = f'point{k}')
                    
                    k+=1
                except KeyError:
                    break
                               
            ax1.legend(bbox_to_anchor=(1.2,1), loc = 'upper left')
            ax1.set_ylabel('Pixelhelligkeit')
            ax1.set_xlabel('Spannung [V]')
            ax1.set_yscale('log')
            
            ax2 = ax1.twinx()
            ax2.errorbar(VoltSet[grenzen[i]:grenzen[i+2]], emissionI[grenzen[i]:grenzen[i+2]], yerr = emissionI_std[grenzen[i]:grenzen[i+2]], label='Emissionsstrom', color = 'red')
            ax2.set_ylabel('Emissionsstrom [A]')
            ax2.set_yscale('log')
            ax2.legend(loc='upper left')
            ax2.set_yscale('log')
            
            if save == True:
                try:
                    plt.savefig(f'{saveunder}sw_{sw}_Plot_Vset_Iemi_brightnessPixelsLoc_eachPoint_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100, bbox_inches="tight")
                except OSError as e:
                    print(e)
                    plt.show()
                    
            ax3 = ax1.twinx()
            ax3.spines['right'].set_position(("axes", 1.2))
            ax3.errorbar(VoltSet[grenzen[i]:grenzen[i+2]], VoltEmi[grenzen[i]:grenzen[i+2]], fmt = 'black', yerr = VoltEmi_std[grenzen[i]:grenzen[i+2]], label='VoltEmi')
            ax3.set_ylabel('VoltEmi [V]')
            ax3.set_yscale('log')
            ax3.legend(loc = 'center left')
            ax1.legend(bbox_to_anchor=(1.4,1), loc = 'upper left')
            
            if save == True:
                try:
                    plt.savefig(f'{saveunder}sw_{sw}_Plot_Vset_Vemi_Iemi_brightnessPixelsLoc_eachPoint_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100, bbox_inches="tight")
                except OSError as e:
                    print(e)
                    plt.show()

            fig, ax1 = plt.subplots()
            
            k = 0            
            while True:
                try:
                    if len(plotPoints[f'xFoto{k}']) > 0:
                        xk, pointk, pointfehlerk = list(), list(), list()
                        for fotonr in plotPoints[f'xFoto{k}']:
                            if fotonummer[grenzen[i]] <= fotonr <= fotonummer[grenzen[i+2]]:
                                index = plotPoints[f'xFoto{k}'].index(fotonr)  
                                xk.append(fotonr)
                                pointk.append(plotPoints[f'point{k}'][index])
                                pointfehlerk.append(plotPoints[f'point_fehler{k}'][index])
                        #hier plot über fotonummer
                        ax1.errorbar(xk, pointk, yerr = pointfehlerk, label = f'point{k}')
                    k+=1
                except KeyError:
                    break
            
            ax1.errorbar(fotonummer[grenzen[i]:grenzen[i+2]], sumLoc[grenzen[i]:grenzen[i+2]], yerr = sumLoc_std[grenzen[i]:grenzen[i+2]], label='alle Punkte')
            ax1.legend(bbox_to_anchor=(1.2,1), loc = 'upper left')
            ax1.set_ylabel('Pixelhelligkeit')
            ax1.set_xlabel('Fotonummer')
            ax1.set_yscale('log')
            
            ax2 = ax1.twinx()
            ax2.errorbar(fotonummer[grenzen[i]:grenzen[i+2]], emissionI[grenzen[i]:grenzen[i+2]], yerr = emissionI_std[grenzen[i]:grenzen[i+2]], label='Emissionsstrom', color = 'red')
            ax2.set_ylabel('Emissionsstrom [A]')
            ax2.set_yscale('log')
            ax2.legend(loc='upper left')
            
            if save == True:
                try:
                    plt.savefig(f'{saveunder}sw_{sw}_Plot_Fotonr_Iemi_brightnessPixelsLoc_allPixels_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100, bbox_inches="tight")
                except OSError as e:
                    print(e)
                    plt.show()
                    
            ax3 = ax1.twinx()
            ax3.spines['right'].set_position(("axes", 1.2))
            ax3.errorbar(fotonummer[grenzen[i]:grenzen[i+2]], VoltEmi[grenzen[i]:grenzen[i+2]],fmt = 'black', yerr = VoltEmi_std[grenzen[i]:grenzen[i+2]], label='VoltEmi')
            ax3.set_ylabel('VoltEmi [V]')
            ax3.set_yscale('log')
            ax3.legend(loc = 'center left')
            ax1.legend(bbox_to_anchor=(1.4,1), loc = 'upper left')
            
            if save == True:
                try:
                    plt.savefig(f'{saveunder}sw_{sw}_Plot_Fotonr_Vemi_Iemi_brightnessPixelsLoc_allPixels_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100, bbox_inches="tight")
                except OSError as e:
                    print(e)
                    plt.show()

            fig, ax1 = plt.subplots()
            
            k = 0            
            while True:
                try:
                    if len(plotPoints[f'xFoto{k}']) > 0:
                        xk, pointk, pointfehlerk = list(), list(), list()
                        for fotonr in plotPoints[f'xFoto{k}']:
                            if fotonummer[grenzen[i]] <= fotonr <= fotonummer[grenzen[i+2]]:
                                index = plotPoints[f'xFoto{k}'].index(fotonr)  
                                xk.append(fotonr)
                                pointk.append(plotPoints[f'point{k}'][index])
                                pointfehlerk.append(plotPoints[f'point_fehler{k}'][index])
                        #hier plot über fotonummer
                        ax1.errorbar(xk, pointk, yerr = pointfehlerk, label = f'point{k}')
                    k+=1
                except KeyError:
                    break
                              
            ax1.legend(bbox_to_anchor=(1.2,1), loc = 'upper left')
            ax1.set_ylabel('Pixelhelligkeit')
            ax1.set_xlabel('Fotonummer')
            ax1.set_yscale('log')
            
            ax2 = ax1.twinx()
            ax2.errorbar(fotonummer[grenzen[i]:grenzen[i+2]], emissionI[grenzen[i]:grenzen[i+2]],yerr = emissionI_std[grenzen[i]:grenzen[i+2]], label='Emissionsstrom', color = 'red')
            ax2.set_ylabel('Emissionsstrom [A]')
            ax2.set_yscale('log')
            ax2.legend(loc='upper left')
            ax2.set_yscale('log')
            
            if save == True:
                try:
                    plt.savefig(f'{saveunder}sw_{sw}_Plot_Fotonr_Iemi_brightnessPixelsLoc_eachPoint_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100, bbox_inches="tight")
                except OSError as e:
                    print(e)
                    plt.show()
                    
            ax3 = ax1.twinx()
            ax3.spines['right'].set_position(("axes", 1.2))
            ax3.errorbar(fotonummer[grenzen[i]:grenzen[i+2]], VoltEmi[grenzen[i]:grenzen[i+2]],fmt = 'black', yerr = VoltEmi_std[grenzen[i]:grenzen[i+2]], label='VoltEmi')
            ax3.set_ylabel('VoltEmi [V]')
            ax3.set_yscale('log')
            ax3.legend(loc = 'center left')
            ax1.legend(bbox_to_anchor=(1.4,1), loc = 'upper left')
            
            if save == True:
                try:
                    plt.savefig(f'{saveunder}sw_{sw}_Plot_Fotonr_Vemi_Iemi_brightnessPixelsLoc_eachPoint_widthPoint_{width_point}_limitBrightness_{limitBrightness}.png', dpi=100, bbox_inches="tight")
                except OSError as e:
                    print(e)
                    plt.show()
                    
            sw += 1            
            plt.close('all')
            
        return plotPoints

#%% plotdict MEAN

def plotDictMEAN(locationPointsPerFile, width_point = 5, LT=False):
        '''
        generates dictionary to plot single emission spots
        including brightness, current, etc.
    
        Parameters
        ----------
        locationPointsPerFile : dict returned from detectPoints()
        width_point : area around one point -> used to combine corresponding points in different measurement-images
    
        Returns
        -------
        plotPoints : dict() with all points
    
        '''    
        
        plotPoints = dict()
        PiCamLT=[]
        for key in locationPointsPerFile:
            try:
                for keyPos in reversed(locationPointsPerFile[key]):
                    if type(keyPos) == tuple:
                        #25.04.2022 : Punkte in Dict über Tuple Bedingung statt über -12
                        for k in range(1,len([point for point in [*locationPointsPerFile[key]] if type(point)==tuple])+1): #Anzahl Punkte = alle Tupel in Key-Liste
                            # print(k)
                            try:
                                if len(plotPoints[f'x{k}'])>= 0:
                                    pass
                            except KeyError:
                                plotPoints[f'x{k}'] = list()
                                plotPoints[f'x_std{k}'] = list()
                                plotPoints[f'point{k}'] = list()
                                plotPoints[f'point_fehler{k}'] = list()
                                plotPoints[f'loc{k}'] = list()
                                plotPoints[f'xFoto{k}'] = list()
                                #04.02.2022 : Iemi pro Punkt + Fehler ergänzt
                                plotPoints[f'pointI{k}'] = list()
                                plotPoints[f'pointI_fehler{k}'] = list()
                        
                        # if type(keyPos) == tuple:
                            if len(plotPoints[f'point{k}']) == 0 \
                                or (abs(keyPos[0]-plotPoints[f'keyPos_before{k}'][0])<=width_point \
                                    and abs(keyPos[1]-plotPoints[f'keyPos_before{k}'][1])<=width_point):
                                plotPoints[f'point{k}'].append(locationPointsPerFile[key][keyPos])
                                plotPoints[f'point_fehler{k}'].append(locationPointsPerFile[key][f'fehler_{keyPos}'])
                                plotPoints[f'loc{k}'].append(keyPos)
                                plotPoints[f'xFoto{k}'].append(np.mean([float(key[:-4].split('-')[1]),float(key[:-4].split('-')[0])]))
                                if LT:
                                    try:
                                        PiCamLT.append(np.mean([float(key[:-4].split('-')[1]),float(key[:-4].split('-')[0])])) #gemittelte FotoNr
                                        plotPoints[f'x{k}'].append(locationPointsPerFile[key]['Time'])
                                        plotPoints[f'x_std{k}'].append(locationPointsPerFile[key]['Time_std'])
                                    except KeyError:
                                        try: 
                                            plotPoints[f'x{k}'].append(locationPointsPerFile[key]['VoltEmi']) #24.04.2022 : VoltSet -> VoltEmi
                                            plotPoints[f'x_std{k}'].append(locationPointsPerFile[key]['VoltEmi_std'])
                                        except IndexError as e:
                                            plotPoints[f'x{k}'].append(0)
                                            print(e)
                                        except KeyError as e:
                                            print(e)
                                else:
                                    try: 
                                        plotPoints[f'x{k}'].append(locationPointsPerFile[key]['VoltEmi']) #24.04.2022 : VoltSet -> VoltEmi
                                        plotPoints[f'x_std{k}'].append(locationPointsPerFile[key]['VoltEmi_std'])
                                    except IndexError as e:
                                        plotPoints[f'x{k}'].append(0)
                                        print(e)
                                    except KeyError as e:
                                        print(e)

                                try:
                                    # 25.07.22: SumPixelsAll statt SumPixelsLoc für Sens -> macht mehr Sinn!
                                    plotPoints[f'pointI{k}'].append(locationPointsPerFile[key]['IEmi']/locationPointsPerFile[key]['SumPixelsAll']*locationPointsPerFile[key][keyPos])
                                    #Fehlerfortpflanzung: Ip = Hp * I/H -> dIP = sqrt((Hp/H*dI)^2+(I/H*dHp)^2+(-Hp*I/H^2 *dH)^2)
                                    plotPoints[f'pointI_fehler{k}'].append(np.sqrt((locationPointsPerFile[key][keyPos]/locationPointsPerFile[key]['SumPixelsAll']*locationPointsPerFile[key]['IEmi_std'])**2 \
                                                                                   + (locationPointsPerFile[key]['IEmi']/locationPointsPerFile[key]['SumPixelsAll']*locationPointsPerFile[key][f'fehler_{keyPos}'])**2 \
                                                                                       + (locationPointsPerFile[key][keyPos]*locationPointsPerFile[key]['IEmi']/(locationPointsPerFile[key]['SumPixelsAll']**2)*locationPointsPerFile[key]['SumPixelsAll_std'])**2))
                                except ZeroDivisionError:
                                    plotPoints[f'pointI{k}'].append(0)
                                    plotPoints[f'pointI_fehler{k}'].append(0)
                                except IndexError as e: 
                                    print(e)
                                try:
                                    plotPoints[f'keyPos_before{k}'] #TODO hier noch neuen Punkt anhängen und mittelpunkte mitteln
                                except KeyError:
                                    plotPoints[f'keyPos_before{k}'] = keyPos 
                                break
            except KeyError:
                pass
            # except IndexError:
                #     return 'break because measurement was interrupted'
        if LT==True:
            return plotPoints, PiCamLT
        return plotPoints

#%% plotPoints LT

def plotPointsLT(locationPointsPerFile, width_point = 5):
        '''
        generates dictionary to plot single emission spots
        including brightness, current, etc., seperated by before, LT and after.
    
        Parameters
        ----------
        locationPointsPerFile : dict returned from detectPoints()
        width_point : area around one point -> used to combine corresponding points in different measurement-images
    
        Returns
        -------
        plotPoints : dict() with all points
    
        '''    

        plotPoints = dict()
        for key in locationPointsPerFile:
            if 'VoltSet_up' in locationPointsPerFile[key]:
                belongsto='before'
            elif 'VoltSet_down' in locationPointsPerFile[key]:
                belongsto='after'
            else:
                belongsto='LT'
            try:
                if len(plotPoints[belongsto])>= 0:
                    pass
            except KeyError:
                plotPoints[belongsto]={}
            try:
                for keyPos in reversed(locationPointsPerFile[key]):
                    if type(keyPos) == tuple:
                        #25.04.2022 : Punkte in Dict über Tuple Bedingung statt über -12
                        for k in range(1,len([point for point in [*locationPointsPerFile[key]] if type(point)==tuple])+1): #Anzahl Punkte = alle Tupel in Key-Liste
                            # print(k)
                            try:
                                if len(plotPoints[belongsto][f'x{k}'])>= 0:
                                    pass
                            except KeyError:
                                plotPoints[belongsto][f'x{k}'] = list()
                                plotPoints[belongsto][f'x_std{k}'] = list()
                                plotPoints[belongsto][f'point{k}'] = list()
                                plotPoints[belongsto][f'point_fehler{k}'] = list()
                                plotPoints[belongsto][f'loc{k}'] = list()
                                plotPoints[belongsto][f'xFoto{k}'] = list()
                                #04.02.2022 : Iemi pro Punkt + Fehler ergänzt
                                plotPoints[belongsto][f'pointI{k}'] = list()
                                plotPoints[belongsto][f'pointI_fehler{k}'] = list()
                        
                        # if type(keyPos) == tuple:
                            if len(plotPoints[belongsto][f'point{k}']) == 0 \
                                or (abs(keyPos[0]-plotPoints[belongsto][f'keyPos_before{k}'][0])<=width_point \
                                    and abs(keyPos[1]-plotPoints[belongsto][f'keyPos_before{k}'][1])<=width_point):
                                plotPoints[belongsto][f'point{k}'].append(locationPointsPerFile[key][keyPos])
                                plotPoints[belongsto][f'point_fehler{k}'].append(locationPointsPerFile[key][f'fehler_{keyPos}'])
                                plotPoints[belongsto][f'loc{k}'].append(keyPos)
                                plotPoints[belongsto][f'xFoto{k}'].append(np.mean([float(key[:-4].split('-')[1]),float(key[:-4].split('-')[0])]))
                                if belongsto=='LT':
                                    try:
                                        plotPoints[belongsto][f'x{k}'].append(locationPointsPerFile[key]['Time'])
                                        plotPoints[belongsto][f'x_std{k}'].append(locationPointsPerFile[key]['Time_std'])
                                    except IndexError as e:
                                        plotPoints[belongsto][f'x{k}'].append(0)
                                        print(e)
                                    except KeyError as e:
                                        print(e)
                                else:  
                                    try: 
                                        plotPoints[belongsto][f'x{k}'].append(locationPointsPerFile[key]['VoltEmi']) #24.04.2022 : VoltSet -> VoltEmi
                                        plotPoints[belongsto][f'x_std{k}'].append(locationPointsPerFile[key]['VoltEmi_std'])
                                    except IndexError as e:
                                        plotPoints[belongsto][f'x{k}'].append(0)
                                        print(e)
                                    except KeyError as e:
                                        print(e)


                                try:
                                    # 25.07.22: SumPixelsAll statt SumPixelsLoc für Sens -> macht mehr Sinn!
                                    plotPoints[belongsto][f'pointI{k}'].append(locationPointsPerFile[key]['IEmi']/locationPointsPerFile[key]['SumPixelsAll']*locationPointsPerFile[key][keyPos])
                                    #Fehlerfortpflanzung: Ip = Hp * I/H -> dIP = sqrt((Hp/H*dI)^2+(I/H*dHp)^2+(-Hp*I/H^2 *dH)^2)
                                    plotPoints[belongsto][f'pointI_fehler{k}'].append(np.sqrt((locationPointsPerFile[key][keyPos]/locationPointsPerFile[key]['SumPixelsAll']*locationPointsPerFile[key]['IEmi_std'])**2 \
                                                                                   + (locationPointsPerFile[key]['IEmi']/locationPointsPerFile[key]['SumPixelsAll']*locationPointsPerFile[key][f'fehler_{keyPos}'])**2 \
                                                                                       + (locationPointsPerFile[key][keyPos]*locationPointsPerFile[key]['IEmi']/(locationPointsPerFile[key]['SumPixelsAll']**2)*locationPointsPerFile[key]['SumPixelsAll_std'])**2))
                                except ZeroDivisionError:
                                    plotPoints[belongsto][f'pointI{k}'].append(0)
                                    plotPoints[belongsto][f'pointI_fehler{k}'].append(0)
                                except IndexError as e: 
                                    print(e)
                                try:
                                    plotPoints[belongsto][f'keyPos_before{k}'] #TODO hier noch neuen Punkt anhängen und mittelpunkte mitteln
                                except KeyError:
                                    plotPoints[belongsto][f'keyPos_before{k}'] = keyPos 
                                break
            except KeyError:
                pass
            # except IndexError:
                #     return 'break because measurement was interrupted'
        return plotPoints


#%% centroid und active points

def centroid_activeSpots(locationPointsPerFile_10000, saveunder, LT = False, LTT=False):
    
    Iemi_Fehler = 0 #höchster Wert vom Rauschen ## verändert nichts!
    
    VSet = [] 
    IEmi = []
    VSet_davor = [] 
    IEmi_davor = []
    VSet_danach = [] 
    IEmi_danach = []
    VEmi_all = []
    IEmi_all = []
    spots_all = []
    for key in locationPointsPerFile_10000:
        if 'VoltSet_up' in [*locationPointsPerFile_10000[key]]:
            try:
                VSet_davor.append(float(locationPointsPerFile_10000[key]['VoltSet'])) #VoltSet = IEmi soll
                IEmi_davor.append(float(locationPointsPerFile_10000[key]['IEmi']))
                VSet.append(float(locationPointsPerFile_10000[key]['VoltSet'])) #VoltSet = VoltEmi
            except KeyError as e:
                print(e)
        elif 'VoltSet_down' in [*locationPointsPerFile_10000[key]]:
            try:
                VSet_danach.append(float(locationPointsPerFile_10000[key]['VoltSet'])) #VoltSet = VoltEmi
                IEmi_danach.append(float(locationPointsPerFile_10000[key]['IEmi']))
                VSet.append(float(locationPointsPerFile_10000[key]['VoltSet'])) #VoltSet = VoltEmi
            except KeyError as e:
                print(e)
        else:
            try:
                VSet.append(float(locationPointsPerFile_10000[key]['VoltSet'])) #VoltSet = VoltEmi
                IEmi.append(float(locationPointsPerFile_10000[key]['IEmi']))
                
            except KeyError as e:
                print(e)
    
    if LTT: # Stromgeregelt -> Ströme für Grenzen
        grenzen_davor, nrsweeps_davor = sweeps(np.log10(VSet_davor))
        grenzen_danach, nrsweeps_danach = sweeps(np.log10(VSet_danach))
    else:
        grenzen, nrsweeps = sweeps(VSet)
        if len(grenzen) > 20:
            grenzen=[0,int((len(VSet)-1)/2),len(VSet)-1]
            print('grenzen: hat nicht funktioniert')
        else:
            print(f'grenzen: {grenzen}')
    
    
    
    
    if LTT:
        AllGrenzen=[grenzen_davor,grenzen_danach]
        ALLVSet=[VSet_davor,VSet_danach]
        ALLIEemi=[IEmi_davor,IEmi_danach]
        Filter=['VoltSet_up','VoltSet_down']
    else:
        AllGrenzen=[grenzen]
        ALLVSet=[VSet]
        ALLIEemi=[IEmi]
        Filter=['VoltSet']
    
    ''' Formeln für Fehlerrechnung sind noch drin, werden aber nicht verwendet, da nur mit der Standardabweichung Fehler für die plots berechnet werden '''
    for grenzen, part in zip(AllGrenzen, Filter):
        sw = 1
        for i in range(0, len(grenzen)-1, 2):
            #print(f'grenzen[i] : {grenzen[i]} und grenzen [i+2] : {grenzen[i+2]}')
            #print(f'VoltSet[i]: {VSet[grenzen[i]]} und VoltSet[i+2]: {VSet[grenzen[i+2]]}')
            helligkeit_pro_punkt = []
            strom_pro_punkt = []
            mu = []
            sigma = []
            VoltEmi = []
            VoltEmi_std = []
            VoltSet = []
            VoltSet_std = []
            IEmi = []
            IEmi_std = []
            spots = []
            spots_std = []
            counter = 0
            for filename in locationPointsPerFile_10000:
                if part in [*locationPointsPerFile_10000[filename]]: # für Unterteilung in Davor, Danach usw, part e Filter
                    if counter >= grenzen[i] and counter <= grenzen[i+2]: #TODO: Hier stimmts noch nicht mit Stromregelung!
                        strom_pro_punkt = []
                        err_strom_pro_punkt = []
                        helligkeit_pro_punkt = []
                        fehler = []
                        for point in locationPointsPerFile_10000[filename]:
                            if 'fehler' in point:
                                continue
                            if type(point) == tuple:
                                
                                helligkeit_pro_punkt.append(locationPointsPerFile_10000[filename][point])
                                fehler.append(locationPointsPerFile_10000[filename][f'fehler_{point}'])
                        try:
                            # 25.07.22: SumPixelsAll statt SumPixelsLoc für Sens -> macht mehr Sinn!
                            strom_pro_helligkeit=locationPointsPerFile_10000[filename]['IEmi']/locationPointsPerFile_10000[filename]['SumPixelsAll']
                        except ZeroDivisionError:
                            strom_pro_helligkeit = 0
                        except RuntimeWarning:
                            strom_pro_helligkeit = 0
                        except KeyError:
                            continue
                            
                        try:
                            '''
                            fehler strom_pro_helligkeit = 
                            Iemi/(SumPixelsAll)**2*sqrt(sum(fehler_helligkeit_pro_punkt))+fehler_Iemi/sum(SumPixelsAll)
                            '''
                            err_strom_pro_helligkeit = locationPointsPerFile_10000[filename]['IEmi']/(locationPointsPerFile_10000[filename]['SumPixelsAll'])**2*locationPointsPerFile_10000[filename]['SumPixelsAll_std']+\
                                Iemi_Fehler/locationPointsPerFile_10000[filename]['SumPixelsAll']
                        except ZeroDivisionError:
                            err_strom_pro_helligkeit = 0
                        except RuntimeWarning:
                            err_strom_pro_helligkeit = 0
                        #print(f'file: {filename}, strom pro helligkeit: {strom_pro_helligkeit}')
                        
                        #Werte für Bild 1 und Bild2 pro Vset mitteln: 
                        for k,j in zip(helligkeit_pro_punkt, fehler):
                            strom_pro_punkt.append(np.log10(strom_pro_helligkeit*k))
                            '''
                            fehler strom_pro_punkt = 
                            helligkeit_pro_punkt * fehler_strom_pro_helligkeit + Fehler_helligkeit * Strom_pro_helligkeit
                            '''
                            err_strom_pro_punkt.append(np.log10(k*err_strom_pro_helligkeit+j*strom_pro_helligkeit))
                        #print(f'Summe aller Ströme pro Punkte: {sum(strom_pro_punkt)}')
                        
                        spots.append(len(strom_pro_punkt))
                        spots_all.append(len(strom_pro_punkt))
                        mu.append(np.mean(strom_pro_punkt))
                        sigma.append(np.std(strom_pro_punkt))
                        
                        '''
                        fehler: strom_pro_punkt*10**(strom_pro_punkt-1)*err_strom_pro_punkt
                        '''
                        try:
                            VoltSet.append(locationPointsPerFile_10000[filename]['VoltSet'])
                            VoltSet_std.append(locationPointsPerFile_10000[filename]['VoltSet_std'])
                        except KeyError:
                            VoltSet.append(max(VSet))
                            VoltSet_std.append(0)
                        VoltEmi.append(locationPointsPerFile_10000[filename]['VoltEmi'])
                        VoltEmi_std.append(locationPointsPerFile_10000[filename]['VoltEmi_std'])
                        IEmi.append(locationPointsPerFile_10000[filename]['IEmi'])
                        IEmi_std.append(locationPointsPerFile_10000[filename]['IEmi_std'])
                        VEmi_all.append(float(locationPointsPerFile_10000[filename]['VoltEmi']))
                        IEmi_all.append(float(locationPointsPerFile_10000[filename]['IEmi']))
                        
                    counter += 1
                    
            ################ centroid über Vset ####################################
            fig, ax1 = plt.subplots()
            
            # plot der Datenpunkte auf logharithmischer Skala
            g = int(len(VoltSet)/2) #teilen in erste und zweite Hälfte - up und down sweep
            ax1.plot(VoltSet[:g], 10**np.array(mu[:g]), 'None', markersize = 5, label = 'up sweep')#, ecolor = 'lightblue')
            ax1.plot(VoltSet[g:], 10**np.array(mu[g:]), 'None', markersize = 5, label = 'down sweep')#, ecolor = 'lightblue')
            
            ax1.set_yscale('log')
            ax1.set_ylabel('centroid of log. distribution (A)')
            ax1.set_xlabel('set voltage (V)')
            # ax1.set_xlim(500,1250)
            
            #plot der Fehler auf linearer Skala, die dann ausgeblendet wird
            ax2 = ax1.twinx()
            if LT == False:
                g = int(len(VoltSet)/2)
                ax2.errorbar(VoltSet[:g], mu[:g], yerr = sigma[:g], xerr =VoltSet_std[:g], fmt = 'k.', markersize = 5, color = 'black', ecolor = 'royalblue', label = 'up sweep')#, ecolor = 'lightblue')
                ax2.errorbar(VoltSet[g:], mu[g:], yerr = sigma[g:],xerr =VoltSet_std[g:], fmt = 'k.', markersize = 5, color = 'black', ecolor = 'orange', label = 'down sweep')#, ecolor = 'lightblue')
            elif LT == True:
                ax2.errorbar(VoltSet, mu, yerr = sigma, xerr =VoltSet_std, fmt = 'k.', markersize = 5, color = 'black', ecolor = 'royalblue')#, ecolor = 'lightblue')
                
            # ax2.set_ylim(np.log10(ymin/2), np.log10(ymax*2))
            
            ymin, ymax = ax1.get_ylim()
            
            if ymin < 1e-10:
                ax1.set_ylim(ymin/2, 1e-6)
                ax2.set_ylim(np.log10(ymin/2), -6)
            elif ymax > 1e-6:
                ax1.set_ylim(1e-10, ymax*2)
                ax2.set_ylim(-10, np.log10(ymax*2))  
            elif ymin < 1e-10 and ymax > 1e-6:
                ax1.set_ylim(ymin/2, ymax*2)
                ax2.set_ylim(np.log10(ymin/2), np.log10(ymax*2))
            else:
                ax1.set_ylim(1e-10, 1e-6)
                ax2.set_ylim(-10, -6)
    
            ax2.get_yaxis().set_visible(False)
            
            handles2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(handles2, labels2)#, loc = 'upper right')
            ax1.grid(which='both', axis = 'both', zorder=0)
            ax1.set_axisbelow(True)
            plt.title(f'sweep {sw}')
            plt.savefig(saveunder+f'sw={sw}_centroid_Vset.png', dpi = 1000, bbox_inches="tight")
            
            ###################### centroid über V_emi ###########################
            fig, ax1 = plt.subplots()
            
            # plot der Datenpunkte auf logharithmischer Skala
            g = int(len(VoltEmi)/2) #teilen in erste und zweite Hälfte - up und down sweep
            ax1.plot(VoltEmi[:g], 10**np.array(mu[:g]), 'None', markersize = 5, label = 'up sweep')#, ecolor = 'lightblue')
            ax1.plot(VoltEmi[g:], 10**np.array(mu[g:]), 'None', markersize = 5, label = 'down sweep')#, ecolor = 'lightblue')
            
            ax1.set_yscale('log')
            ax1.set_ylabel('centroid of log. distribution (A)')
            ax1.set_xlabel('emission voltage (V)')
            # ax1.set_xlim(500,1250)
            
            #plot der Fehler auf linearer Skala, die dann ausgeblendet wird
            ax2 = ax1.twinx()
            if LT == False:
                g = int(len(VoltEmi)/2)
                ax2.errorbar(VoltEmi[:g], mu[:g], yerr = sigma[:g], xerr =VoltEmi_std[:g], fmt = 'k.', markersize = 5, color = 'black', ecolor = 'royalblue', label = 'up sweep')#, ecolor = 'lightblue')
                ax2.errorbar(VoltEmi[g:], mu[g:], yerr = sigma[g:],xerr =VoltEmi_std[g:], fmt = 'k.', markersize = 5, color = 'black', ecolor = 'orange', label = 'down sweep')#, ecolor = 'lightblue')
            elif LT == True:
                ax2.errorbar(VoltEmi, mu, yerr = sigma, xerr =VoltEmi_std, fmt = 'k.', markersize = 5, color = 'black', ecolor = 'royalblue')#, ecolor = 'lightblue')
                
            # ax2.set_ylim(np.log10(ymin/2), np.log10(ymax*2))
            
            ymin, ymax = ax1.get_ylim()
            
            if ymin < 1e-10:
                ax1.set_ylim(ymin/2, 1e-6)
                ax2.set_ylim(np.log10(ymin/2), -6)
            elif ymax > 1e-6:
                ax1.set_ylim(1e-10, ymax*2)
                ax2.set_ylim(-10, np.log10(ymax*2))  
            elif ymin < 1e-10 and ymax > 1e-6:
                ax1.set_ylim(ymin/2, ymax*2)
                ax2.set_ylim(np.log10(ymin/2), np.log10(ymax*2))
            else:
                ax1.set_ylim(1e-10, 1e-6)
                ax2.set_ylim(-10, -6)
    
            ax2.get_yaxis().set_visible(False)
            
            handles2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(handles2, labels2)#, loc = 'upper right')
            ax1.grid(which='both', axis = 'both', zorder=0)
            ax1.set_axisbelow(True)
            plt.title(f'sweep {sw}')
            if part == Filter[0] and part != 'VSet':
                plt.savefig(saveunder+f'sw={sw}_davor_centroid_Vemi.png', dpi = 1000, bbox_inches="tight")
            elif part == Filter[1]:
                plt.savefig(saveunder+f'sw={sw}_danach_centroid_Vemi.png', dpi = 1000, bbox_inches="tight")
            else:
                plt.savefig(saveunder+f'sw={sw}_centroid_Vemi.png', dpi = 1000, bbox_inches="tight")
            
            ################### centroid über Iemi ###############################
            fig, ax1 = plt.subplots()
            
            # plot der Datenpunkte auf logharithmischer Skala
            g = int(len(IEmi)/2) #teilen in erste und zweite Hälfte - up und down sweep
            ax1.plot(IEmi[:g], 10**np.array(mu[:g]), 'None', markersize = 5, label = 'up sweep')#, ecolor = 'lightblue')
            ax1.plot(IEmi[g:], 10**np.array(mu[g:]), 'None', markersize = 5, label = 'down sweep')#, ecolor = 'lightblue')
            
            ax1.set_yscale('log')
            ax1.set_xscale('log')
            ax1.set_ylabel('centroid of log. distribution (A)')
            ax1.set_xlabel('emission current (A)')
            # ax1.set_xlim(500,1250)
            
            #plot der Fehler auf linearer Skala, die dann ausgeblendet wird
            ax2 = ax1.twinx()
            if LT == False:
                g = int(len(IEmi)/2)
                ax2.errorbar(IEmi[:g], mu[:g], yerr = sigma[:g], xerr =IEmi_std[:g], fmt = 'k.', markersize = 5, color = 'black', ecolor = 'royalblue', label = 'up sweep')#, ecolor = 'lightblue')
                ax2.errorbar(IEmi[g:], mu[g:], yerr = sigma[g:], xerr =IEmi_std[g:], fmt = 'k.', markersize = 5, color = 'black', ecolor = 'orange', label = 'down sweep')#, ecolor = 'lightblue')
            elif LT == True:
                ax2.errorbar(IEmi, mu, yerr = sigma, xerr =IEmi_std, fmt = 'k.', markersize = 5, color = 'black', ecolor = 'royalblue')#, ecolor = 'lightblue')
                
            # ax2.set_ylim(np.log10(ymin/2), np.log10(ymax*2))
            
            ymin, ymax = ax1.get_ylim()
            
            if ymin < 1e-10:
                ax1.set_ylim(ymin/2, 1e-6)
                ax2.set_ylim(np.log10(ymin/2), -6)
            elif ymax > 1e-6:
                ax1.set_ylim(1e-10, ymax*2)
                ax2.set_ylim(-10, np.log10(ymax*2))  
            elif ymin < 1e-10 and ymax > 1e-6:
                ax1.set_ylim(ymin/2, ymax*2)
                ax2.set_ylim(np.log10(ymin/2), np.log10(ymax*2))
            else:
                ax1.set_ylim(1e-10, 1e-6)
                ax2.set_ylim(-10, -6)
    
            ax2.get_yaxis().set_visible(False)
            
            handles2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(handles2, labels2)#, loc = 'upper right')
            ax1.grid(which='both', axis = 'both', zorder=0)
            ax1.set_axisbelow(True)
            plt.title(f'sweep {sw}')
            
            if part == Filter[0] and part != 'VSet':
                plt.savefig(saveunder+f'sw={sw}_davor_centroid_Iemi.png', dpi = 1000, bbox_inches="tight")
            elif part == Filter[1]:
                plt.savefig(saveunder+f'sw={sw}_danach_centroid_Iemi.png', dpi = 1000, bbox_inches="tight")
            else:
                plt.savefig(saveunder+f'sw={sw}_centroid_Iemi.png', dpi = 1000, bbox_inches="tight")
            
            #plot der Anzahl der aktiven Spitzen
            fig, ax2 = plt.subplots()
            if LT == False:
                g = int(len(VoltEmi)/2)
                ax2.plot(VoltEmi[:g], spots[:g], '.', markersize=5, color='royalblue', label = 'up sweep')
                ax2.plot(VoltEmi[g:], spots[g:], '.', markersize=5, color='orange', label = 'down sweep')
                ax2.legend()
            elif LT == True:
                ax2.plot(VoltEmi, spots, '.', markersize=5, color='royalblue')
            ax2.set_ylabel('number of emission spots')
            ax2.set_xlabel('emission voltage (V)')
            # ax2.set_xlim(500, 1250)
            ax2.grid(which='both', axis = 'both')
            
            plt.title(f'sweep {sw}')
            plt.savefig(saveunder+f'sw={sw}_active_points.png', dpi = 1000, bbox_inches="tight")
            
            #plot der Anzahl aktiver Spitzen über den Strom
            fig, ax2 = plt.subplots()
            if LT == False:
                g = int(len(IEmi)/2)
                ax2.plot(IEmi[:g], spots[:g], '.', markersize=5, color='royalblue', label = 'up sweep')
                ax2.plot(IEmi[g:], spots[g:], '.', markersize=5, color='orange', label = 'down sweep')
                ax2.legend()
            elif LT == True:
                ax2.plot(IEmi, spots, '.', markersize=5, color='royalblue', label = 'up sweep')
            ax2.set_ylabel('number of emission spots')
            ax2.set_xlabel('emission current (A)')
            # ax2.set_xlim(500, 1250)
            ax2.grid(which='both', axis = 'both')
            
            plt.title(f'sweep {sw}')
            plt.savefig(saveunder+f'sw={sw}_active_points_per_current.png', dpi = 1000, bbox_inches="tight")
            
            ax2.set_xscale('log')
            if part == Filter[0] and part != 'VSet':
                plt.savefig(saveunder+f'sw={sw}_davor_active_points_per_current_log.png', dpi = 1000, bbox_inches="tight")
            elif part == Filter[1]:
                plt.savefig(saveunder+f'sw={sw}_danach_active_points_per_current_log.png', dpi = 1000, bbox_inches="tight")
            else:
                plt.savefig(saveunder+f'sw={sw}_active_points_per_current_log.png', dpi = 1000, bbox_inches="tight")
            
            plt.close('all')
            sw+=1
        
        #plot der Anzahl der aktiven Spitzen
        fig, ax2 = plt.subplots()
        ax2.plot(VEmi_all, spots_all, '.', markersize=5, color='royalblue')
        ax2.set_ylabel('number of emission spots')
        ax2.set_xlabel('emission voltage (V)')
        # ax2.set_xlim(500, 1250)
        ax2.grid(which='both', axis = 'both')
        plt.title('all sweeps')
        plt.savefig(saveunder+'sw=all_active_points_vemi.png', dpi = 1000, bbox_inches="tight")
        
        #plot der Anzahl aktiver Spitzen über den Strom
        fig, ax2 = plt.subplots()
        ax2.plot(IEmi_all, spots_all, '.', markersize=5, color='royalblue')
        # ax2.plot(IEmi_all[g:], spots_all[g:], '.', markersize=5, color='orange', label = 'down sweep')
        ax2.set_ylabel('number of emission spots')
        ax2.set_xlabel('emission current (A)')
        # ax2.set_xlim(500, 1250)
        ax2.grid(which='both', axis = 'both')
        plt.title('all sweeps')
        plt.savefig(saveunder+'sw=all_active_points_per_current.png', dpi = 1000, bbox_inches="tight")
        
        ax2.set_xscale('log')
        plt.savefig(saveunder+'sw=all_active_points_per_current_log.png', dpi = 1000, bbox_inches="tight")
        
        plt.close('all')

#%% Histogramme automatisch erstellen

def histogramme(locationPointsPerFile, files, nrbins=8, transparency=0.7):
    '''
    

    Parameters
    ----------
    locationPointsPerFile : dictionary
        von detect_points oder getDictfromTXTwithSTDproPunkt.
    files : List
        Liste mit Nummern (ints) der Bilder, für die je ein Histogramm geplotted werden soll.

    Returns
    -------
    None.

    '''
    
    
    for file in files:
         
         for filename in locationPointsPerFile:
             
             if str(file) in filename:
                 strom_pro_punkt = []
                 helligkeit_pro_punkt = []
                 for point in locationPointsPerFile[filename]:
                     if type(point) == tuple:
                         
                         helligkeit_pro_punkt.append(locationPointsPerFile[filename][point])
                 
                 try:
                     # 25.07.22: SumPixelsAll statt SumPixelsLoc für Sens -> macht mehr Sinn!
                     strom_pro_helligkeit=locationPointsPerFile[filename]['IEmi']/locationPointsPerFile[filename]['SumPixelsAll']
                 except ZeroDivisionError:
                     print('zero division error..')
                     strom_pro_helligkeit = 0
                 print(f'file: {filename}, strom pro helligkeit: {strom_pro_helligkeit}')
                     
                 for i in helligkeit_pro_punkt:
                     strom_pro_punkt.append(strom_pro_helligkeit*i)
                 print(f'Summe aller Ströme pro Punkte: {sum(strom_pro_punkt)}')
                 break
         # Min, Max und Anzahl für das Erstellen der bins des Histogramms
         try:
             MIN, MAX, ANZAHL = min(strom_pro_punkt), max(strom_pro_punkt), nrbins#int(np.sqrt(len(strom_pro_punkt)))+1#8
         except ValueError:
             print('keine Punkte detektiert, kein Histogramm möglich')
             continue
         print(f'file: {filename}, min: {MIN}, max: {MAX}, Anzahl: {ANZAHL}')
         beschrV = locationPointsPerFile[filename]['VoltEmi']
         beschrI = locationPointsPerFile[filename]['IEmi'] *1e6 #Umrechnung in uA
         # if file in files[0:2]:
         #     beschriftung = '$I_{emi} \\uparrow = $ ' + f'{beschrI:.2f} $\mu A$' # Pfeil hoch für upsweep
         # if file in files[2:4]:
         #     beschriftung = '$I_{emi} \\downarrow = $ ' + f'{beschrI:.2f} $\mu A$' # Pfeil runter für downsweep
         beschriftung = f'{beschrV:.2f} V, {beschrI:.2f} $\mu A$'
         # plt.figure(filename)
         ax = plt.subplot(111)
         # Grenzen -0.1 bzw. +0.1, damit Minimum und Maximum nicht außerhalb der bins des histogramms liegen können
         ax.hist(strom_pro_punkt, bins = 10 ** np.linspace(np.log10(MIN)-0.1, np.log10(MAX)+0.1, ANZAHL, endpoint=True), label = beschriftung, ec = 'black', alpha=transparency)#int(np.sqrt(len(strom_pro_punkt)))))
         ax.tick_params(direction='in', which='both',pad=2.5)
         plt.xscale('log')
         plt.xlabel('emission current (A)', labelpad=0)
         plt.ylabel('emission spots', labelpad=0)
         ax.legend(handlelength = 0.5, columnspacing = 1)#, title='Line', loc='upper left')
         
         plt.show()

#%% plot everything for Long Term Test!
    
def plotResultsMEANLT(locationPointsPerFile, saveunder, save=True, width_point=5):
        '''
        generates and saves (if save == True) plots of results(=locationPointsPerFile)
        from detectPoints() of Long Term Tests
    
        Parameters
        ----------
        locationPointsPerFile : dict returned from detectPoints()
        path : path of measurement data
        saveunder : path for saving plots
        save : True for saving figures, False for only showing figures
    
        Returns
        -------
        plotPoints : dict() with all points
    
        '''    
        if saveunder[-1] == '/':
            pass
        else:
            saveunder = saveunder+'/'
        
        if not os.path.exists(saveunder):
            os.makedirs(saveunder)

        #  Plot brightness of all pixels for each photo
        Fotonr = []
        sumPxs = []
        sumPxs_std = []
        sumLoc = []
        sumLoc_std = []
        VoltSet = []
        VoltEmi = []
        emissionI = []
        VoltSet_std = []
        VoltEmi_std = []
        emissionI_std = []
        Time = []
        Time_std = []
        TimeX = []
        TimeX_std = []
        for key in locationPointsPerFile:
            try:
                VoltSet.append(locationPointsPerFile[key]['VoltSet']) # ist hier IEmi Set
                VoltSet_std.append(locationPointsPerFile[key]['VoltSet_std'])
            except KeyError:
                try:
                    Time.append(locationPointsPerFile[key]['Time'])
                    Time_std.append(locationPointsPerFile[key]['Time_std'])
                    TimeX.append(np.mean([float(key[:-4].split('-')[1]),float(key[:-4].split('-')[0])])/2)
                    TimeX_std.append(np.std([float(key[:-4].split('-')[1]),float(key[:-4].split('-')[0])])/2)
                except KeyError as e:
                    print(e)
                
            try:
                VoltEmi.append( locationPointsPerFile[key]['VoltEmi'])
                VoltEmi_std.append( locationPointsPerFile[key]['VoltEmi_std'])
                emissionI.append( locationPointsPerFile[key]['IEmi'])
                emissionI_std.append( locationPointsPerFile[key]['IEmi_std'])
                Fotonr.append(np.mean([float(key[:-4].split('-')[1]),float(key[:-4].split('-')[0])]))
                sumPxs.append(locationPointsPerFile[key]['SumPixelsAll'])
                sumPxs_std.append(locationPointsPerFile[key]['SumPixelsAll_std'])
                sumLoc.append(locationPointsPerFile[key]['SumPixelsLoc'])
                sumLoc_std.append(locationPointsPerFile[key]['SumPixelsLoc_std'])
            except KeyError as e:
                print(e)
        
        fig, ax = plt.subplots()
        ax.errorbar(Fotonr, sumLoc, yerr = sumLoc_std, capsize = 1, color = 'royalblue',\
                    ecolor = 'cornflowerblue', elinewidth = 0.1)
        ax.set_ylabel('Pixelhelligkeit', color = 'royalblue')
        ax.set_yscale('log')

        ax.set_xlabel('Fotonummer')
        if save == True:
            plt.savefig(f'{saveunder}FullPlot_Fotonr_brightnessPixelsLoc_widthPoint_{width_point}.png', dpi=100, bbox_inches="tight")
        
        ax2 = ax.twinx()
        ax2.errorbar(Fotonr, emissionI, yerr = emissionI_std, capsize = 1,\
                    color = 'red', ecolor = 'lightcoral', elinewidth = 0.1)
        ax2.set_yscale('log')
        ax2.set_ylabel('I_emi [A]', color = 'red')
        if save == True:
            plt.savefig(f'{saveunder}FullPlot_Fotonr_Iemi_brightnessPixelsLoc_widthPoint_{width_point}.png', dpi=100, bbox_inches="tight")
        
        ax3 = ax.twinx()
        ax3.errorbar(Fotonr, VoltEmi, yerr = VoltEmi_std, capsize = 1,\
                    color = 'black', ecolor = 'grey', elinewidth = 0.1)
        ax3.set_yscale('log')
        ax3.set_ylabel('V_emi [V]')
        ax3.spines['right'].set_position(("axes", 1.2))
        if save == True:
            plt.savefig(f'{saveunder}FullPlot_Fotonr_Iemi_Vemi_brightnessPixelsLoc_widthPoint_{width_point}.png', dpi=100, bbox_inches="tight")
        
        
        # Plot brightness against emission current
        plt.close('all')
        
        plotPoints, PiCamLT = plotDictMEAN(locationPointsPerFile, width_point = width_point, LT=True) #13.05.2022: Redundanz behoben durch Funktion
        
        sw=1
        
        fig,ax1 = plt.subplots()
        ax1.errorbar(Fotonr, emissionI, yerr = emissionI_std, color = 'red', ecolor = 'lightcoral', label = 'Emissionsstrom')#, label = 'down')
        ax1.set_xlabel('Fotonummer')
        ax1.set_ylabel('Emissionsstrom [A]')
        ax1.set_yscale('log')
        ax2 = ax1.twinx()
        k = 0            
        while True:
            try:
                if len(plotPoints[f'point{k}']) > 0:
                    ax2.errorbar(plotPoints[f'xFoto{k}'], plotPoints[f'point{k}'], yerr = plotPoints[f'point_fehler{k}'], label = f'point{k}')
                k+=1
            except KeyError:
                break
        ax2.set_ylabel('Pixelhelligkeit')
        ax2.set_yscale('log')
        ax2.yaxis.set_label_position("right")
        
        handles, labels = ax1.get_legend_handles_labels()
        ha,la = ax2.get_legend_handles_labels()
        for h, l in zip(ha,la):
            handles.append(h)
            labels.append(l)
        ax2.legend(handles, labels, bbox_to_anchor=(1.5,1))#, title='Line', loc='upper left')
    
        if save == True:
            plt.savefig(f'{saveunder}sw_{sw}_Plot_Fotonr_emissionCurrent_brightnessPixelsEach_widthPoint_{width_point}', dpi=100, bbox_inches="tight")
        
        ax3 = ax1.twinx()
        ax3.errorbar(Fotonr, VoltEmi, yerr=VoltEmi_std, color = 'black', ecolor = 'gray', label = 'Emissionsspannung')
        ax3.set_ylabel('Emissionsspannung [V]')
        # ax3.set_yscale('log')
        ax3.spines['right'].set_position(("axes", 1.2))
        ax3.set_yscale('log')
        ha,la = ax3.get_legend_handles_labels()
        for h, l in zip(ha,la):
            handles.append(h)
            labels.append(l)
        ax2.get_legend().remove()
        ax3.legend(handles, labels, bbox_to_anchor=(1.8,1))
        
        if save == True:
            plt.savefig(f'{saveunder}sw_{sw}_Plot_Fotonr_emissionCurrent_VoltEmi_brightnessPixelsEach_widthPoint_{width_point}', dpi=100, bbox_inches="tight")
        
        try:
            fig,ax1 = plt.subplots()
            ax1.errorbar(Time, [emissionI[int(xx)] for xx in TimeX], yerr = [emissionI_std[int(xx)] for xx in TimeX], color = 'red', ecolor = 'lightcoral', label='Emissionsstrom')
            ax1.set_xlabel('Zeit [s]')
            ax1.set_ylabel('Emissionsstrom [A]')
            ax1.set_yscale('log')
            ax2 = ax1.twinx()
            ax2.errorbar(Time, [sumLoc[int(xx)] for xx in TimeX], yerr = [sumLoc_std[int(xx)] for xx in TimeX], color = 'royalblue', ecolor = 'cornflowerblue', label = 'Pixelhelligkeit')
            
            ax2.set_ylabel('Pixelhelligkeit')
            ax2.set_yscale('log')
            handles, labels = ax1.get_legend_handles_labels()
            ha,la = ax2.get_legend_handles_labels()
            for h, l in zip(ha,la):
                handles.append(h)
                labels.append(l)
            ax2.legend(handles, labels)
            if save == True:
                plt.savefig(f'{saveunder}sw_{sw}_LT_Plot_Time_emissionCurrent_brightness_widthPoint_{width_point}', dpi=100, bbox_inches="tight")
        except IndexError:
            print('index error. measurement interrupted, break..')
            return plotPoints
        
        k = 0            
        while True:
            try:
                if len(plotPoints[f'point{k}']) > 0:
                    indizes = []
                    for pp in PiCamLT:
                        try:
                            indizes.append(plotPoints[f'xFoto{k}'].index(pp))
                        except ValueError:
                            pass
                    poTime, poBrigh, poFehler = list(), list(), list()
                    for ii in indizes:
                        try:
                            poTime.append(plotPoints[f'x{k}'][ii])
                            poBrigh.append(plotPoints[f'point{k}'][ii])
                            poFehler.append(plotPoints[f'point_fehler{k}'][ii])
                        except IndexError:
                            pass
                    ax2.errorbar(poTime, poBrigh, yerr = poFehler, label = f'point{k}')
                k+=1
            except KeyError:
                break
        handles, labels = ax1.get_legend_handles_labels()
        ha,la = ax2.get_legend_handles_labels()
        for h, l in zip(ha,la):
            handles.append(h)
            labels.append(l)
        ax2.legend(handles, labels, bbox_to_anchor=(1.5,1))#, title='Line', loc='upper left')
        
        if save == True:
            plt.savefig(f'{saveunder}sw_{sw}_LT_Plot_Time_emissionCurrent_points_widthPoint_{width_point}', dpi=100, bbox_inches="tight")
        
        
        ax3 = ax1.twinx()
        ax3.errorbar(Time, [VoltEmi[int(xx)] for xx in TimeX], yerr = [VoltEmi_std[int(xx)] for xx in TimeX], color = 'black', ecolor = 'gray', label = 'Emissionsspannung')
        ax3.set_xlabel('Zeit [s]')
        ax3.set_ylabel('Emissionsspannung [V]')
        ax3.set_yscale('log')
        ax3.spines['right'].set_position(("axes", 1.2))
        ha,la = ax3.get_legend_handles_labels()
        for h, l in zip(ha,la):
            handles.append(h)
            labels.append(l)
        ax2.get_legend().remove()
        ax3.legend(handles, labels, bbox_to_anchor=(1.8,1))
        
        if save == True:
            plt.savefig(f'{saveunder}sw_{sw}_LT_Plot_Time_emissionCurrent_Vemi_points_widthPoint_{width_point}', dpi=100, bbox_inches="tight")
            
        plt.close('all')
        
        return plotPoints


#%% Save dictionary to txt file
    
def saveDictSTDproPunkt(saveunder, locationPointsPerFile,width_point = 5,limitBrightness = 5):
    '''
    saves dictionary (detected points with location etc.) provided by 
    detectPoints() in txt file

    Parameters
    ----------
    saveunder : path for saving txt file

    Returns
    -------
    None.

    '''
    
    if type(locationPointsPerFile) is not dict:
        print('skip saving dict!')
        return None
    
    if saveunder[-1] == '/':
        pass
    else:
        saveunder = saveunder+'/'
    
    if not os.path.exists(saveunder):
        os.makedirs(saveunder)
            
    #filename = f'auswertung_widthPoint_{width_point}_limitBrightness_{limitBrightness}.txt'
    filename = str(saveunder.split('/')[-2])+f'_auswertung_widthPoint_{width_point}_limitBrightness_{limitBrightness}.txt'
    
    file = open(saveunder+filename, 'w')
    file.write('Filename \t SumLoc/SumAll \t SumPixelsLoc \t SumPixelsLoc_std \t SumPixelsAll \t SumPixelsAll_std \t coordinates \t brightness \t error \n')
    for key in locationPointsPerFile:
        file.write(key+'\t')
        datakey = 'SumLoc/SumAll'
        file.write(f'{locationPointsPerFile[key][datakey]:08.2f}\t')
        datakey = 'SumPixelsLoc'
        file.write(f'{locationPointsPerFile[key][datakey]:08.2f}\t')
        datakey = 'SumPixelsLoc_std'
        file.write(f'{locationPointsPerFile[key][datakey]:08.2f}\t')
        datakey = 'SumPixelsAll'
        file.write(f'{locationPointsPerFile[key][datakey]:08.2f}\t')
        datakey = 'SumPixelsAll_std'
        file.write(f'{locationPointsPerFile[key][datakey]:08.2f}\t')
        for datakey in reversed(locationPointsPerFile[key]):
            if type(datakey) == tuple:
                    fehler = locationPointsPerFile[key][f'fehler_{datakey}']
                    file.write(f'{datakey} \t {locationPointsPerFile[key][datakey]:08.2f} \t {fehler:08.2f} \t ')
        file.write('\n')
        
    file.close()
        

#%% read saved txt to get dict


def getDictfromTXTwithSTDproPunkt(filename):
    
    locationPointsPerFile = dict()
    
    file = open(filename, 'r')
    data = file.readlines()
    for lines in data[1:]:
        
        locationPoints = dict()
        
        lines = lines.split('\t')
        lines = lines[:-1]
        locationPoints['SumLoc/SumAll'] = float(lines[1])
        locationPoints['SumPixelsLoc'] = float(lines[2])
        locationPoints['SumPixelsLoc_std'] = float(lines[3])
        locationPoints['SumPixelsAll'] = float(lines[4])
        locationPoints['SumPixelsAll_std'] = float(lines[5])
        
        for i in range(6, len(lines)-2, 3):
            line = lines[i].strip()
            line = line[1:-1].split(',')
            # print(line)
            locationPoints[int(float(line[0])), int(float(line[1]))] = float(lines[i+1])
            locationPoints[f'fehler_{int(float(line[0])), int(float(line[1]))}'] = float(lines[i+2])
            
        locationPointsPerFile[lines[0]] = locationPoints
        
    file.close()
    
    return locationPointsPerFile

#%% add current and voltage to dict from measurement txt file

def addVItoDictwithMEAN(measfile, locationPointsPerFile, LT = False, LTT=False):
    # measfile consists of path and name of measurement file
    # locationPointsPerFile is dict with all detected points
    
    #seit 18.03.22 mit Unterscheidung zwischen VoltSet_up und _down
    measdict = dict()
    file = open(measfile, 'r')
    data = file.readlines()
    for lines in data[1:]:
        lines = lines.split('\t') #jeweiliger Messpunkt als array
        measdict_file = dict()
        try:
            if LT == True:
                if 'downSwp' in measfile:
                    if LTT == True:
                        measdict_file['VoltSet'] = float(lines[0]) # eigentlich IEmi_Set, Vset bei LTT unsinnig
                        measdict_file['VoltSet_down'] = float(lines[5]) # eigentlich VEmi, Vset bei LTT unsinnig
                    else:
                        measdict_file['VoltSet'] = float(lines[0])
                        measdict_file['VoltSet_down'] = float(lines[0]) 
                elif 'upSwp' in measfile:
                    if LTT == True:
                        measdict_file['VoltSet'] = float(lines[0]) # eigentlich IEmi_Set, Vset bei LTT unsinnig
                        measdict_file['VoltSet_up'] = float(lines[5]) # eigentlich VEmi, Vset bei LTT unsinnig
                    else:
                        measdict_file['VoltSet'] = float(lines[0])
                        measdict_file['VoltSet_up'] = float(lines[0]) 
                else:
                    measdict_file['Time'] = float(lines[0])
            elif LT == False and LTT == False:
                measdict_file['VoltSet'] = float(lines[0])
            measdict_file['VoltEmi'] = float(lines[5])
            if LTT == False:
                measdict_file['IEmi'] = float(lines[3])
            else:
                measdict_file['IEmi'] = float(lines[1])
        except ValueError as e:
            print(e)
        except IndexError as e:
            print(e)
        except KeyError as e:
            print(e)
        measdict[int(float(lines[4]))] = measdict_file
    file.close()
    
    for file in locationPointsPerFile:
        filenrs = file[:-4].split('-')
        filenrs = (int(float(filenrs[0])), int(float(filenrs[1])))
        if filenrs[0] not in measdict or filenrs[1] not in measdict:
            continue
        try:
            locationPointsPerFile[file]['VoltSet'] = np.mean([measdict[filenrs[0]]['VoltSet'], measdict[filenrs[1]]['VoltSet']])
            locationPointsPerFile[file]['VoltSet_std'] = np.std([measdict[filenrs[0]]['VoltSet'], measdict[filenrs[1]]['VoltSet']])
        except KeyError:
            locationPointsPerFile[file]['Time'] = np.mean([measdict[filenrs[0]]['Time'], measdict[filenrs[1]]['Time']])
            locationPointsPerFile[file]['Time_std'] = np.std([measdict[filenrs[0]]['Time'], measdict[filenrs[1]]['Time']])
        try:
            locationPointsPerFile[file]['VoltEmi'] = np.mean([measdict[filenrs[0]]['VoltEmi'], measdict[filenrs[1]]['VoltEmi']])
            locationPointsPerFile[file]['VoltEmi_std'] = np.std([measdict[filenrs[0]]['VoltEmi'], measdict[filenrs[1]]['VoltEmi']])
            locationPointsPerFile[file]['IEmi'] = np.mean([measdict[filenrs[0]]['IEmi'], measdict[filenrs[1]]['IEmi']])
            locationPointsPerFile[file]['IEmi_std'] = np.std([measdict[filenrs[0]]['IEmi'], measdict[filenrs[1]]['IEmi']])
        except KeyError as e:
            print(e)
        try:
            locationPointsPerFile[file]['VoltSet_up'] = np.mean([measdict[filenrs[0]]['VoltSet_up'], measdict[filenrs[1]]['VoltSet_up']])
        except KeyError:
            pass
        try:
            locationPointsPerFile[file]['VoltSet_down'] = np.mean([measdict[filenrs[0]]['VoltSet_down'], measdict[filenrs[1]]['VoltSet_down']])
        except KeyError:
            pass
    return locationPointsPerFile


#%% ersetze überbelichtete Punkte mit Punkten aus geringerem shutter speed
def replaceOverexposedPointsSTDproPunkt(pathDict,pathImages, ss, numberImagesPerVoltage=3, numberMeasurementsPerVoltage=2, LT=False, img0_nr = 0, LTT=False, locationPointsPerFile_highss=False):
    # check original images for overexposure and save locations in dict
    # wenn für locationPointsPerFile_highss ein dictionary übergeben wird, wird dieses verwendet, statt ein neues einzulesen
    ss.sort(reverse=True)
    
    for i in range(len(ss)-1):
        ss_high = ss[i]
        ss_low = ss[i+1]
        
        overexposure = findOverexposureMEAN(pathImages, shutterSpeed = ss_high, numberImagesPerVoltage=numberImagesPerVoltage, numberMeasurementsPerVoltage=numberMeasurementsPerVoltage, img0_nr = img0_nr, LTT=LTT)
        
        measfile = glob.glob(pathImages+'*.txt')
        #read dict of high ss
        if locationPointsPerFile_highss == False:
            filename_highss = glob.glob(pathDict+f'ss={ss_high}'+'/*auswertung*.txt')
            if len(filename_highss) == 0: 
                print(f'could not find folder in \n {pathDict}/ss={ss_high}/')
                return None
            locationPointsPerFile_highss = getDictfromTXTwithSTDproPunkt(filename_highss[0])
            
        if LT == False:
            locationPointsPerFile_highss = addVItoDictwithMEAN(measfile=measfile[0], locationPointsPerFile=locationPointsPerFile_highss)
        elif LT == True:
            #3 txt files (up- + down-sweep + LT)
            if LTT==True:
                for mfile in measfile:
                    locationPointsPerFile_highss = addVItoDictwithMEAN(measfile=mfile, locationPointsPerFile=locationPointsPerFile_highss, LT=True, LTT=True)
            else:
                for mfile in measfile:
                    locationPointsPerFile_highss = addVItoDictwithMEAN(measfile=mfile, locationPointsPerFile=locationPointsPerFile_highss, LT=True)
        
        if len(overexposure) == 0:
            # wenn keine Überbelichtung gefunden wurde, wird dictionary mit langer
            # Belichtungszeit einfach wieder ausgegeben
            return locationPointsPerFile_highss
        
        #read dict of low ss
        filename_lowss = glob.glob(pathDict+f'ss={ss_low}'+'/*auswertung*.txt')
        if len(filename_lowss) == 0: 
            print(f'could not find folder in \n {pathDict}/ss={ss_low}/')
            return None
        locationPointsPerFile_lowss = getDictfromTXTwithSTDproPunkt(filename_lowss[0])
        if LT == False:
            locationPointsPerFile_lowss = addVItoDictwithMEAN(measfile=measfile[0], locationPointsPerFile=locationPointsPerFile_lowss)
        elif LT == True:
            #3 txt files (up- + down-sweep + LT)
            if LTT==True:
                for mfile in measfile:
                    locationPointsPerFile_highss = addVItoDictwithMEAN(measfile=mfile, locationPointsPerFile=locationPointsPerFile_highss, LT=True, LTT=True)
            else:
                for mfile in measfile:
                    locationPointsPerFile_highss = addVItoDictwithMEAN(measfile=mfile, locationPointsPerFile=locationPointsPerFile_highss, LT=True,)
        
        for file in locationPointsPerFile_highss:
            # check for overexposure and calculate points new
            width = 5
            for points in locationPointsPerFile_highss[file]:
                if type(points) == tuple:
                    for overexp in overexposure[file]:
                        if abs(points[0]-overexp[0]) <= width:
                            if abs(points[1]-overexp[1]) <= width:
                                print(f'file: {file}, found overexp at point {points}')
                                #find point in 1000er ss and calculate new for 10 000 er ss 
                                for newpoint in locationPointsPerFile_lowss[file]:
                                    if type(newpoint) == tuple:
                                        if abs(newpoint[0]-points[0]) <= width:
                                            if abs(newpoint[1]-points[1]) <= width:
                                                faktor = float(ss[0])/float(ss_low) #Faktor errechnet sich immer aus max belz / low belz
                                                print(f'faktor = {faktor}')
                                                print(f'will replace {points}, {locationPointsPerFile_highss[file][points]} with {newpoint}, {locationPointsPerFile_lowss[file][newpoint]} * {faktor}')
                                                locationPointsPerFile_highss[file]['SumPixelsLoc'] = \
                                                    locationPointsPerFile_highss[file]['SumPixelsLoc'] - \
                                                    locationPointsPerFile_highss[file][points] + \
                                                    locationPointsPerFile_lowss[file][newpoint] * faktor
                                                locationPointsPerFile_highss[file]['SumPixelsAll'] = \
                                                    locationPointsPerFile_highss[file]['SumPixelsAll'] - \
                                                    locationPointsPerFile_highss[file][points] + \
                                                    locationPointsPerFile_lowss[file][newpoint] * faktor                                                
                                                locationPointsPerFile_highss[file][points] = \
                                                    locationPointsPerFile_lowss[file][newpoint] * faktor
                                                #fehler --> fehlerfortpflanzung!!
                                                locationPointsPerFile_highss[file][f'fehler_{points}'] = \
                                                    np.sqrt(locationPointsPerFile_lowss[file][f'fehler_{newpoint}']**2 * faktor)
                                                
    ss.sort(reverse=True)
    
    return locationPointsPerFile_highss


#%% Erstelle Referenzbild mit nummerierten detektierten Punkten

def PointPositionReferenceImage(locationPointsPerFile, measurement,  saveunder,MaxSS, current=None, highestSS=-1, rawdir='//fs-01/KETEK-NET/Prozess/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam_LTT/', save=True, width_point=5, LT=False, LTT=False):
    '''
    highestSS:      defines the Shutterspeed the image is taken from. -1 means highest SS, -2 second high
    '''
    
    if rawdir[-1] != '/':
        rawdir=rawdir+'/'
    if saveunder[-1] != '/':
        saveunder=saveunder+'/'
    
    
    if LT==True:
        plotPoints, PiCamLT = plotDictMEAN(locationPointsPerFile, width_point = width_point, LT=LT)
    else:
        plotPoints = plotDictMEAN(locationPointsPerFile, width_point = width_point, LT=LT)
    LocationKeys=[key for key in [*plotPoints] if  ('loc' in key)]
    PointPositions=[]
    for key in LocationKeys:
        pos=[sum(x)/len(x) for x in zip(*plotPoints[key])]
        pos=(round(pos[0]),round(pos[1]))
        PointPositions.append(pos)

    #select image middle of measurement with highest ss
    if LTT==True:
        file=glob.glob(rawdir+f'{measurement}/{current}/*jpg')
    else:
        file=glob.glob(rawdir+f'{measurement}/*jpg')
    file=[nr for nr in file if  (file[round(len(file)/2)][-29:-21] in nr)]
    maxss=[]
    for ss in range(0,len(file)-1):
        maxss.append(file[ss][-17:-8])
    maxss=natsort.os_sorted(maxss)[highestSS]
    file=[ss for ss in file if  (maxss in ss)][0]

    img_subdraw=cv.imread(file,0).astype(np.float64)
    i=1
    for xy in PointPositions:
        #cv.circle(img_subdraw, xy, width_point, 255, thickness=-1)
        cv.rectangle(img_subdraw, tuple(map(sum, zip(xy, (width_point,-width_point)))),np.subtract(xy,(width_point,-width_point)), color= 255, thickness=-1)
        cv.putText(img_subdraw,f'{i}',np.subtract(xy,(round(1.5*width_point),-round(width_point/2))),cv.FONT_HERSHEY_SCRIPT_SIMPLEX ,.3,(127,0,0),1,5)
        i=i+1
    plt.imshow(img_subdraw, cmap='bwr')
    plt.title('Point Detection Reference')
    if save==True:
        plt.savefig(f'{saveunder}PointDetectionReference_{MaxSS}.png', dpi = 200)
    return


#%% copy files in currdep folder
#TODO: funktioniert so nur mit LT oder LTT, könnte aber auch mit nur sweeps genauso gehen
def CopyCDLFiles(measpath, curr, numberMeasurementsPerVoltage=2):
    '''
    Copies Measfiles into CDL folder -> makes it readable for Currdeplife (object oriented) evaluation

    Parameters
    ----------
    measpath : string
        path to measurement (txt.-files).
    curr : str
        acutual current to evaluate (for LTT). In case of LT or sweeps curr=''
    numberMeasurementsPerVoltage : int, optional
        number of measurements per voltage. The default is 2.

    Returns
    -------
    None.

    '''
    #Currents = os.listdir(measpath)
    #Currents = [folder for folder in Currents if not '.txt' in folder]
    #Currents = [folder for folder in Currents if not 'CDL' in folder]
    if measpath[-1]!='/':
        measpath=measpath+'/'
    originalIV_LT=[] # list of IV-LT files
    CamDataFiles100=[] # list of CamData files with MaxSS=100 (100ersetzt)
    CamDataFiles10=[] # list of CamData files with MaxSS=10 (10ersetzt)
    targetIV_List_Up=[] # list of designated paths of davor IV files
    targetIV_List_Down=[] # list of designated paths of davor IV files 
    CamDataFiles100_LT=[] # read lines of CamData LT files
    CamDataFiles10_LT=[] # read lines of CamData LT files  
    #for curr in Currents:
    if curr!='':
        currpath = measpath + curr + '/'
    else:
        currpath = measpath
    # find IV-Sweep files per curr
    IVmeasfiles = glob.glob(currpath+'*.txt')
    originalIV_Up=[up for up in IVmeasfiles if '_upSwp' in up][0]    
    originalIV_Down=[down for down in IVmeasfiles if '_downSwp' in down][0]
    
    # append IV-LT file per curr
    originalIV_LT.append([LT for LT in IVmeasfiles if '_LT.txt' in LT][0])
    
    # append CamDataFile for both MaxSS per curr
    CamDataPath= natsort.natsorted([f.path for f in os.scandir(currpath) if (f.is_dir() and 'ersetzt' in f.name)])
    i=0
    for MaxSSPath in CamDataPath:
        if i==0:
            CamDataFiles10.append([f.path for f in os.scandir(MaxSSPath) if ('.txt' in f.path)][0])
            i=1
        else:
            CamDataFiles100.append([f.path for f in os.scandir(MaxSSPath) if ('.txt' in f.path)][0])
    
    #create CDL path
    if not os.path.exists(measpath+'CDL/'):
        os.makedirs(measpath+'CDL/')
    
    # UP-IV CDL-file
    targetIV_Up=originalIV_Up.replace('\\','/').split('/')[-1][0:-10]
    if '_LT' in targetIV_Up:
        targetIV_Up=targetIV_Up.replace('_LT','') # remove LT from name -> problem
    targetIV_Up=measpath+'CDL/'+targetIV_Up+'.txt'
    targetIV_List_Up.append(targetIV_Up)
    shutil.copyfile(originalIV_Up,targetIV_Up)
    # DOWN-IV CDL-file
    targetIV_Down=originalIV_Down.replace('\\','/').split('/')[-1][0:-12]
    if '_LT' in targetIV_Down:
        targetIV_Down=targetIV_Down.replace('_LT','') # remove LT from name -> problem
    targetIV_Down=measpath+'CDL/'+targetIV_Down+'_danach.txt'
    targetIV_List_Down.append(targetIV_Down)
    shutil.copyfile(originalIV_Down,targetIV_Down)
        
    # sort IV-Files and CamDataFiles by current
    sortlist=[]
    for files in originalIV_LT:
        sortlist.append(files.replace('\\','/').split('/')[-1])
    originalIV_LT = [x for y,x in natsort.natsorted(zip(sortlist,originalIV_LT))]
    CamDataFiles100 = [x for y,x in natsort.natsorted(zip(sortlist,CamDataFiles100))]
    CamDataFiles10 = [x for y,x in natsort.natsorted(zip(sortlist,CamDataFiles10))]
    targetIV_List_Up = [x for y,x in natsort.natsorted(zip(sortlist,targetIV_List_Up))]
    targetIV_List_Down = [x for y,x in natsort.natsorted(zip(sortlist,targetIV_List_Down))]
    
    # CamDataFiles
    i=0
    j=0
    for (CamDataFile100,CamDataFile10,UpFile,DownFile) in zip(CamDataFiles100,CamDataFiles10,targetIV_List_Up,targetIV_List_Down):
        # 100ersetzt
        if 'LT' in CamDataFile100.replace('\\','/').split('/')[-4]:
            Sample=CamDataFile100.replace('\\','/').split('/')[-4].replace('_LT','')
        else:
            Sample=CamDataFile100.replace('\\','/').split('/')[-4]
        Current=CamDataFile100.replace('\\','/').split('/')[-3]
        CamDataFile100 = CamDataFile100.replace('\\','/')
        MaxSS_1=CamDataFile100.split('/')[-2][:-7]
        # UP
        target_CamDataFile100_Up=(measpath+'CDL/'+Sample+'_'+Current+'_'+f'CamData{MaxSS_1}ms.txt')
        num_lines_up = int((sum(1 for line in open(UpFile))+1)/numberMeasurementsPerVoltage) # Anzahl lines in UpFile +1/2 weil Kopfzeile und CamData schon gemittelt 
        with open(target_CamDataFile100_Up, 'w') as outfile:
            with open(CamDataFile100) as infile:
                Camlines=infile.readlines()
                for line in Camlines[0:num_lines_up]:
                    outfile.write(line)
        # Down
        target_CamDataFile100_Down=(measpath+'CDL/'+Sample+'_'+Current+'_'+f'CamData{MaxSS_1}ms_danach.txt')
        num_lines_down = int((sum(1 for line in open(DownFile))+1)/numberMeasurementsPerVoltage) # Anzahl lines in UpFile +1/2 weil Kopfzeile und CamData schon gemittelt
        with open(target_CamDataFile100_Down, 'w') as outfile:
            with open(CamDataFile100) as infile:
                lines=infile.readlines()
                outfile.write(lines[0]) #head
                for line in lines[-num_lines_down+1:]:
                    outfile.write(line)
        # LT
        with open(CamDataFile100) as infile:
            lines=infile.readlines()
        if i==0:
            CamDataFiles100_LT.append(lines[0]) #head
            i=1
        for line in lines[num_lines_up:-num_lines_down+1]:
            CamDataFiles100_LT.append(line)
        
        
        #10ersetzt
        if 'LT' in CamDataFile10.replace('\\','/').split('/')[-4]:
            Sample=CamDataFile10.replace('\\','/').split('/')[-4].replace('_LT','')
        else:
            Sample=CamDataFile10.replace('\\','/').split('/')[-4]
        Current=CamDataFile10.replace('\\','/').split('/')[-3]
        CamDataFile10 = CamDataFile10.replace('\\','/')
        MaxSS_2=CamDataFile10.split('/')[-2][:-7]
        
        # UP
        target_CamDataFile10_Up=(measpath+'CDL/'+Sample+'_'+Current+'_'+f'CamData{MaxSS_2}ms.txt')
        num_lines_up = int((sum(1 for line in open(UpFile))+1)/numberMeasurementsPerVoltage) # Anzahl lines in UpFile +1/2 weil Kopfzeile und CamData schon gemittelt 
        with open(target_CamDataFile10_Up, 'w') as outfile:
            with open(CamDataFile10) as infile:
                Camlines=infile.readlines()
                for line in Camlines[0:num_lines_up]:
                    outfile.write(line)
        # Down
        target_CamDataFile10_Down=(measpath+'CDL/'+Sample+'_'+Current+'_'+f'CamData{MaxSS_2}ms_danach.txt')
        num_lines_down = int((sum(1 for line in open(DownFile))+1)/numberMeasurementsPerVoltage) # Anzahl lines in UpFile +1/2 weil Kopfzeile und CamData schon gemittelt
        with open(target_CamDataFile10_Down, 'w') as outfile:
            with open(CamDataFile10) as infile:
                lines=infile.readlines()
                outfile.write(lines[0]) #head
                for line in lines[-num_lines_down+1:]:
                    outfile.write(line)
        # LT
        with open(CamDataFile10) as infile:
            lines=infile.readlines()
        if j==0:
            CamDataFiles10_LT.append(lines[0]) #head
            j=1
        for line in lines[num_lines_up:-num_lines_down+1]:
            CamDataFiles10_LT.append(line)
            
    #100ersetzt 
    target_CamDataFile100_LT=(measpath+'CDL/'+Sample+'_'+f'CamData{MaxSS_1}ms_LT.txt')
    with open(target_CamDataFile100_LT, 'w') as outfile:  
        for line in CamDataFiles100_LT:
                outfile.write(line)
    #10ersetzt
    target_CamDataFile10_LT=(measpath+'CDL/'+Sample+'_'+f'CamData{MaxSS_2}ms_LT.txt')
    with open(target_CamDataFile10_LT, 'w') as outfile:  
        for line in CamDataFiles10_LT:
                outfile.write(line)
    # LT-IV CDL-file
    targetIV_LT=originalIV_LT[0].replace('\\','/').split('/')[-1][:-14] # name new file
    if '_LT' in targetIV_LT:
        targetIV_LT=targetIV_LT.replace('_LT','') # remove LT from name -> problem
    targetIV_LT=measpath+'CDL/'+targetIV_LT+'LT.txt'
    
    with open(targetIV_LT, 'w') as outfile:
        i=0
        for names in originalIV_LT:
            with open(names) as infile:
                if i==0:
                    lines=infile.readlines()
                    if len(lines)%2 == 0: # mit Kopfzeile löschen wenn gerade
                        for line in lines[:-1]:
                           outfile.write(line)
                    else:
                        for line in lines[:]:
                           outfile.write(line)
                else:
                    lines=infile.readlines()
                    if len(lines)%2 == 0:
                        for line in lines[1:-1]:
                           outfile.write(line)
                    else:
                        for line in lines[1:]:
                           outfile.write(line)
            i=1
    return

#%% Heatmap Emision plot
'''
Erstellt eine Heatmap der Emission. Dazu wird ein leeres Bild genommen
und darauf die Daten der Extrapolation geplottet. Radius der Kreise entspricht einfach dem Ausgewertetem

'''

def EmissionHeatMap(ffs,measdir='//fs-01/KETEK-NET/Prozess/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam_LTT_Ausw/', SaveFolder='C:/Users/asc/Desktop/LTT-Auswertungen/', width_point=4, LT=False, LTT=False, font_size=20, Voltage=False, compression=4, SingleCurr=''):
    
    '''
    ffs:            List of measurements
    measdir:        directory
    SaveFolder:     save dir
    width_point:    diameter of Spots (automatically read in for LTT)
    LT:             Lifetime Measurement?
    LTT:            Lifetime Measurement with multiple currents?
    font_size:      font size of text and Axes
    Voltage:        Write current voltage on Image
    compression:    compression of the GIF. 2 means only every second image is shown
    SingleCurr:     only evaluate one current for LTT
    '''

    
    errorlist=[]

    for meas in ffs:
        print(meas)
        
        if LTT:
            # read width_point from AuswParams.txt
            auswparams=glob.glob(measdir+f'{meas}/'+'*.txt')
            auswparams=open(auswparams[0], 'r')
            width_point=[param for param in auswparams.readlines() if 'width_point' in param]
            width_point=int(width_point[0].split()[-1])
            auswparams.close()
        else:
            width_point=5
        
        if '_p' in meas:
            dot='p'
        elif '_n' in meas:
            dot='n'
        else:
            dot='dot'
        
        if LT and LTT and SingleCurr=='':
            Currents= os.listdir(measdir+meas)
            Currents = [curr for curr in Currents if not ('.txt' in curr)]
            Currents = [curr for curr in Currents if not ('CDL' in curr)]
            Currents = [curr for curr in Currents if not ('_XX' in curr)]
            Currents=natsort.natsorted(Currents)
            FloatCurrents=sorted([float(x) for x in Currents])
        elif SingleCurr != '':
            Currents=[SingleCurr]
        else:
            Currents=['']
        #Currents=[Currents[0]]
        for curr in Currents:
            print('Current: '+curr)
            if LTT and SingleCurr=='':
                i=FloatCurrents.index(float(curr))
            else:
                i=0
            MaxSS = os.listdir(measdir+meas+'/'+curr)
            MaxSS = [ss for ss in MaxSS if  ('ersetzt' in ss)]
            MaxSS = [ss[:-7] for ss in MaxSS]
            # MaxSS=[MaxSS[1]]
            for ersetzt in MaxSS:
                print('MaxSS: '+ersetzt)
                savepath=SaveFolder+f'{meas}/{ersetzt}ersetzt/'
                if not os.path.exists(savepath):
                    os.makedirs(savepath)
                locationPointsPerFile=dict()
                
                if LT and LTT:
                    filename=glob.glob(measdir+f'{meas}/{curr}/{ersetzt}ersetzt/'+'*.txt')
                else:
                    filename=glob.glob(measdir+f'{meas}/{ersetzt}ersetzt/'+'*.txt')
                if len(filename)!=1:
                    e=f'{meas}+{curr}+{filename}+Multiple or no Txt-Files in folder'
                    errorlist.append(e)
                    print(e)
                    break
                else:
                    locationPointsPerFile = getDictfromTXTwithSTDproPunkt(filename[0])
                
                if LT:
                    if LTT:
                        files=glob.glob(measdir+f'{meas}/{curr}/*.txt')
                    else:
                        files=glob.glob(measdir+f'{meas}/*.txt')
                    
                    up = [file for file in files if  ('upSwp' in file[-20:])]
                    lt = [file for file in files if  (('LT' in file[-20:]) and not (('upSwp' in file[-20:]) or ('downSwp' in file[-20:])))]
                    down = [file for file in files if  ('downSwp' in file[-20:])]
                    
                    locationPointsPerFile = addVItoDictwithMEAN(up[0], locationPointsPerFile, LT=LT, LTT=LTT)
                    locationPointsPerFile = addVItoDictwithMEAN(lt[0], locationPointsPerFile, LT=LT, LTT=LTT)
                    locationPointsPerFile = addVItoDictwithMEAN(down[0], locationPointsPerFile, LT=LT, LTT=LTT)
    
                    #plotPoints, PiCamLT = plotDictMEAN(locationPointsPerFile, width_point = width_point, LT=LT)
                elif LT and not LTT:
                    files=glob.glob(measdir+f'{meas}/*.txt')
                    
                    up = [file for file in files if  ('upSwp' in file)]
                    lt = [file for file in files if  (('LT' in file) and not (('upSwp' in file) or ('downSwp' in file)))]
                    down = [file for file in files if  ('downSwp' in file)]
                    
                    locationPointsPerFile = addVItoDictwithMEAN(up[0], locationPointsPerFile, LT=LT, LTT=LTT)
                    locationPointsPerFile = addVItoDictwithMEAN(lt[0], locationPointsPerFile, LT=LT, LTT=LTT)
                    locationPointsPerFile = addVItoDictwithMEAN(down[0], locationPointsPerFile, LT=LT, LTT=LTT)
    
                    #plotPoints, PiCamLT = plotDictMEAN(locationPointsPerFile, width_point = width_point, LT=LT)
                else:
                    files=glob.glob(measdir+f'{meas}/*.txt')
                    locationPointsPerFile = addVItoDictwithMEAN(files[0], locationPointsPerFile)
                    #plotPoints = plotDictMEAN(locationPointsPerFile, width_point = width_point, LT=LT)
                
                    
                
                #Samml_B=[]
                #Samml_I=[]
                #for image in [[*locationPointsPerFile][100]]:
                for image in locationPointsPerFile:
                    schonda=[]
                    schonda = [f.name for f in os.scandir(savepath) if f'{image[:-4]}_{i}_I={curr}' in f.name]
                    if schonda:
                        schonda=[]
                        continue
                        
                    PointPositions=[]
                    PointBrightness=[]
                    #SumPixelsLoc=[]
                    #IEmi=[]
                    PointEmission=[]
                    Sequence=''
                    
                    NumberActiveSpots=0
                    for key in locationPointsPerFile[image]:
                        if type(key)==tuple:
                            NumberActiveSpots+=1
                            PointPositions.append(key)
                            #SumPixelsLoc.append(locationPointsPerFile[image]['SumPixelsLoc'])
                            #IEmi.append(locationPointsPerFile[image]['IEmi'])
                            #Samml_B.append(locationPointsPerFile[image][key])
                            PointBrightness.append(locationPointsPerFile[image][key])
                            try:
                                if locationPointsPerFile[image]['IEmi']==0:
                                    PointEmission.append(1e-12)
                                else:
                                    # 25.07.22: SumPixelsAll statt SumPixelsLoc für Sens -> macht mehr Sinn!
                                    PointEmission.append(locationPointsPerFile[image]['IEmi']/locationPointsPerFile[image]['SumPixelsAll']*locationPointsPerFile[image][key])
                            except KeyError:
                                PointEmission.append(1e-12)
                            #Samml_I.append(locationPointsPerFile[image]['IEmi']/locationPointsPerFile[image]['SumPixelsLoc']*locationPointsPerFile[image][key])
                        
                        elif key=='VoltSet_up':
                            Sequence='before LT'
                        elif key=='VoltSet_down':
                            Sequence='after LT'
                        elif key=='Time':
                            Sequence='LT'
                          
                    
                    '''
                    #select image middle of measurement with second highest ss
                    if LTT==True:
                        file=glob.glob(rawdir+f'{meas}/{curr}/*jpg')
                    else:
                        file=glob.glob(rawdir+f'{meas}/*jpg')
                    file=[nr for nr in file if  (file[round(len(file)/2)][-29:-21] in nr)]
                    maxss=[]
                    for ss in range(0,len(file)-1):
                        if file[ss][-17:-8] not in maxss:
                            maxss.append(file[ss][-17:-8])
                    maxss=natsort.os_sorted(maxss)[-2]
                    file=[ss for ss in file if  (maxss in ss)][0]
                    img_subdraw=cv.imread(file,0).astype(np.float64)
                    '''
                    
                    img_subdraw=np.zeros((380, 507)) #linear
                    img_subdraw[img_subdraw==0]=1e-15 #log
                    
                    
                    for xy, emission in zip(PointPositions,PointEmission):
                        #cv.circle(img_subdraw, xy, width_point, 255, thickness=-1)
                        #cv.rectangle(img_subdraw, tuple(map(sum, zip(xy, (width_point,-width_point)))),np.subtract(xy,(width_point,-width_point)), color=scalarMap.to_rgba(float(bright)), thickness=-1)
                        #cv.rectangle(img_subdraw, tuple(map(sum, zip(xy, (width_point,-width_point)))),np.subtract(xy,(width_point,-width_point)), color= math.log(bright,10), thickness=-1)
                        cv.rectangle(img_subdraw, tuple(map(sum, zip(xy, (width_point,-width_point)))),np.subtract(xy,(width_point,-width_point)), color= emission, thickness=-1)
                        
                    
                    # Create figure and add axis
                    fig = plt.figure(figsize=(8,8))
                    ax = fig.add_subplot(111)
                    # Remove x and y ticks
                    ax.xaxis.set_tick_params(size=0)
                    ax.yaxis.set_tick_params(size=0)
                    ax.set_xticks([])
                    ax.set_yticks([])
                    
                    # plot image
                    vmax=math.ceil(math.log10(max(PointEmission))) # take highest brightness and round up to next magnitude
                    # img=ax.imshow(img_subdraw, cmap='magma', extent=(0, 507, 0, 380), vmin=0, vmax=5000) #linear
                    img=ax.imshow(img_subdraw, cmap='magma', extent=(0, 507, 0, 380), norm=LogNorm(vmin=1e-12, vmax=vmax))
                    
                    # Create scale bar (12.4 um pro pixel -> 80,6*12.4=1mm)
                    ax.fill_between(x=[350, 430], y1=[50, 50], y2=[60, 60], color='white')
                    ax.text(x=390, y=20, s='1 mm', va='bottom', ha='center', color='white', size=font_size)
                    
                    # active Spots, Current und type
                    try:
                        IEmi='I = '+"{:.2e}".format(locationPointsPerFile[image]['IEmi'])
                    except KeyError:
                        IEmi='I = '+"{:.2e}".format(0.00e0)
                    
                    ax.text(x=100, y=350, s=IEmi, va='top', ha='center', color='white', size=font_size)
                    if Voltage:
                        if Sequence=='LT':
                            VEmi='Time = '+"{:.0f} min".format(locationPointsPerFile[image]['Time']/60)
                            ax.text(x=100, y=320, s=VEmi, va='top', ha='center', color='white', size=font_size)
                        else:
                            VEmi='V = '+"{:.0f}".format(locationPointsPerFile[image]['VoltEmi'])
                            ax.text(x=100, y=320, s=VEmi, va='top', ha='center', color='white', size=font_size)
                        ax.text(x=390, y=335, s=f'active spots: {NumberActiveSpots}', va='top', ha='center', color='white', size=font_size)
                    else:
                        ax.text(x=390, y=335, s=f'active spots: {NumberActiveSpots}', va='top', ha='center', color='white', size=font_size)
                    ax.text(x=100, y=30, s=f'{dot} type', va='bottom', ha='center', color='white', size=font_size)
                    
                    
                    # Create axis for colorbar
                    cbar_ax = make_axes_locatable(ax).append_axes(position='right', size='5%', pad=0.1)
                    # Create colorbar
                    cbar = fig.colorbar(mappable=img, cax=cbar_ax)
                    cbar.set_label('spot emission (A)', rotation=270, size=font_size,labelpad=font_size )
                    # Edit colorbar ticks and labels
                    #cbar.set_ticks([0, 4])
                    #cbar.set_ticklabels(['0', '50', '100', '150', '200 nm'])
                    ax.set_title(meas[24:]+f'__{Sequence}', size=font_size)
                    cbar.ax.tick_params(labelsize=font_size)
                    
                    if savepath[-1]!='/':
                        savepath=savepath+'/'
                    fig.savefig(savepath+f'{image[:-4]}_{i}_I={curr}_{Sequence}.png', dpi = 100, bbox_inches='tight')
                    plt.close('all')
        #make gif
        for ersetzt in MaxSS:
            savepath=SaveFolder+f'{meas}/'
            ImagePath=SaveFolder+f'{meas}/{ersetzt}ersetzt/'
            name=meas+f'__{ersetzt}ersetzt__comp={compression}'
            MakeGif(ImagePath, savepath, name, compression)

    return

#%% Heatmap Brightness plot
'''
Erstellt eine Heatmap der Emission. Dazu wird ein leeres Bild genommen
und darauf die Daten der Extrapolation geplottet. Radius der Kreise entspricht einfach dem Ausgewertetem

'''

def BrightnessHeatMap(ffs,measdir='//fs-01/KETEK-NET/Prozess/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam_LTT_Ausw/', SaveFolder='C:/Users/asc/Desktop/LTT-Auswertungen/', width_point=4, LT=False, LTT=False, font_size=20, Voltage=False, compression=4, SingleCurr=''):
    
    '''
    ffs:            List of measurements
    measdir:        directory
    SaveFolder:     save dir
    width_point:    diameter of Spots (automatically read in for LTT)
    LT:             Lifetime Measurement?
    LTT:            Lifetime Measurement with multiple currents?
    font_size:      font size of text and Axes
    Voltage:        Write current voltage on Image
    compression:    compression of the GIF. 2 means only every second image is shown
    SingleCurr:     only evaluate one current for LTT
    '''

    
    errorlist=[]

    for meas in ffs:
        print(meas)
        
        if LTT:
            # read width_point from AuswParams.txt
            auswparams=glob.glob(measdir+f'{meas}/'+'*.txt')
            auswparams=open(auswparams[0], 'r')
            width_point=[param for param in auswparams.readlines() if 'width_point' in param]
            width_point=int(width_point[0].split()[-1])
            auswparams.close()
        else:
            width_point=5
        
        if '_p' in meas:
            dot='p'
        elif '_n' in meas:
            dot='n'
        else:
            dot='dot'
        
        if LT and LTT and SingleCurr=='':
            Currents= os.listdir(measdir+meas)
            Currents = [curr for curr in Currents if not ('.txt' in curr)]
            Currents = [curr for curr in Currents if not ('CDL' in curr)]
            Currents = [curr for curr in Currents if not ('_XX' in curr)]
            Currents=natsort.natsorted(Currents)
            FloatCurrents=sorted([float(x) for x in Currents])
        elif SingleCurr != '':
            Currents=[SingleCurr]
        else:
            Currents=['']
        #Currents=[Currents[0]]
        for curr in Currents:
            print('Current: '+curr)
            if LTT and SingleCurr=='':
                i=FloatCurrents.index(float(curr))
            else:
                i=0
            MaxSS = os.listdir(measdir+meas+'/'+curr)
            MaxSS = [ss for ss in MaxSS if  ('ersetzt' in ss)]
            MaxSS = [ss[:-7] for ss in MaxSS]
            # MaxSS=[MaxSS[1]]
            for ersetzt in MaxSS:
                print('MaxSS: '+ersetzt)
                savepath=SaveFolder+f'{meas}/{ersetzt}ersetzt/'
                if not os.path.exists(savepath):
                    os.makedirs(savepath)
                locationPointsPerFile=dict()
                
                if LT and LTT:
                    filename=glob.glob(measdir+f'{meas}/{curr}/{ersetzt}ersetzt/'+'*.txt')
                else:
                    filename=glob.glob(measdir+f'{meas}/{ersetzt}ersetzt/'+'*.txt')
                if len(filename)!=1:
                    e=f'{meas}+{curr}+{filename}+Multiple or no Txt-Files in folder'
                    errorlist.append(e)
                    print(e)
                    break
                else:
                    locationPointsPerFile = getDictfromTXTwithSTDproPunkt(filename[0])
                
                if LT:
                    if LTT:
                        files=glob.glob(measdir+f'{meas}/{curr}/*.txt')
                    else:
                        files=glob.glob(measdir+f'{meas}/*.txt')
                    
                    up = [file for file in files if  ('upSwp' in file[-20:])]
                    lt = [file for file in files if  (('LT' in file[-20:]) and not (('upSwp' in file[-20:]) or ('downSwp' in file[-20:])))]
                    down = [file for file in files if  ('downSwp' in file[-20:])]
                    
                    locationPointsPerFile = addVItoDictwithMEAN(up[0], locationPointsPerFile, LT=LT, LTT=LTT)
                    locationPointsPerFile = addVItoDictwithMEAN(lt[0], locationPointsPerFile, LT=LT, LTT=LTT)
                    locationPointsPerFile = addVItoDictwithMEAN(down[0], locationPointsPerFile, LT=LT, LTT=LTT)
    
                    #plotPoints, PiCamLT = plotDictMEAN(locationPointsPerFile, width_point = width_point, LT=LT)
                elif LT and not LTT:
                    files=glob.glob(measdir+f'{meas}/*.txt')
                    
                    up = [file for file in files if  ('upSwp' in file)]
                    lt = [file for file in files if  (('LT' in file) and not (('upSwp' in file) or ('downSwp' in file)))]
                    down = [file for file in files if  ('downSwp' in file)]
                    
                    locationPointsPerFile = addVItoDictwithMEAN(up[0], locationPointsPerFile, LT=LT, LTT=LTT)
                    locationPointsPerFile = addVItoDictwithMEAN(lt[0], locationPointsPerFile, LT=LT, LTT=LTT)
                    locationPointsPerFile = addVItoDictwithMEAN(down[0], locationPointsPerFile, LT=LT, LTT=LTT)
    
                    #plotPoints, PiCamLT = plotDictMEAN(locationPointsPerFile, width_point = width_point, LT=LT)
                else:
                    files=glob.glob(measdir+f'{meas}/*.txt')
                    locationPointsPerFile = addVItoDictwithMEAN(files[0], locationPointsPerFile)
                    #plotPoints = plotDictMEAN(locationPointsPerFile, width_point = width_point, LT=LT)
                
                    
                
                #Samml_B=[]
                #Samml_I=[]
                #for image in [[*locationPointsPerFile][100]]:
                for image in locationPointsPerFile:
                    schonda=[]
                    schonda = [f.name for f in os.scandir(savepath) if f'{image[:-4]}_{i}_I={curr}' in f.name]
                    if schonda:
                        schonda=[]
                        continue
                        
                    PointPositions=[]
                    PointBrightness=[]
                    #SumPixelsLoc=[]
                    #IEmi=[]
                    #PointEmission=[]
                    Sequence=''
                    
                    NumberActiveSpots=0
                    for key in locationPointsPerFile[image]:
                        if type(key)==tuple:
                            NumberActiveSpots+=1
                            PointPositions.append(key)
                            #SumPixelsLoc.append(locationPointsPerFile[image]['SumPixelsLoc'])
                            #IEmi.append(locationPointsPerFile[image]['IEmi'])
                            #Samml_B.append(locationPointsPerFile[image][key])
                            PointBrightness.append(locationPointsPerFile[image][key])
                            # try:
                            #     if locationPointsPerFile[image]['IEmi']==0:
                            #         PointEmission.append(1e-12)
                            #     else:
                            #         PointEmission.append(locationPointsPerFile[image]['IEmi']/locationPointsPerFile[image]['SumPixelsLoc']*locationPointsPerFile[image][key])
                            # except KeyError:
                            #     PointEmission.append(1e-12)
                            # #Samml_I.append(locationPointsPerFile[image]['IEmi']/locationPointsPerFile[image]['SumPixelsLoc']*locationPointsPerFile[image][key])
                        
                        elif key=='VoltSet_up':
                            Sequence='before LT'
                        elif key=='VoltSet_down':
                            Sequence='after LT'
                        elif key=='Time':
                            Sequence='LT'
                          
                    
                    '''
                    #select image middle of measurement with second highest ss
                    if LTT==True:
                        file=glob.glob(rawdir+f'{meas}/{curr}/*jpg')
                    else:
                        file=glob.glob(rawdir+f'{meas}/*jpg')
                    file=[nr for nr in file if  (file[round(len(file)/2)][-29:-21] in nr)]
                    maxss=[]
                    for ss in range(0,len(file)-1):
                        if file[ss][-17:-8] not in maxss:
                            maxss.append(file[ss][-17:-8])
                    maxss=natsort.os_sorted(maxss)[-2]
                    file=[ss for ss in file if  (maxss in ss)][0]
                    img_subdraw=cv.imread(file,0).astype(np.float64)
                    '''
                    
                    img_subdraw=np.ones((380, 507))

                    
                    
                    for xy, emission in zip(PointPositions,PointBrightness):
                        #cv.circle(img_subdraw, xy, width_point, 255, thickness=-1)
                        #cv.rectangle(img_subdraw, tuple(map(sum, zip(xy, (width_point,-width_point)))),np.subtract(xy,(width_point,-width_point)), color=scalarMap.to_rgba(float(bright)), thickness=-1)
                        #cv.rectangle(img_subdraw, tuple(map(sum, zip(xy, (width_point,-width_point)))),np.subtract(xy,(width_point,-width_point)), color= math.log(bright,10), thickness=-1)
                        cv.rectangle(img_subdraw, tuple(map(sum, zip(xy, (width_point,-width_point)))),np.subtract(xy,(width_point,-width_point)), color= emission, thickness=-1)
                        
                    
                    # Create figure and add axis
                    fig = plt.figure(figsize=(8,8))
                    ax = fig.add_subplot(111)
                    # Remove x and y ticks
                    ax.xaxis.set_tick_params(size=0)
                    ax.yaxis.set_tick_params(size=0)
                    ax.set_xticks([])
                    ax.set_yticks([])
                    
                    #create image
                    vmax=math.ceil(math.log10(max(PointBrightness))) # take highest brightness and round up to next magnitude
                    img=ax.imshow(img_subdraw, cmap='magma', extent=(0, 507, 0, 380), norm=LogNorm(vmin=1e0, vmax=vmax))
                    
                    # Create scale bar (12.4 um pro pixel -> 80,6*12.4=1mm)
                    ax.fill_between(x=[350, 430], y1=[50, 50], y2=[60, 60], color='white')
                    ax.text(x=390, y=20, s='1 mm', va='bottom', ha='center', color='white', size=font_size)
                    
                    # active Spots, Current und type
                    try:
                        IEmi='I = '+"{:.2e}".format(locationPointsPerFile[image]['IEmi'])
                    except KeyError:
                        IEmi='I = '+"{:.2e}".format(0.00e0)
                    
                    ax.text(x=100, y=350, s=IEmi, va='top', ha='center', color='white', size=font_size)
                    if Voltage:
                        if Sequence=='LT':
                            VEmi='Time = '+"{:.0f} min".format(locationPointsPerFile[image]['Time']/60)
                            ax.text(x=100, y=320, s=VEmi, va='top', ha='center', color='white', size=font_size)
                        else:
                            VEmi='V = '+"{:.0f}".format(locationPointsPerFile[image]['VoltEmi'])
                            ax.text(x=100, y=320, s=VEmi, va='top', ha='center', color='white', size=font_size)
                        ax.text(x=390, y=335, s=f'active spots: {NumberActiveSpots}', va='top', ha='center', color='white', size=font_size)
                    else:
                        ax.text(x=390, y=335, s=f'active spots: {NumberActiveSpots}', va='top', ha='center', color='white', size=font_size)
                    ax.text(x=100, y=30, s=f'{dot} type', va='bottom', ha='center', color='white', size=font_size)
                    
                    
                    # Create axis for colorbar
                    cbar_ax = make_axes_locatable(ax).append_axes(position='right', size='5%', pad=0.1)
                    # Create colorbar
                    cbar = fig.colorbar(mappable=img, cax=cbar_ax)
                    cbar.set_label('spot brightness (a.u.)', rotation=270, size=font_size,labelpad=font_size )
                    # Edit colorbar ticks and labels
                    #cbar.set_ticks([0, 4])
                    #cbar.set_ticklabels(['0', '50', '100', '150', '200 nm'])
                    ax.set_title(meas[24:]+f'__{Sequence}', size=font_size)
                    cbar.ax.tick_params(labelsize=font_size)
                    
                    if savepath[-1]!='/':
                        savepath=savepath+'/'
                    fig.savefig(savepath+f'{image[:-4]}_Bright_{i}_I={curr}_{Sequence}.png', dpi = 100, bbox_inches='tight')
                    plt.close('all')
        #make gif
        for ersetzt in MaxSS:
            savepath=SaveFolder+f'{meas}/'
            ImagePath=SaveFolder+f'{meas}/{ersetzt}ersetzt/'
            name=meas+f'__{ersetzt}ersetzt__comp={compression}'
            MakeGif(ImagePath, savepath, name, compression)

    return

#%% Make Gif
from PIL import Image

def MakeGif(ImagePath, SavePath, name, compression=4, Currdep=False):
    '''
    ImagePath:      Path of images
    SavePath:       where to save
    name:           name of the gif
    compression:    number of skipped images in Gif. Maximum Speed is limited by duration = 1 ms
    '''
    images = []
    #ImagePath='C:/Users/asc/Desktop/LTT-Auswertungen/Heatmaps/2022-05-16_220329_W2_V1_pM4/100ersetzt/'
    filenames=glob.glob(ImagePath+'*.png')
    
    for filename in filenames[0::compression]: #nur jedes zweite
        images.append(Image.open(filename))
    
    if SavePath[-1]!='/':
        SavePath=SavePath+'/'
    images[0].save(SavePath+name+'.gif',
                   save_all=True, append_images=images[1:], optimize=False, duration=1, loop=0) # duration 1 ms ist minimum

#%% run detectPoints

import shutil

if __name__ == '__main__':
    
    ffs = ['2022-04-13_08-50_220329_W1_V1_nM2','2022-04-13_13-40_220329_W1_V1_nM3','2022-04-13_16-00_220329_W1_V1_nM4','2022-04-19_08-22_220329_W1_V1_nM5','2022-04-20_08-25_220329_W2_V1_pM1','2022-04-20_09-28_220329_W2_V1_pM1','2022-04-20_13-00_220329_W2_V1_pM2_1uA_1sweep','2022-04-20_13-38_220329_W2_V1_pM2_10uA_1sweep','2022-04-20_14-00_220329_W2_V1_pM2_10uA_1sweep'] 
    
    
    #tars entpacken (überspringt automatisch Ordner, falls Verzeichnis schon entpackt)
    extract_tar(ffs)
    
    for folder in ffs:
        #Messdaten unter:
        path = '//fs-01/KETEK-NET/Prozess/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam/'+folder+'/'
        measfile = glob.glob(path+'*.txt')[0]
        
        #detektierte Punkte und Plots speichern unter:
        # saveunder = 'P:/Produktentwicklung/3.2.12_XRAYSOURCE/Daniela_Ritter/Punktdetektion/'+folder+'_neue_detektion_test2/'
        saveunder = '//fs-01/KETEK-NET/Prozess/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam_Auswertung/'+folder+'/'
        
        # only evaluate this shutter speed (if images were taken with only one ss, set False)
        # shutterSpeed = 10000
        
        save = True                #Save results and figures?
        width_point = 4          #width for sum of pixels (effetive pixel diameter approx. 12.4 um)
        limitBrightness = 5         #limit for detection of points
        numberImagesPerVoltage = 3  #how many images per voltage were taken?
        radiusOfCircles = 5        #circles around detected points 
        numberMeasurementsPerVoltage = 2
        img0_nr = 0
        # saveundernew = saveunder + '/plots_withoutlog_ss=5000/'
        
        # call functions:
        for shutterSpeed in [1000,5000,10000,100000]:
            saveundernew, locationPointsPerFile, filenames = detectPoints(path, saveunder, shutterSpeed, save, width_point, limitBrightness, numberImagesPerVoltage, numberMeasurementsPerVoltage, radiusOfCircles, img0_nr, mesh = False, treshadjust=False)
            if locationPointsPerFile == 'break':
                continue
            # locationPointsPerFile = deleteArtefacts(locationPointsPerFile)
            saveDictSTDproPunkt(saveundernew, locationPointsPerFile, limitBrightness=limitBrightness)
            locationPointsPerFile = addVItoDictwithMEAN(measfile, locationPointsPerFile)
            plotPoints = plotResultsMEAN(locationPointsPerFile, saveundernew, save, limitBrightness=limitBrightness)
            if type(plotPoints) == str: # if measurement was interrupted, a string is returned
                print(plotPoints)
                continue
            centroid_activeSpots(locationPointsPerFile, saveundernew)
            
        #replace overexp points and plot results again
        
        locationPointsPerFile = replaceOverexposedPointsSTDproPunkt(saveunder, path, ss=[1000,5000,10000,100000])
        saveDictSTDproPunkt(saveunder+'100ersetzt/', locationPointsPerFile, limitBrightness=limitBrightness)
        plotPoints = plotResultsMEAN(locationPointsPerFile, saveunder+'100ersetzt/', save=True)
        if type(plotPoints) == str: # if measurement was interrupted, a string is returned
                print(plotPoints)
                continue
        centroid_activeSpots(locationPointsPerFile, saveunder+'100ersetzt/')
        
        locationPointsPerFile = replaceOverexposedPointsSTDproPunkt(saveunder, path, ss=[1000,5000,10000])
        saveDictSTDproPunkt(saveunder+'10ersetzt/', locationPointsPerFile, limitBrightness=limitBrightness)
        plotPoints = plotResultsMEAN(locationPointsPerFile, saveunder+'10ersetzt/', save=True)
        if type(plotPoints) == str: # if measurement was interrupted, a string is returned
                print(plotPoints)
                continue
        centroid_activeSpots(locationPointsPerFile, saveunder+'10ersetzt/')
        
        # locationPointsPerFile = replaceOverexposedPointsSTDproPunkt(saveunder, path, ss=[10000,100000,500000])
        # saveDictSTDproPunkt(saveunder+'500ersetzt/', locationPointsPerFile, limitBrightness=limitBrightness)
        # plotPoints = plotResultsMEAN(locationPointsPerFile, saveunder+'500ersetzt/', save=True)
        # if type(plotPoints) == str: # if measurement was interrupted, a string is returned
        #         print(plotPoints)
        #         continue
        # centroid_activeSpots(locationPointsPerFile, saveunder+'500ersetzt/')
        
        # locationPointsPerFile = replaceOverexposedPointsSTDproPunkt(saveunder, path, ss=[250000,500000])
        # saveDictSTDproPunkt(saveunder+'500ersetzt/', locationPointsPerFile, limitBrightness=limitBrightness)
        # plotPoints = plotResultsMEAN(locationPointsPerFile, saveunder+'500ersetzt/', save=True)
        # if type(plotPoints) == str: # if measurement was interrupted, a string is returned
        #         print(plotPoints)
        #         continue
        # centroid_activeSpots(locationPointsPerFile, saveunder+'500ersetzt/')
        
        #Messdaten in Auswertungs-Odner kopieren
        shutil.copy2(measfile, saveunder)
        # compareShutterSpeed(saveunder, path)


#%% get dict from TXT and plot
'''
if __name__ == '__main__':
        # for ss in [1000,10000]:
            
        folder = '2021-08-16_10-14_210127_W2_V2_nL11_Array_Neue_Cam'
        path = 'P:/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam/'+folder+'/'
        saveunder = 'P:/Produktentwicklung/3.2.12_XRAYSOURCE/Daniela_Ritter/Punktdetektion/'+folder+'_TEST/ss=10000'
        measfile = glob.glob(path+'*.txt')
        
        filename = glob.glob(saveunder+'/'+'auswertung*.txt')
        
        locationPointsPerFile = getDictfromTXTwithSTDproPunkt(filename[0])
        locationPointsPerFile = addVItoDictwithMEAN(measfile[0], locationPointsPerFile)
        
        # plotPoints = plotResults(locationPointsPerFile, path, saveunder=saveunder, save=True)
        
        #replace overexp points and plot results again
        # folder = '2021-08-16_10-14_210127_W2_V2_nL11_Array_Neue_Cam_TEST'
        # saveunder = 'P:/Produktentwicklung/3.2.12_XRAYSOURCE/Daniela_Ritter/Punktdetektion/'+folder+'/'
        # path = 'P:/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam/'+folder+'/'
        # locationPointsPerFile = replaceOverexposedPointsSTDproPunkt(saveunder, path, ss_low=1000, ss_high=10000)
        # # plotPoints = plotResults(locationPointsPerFile, path, saveunder+'plots/', save=True)
        # saveDictSTDproPunkt(saveunder+'plots/', locationPointsPerFile, reverse=False)
'''
