import os
import parse
import shutil



ReadFormat = "{}_rPiHQCam-{}_ss={}_{}.jpg"
ConvertFormat = "LT{:08d}_ss={:09d}_{:03d}"


ImgDir = r"<Drive>\<Input Pics folderpath here>"
OutDir = r"<Drive>\<Output Pics folderpath here>",
if not os.path.exists(OutDir):
  os.makedirs(OutDir)

fList = os.listdir(ImgDir)
outFNames = list()


for file in fList:
    if not file.endswith(os.path.splitext(ReadFormat)[1]): # Be sure only scanning filetype of interest! Sometimes a 0kb tar.gz can be within the pictures
      print("Non-matching filetype detected: " + file)
      fList.remove(file)
    else:
      _parsed = parse.parse(ReadFormat, file)
      _nums = list()
      for _iPrsd in range(1, len(_parsed.fixed)):
        _nums.append(int(_parsed[_iPrsd]))
      outFNames.append(str.format(ConvertFormat + ".jpg", _nums[0], _nums[1], _nums[2]))

for _iFile in range(len(fList)):
  src = os.path.join(ImgDir, fList[_iFile])
  dst = os.path.join(OutDir, outFNames[_iFile])
  shutil.copy(src, dst)