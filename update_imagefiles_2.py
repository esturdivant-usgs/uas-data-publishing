#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: esturdivant@usgs.gov

This will 1) copy photos matching an altitude constraint into keep folder,
2) add values to image headers to prep for publication, and 3) rename the
images to a standard scheme. It was modified from update_imagefiles.py for
use with tif files from MicaSense RedEdge.

Improvements:
    - Micasense will be organized into folders by flight. So this needs to be able to get the flight number dynamically from the folder name. Or the flight number portion of the output image filename should be removed.

Requirements:
    - ExifTool by Phil Harvey must be installed

Code status: Incomplete as of 10/9/2018. The function should all be functioning correctly. Some of them have been changed from functions with the same names in update_imagefiles.py. The execution section is very rough. I was trying to revise it to work for micasense photos, but then switched to working on the ipython notebook on Seth's github. 
"""
import os
import subprocess
import datetime as DT
import pytz
import pandas as pd
# import pyproj
import shutil
import glob

#%% Thoughts about workflow structure
# Call ExifTool once to get all the values. Then work with values to... change filename,

#%% Functions
def write_WHSC_exiftags(imgdir, credit, comment, keywords, contact, recursive=False):
    # Tags that will be identical for all images in the folder
    tagvalues = {}
    tagvalues['imgdir'] = imgdir
    tagvalues['credit'] = credit
    tagvalues['artist'] = credit
    tagvalues['contact'] = contact
    tagvalues['comment'] = comment
    tagvalues['keywords'] = keywords
    tagvalues['copyright'] = "Public Domain. Please credit {credit}".format(**tagvalues)
    # Write to EXIF
    if recursive:
        cmd = """exiftool -Artist="{artist} " -Credit="{credit} " -Contact="{contact} " -comment="{comment} " -sep ", " -keywords="{keywords} " -Caption="{comment} " -Copyright="{copyright} " -CopyrightNotice="{copyright} " -Caption-Abstract="{comment} " -ImageDescription="{comment} " -r {imgdir}""".format(**tagvalues)
    else:
        cmd = """exiftool -Artist="{artist} " -Credit="{credit} " -Contact="{contact} " -comment="{comment} " -sep ", " -keywords="{keywords} " -Caption="{comment} " -Copyright="{copyright} " -CopyrightNotice="{copyright} " -Caption-Abstract="{comment} " -ImageDescription="{comment} " {imgdir}""".format(**tagvalues)
    subprocess.check_call(cmd, shell=True)
    return(True)

def rename_image_from_exif(imgdir, img, survey_id, uas_id, flight_id, cam_id):
    # save original filename to EXIF and rename file
    fullimg = os.path.join(imgdir, img)
    isotime = exifTime_to_iso(fullimg, local_tz = 'US/Eastern')

    # Save original filename to OriginalFileName tag
    cmd2 = """exiftool -OriginalFileName="{} " -overwrite_original {}""".format(img, fullimg)
    subprocess.check_call(cmd2, shell=True)

    # Rename file using os.rename()
    # cmd2 = """exiftool "-FileName<CreateDate" -d "%Y%m%dT%H%M%SZ.%%e" DIR""".format(img, fullimg) # use exiftool to rename... not fully developed
    new_img = "{}_{}{}{}_{}_{}".format(survey_id, uas_id, flight_id, cam_id, isotime, img) # -> nnnnnnnnFA_Unnn_fnncnn_yyyymmddThhmmssZ_origname.ext
    os.rename(fullimg, os.path.join(imgdir, new_img))
    return new_img

def rename_images(imgdir, survey_id, uas_id, flight_id, cam_id):
    for f in os.listdir(imgdir):
        if f.lower().endswith('.jpg') or f.lower().endswith('.tif') or f.lower().endswith('.dng'):
            rename_image_from_exif(imgdir, f, survey_id, uas_id, flight_id, cam_id)
    return

def exifTime_to_iso(fullimg, local_tz='US/Eastern', iso_fmt="%Y%m%dT%H%M%SZ"):
    # extract datetime from EXIF, convert to UTC, and format for filename
    cmd1 = """exiftool -s3 -DateTimeOriginal {}""".format(fullimg) # return values only
    dtstr = subprocess.check_output(cmd1, shell=True)[:-1]
    in_fmt = '%Y:%m:%d %H:%M:%S'
    dt = DT.datetime.strptime(dtstr, in_fmt)
    eastern = pytz.timezone(local_tz)
    dt = eastern.localize(dt, is_dst=None)
    dtz = dt.astimezone(pytz.utc)
    isotime = dtz.strftime(iso_fmt)
    return(isotime)

def geo2utm(df, lat_col = 'Latitude', lon_col = 'Longitude', gcs='wgs', pcs='utm19'):
    # Add column of GPS values converted from geographic to projected CS to desired units (UT, NAD83, meters)
    if gcs == 'wgs':
        geo = pyproj.Proj(init='epsg:4326') # WGS84
    elif gcs == 'nad':
        geo = pyproj.Proj(init='epsg:4269') # NAD83
    if pcs == 'utm19':
        utm = pyproj.Proj(init='epsg:26919') # utm zone 19N

    x_col = 'Easting'
    y_col = 'Northing'

    in_y = df[lat_col].tolist()
    in_x = df[lon_col].tolist()

    out_x, out_y = pyproj.transform(p1=geo, p2=utm, x=in_x, y=in_y)

    df[x_col] = out_x
    df[y_col] = out_y
    return(df)

def pcs2geo(df, x_col = 'Easting', y_col = 'Northing', gcs='wgs', pcs='utm19'):
    # Add column of GPS values converted from projected to geographic CS to desired units (UT, NAD83, meters)
    if gcs == 'wgs':
        geo = pyproj.Proj(init='epsg:4326') # WGS84
    elif gcs == 'nad':
        geo = pyproj.Proj(init='epsg:4269') # NAD83
    if pcs == 'utm19':
        utm = pyproj.Proj(init='epsg:26919') # utm zone 19N

    in_y = df[y_col].tolist()
    in_x = df[x_col].tolist()

    lon, lat = pyproj.transform(p1=utm, p2=geo, x=in_x, y=in_y)

    df[lon_col] = lon
    df[lat_col] = lat
    return(df)

def format_csv_for_pub(exif_csv, out_csv, dt_colname = 'DateTimeOriginal', in_dt_fmt= "%Y:%m:%d %H:%M:%S", in_tz='US/Eastern'):
    # Import CSV with datetime parsed
    dateparse = lambda x: pd.datetime.strptime(x, in_fmt)
    df = pd.read_csv(exif_csv, parse_dates=[dt_colname], date_parser=dateparse)
    # split datetime column
    dt = pd.DatetimeIndex(df[dt_colname], tz=pytz.timezone(in_tz)).tz_convert(pytz.utc)
    df.insert(2, 'Date', dt.date)
    df.insert(3, 'Time', dt.time)
    # add columns with projected coordinates
    df.drop(['SourceFile', dt_colname], axis=1, inplace=True, errors='ignore')
    df.rename(index=str, columns={'GPSLatitude':'Latitude', 'GPSLongitude':'Longitude', 'GPSAltitude':'Altitude_ft'}, inplace=True)
    df = geo2utm(df, 'Latitude', 'Longitude', gcs='wgs', pcs='utm19')
    # Export to CSV
    df.to_csv(out_csv, index=False)
    return(df)

def filter_photos_by_altitude(imgdir, min_altitude, max_altitude):
    # Print altitudes to CSV and convert CSV to pandas dataframe
    exif_csv = "altitudes_{}.csv".format(os.path.basename(imgdir))
    cmd1 = """exiftool -csv -GPSAltitude -n -r {} > {}""".format(imgdir, os.path.join(imgdir, exif_csv))
    subprocess.check_call(cmd1, shell=True)
    df = pd.read_csv(os.path.join(imgdir, exif_csv))

    # Send photos with target altitudes to 'keep' folder.
    keepdir = os.path.join(imgdir, 'keep_alt{}to{}'.format(min_altitude, max_altitude))
    keepct = 0
    rct = 0
    for index, row in df.iterrows():
        fpath = row.SourceFile
        fname = os.path.basename(row.SourceFile)
        alt = row.GPSAltitude
        if alt < min_altitude or alt > max_altitude:
            rct += 1
        else:
            try:
                shutil.move(fpath, os.path.join(keepdir, fname))
                keepct += 1
            except:
                pass
    print("Number of image files copied to {}: {}".format(keepdir, keepct))
    return(keepdir)


#%% Input Values
imgdir = r"/Users/esturdivant/Desktop/photos_test"
fan = "2018-046-FA"
survey_id = fan.replace("-","") # Use the Field Activity Number without the dashes
uas_id = ""
cam_id = "m01" # intended for 6 digits indicating flight and camera ID.

# Values for image headers
credit = "USGS"
comment = "Multispectral low-altitude aerial photograph from survey {0} (https://cmgds.marine.usgs.gov/fan_info.php?fa={0}).".format(fan)
keywords = "Great Marsh, Sandy Neck, Barnstable County, Massachusetts, {}, UAS, nadir, multispectral, USGS".format(fan)
contact = "WHSC_data_contact@usgs.gov"

min_altitude = 70
max_altitude = 95

#%% Execute
flight_id = 'X'
for root, dirs, files in os.walk(imgdir):
    if os.path.basename(root).startswith('f'):
        flight_id = os.path.basename(root)
    for d in dirs:
        print(root + ' --- ' + d)# print d in dirs:
        print('flight num: {}'.format(flight_id))
        idir = os.path.join(root,d)
        imagelist = glob.glob(os.path.join(idir,'*.tif'))
        if len(imagelist):
            rename_images(idir, survey_id, uas_id, flight_id, cam_id)

dt = [datetime.datetime.strptime(Image.open(f)._getexif()[36867], fmt) for f in flist]
imgdf = pd.DataFrame({'orig_name': [os.path.basename(f) for f in flist],
                      'time_utc': dt,
                      'time_epoch': pd.to_datetime(dt, format = tfmt_exif).astype(np.int64) // 10**9,
                      'time_iso': [t.strftime(iso_fmt) for t in dt],
                      'new_name': np.nan,
                      'lon': np.nan,
                      'lat': np.nan,
                      'ele': np.nan,
                      'interpolated': 0},
                        columns=['new_name', 'lat', 'lon', 'ele', 'time_utc', 'orig_name',
                                 'time_epoch', 'time_iso', 'interpolated'])


rename_images(imgdir, survey_id, uas_id, flight_id, cam_id)
write_WHSC_exiftags(imgdir, credit, comment, keywords, contact, recursive=False)

# alternative rename_images, which could allow for recursive call
cmd1 = """exiftool -s3 -DateTimeOriginal {}""".format(fullimg) # return values only
new_img = "{}_{}{}{}_{}_{}".format(survey_id, uas_id, flight_id, cam_id, isotime, img) # -> nnnnnnnnFA_Unnn_fnncnn_yyyymmddThhmmssZ_origname.ext
cmd2 = """exiftool "-FileName<CreateDate" -d "{}_{}{}{}_%Y%m%dT%H%M%SZ.%%e" DIR""".format(survey_id, uas_id, flight_id, cam_id, img, fullimg) # use exiftool to rename... not fully developed

dtstr = subprocess.check_output(cmd1, shell=True)[:-1]

# Delete originals
cmd = "exiftool -delete_original {}".format(imgdir)
subprocess.check_call(cmd, shell=True)


imgdir = filter_photos_by_altitude(imgdir, min_altitude, max_altitude)
