#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: esturdivant@usgs.gov
"""
import os
import pyproj
import pandas as pd


in_file = r"/Users/esturdivant/Documents/Projects/Ontario/GreigSt/2017-07-14-SODUSA.txt"
# Enter benchmark position
bm_position = {'el_hgt':40.992, 'ortho_hgt':76.120, 'northing': 4793031.067, 'easting': 339787.326}

# Get points as dataframe
df = pd.read_csv(in_file, squeeze=True, header=None)
df.columns = ['ID', 'Northing', 'Easting', 'Ortho_height', 'Elevation', 'Label']

# Calculate difference from benchmark to SODUSREF
df[]

df.where(df.Label=='SODUSREF')

df

import sys
sys.version
