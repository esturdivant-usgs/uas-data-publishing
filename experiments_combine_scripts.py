# -*- coding: utf-8 -*-
"""
@author: esturdivant@usgs.gov

Requirements:
    - ExifTool by Phil Harvey must be installed

Script derived from update_imagefiles.py, csherwood-usgs\UASTools, sackerman-usgs\SEABOSStools, sackerman-usgs\EXIF_updater

1. gpx to dataframe, export as csv
2.

other 'candies' on the to-do list:
- rename tlog file based on start time
- interpolate trackpts and indicate positions that were interpolated vs. original

"""
# update_imagefiles: Check that the language for this file is set in Atom and that you have a Jupyter kernel installed for it.
import os
import subprocess
import datetime as DT
import pytz
import pandas as pd
import pyproj
# test_read_exif_and_gpx:
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ExifTags
from datetime import datetime
from lxml import etree

#%% Parse GPX file
path = '.'
glist=[os.path.join(path,g) for g in os.listdir(path) if (g.lower.endswith('.gpx'))]
gpxfile = glist[0]
gpxfile = r'C:\Users\esturdivant.GS\Documents\GitHub\UASTools\solo2.gpx'
tree = etree.parse(gpxfile)
# how many tracks in this file (none)?
# trks = tree.findall("{%s}trk" % namespace)
# print(trks)


# This works -
elist = tree.xpath('./def:trk//def:trkpt',namespaces=namespace)
lonlat = [e.values() for e in elist]
lonlat = np.array(lonlat,dtype="float")
pd.DataFrame(lonlat)
print(lonlat[0])
print(np.shape(lonlat))

# This works
elist = tree.xpath('./def:trk//def:trkpt//def:time',namespaces=namespace)
fmt = '%Y-%m-%dT%H:%M:%S-04:00' #2017-05-04T14:14:12-04:00
time = [datetime.strptime(e.text, fmt) for e in elist]
print(time[0],time[-1], np.shape(time))


plt.plot(lonlat[:,1],lonlat[:,0])
plt.show()
