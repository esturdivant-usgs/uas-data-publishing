# -*- coding: utf-8 -*-
"""
Portions of this script were derived from UpdatePhotoEXIFv3a.py, originally created by VeeAnn Cross (USGS)
and based on the code from the script MCZM_writeexif_2_readfile.py

Requirements:
    - ExifTool by Phil Harvey must be installed

It should be possible to perform all actions below only using ExifTool. E.g.
    exiftool -d %Y%m%dT%H%M%SZ.%%e "-filename<DateTimeOriginal" imgdir
"""
import os
import subprocess
from datetime import datetime
import pytz

imgdir = r"/Users/esturdivant/Documents/Projects/UAS_BlackBeach/Data_publishing/data_release/Images/images_working2"
fan = "2016-010-FA"
survey_id = fan.replace("-","")
uas_id = ""
fc_id = "f01c01"

# Tags that will be identical for all images in the folder
tagvalues = {}
tagvalues['imgdir'] = imgdir
tagvalues['artist'] = "Woods Hole Analytics, in collaboration with Marine Biological Laboratory and the U.S. Geological Survey"
tagvalues['credit'] = tagvalues['artist']
tagvalues['contact'] = "WHSC_data_contact@usgs.gov"
tagvalues['comment'] = "Low-altitude aerial photograph of Black Beach, Falmouth, MA from survey 2016-010-FA (https://cmgds.marine.usgs.gov/fan_info.php?fa={}).".format(fan)
tagvalues['keywords'] = "Black Beach, Great Sippewissett Marsh, Falmouth, Massachusetts, {}, UAS, nadir, USGS".format(fan)
tagvalues['copyright'] = "Public Domain. Please credit {credit}".format(**tagvalues)

# Write to EXIF
# cmd = """exiftool -Artist="{artist} " {imgdir}""".format(**tagvalues)
# subprocess.check_call(cmd, shell=True)
# cmd2 = """exiftool -Credit="{credit} " -Contact="{contact} " {imgdir}""".format(**tagvalues)
# subprocess.check_call(cmd2, shell=True)
# #jpeg comment
# cmd3 = """exiftool -comment="{comment} " {imgdir}""".format(**tagvalues)
# subprocess.check_call(cmd3, shell=True)
# #iptc info
# cmd4 = """exiftool -sep ", " -keywords="{keywords} " {imgdir}""".format(**tagvalues)
# subprocess.check_call(cmd4, shell=True)
# #xmp info
# cmd6 = """exiftool -Caption="{comment} " {imgdir}""".format(**tagvalues)
# subprocess.check_call(cmd6, shell=True)
# #EXIF info
# cmd7 = """exiftool -Copyright="{copyright} " {imgdir}""".format(**tagvalues)
# subprocess.check_call(cmd7, shell=True)
# #iptc info
# cmd8 = """exiftool -CopyrightNotice="{copyright} " {imgdir}""".format(**tagvalues)
# subprocess.check_call(cmd8, shell=True)
# #iptc info
# cmd9 = """exiftool -Caption-Abstract="{comment} " {imgdir}""".format(**tagvalues)
# subprocess.check_call(cmd9, shell=True)
# #exif info - software such as Picasso use this as the caption
# cmd10 = """exiftool -ImageDescription="{comment} " {imgdir}""".format(**tagvalues)
# subprocess.check_call(cmd10, shell=True)

cmd = """exiftool -Artist="{artist} " -Credit="{credit} " -Contact="{contact} " -comment="{comment} " -sep ", " -keywords="{keywords} " -Caption="{comment} " -Copyright="{copyright} " -CopyrightNotice="{copyright} " -Caption-Abstract="{comment} " -ImageDescription="{comment} " {imgdir}""".format(**tagvalues)
subprocess.check_call(cmd, shell=True)


def exifGPS_to_csv(imgdir, csv_name=''):
    # Write CSV of image locations
    if len(csv_name) < 1:
        csv_name = "imagelocations_{}.csv".format(os.path.basename(imgdir))
    cmd = "cd {}".format(imgdir)
    cmd1 = """exiftool -csv -filename -DateTimeOriginal -GPSLongitude -GPSLatitude -GPSAltitude -n {} > {}""".format(imgdir, csv_name)
    subprocess.check_call(cmd, shell=True)
    subprocess.check_call(cmd1, shell=True)
    return(csv_name)

# Convert datetime and GPS values to desired units (UT, NAD83, meters)
# Change column labels

def rename_image_from_exif(imgdir, img, survey_id, uas_id, fc_id):
    # save original filename to EXIF and rename file based on
    fullimg = os.path.join(imgdir, img)
    isotime = isotime_from_exif(fullimg)
    cmd2 = """exiftool -OriginalFileName="{} " -overwrite_original {}""".format(img, fullimg)
    subprocess.check_call(cmd2, shell=True)
    # new_img = "{}_{}{}".format(survey_id, isotime, os.path.splitext(img)[1])
    new_img = "{}_{}_{}_{}_{}".format(survey_id, uas_id, fc_id, isotime, img) # -> nnnnnnnnFA_Unnn_fnncnn_yyyymmddThhmmssZ_origname.ext
    os.rename(fullimg, os.path.join(imgdir, new_img))
    return new_img

def isotime_from_exif(fullimg, iso_fmt="%Y%m%dT%H%M%SZ"):
    # extract datetime from EXIF and format for filename
    in_fmt = "%Y:%m:%d %H:%M:%S"
    cmd1 = """exiftool -s3 -DateTimeOriginal {}""".format(fullimg) # return values only
    dtstr = subprocess.check_output(cmd1, shell=True)[:-1]
    dt = datetime.strptime(dtstr, in_fmt)
    dt = dt.replace(tzinfo=pytz.timezone('US/Eastern'))
    dtz = dt.astimezone(pytz.utc)
    isotime = dtz.strftime(iso_fmt)
    return isotime

results = []
for f in os.listdir(imgdir):
    if f.lower().endswith('.jpg'):
        rename_image_from_exif(imgdir, f, survey_id, uas_id, fc_id)
exifGPS_to_csv(imgdir)
