#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: esturdivant
"""
import os, pandas
import matplotlib.pyplot as plt


sourcedir = r'/Users/esturdivant/Documents/Projects/UAS_BlackBeach/working/working_Python'
filename = os.path.join(sourcedir,'feature_extraction_success.csv')
with open(filename, 'rb') as csvfile:
    df = pandas.read_csv(csvfile,squeeze=True)

# Plot all 6 variations
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlabel('Avg. spacing of point cloud (cm)', fontsize = 12)
ax.set_ylabel('Success rate (%)', fontsize = 12)
xaxis = [15, 35, 50]
ax.plot(xaxis, df['low-res shl'], color='b', linestyle='--', linewidth = 2, marker='|', markersize=8, markeredgewidth=2)
ax.plot(xaxis, df['high-res shl'], color='b', linestyle='-', linewidth = 2, marker='o', markeredgewidth=0)
ax.plot(xaxis, df['low-res dhi'], color='m', linestyle='--', linewidth = 2, marker='o', markeredgewidth=0)
ax.plot(xaxis, df['high-res dhi'], color='m', linestyle='-', linewidth = 2, marker='o', markeredgewidth=0)
ax.plot(xaxis, df['low-res dlo'], color='k', linestyle='--', linewidth = 2, marker='o', markeredgewidth=0)
ax.plot(xaxis, df['high-res dlo'], color='k', linestyle='-', linewidth = 2, marker='o', markeredgewidth=0)
ax.axis([10, 55, 0, 100]) # range of both axes: [x min, x max, y min, y max]
#ax.axis('equal')
ax.axis('scaled')
plt.show()

fig.savefig("fig2.png")
fig.clear()

# Experiment with vlines
fig = plt.figure(figsize=(12, 6))
vax = fig.add_subplot(121)
vax.set_xlabel('Avg. spacing of point cloud (cm)', fontsize = 16)
vax.set_ylabel('Success rate (%)', fontsize = 16)
#vax.plot(xaxis, df['low-res shl'], '^')
vax.vlines(xaxis, [0], df['low-res shl'])
vax.set_xlabel('time (s)')
vax.set_title('Vertical lines demo')
plt.show()


linestyle = {"linestyle":"", "linewidth":0, "markeredgewidth":2, "elinewidth":2, "capsize":4}
for f in ['MLC_Z_SEG','MLC_RGB_SEG','MLC_Z','MLC_RGB']:
    upper = df['{}.2'.format(f)]
    lower = df['{}.1'.format(f)]
    mean1 = df[f]
    se = (upper - lower)/2.0
    mean = lower + se
    ax.errorbar(xaxis, mean, yerr = se, color="r", **linestyle)
    ax.plot(xaxis, mean1, color='r', linestyle='-', linewidth = 2)
