# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import os
import copy
from scipy.interpolate import interp1d
from PIL import Image, ExifTags
# import datetime as dt
import pytz
from datetime import datetime as DT
import pandas as pd
from lxml import etree

#%% This is where the elements of the xml (gpx) file are defined
namespace = {'def': 'http://www.topografix.com/GPX/1/1'}
tfmt_exif = '%Y:%m:%d %H:%M:%S' #2017-05-04T14:14:12-04:00
tfmt_gpx = '%Y-%m-%dT%H:%M:%S-04:00' #2017-05-04T14:14:12-04:00

#%% User input
# Enter name of .gpx file and folder with associated images
# logfile = r'G:\2017-06-12_Duck_UAS\gpx\f5.gpx'
# imagefolder = r'G:\2017-06-12_Duck_UAS\jpeg\f5'
logfile = r'/Users/emilysturdivant/GitHub/uas-data-publishing/solo2.gpx'
imagefolder = r'/Users/emilysturdivant/GitHub/uas-data-publishing/solo2.gpx'

# Enter time offset (seconds) so that imagetime + offset = log time
toff = -4.*3600. # The GPS data is being read in local time, the images are stamped with UTC

#%% Functions
def dt_to_UTCval(dtstr, in_fmt, local_tz='US/Eastern'):
    # convert datetime string in local time to timestamp in UTC
    eastern = pytz.timezone(local_tz)
    timeval = eastern.localize(DT.strptime(e.text, in_fmt), is_dst=None).astimezone(pytz.utc).timestamp()
    return(timeval)

def gpx_tag_to_pdseries(tree, namespace, tag):
    elist = tree.xpath('./def:trk//def:trkpt//def:'+tag, namespaces=namespace)
    ser = pd.Series([e.text for e in elist], name=tag)
    return(ser)


#%% Parse GPX and extract components from the trackpoints (ignore the waypoints)
tree = etree.parse(logfile)

# latitude and longitude
elist = tree.xpath('./def:trk//def:trkpt',namespaces=namespace)
lonlat = pd.DataFrame([e.values() for e in elist], columns=['lat', 'lon'])
gpxdf = lonlat

# time
tag = 'time'
elist = tree.xpath('./def:trk//def:trkpt//def:'+tag, namespaces=namespace)
# time = pd.DataFrame([dt_to_UTCval(e.text, tfmt_gpx, local_tz='US/Eastern') for e in elist], columns=[tag])
# time = [eastern.localize(DT.strptime(e.text, tfmt_gpx), is_dst=None).astimezone(pytz.utc).timestamp() for e in elist]
gpxdf = gpxdf.join(pd.DataFrame([dt_to_UTCval(e.text, tfmt_gpx, local_tz='US/Eastern') for e in elist], columns=[tag]))

# all other tags
taglist = ['ele', 'ele2', 'course', 'roll', 'pitch', 'mode']
for tag in taglist:
    gpxdf = gpxdf.join(gpx_tag_to_pdseries(tree, namespace, tag))

#%% PLOT!
plt.plot(gpxdf.lat,gpxdf.lon,'.')
plt.show()

#%% Work with images
# get a list of image files
flist=[os.path.join(imagefolder,f) for f in os.listdir(imagefolder) if f.lower.endswith('.jpg')]
print("Found {} images in {}.".format(len(flist),imagefolder))

img_name = [] # list of file names
img_dn = []   # array of Matlab times
for f in flist:
    # read the image time stamps and add the time correction toff
    dtstr = Image.open(f)._getexif()[36867]
    t = dt_to_UTCval(dtstr, tfmt_exif, local_tz='US/Eastern') + toff # add time offset in seconds
    img_name.append(f)
    img_dn.append(t)

imgdf = pd.DataFrame({'img_name': flist})
imgtime = pd.Series(dt_to_UTCval(Image.open(df.img_name)._getexif()[36867], tfmt_exif, local_tz='US/Eastern') + toff, name='img_time')
imgdf = imgdf.join(imgdf, imgtime)

# print first and last image name and times
print("{}, {}, {}".format(img_name[0],img_dt[0],img_dn[0]))
print("{}, {}, {}".format(img_name[-1],img_dt[-1],img_dn[-1]))
# print first and last times in .gpx file
print("{} from {} {} to {} {}".format(logfile,time[0],dn[0],time[-1],dn[-1]))
