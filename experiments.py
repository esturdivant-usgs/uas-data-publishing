# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.interpolate import interp1d
from PIL import Image, ExifTags
# import datetime as dt
import pytz
from datetime import datetime as DT
import pandas as pd
from lxml import etree
from dateutil import parser

#%% This is where the elements of the xml (gpx) file are defined
namespace = {'def': 'http://www.topografix.com/GPX/1/1'}
tfmt_exif = '%Y:%m:%d %H:%M:%S' #2017-05-04T14:14:12-04:00
tfmt_gpx = '%Y-%m-%dT%H:%M:%S-04:00' #2017-05-04T14:14:12-04:00
iso_fmt="%Y%m%dT%H%M%SZ"

#%% User input
# Enter name of .gpx file and folder with associated images
homedir = r'/Users/emilysturdivant/Desktop/uas_data'
logfile = os.path.join(homedir, 'f8.gpx')
imagefolder = os.path.join(homedir, 'f8')

<<<<<<< HEAD
survey_id = '2016-010FA'
uas_id = 'u031'
fc_id = 'f04r01'

#%% Functions
def dt_to_UTCval(dtstr, fmt, local_tz='US/Eastern'):
    time = (pytz.timezone(local_tz).localize(DT.strptime(e.text, tfmt_gpx), is_dst=None)
                                .astimezone(pytz.utc)
                                .timestamp())
    return(time)
=======
# Enter time offset (seconds) so that imagetime + offset = log time
toff = -4.*3600. # The GPS data is being read in local time, the images are stamped with UTC

#%% Functions
def dt_to_UTCval(dtstr, in_fmt, local_tz='US/Eastern'):
    # convert datetime string in local time to timestamp in UTC
    timeval = (pytz.timezone(local_tz)
                    .localize(DT.strptime(e.text, in_fmt), is_dst=None)
                    .astimezone(pytz.utc)
                    .timestamp())
    return(timeval)
>>>>>>> origin/master

def gpx_tag_to_pdseries(tree, namespace, tag):
    elist = tree.xpath('./def:trk//def:trkpt//def:'+tag, namespaces=namespace)
    ser = pd.Series([e.text for e in elist], name=tag)
    return(ser)


#%% Parse GPX and extract components from the trackpoints (ignore the waypoints)
tree = etree.parse(logfile)

# latitude and longitude
elist = tree.xpath('./def:trk//def:trkpt',namespaces=namespace)
lonlat = pd.DataFrame([e.values() for e in elist], columns=['lat', 'lon'])

# time
tag = 'time'
elist = tree.xpath('./def:trk//def:trkpt//def:'+tag, namespaces=namespace)
<<<<<<< HEAD
dt = [parser.parse(e.text) for e in elist] # parser will detect time zones
dtz = [dti.astimezone(pytz.utc) for dti in dt]

dtz = [time.mktime(dti.utctimetuple()) for dti in dt]
dtz = [pytz.timezone(local_tz).localize(DT.strptime(e.text, tfmt_gpx), is_dst=None)
                            .astimezone(pytz.utc) for e in elist]
t = [dt.timestamp() for dt in img_dt]
gpxdf = lonlat.join(pd.DataFrame({'time_utc':dtz}))
                                    #, 'time_epoch':t}))
# gpxdf = gpxdf.join(pd.Series(t, name='time_epoch'))
gpxdf
=======
local_tz='US/Eastern'
t = [dt_to_UTCval(e.text, tfmt_gpx, local_tz=local_tz) for e in elist]
t = pd.Series(t, name=tag)
gpxdf = gpxdf.join(t)
>>>>>>> origin/master

# all other tags
taglist = ['ele', 'ele2', 'course', 'roll', 'pitch', 'mode']
for tag in taglist:
    gpxdf = gpxdf.join(gpx_tag_to_pdseries(tree, namespace, tag))

# Export CSV
gpxdf.to_csv(os.path.splitext(logfile)[0]+'_gpx.csv', index=False)

#%% PLOT!
plt.plot(gpxdf.lat,gpxdf.lon,'.')
plt.show()

# print first and last times in .gpx file
start_gpxtime = gpxdf.time_epoch.iloc[0]
end_gpxtime = gpxdf.time_epoch.iloc[-1]
start_gpxtime
end_gpxtime
print("{} from {} to {}".format(logfile, start_gpxtime, end_gpxtime))
start_gpxtime = gpxdf.time_utc.iloc[0]
end_gpxtime = gpxdf.time_utc.iloc[-1]
start_gpxtime
end_gpxtime
print("{} from {} to {}".format(logfile, start_gpxtime, end_gpxtime))


#%% Work with images
# List all JPEGS in imagefolder
flist=[os.path.join(imagefolder,f) for f in os.listdir(imagefolder) if f.endswith('.jpg') or f.endswith('.JPG')]
print("Found {} images in {}.".format(len(flist),imagefolder))

# Get filename and DateTimeOriginal of each photo
#FIXME: how to get tzinfo from EXIF? Looks like these were recorded in UTC...
# raw_dt = [Image.open(f)._getexif()[36867] for f in flist]
dt = [DT.strptime(Image.open(f)._getexif()[36867], tfmt_exif) for f in flist]
imgdf = pd.DataFrame({'orig_name': [os.path.basename(f) for f in flist],
                      'time_utc': dt,
                      'time_epoch': [t.timestamp() for t in dt],
                      'time_iso': [t.strftime(iso_fmt) for t in dt]})
# dt = [parser.parse(Image.open(f)._getexif()[36867]) for f in flist] # parser changed day to 23 instead of 13
# img_dt = [dti.astimezone(pytz.utc) for dti in dt] # no need since already seems to be in UTC
# # img_dt = [(pytz.timezone(local_tz).localize(DT.strptime(Image.open(f)._getexif()[36867], tfmt_exif), is_dst=None).astimezone(pytz.utc)) for f in flist]
imgdf.head()

# Export CSV
imgdf.to_csv(imagefolder+'_stage1.csv', index=False)

# Rename photos
#TODO move/copy them first? / don't run if the names have already been changed...
for idx, row in imgdf.iterrows():
    img = row.orig_name
    t = row.time_iso
    new_name = "{}_{}_{}_{}_{}".format(survey_id, uas_id, fc_id, t, img) # ->
    os.rename(os.path.join(imagefolder, img), os.path.join(imagefolder, new_name))

# print first and last image name and times
print("First... file: {}, time: {}".format(imgdf.filename.iloc[0],imgdf.time.iloc[0]))
print("Last... file: {}, time: {}".format(imgdf.filename.iloc[-1],imgdf.time.iloc[-1]))
print("{} from {} to {}".format(logfile, start_gpxtime, end_gpxtime))

# combine .gpx data into array
data = np.zeros((3,(len(dn))))
data[0,:]=gpxdf.lat
data[1,:]=gpxdf.lon
data[2,:]=gpxdf.ele
print(np.shape(data),np.shape(dn))

# set up interpolation
set_interp = interp1d(dn, data, kind='linear')

# array for storing lat, lon, and elevation for each image
img_data = np.ones((3,len(img_name)))*np.NaN


dn = np.array(gpxdf.time)
img_dn = np.array(imgdf.time_epoch)
img_name = np.array(imgdf.orig_name)
img_data = np.ones((3,len(img_name)))*np.NaN
for i in range(len(img_name)):
    if(img_dn[i]>=dn[0] and img_dn[i]<=dn[-1] ):
        # image time is within bounds of .gpx data
        img_data[:,i] = set_interp(img_dn[i])
    else:
        # image time is not within .gpx data
        print('No GPS data for {} {}'.format(img_name[i],img_dt[i]))

# use where to find image times within bounds of gps times
ser = imgdf.time_utc
ser.where(ser >= start_gpxtime and ser <= start_gpxtime, np.nan)
df1 = gpxdf
df2 = imgdf
matches = df1[df1.time_epoch.isin(df2.time_epoch)] # All rows in df1 that have a match in df2.
matches.head()

start_gpxtime = gpxdf.time_utc.iloc[0]
end_gpxtime = gpxdf.time_utc.iloc[-1]
start_gpxtime
end_gpxtime
imgdf.time_utc.iloc[0]
no = imgdf.time_utc <= start_gpxtime


# loop through the images and interpolate .gpx data
for idx, row in imgdf.iterrows():
    if row.time_epoch >= gpxdf.time.iloc[0] and row.time_epoch <= gpxdf.time.iloc[-1]:
        img_data[:,idx] = set_interp(row.time_epoch)
    else:
        # image time is not within .gpx data
        print('Image {} not acquired between {} and {}'.format(row.orig_name))


# make a bare-bones trackline and overlay image locations
plt.plot(lon[:],lat[:],'-')
plt.plot(data[1,:],data[0,:],'.r')
plt.show()
# print out file name, time, and data
# TODO - write a .csv file with columns in the in the correct order for Photoscan
for i in range(10):
    print("{}, {}, {}, {}".format(img_name[i],img_dt[i],img_data[0,i],img_data[1,i],img_data[2,i]))
