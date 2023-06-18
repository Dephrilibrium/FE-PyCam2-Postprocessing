
# FE-PyCam2-Postprocessing

## Description
This project contains a bunch of python scripts and libs to reconvert and extract data from images which were taken by [FE-PyCam2][PyCam-Server].



----

## Requirements
The tools and scripts were developed on a windows machine using:

- IDE: [Visual Studio Code][vscode] (developed with system-installer, not tested with user-installer)
- IDE-Extensions: Microsoft Python (added as .vscode recommendation, so a popup should appear when the project is opened by VSCode)
- Python: [Python3][python] (developed with Python3.11)
- Python-packages: ```pip install numpy matplotlib opencv-python glob pickle natsort``` (if a package is missing, python let you know which package it is, when you run the script. Just install it then using ```pip```)
- Compression-Tool: [7zip][7zip] (installed to standard-path; alternatively add the executable folder to PATH and modify the ```xCmd = "7z.exe"``` variable -> How to add an executable to PATH: [Microsoft][MicrosoftPATH] or [StackOverflow][StackOverflowPATH])



----

## How to use
Assuming that a data-set created by the [PyCam2-Server][PyCam-Server] and [FEMDAQv2][FEMDAQ] exists, the scripts explained chronical as they are typically carried out.
To run a script, check out [Get started Tutorial for Python][HowToPython]. There is the creation of a virtual environment described, which is not a need.

**Note:** Some of the following scripts scan their paths iteratively and searches automatically for a picture-folder and electrical measurement data. The latter ones are ```*.dat``` files and were created with [FEMDAQv2][FEMDAQ], which is not a need to use. Just search the corresponding script-codeline which checks for the electrical measurement-data file extension and modify it to match with your case.


### _CompressTars_2_7z.py
As we saving our measurements firstly on a server, we compress the archives first, to use less file-size and less amount of files.

The ```wds``` variable can assigned by arbitrary parent folders which are scanned iteratively to the lowest nested folder-level. It searches for archive-types the PyCam2-Server creates (```*.tar```) and compresses them as ```*.7z``` file, normally reducing the size by more than a factor of 10:
| Uncompressed (46.7GB) | Compressed (4GB) |
|-----------------------|-------------------|
| ![Uncompressed](https://github.com/Dephrilibrium/FE-PyCam2-Postprocessing/assets/89015665/73af95c0-21e7-4c30-8a5a-99fab72a73ab) | ![Compressed](https://github.com/Dephrilibrium/FE-PyCam2-Postprocessing/assets/89015665/da989c77-40aa-4108-b439-678996f1743e) |




### _PiCamUnpacker.py
After the files are copied to the data extraction PC, we unpack the compressed archives to get the ```*.raw``` files.

In the ```workDirs``` variable contains the target scan-paths, which can be parent paths (iterates nested folders). Thereby, the script checks each folder if there are ```*.7z``` or ```*.tar.gz``` files, which are then unpacked into ```<current directory>/<xPath>``` (default: ```xPath = "Pics"```). The new folders contain then the ```*.tar``` files, which are extracted first and deleted after the successful extraction.


### _ConvertBayerToGrayscale.py
This scripts takes again a folderpath-vector ```wds``` which are iterated recursively to the deepest nested subfolder. Thereby, the script checks the current scan-folder contains a folder which contains files ending with the ```bayerType (default: "raw")```. When such a folder is detected, it starts with the conversion from RAW Bayer-Images into 16bit grayscale images of the ```demosaicType (default: "png")```. They can now be opened with a image viewer (e.g. Windows Photo Viewer or [IrfanView][IrfanView])

**Note:** When you try to convert high resolution images (big filesize) and a lot of them, you may run out of RAM causing an out-of-memory-exception which crashes the script (in my case no message-dialog popped up, it just crashed!). For that, the option ```ConvertImageByImage (default: False)``` was added to convert one set of RAW images is loaded to create exactly one mean image. After the mean image is dumped, the RAW images RAM is freed.


### _PreClipImages.py - (optional)
As you can now check the images by opening them. If you find out, that you can shrink down the pixel size of the images, you can clip the images before applying the data-extraction algorithm to it. With IrfanView a rectangle can be drawn around the area of interest. The tool shows to the offset of the left upper corner as well as the width and height of the drawn rectangle. These values can directly applied to the ```imgWin (order: [x1,y1,w,h])``` variable defining the position and size of the clip-window.
This is carried out for all folders added to ```wds```, which are again checked recursively. Thereby, the script checks if a folder contains electrical measurement-data (```.dat``` files, created by [FEMDAQv2][FEMDAQ]) and a picture-folder (```default: "Pics"``` folder). If that is true, the script enters the picture-folder, opens all images (```*.png``` and ```*.jpg```), clips them and overrides them.


### PiMagePro (DataExtraction).py
PiMagePro (PMP) scans the folderpath ```parentDir``` recursively and checks for an existing picture-folder (```picDir (default: "Pics")```) as well as for electrical data (```*.dat``` files, created by [FEMDAQv2][FEMDAQ]). When a measurement folder is detected, it starts by extracting the existing SS by analyzing the filenames. For that, checkout PMPLib/ImgFileHandling.py:
```python
SS_Index        (default: 2)
BlackFormat     (default: "{}_rPiHQCam2-BlackSubtraction_ss={}_{}.{}"
ImageFormat     (default: "{}_rPiHQCam2-{}_ss={}_{}.{}")
```

Based on the options you choosed, the data extraction algorithm runs through and saves the results as serialized binary dumps (pythons ```pickle``` package), image collections and copies of your electrical data (```".png"```, ```".dat"```, ```".swp"```, ```".resistor"```) in the same path as ```parentDir```, but with a replaced substring to separate in- and output data (```saveDir = str.replace(parentDir, <substring of parentDir>, <replacement for substring>```). The originally subfolderstructure of the input ```parentDir``` is copied to the output ```saveDir```, e.g.:

```python
parentDir   = r"C:\<Inputpath>\<To my actual>\Measurements\<sample XY>" # Input-Directory
saveDir     = str.replace(parentDir, "Measurements", "Evaluation")
parentDir   = r"C:\<Inputpath>\<To my actual>\Evaluation\<sample XY>"   # Output-Directory
```


### Add_ResistorFile.py - (optional)
When our [FEAR-System][FEAR16] is used to get electrical data, the ```*.dat``` files contain the measured currents as the drop voltages at a shunt-resistor, which actually defines the measurement-range. Therefore the Y-values of the ```*.dat``` file needs to be divided by the resistance-value of the shunt resistor.

Therefore, this script scans recursively through the given ```parentDir```, looking for a subdirectory ```picDir (default: "Pics")``` and electrical measurement-data (```*.dat``` files). When such a folder is detected, the script creates a ```value.resistor``` file, only containing the resistance-value, so that the used resistance can be loaded automatically during the data-evaluation, when having measurements with different shunt-resistors.


### RenameFileExtension.py - (optional)
This script can rename the image archives file extension. Reason is, that during development, once the compression option was added, the [PyCam2-Server][PyCam-Server] used for compressed and uncompressed files the ```*.tar.gz``` extension. As the archives were not compressed, it was neccessary to rename the file-extension back to ```*.tar```.


### RenameFiles.py - (optional)
If you want to exchange some data sets with other groups, which are may using custom file-formats, this script can be used to rename files from one to another format, e.g.:
```python
ReadFormat      = "{}_rPiHQCam-{}_ss={}_{}.jpg"     # Arbitrary input format
ConvertFormat   = "LT{:08d}_ss={:09d}_{:03d}"       # Arbitrary output format
ImgDir          = r"C:\Users\ham38517\Downloads\220725 PiCam Einzelemitter\Messungen\03 1h I500nA U1400V\220804_163908 (#3)\Pics"       # Input-folder
OutDir          = r"C:\Users\ham38517\Downloads\220725 PiCam Einzelemitter\Messungen\03 1h I500nA U1400V\220804_163908 (#3)\Pics Ketek" # Output-folder
```
where the script scans for the ```ReadFormat``` named files in the ```ImgDir``` folder, and saves them with the ```ConvertFormat``` into the ```OutDir```.


----

README by haum


[PyCam-Server]: https://github.com/Dephrilibrium/FE-PyCam2-Server.git
[vscode]:https://code.visualstudio.com/
[python]: https://www.python.org/downloads/
[7zip]: https://www.7-zip.org/
[MicrosoftPATH]: https://learn.microsoft.com/en-us/previous-versions/office/developer/sharepoint-2010/ee537574(v=office.14)
[StackOverflowPATH]: https://learn.microsoft.com/en-us/previous-versions/office/developer/sharepoint-2010/ee537574(v=office.14)
[IrfanView]: https://www.irfanview.com/
[FEMDAQ]: https://github.com/Dephrilibrium/FEMDAQv2
[HowToPython]: https://code.visualstudio.com/docs/python/python-tutorial
[FEAR16]: https://github.com/Dephrilibrium/FE-FEAR16v2
