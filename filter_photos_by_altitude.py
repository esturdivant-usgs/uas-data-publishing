"""
Written to filter rededge photos into keep folder. Works recursively.

@esturdivant-usgs
"""
#%%
import pandas as pd
import os
import subprocess
import shutil

# Only used flights 11-32, i.e. photos collected on 8/7 and 8/8. RedEdge surveying on 8/6 (flights 2–10) had many gaps.
imgdir = r"/Volumes/stor/Projects/UAS_SfM/2018_046_FA_GreatMarsh/micasense"
min_altitude = 70
max_altitude = 95

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
