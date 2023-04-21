import numpy as np
import math


def cart2pol_pi(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    
    if(abs(rho) < 1e-3):
      rho = 0
    if abs(phi) < 1e-3: # less than millidegree
      phi = 0

    return(rho, phi)

def pol2cart_pi(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)

    if abs(x) < 1e-3:
      x = 0
    if abs(y) < 1e-3:
      y = 0
    
    return(x, y)
  

def cart2pol_deg(x, y):
  (rho, phi) = cart2pol_pi(x, y)
  deg = math.degrees(phi)
  return(rho, deg)

def pol2cart_deg(rho, phi):
  rad = math.radians(phi)
  (x, y) = pol2cart_pi(rho, rad)
  return(x, y)
  

