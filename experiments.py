# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import os
import copy
from scipy.interpolate import interp1d
from PIL import Image, ExifTags
import datetime as dt
import pandas as pd
from lxml import etree

#%% This is where the elements of the xml (gpx) file are defined
namespace = {'def': 'http://www.topografix.com/GPX/1/1'}

#%% User input
# Enter name of .gpx file and folder with associated images
# logfile = r'G:\2017-06-12_Duck_UAS\gpx\f5.gpx'
# imagefolder = r'G:\2017-06-12_Duck_UAS\jpeg\f5'
logfile = r'/Users/emilysturdivant/GitHub/uas-data-publishing/solo2.gpx'
imagefolder = r'/Users/emilysturdivant/GitHub/uas-data-publishing/solo2.gpx'

# Enter time offset (seconds) so that imagetime + offset = log time
toff = -4.*3600. # The GPS data is being read in local time, the images are stamped with UTC

#%%
# How to get datetime as single value: dt.timestamp(), only python3.3 and above
dtn=dt.datetime(2012, 2, 13, 6, 56, 2, 619000)
dtn.timestamp()


#%% Parse .gpx
# parse GPX
tree = etree.parse(logfile)

# Extract components from the trackpoints (ignore the waypoints)
# latitude and longitude
elist = tree.xpath('./def:trk//def:trkpt',namespaces=namespace)
lonlat = [e.values() for e in elist]
lonlat = pd.DataFrame(lonlat, columns=['lat', 'lon'])

# time
elist = tree.xpath('./def:trk//def:trkpt//def:'+tag, namespaces=namespace)
time = [dt.datetime.strptime(e.text, fmt).timestamp() for e in elist]
time = pd.DataFrame(time, columns=['time'])

# Elevation
tag = 'ele'
elist = tree.xpath('./def:trk//def:trkpt//def:'+tag,namespaces=namespace)
ele = [e.values() for e in elist]
ele = pd.DataFrame(ele, columns=['ele'])

pd.DataFrame(columns={'lat':lonlat[:0]})



def get_tagvalue_from_xml(tree, namespace, tag, fmt):
    elist = tree.xpath('./def:trk//def:trkpt//def:'+tag, namespaces=namespace)
    ls = [dt.datetime.strptime(e.text, fmt).timestamp() for e in elist]
    df = pd.DataFrame(ls, columns=[tag])
    return(df)




tag = 'time'
fmt = '%Y-%m-%dT%H:%M:%S-04:00' #2017-05-04T14:14:12-04:00
df = get_tagvalue_from_xml(tree, namespace, tag, fmt)
df
