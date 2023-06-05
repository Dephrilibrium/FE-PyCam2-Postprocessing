

def GetXYArea_XYX2Y2(XYTuple:tuple, pxWidth:int, pxHeight:int):
  """Calculates the coordinates of the left upper (x1,y1) and right lower corner (x2,y2) for the given width and height around the XY center-coordinate.

  Args:
      XYTuple (tuple): Centercoordinates.
      pxWidth (int): Target width.
      pxHeight (int): Target height.

  Returns:
      x1,y1,x2,y2: x1, y1 = left upper corner; x2, y2 = right lower corner
  """
  halfWLen = int(pxWidth/2)
  halfHLen = int(pxHeight/2)

  x = XYTuple[0] - halfWLen
  y = XYTuple[1] - halfHLen
  x2 = x + pxWidth
  y2 = y + pxHeight
  return x, y, x2, y2


def GetXYArea_XYWH(XYTuple:tuple, pxWidth:int, pxHeight:int):
  """Calculates the coordinates of the left upper corner (x1,y1) and the image width and height (w,h)

  Args:
      XYTuple (tuple): Centercoordinates.
      pxWidth (int): Target width.
      pxHeight (int): Target height.

  Returns:
      x1,y1,w,h: x1, y1 = left upper corner; w,h = width and height of the image.
  """
  x1, y1, x2, y2 = GetXYArea_XYX2Y2(XYTuple=XYTuple, pxWidth=pxWidth, pxHeight=pxHeight)
  return x1, y1, x2-x1, y2-y1


def GetCircleArea_XYX2Y2(Circle, pxSidelen:int, AddPxTolerance:bool):
  """Determines the corner-coordinates (left upper, right lower) of a square around the circle-center.

  Args:
      Circle (circle): Circle object
      pxSidelen (int): Sidelength of a square surrounding the circle-center.
      AddPxTolerance (bool): If enabled, the circles radius is added to pxSidelen.

  Returns:
      x1,y1,x2,y2: Returns the coordinate of the left upper (x1,y1) and the right lower (x2,y2) corners.
  """
  if AddPxTolerance == True:
    pxSideLen = pxSidelen + 2*Circle["radius"]
    return GetXYArea_XYX2Y2(XYTuple=Circle["center"], pxWidth=pxSideLen, pxHeight=pxSideLen)
  else:
    pxSideLen = + pxSidelen #+ 2*Circle["radius"]
    return GetXYArea_XYX2Y2(XYTuple=Circle["center"], pxWidth=pxSideLen, pxHeight=pxSideLen)



def GetCircleArea_XYWH(Circle, pxSidelen:int, AddPxTolerance:bool):
  """Determines the left upper corner-coordinate (x1,y1) and the image size (w,h) of a square around the circle-center.

  Args:
      Circle (_type_): Circle object.
      pxSidelen (int): Sidelength of the square around the circle-center.
      AddPxTolerance (bool): If enabled, the circle radius is added to pxSidelen.

  Returns:
      x1,y1,w,h: Left upper corner-coordinate (x1,y1) and the image size (w,h).
  """
  x1, y1, x2, y2 = GetCircleArea_XYX2Y2(Circle=Circle, pxSidelen=pxSidelen, AddPxTolerance=AddPxTolerance)
  return x1, y1, x2-x1, y2-y1
