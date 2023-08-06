from __future__ import division,print_function
import os,os.path
import numpy as np
import pkg_resources
import logging

from scipy.interpolate import LinearNDInterpolator as interpnd
try:
    import pandas as pd
except ImportError:
    pd = None
    
import pickle

from .isochrone import Isochrone

#DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
DATADIR = os.getenv('ISOCHRONES',
                    os.path.expanduser(os.path.join('~','.isochrones')))
if not os.path.exists(DATADIR):
    os.mkdir(DATADIR)

MASTERFILE = '{}/parsec.h5'.format(DATADIR)
TRI_FILE = '{}/parsec.tri'.format(DATADIR)

####### utility function to generate master dataframe from raw files ######

