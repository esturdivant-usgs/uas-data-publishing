# -*- coding: utf-8 -*-
"""
Portions of this script were derived from UpdatePhotoEXIFv3a.py, originally created by VeeAnn Cross (USGS)
and based on the code from the script MCZM_writeexif_2_readfile.py

"""
import os
import subprocess

imgdir = r"/Users/esturdivant/Documents/Projects/UAS_BlackBeach/data_release/Images/images_working"

# imagefolder = self.entryJPGS.get()
# fullimg = os.path.join(imagefolder, img)
# tagvalues['fullimg'] = fullimg.replace('\\','/')

# Tags that will be identical for all images in the folder
tagvalues = {}
tagvalues['imgdir'] = imgdir
tagvalues['artist'] = "Woods Hole Analytics, in collaboration with Marine Biological Laboratory and the U.S. Geological Survey"
tagvalues['credit'] = tagvalues['artist']
tagvalues['contact'] = "WHSC_data_contact@usgs.gov"
tagvalues['comment'] = "Low-altitude aerial photograph of Black Beach, Falmouth, MA from survey 2016-010-FA (https://cmgds.marine.usgs.gov/fan_info.php?fa=2016-010-FA)."
tagvalues['keywords'] = "Black Beach, Great Sippewissett Marsh, Falmouth, Massachusetts, 2016-010-FA, UAS, nadir, USGS"
tagvalues['copyright'] = "Public Domain. Please credit {credit}".format(**tagvalues)

# Write to EXIF
cmd = """exiftool -Artist="{artist} " {imgdir}""".format(**tagvalues)
subprocess.check_call(cmd, shell=True)
cmd2 = """exiftool -Credit="{credit} " -Contact="{contact} " {imgdir}""".format(**tagvalues)
subprocess.check_call(cmd2, shell=True)
#jpeg comment
cmd3 = """exiftool -comment="{comment} " {imgdir}""".format(**tagvalues)
subprocess.check_call(cmd3new, shell=True)
#iptc info
cmd4 = """exiftool -sep ", " -keywords="{keywords} " {imgdir}""".format(**tagvalues)
subprocess.check_call(cmd4, shell=True)
#xmp info
cmd6 = """exiftool -Caption="{comment} " {imgdir}""".format(**tagvalues)
subprocess.check_call(cmd6, shell=True)
#EXIF info
cmd7 = """exiftool -Copyright="{copyright} " {imgdir}""".format(**tagvalues)
subprocess.check_call(cmd7, shell=True)
#iptc info
cmd8 = """exiftool -CopyrightNotice="{copyright} " {imgdir}""".format(**tagvalues)
subprocess.check_call(cmd8, shell=True)
#iptc info
cmd9 = """exiftool -Caption-Abstract="{comment} " {imgdir}""".format(**tagvalues)
subprocess.check_call(cmd9, shell=True)
#exif info - software such as Picasso use this as the caption
cmd10 = """exiftool -ImageDescription="{comment} " {imgdir}""".format(**tagvalues)
subprocess.check_call(cmd10, shell=True)

# Change image file names
# extract datetime from EXIF

#testing on single image
from datetime import datetime
import pytz

imgdir = r"/Users/esturdivant/Documents/Projects/UAS_BlackBeach/data_release/Images/images_working"
fullimg = os.path.join(imgdir, 'DJI_0183.JPG')
fan = "2016-010-FA"
survey_id = fan.replace("-","")

cmd11 = """exiftool -OriginalFileName {}""".format(fullimg)
subprocess.check_output(cmd11, shell=True)

def image_name_from_exif(fullimg, survey_id):
    from datetime import datetime
    import pytz

    in_fmt = "%Y:%m:%d %H:%M:%S"
    out_fmt = "{}_%Y%m%dT%H%M%SZ".format(survey_id)

    cmd = """exiftool -s3 -DateTimeOriginal {}""".format(fullimg) # return values only
    dtstr = subprocess.check_output(cmd, shell=True)[:-1]
    cmd11 = """exiftool -OriginalFileName="{photo} " {fullimg}""".format(**tagvalues)
    subprocess.check_call(cmd11, shell=True)
    dt = datetime.strptime(dtstr, in_fmt)
    dt = dt.replace(tzinfo=pytz.timezone('US/Eastern'))
    dtz = dt.astimezone(pytz.utc)
    imgname = dtz.strftime(out_fmt)
    return imgname

suffix = os.path.splitext(fullimg)[1]

for root, dirs, files in os.walk(imgdir):
    for photo in files: #photo includes .jpg extension # List photos from those in folder
        fullimg = os.path.join(root, photo)
        new_imgname = image_name_from_exif(fullimg, survey_id)
        new_fullimg = os.path.join(root, new_imgname, os.path.splitext(photo)[1])

        os.rename(fullimg, new_fullimg)
