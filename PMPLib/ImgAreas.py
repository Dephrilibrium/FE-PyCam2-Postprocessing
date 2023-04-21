

def GetXYArea_XYX2Y2(XYTuple, pxWidth, pxHeight):
  halfWLen = int(pxWidth/2)
  halfHLen = int(pxHeight/2)

  x = XYTuple[0] - halfWLen
  y = XYTuple[1] - halfHLen
  x2 = x + pxWidth
  y2 = y + pxHeight
  return x, y, x2, y2


def GetXYArea_XYWH(XYTuple, pxWidth, pxHeight):
  x1, y1, x2, y2 = GetXYArea_XYX2Y2(XYTuple=XYTuple, pxWidth=pxWidth, pxHeight=pxHeight)
  return x1, y1, x2-x1, y2-y1


def GetCircleArea_XYX2Y2(Circle, pxTolerance, AddPxTolerance):
  # halfTol = int(pxTolerance / 2)
  if AddPxTolerance == True:
    # x = Circle["center"][0] - Circle["radius"] - halfTol
    # y = Circle["center"][1] - Circle["radius"] - halfTol
    # x2 = x + 2*Circle["radius"] + pxTolerance
    # y2 = y + 2*Circle["radius"] + pxTolerance
    pxSideLen = pxTolerance + 2*Circle["radius"]
    return GetXYArea_XYX2Y2(XYTuple=Circle["center"], pxWidth=pxSideLen, pxHeight=pxSideLen)
  else:
    # x = Circle["center"][0] - halfTol
    # y = Circle["center"][1] - halfTol
    # x2 = x + pxTolerance
    # y2 = y + pxTolerance
    pxSideLen = + pxTolerance #+ 2*Circle["radius"]
    return GetXYArea_XYX2Y2(XYTuple=Circle["center"], pxWidth=pxSideLen, pxHeight=pxSideLen)

  # return x, y, x2, y2



def GetCircleArea_XYWH(Circle, pxTolerance, AddPxTolerance):
  x1, y1, x2, y2 = GetCircleArea_XYX2Y2(Circle=Circle, pxTolerance=pxTolerance, AddPxTolerance=AddPxTolerance)
  return x1, y1, x2-x1, y2-y1
