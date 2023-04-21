# -*- coding: utf-8 -*-
"""
Created on Mon Aug  9 10:11:26 2021

@author: dar
"""

import tarfile 
import glob, os
import shutil
import time

def howlong(starttime):
    endtime = time.time()
    duration = endtime-starttime
    print(f'took {duration} s!')
    
def extract_tar(folders, path = '//fs-01/KETEK-NET/Prozess/Produktentwicklung/3.2.12_XRAYSOURCE/Messdaten/PiCam/', LTT=False):
    print('start extracting tar...')
    j = 1
    for files in folders:
        if LTT == True:
            k = 1
            currents = os.listdir(path+files)
            for curr in currents:
                subfolder = files+'/' + curr + '/'
                #check if already extracted...
                jpgfiles = glob.glob(path+subfolder+'*.jpg', recursive = False)
                if len(jpgfiles) > 0:
                    print(f'folder {files} already extracted, continue with next one...')
                    print(f'done current {k}/{len(currents)} in folder {j}/{len(folders)}')
                    k+=1
                    continue
                tarfiles = glob.glob(path+subfolder+'*.tar.gz', recursive = False)
                i = 1
                for fname in tarfiles:
                    start = time.time()
                    tar = tarfile.open(fname, "r:gz")
                    tar.extractall(path+subfolder)
                    tar.close()
                    print(f'extracting {curr} {i}/{len(tarfiles)}'), howlong(start)
                    start = time.time()
                    pictures = glob.glob(path+subfolder+'media/ramdisk/*.jpg', recursive = False)
                    for pics in pictures:
                        try:
                            shutil.move(pics, path+subfolder) 
                        except OSError as e:
                            print(e)
                            continue
                    print('moving'), howlong(start)
                    shutil.rmtree(path+subfolder+'media/')
                    print(f'done tar {i}/{len(tarfiles)}')
                    i+=1
                print(f'done folder {j}/{len(folders)*len(currents)}')
                k += 1
        
        else:
            files = files+'/'
            #check if already extracted...
            jpgfiles = glob.glob(path+files+'*.jpg', recursive = False)
            if len(jpgfiles) > 0:
                print(f'folder {files} already extracted, continue with next one...')
                print(f'done folder {j}/{len(folders)}')
                j+=1
                continue
            tarfiles = glob.glob(path+files+'*.tar.gz', recursive = False)
            i = 1
            for fname in tarfiles:
                start = time.time()
                tar = tarfile.open(fname, "r:gz")
                tar.extractall(path+files)
                tar.close()
                print('extracting'), howlong(start)
                start = time.time()
                pictures = glob.glob(path+files+'media/ramdisk/*.jpg', recursive = False)
                for pics in pictures:
                    try:
                        shutil.move(pics, path+files) 
                    except OSError as e:
                        print(e)
                        continue
                print('moving'), howlong(start)
                shutil.rmtree(path+files+'media/')
                print(f'done tar {i}/{len(tarfiles)}')
                i+=1
            print(f'done folder {j}/{len(folders)}')
        j += 1


if __name__ == '__main__':

    folders = ['2022-05_03_220329_W1_V1_nM9_Besch_2']  #type or copy in folders directly
    #folders = ['LTT_Test_ASC_2 - Kopie']  #type or copy in folders directly
    # folders = glob.glob(path+'2021_08_09*', recursive = False)  #or find all folders of one specific day
    
    extract_tar(folders, LTT=True)