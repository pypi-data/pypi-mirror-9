#!/usr/bin/python
# Filename: common.py
#
# Code by Martin Jucker, distributed under an MIT License
# Any publication benefitting from this piece of code should cite
# Jucker, M 2014. Scientific Visualisation of Atmospheric Data with ParaView.
# Journal of Open Research Software 2(1):e4, DOI: http://dx.doi.org/10.5334/jors.al
#
# Python interface for ParaView (www.paraview.org). Provides functions neede by all other files
# in pv_atmos.

##### needed modules: paraview.simple, math #########################
from paraview.simple import *
from math import pi,log10


##### common functions ##############################################
def Cart2Spherical(radius=1.0, src=GetActiveSource()):
    """Convert Cartesian to spherical coordinates.
        
        Assumes X coordinate is longitude, Y coordinate latitude, Z coordinate vertical.
        Adds Calculator filter to the pipeline.
        radius -- radius of the sphere, where coordZ = basis
        src    -- filter in pipeline to attach to
        """
    calc=Calculator(src)
    strRad = str(radius)
    try:
        calc.Function = 'iHat*('+strRad+'+coordsZ)*cos(coordsY*'+strPi+'/180)*cos(coordsX*'+strPi+'/180) + jHat*('+strRad+'+coordsZ)*cos(coordsY*'+strPi+'/180)*sin(coordsX*'+strPi+'/180) + kHat*('+strRad+'+coordsZ)*sin(coordsY*'+strPi+'/180)'
    except:
        calc.Function = 'iHat*'+strRad+'*cos(coordsY*'+strPi+'/180)*cos(coordsX*'+strPi+'/180) + jHat*'+strRad+'*cos(coordsY*'+strPi+'/180)*sin(coordsX*'+strPi+'/180) + kHat*'+strRad+'*sin(coordsY*'+strPi+'/180)'
    calc.CoordinateResults = 1
    RenameSource('Cart2Spherical',calc)
    return calc