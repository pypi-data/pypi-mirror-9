'''
pyhum_map.py
Part of PyHum software 

INFO:

Author:    Daniel Buscombe
           Grand Canyon Monitoring and Research Center
           United States Geological Survey
           Flagstaff, AZ 86001
           dbuscombe@usgs.gov
Version: 1.2.2      Revision: Mar, 2015

For latest code version please visit:
https://github.com/dbuscombe-usgs

This function is part of 'PyHum' software
This software is in the public domain because it contains materials that originally came from the United States Geological Survey, an agency of the United States Department of Interior. 
For more information, see the official USGS copyright policy at 
http://www.usgs.gov/visual-id/credit_usgs.html#copyright

This software has been tested with Python 2.7 on Linux Fedora 16 & 20, Ubuntu 12.4 & 13.4, and Windows 7.
This software has (so far) been used only with Humminbird 998 and 1198 series instruments. 
'''

# =========================================================
# ====================== libraries ======================
# =========================================================

# operational
from __future__ import division
from scipy.io import loadmat
import os, time, sys, getopt
from Tkinter import Tk
from tkFileDialog import askopenfilename, askdirectory
from joblib import Parallel, delayed, cpu_count
import pyproj

# numerical
import numpy as np
import pyproj
import PyHum.utils as humutils
from scipy.interpolate import griddata
from scipy.spatial import cKDTree as KDTree
from scipy.ndimage.filters import median_filter

# plotting
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import simplekml

# suppress divide and invalid warnings
np.seterr(divide='ignore')
np.seterr(invalid='ignore')

__all__ = [
    'domap',
    'custom_save',
    'custom_save2',    
    'bearingBetweenPoints',
    'calc_beam_pos',
    ]

#################################################
def domap(humfile, sonpath, cs2cs_args, dogrid, calc_bearing, filt_bearing, res):
         
    # prompt user to supply file if no input file given
    if not humfile:
       print 'An input file is required!!!!!!'
       Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
       inputfile = askopenfilename(filetypes=[("DAT files","*.DAT")]) 

    # prompt user to supply directory if no input sonpath is given
    if not sonpath:
       print 'A *.SON directory is required!!!!!!'
       Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
       sonpath = askdirectory() 

    # print given arguments to screen and convert data type where necessary
    if humfile:
       print 'Input file is %s' % (humfile)

    if sonpath:
       print 'Sonar file path is %s' % (sonpath)

    if cs2cs_args:
       print 'cs2cs arguments are %s' % (cs2cs_args)

    if dogrid:
       dogrid = int(dogrid)
       if dogrid==0:
          print "Data will be gridded"      

    if calc_bearing:
       calc_bearing = int(calc_bearing)
       if calc_bearing==1:
          print "Bearing will be calculated from coordinates"     
 
    if filt_bearing:
       filt_bearing = int(filt_bearing)
       if filt_bearing==1:
          print "Bearing will be filtered"      

    if res:
       res = np.asarray(res,float)
       print 'Gridding resolution: %s' % (str(res))      

    if not cs2cs_args:
       # arguments to pass to cs2cs for coordinate transforms
       cs2cs_args = "epsg:26949"
       print '[Default] cs2cs arguments are %s' % (cs2cs_args)

    if not dogrid:
       if dogrid != 0:
          dogrid = 1
          print "[Default] Data will be gridded"

    if not calc_bearing:
       if calc_bearing != 1:
          calc_bearing = 0
          print "[Default] Heading recorded by instrument will be used"

    if not filt_bearing:
       if filt_bearing != 0:
          filt_bearing = 1
          print "[Default] Heading will be filtered"

    if not res:
       res = 0.05
       print '[Default] Grid resolution is %s m' % (str(res))

    trans =  pyproj.Proj(init=cs2cs_args)

    # if son path name supplied has no separator at end, put one on
    if sonpath[-1]!=os.sep:
       sonpath = sonpath + os.sep

    base = humfile.split('.DAT') # get base of file name for output
    base = base[0].split(os.sep)[-1]

    esi = np.squeeze(loadmat(sonpath+base+'meta.mat')['e'])
    nsi = np.squeeze(loadmat(sonpath+base+'meta.mat')['n']) 

    pix_m = np.squeeze(loadmat(sonpath+base+'meta.mat')['pix_m'])
    dep_m = np.squeeze(loadmat(sonpath+base+'meta.mat')['dep_m'])
    c = np.squeeze(loadmat(sonpath+base+'meta.mat')['c'])

    # over-ride measured bearing and calc from positions
    if calc_bearing==1:
       lat = np.squeeze(loadmat(sonpath+base+'meta.mat')['lat'])
       lon = np.squeeze(loadmat(sonpath+base+'meta.mat')['lon']) 

       #point-to-point bearing
       bearing = np.zeros(len(lat))
       for k in xrange(len(lat)-1):
          bearing[k] = bearingBetweenPoints(lat[k], lat[k+1], lon[k], lon[k+1])
       del lat, lon

    else:
       # reported bearing by instrument (Kalman filtered?)
       bearing = np.squeeze(loadmat(sonpath+base+'meta.mat')['heading'])

    # if stdev in heading is large, there's probably noise that needs to be filtered out
    if np.std(bearing)>90:
       print "WARNING: large heading stdev - attempting filtering"
       from sklearn.cluster import MiniBatchKMeans
       # can have two modes
       data = np.column_stack([bearing, bearing])
       k_means = MiniBatchKMeans(2)
       # fit the model
       k_means.fit(data) 
       values = k_means.cluster_centers_.squeeze()
       labels = k_means.labels_

       if np.sum(labels==0) > np.sum(labels==1):
          bearing[labels==1] = np.nan
       else:
          bearing[labels==0] = np.nan

       nans, y= humutils.nan_helper(bearing)
       bearing[nans]= np.interp(y(nans), y(~nans), bearing[~nans])

       # save this filtered version to file
       meta = loadmat(sonpath+base+'meta.mat')
       meta['heading_filt'] = bearing
       savemat(sonpath+base+'meta.mat', meta ,oned_as='row')
       del meta   

    if filt_bearing ==1:
       bearing = humutils.runningMeanFast(bearing, len(bearing)/100)

    theta = np.asarray(bearing, 'float')/(180/np.pi)

    # load memory mapped scans
    shape_port = np.squeeze(loadmat(sonpath+base+'meta.mat')['shape_port'])
    if shape_port!='':
       port_fp = np.memmap(sonpath+base+'_data_port_l.dat', dtype='float32', mode='r', shape=tuple(shape_port))

    shape_star = np.squeeze(loadmat(sonpath+base+'meta.mat')['shape_star'])
    if shape_star!='':
       star_fp = np.memmap(sonpath+base+'_data_star_l.dat', dtype='float32', mode='r', shape=tuple(shape_star))

    # time varying gain
    tvg = ((8.5*10**-5)+(3/76923)+((8.5*10**-5)/4))*c
        
    # depth correction
    dist_tvg = ((np.tan(np.radians(25)))*dep_m)-(tvg)

    for p in xrange(len(star_fp)):
       make_map(esi[shape_port[-1]*p:shape_port[-1]*(p+1)], nsi[shape_port[-1]*p:shape_port[-1]*(p+1)], theta[shape_port[-1]*p:shape_port[-1]*(p+1)], dist_tvg[shape_port[-1]*p:shape_port[-1]*(p+1)], port_fp[p], star_fp[p], pix_m, res, cs2cs_args, sonpath, p, dogrid)


# =========================================================
def custom_save(figdirec,root):
    plt.savefig(figdirec+root,bbox_inches='tight',dpi=400,transparent=True)

# =========================================================
def calc_beam_pos(dist, bearing, x, y):

   dist_x, dist_y = (dist*np.sin(bearing), dist*np.cos(bearing))
   xfinal, yfinal = (x + dist_x, y + dist_y)
   return (xfinal, yfinal)

# =========================================================
def bearingBetweenPoints(pos1_lat, pos2_lat, pos1_lon, pos2_lon):
   lat1 = np.deg2rad(pos1_lat)
   lon1 = np.deg2rad(pos1_lon)
   lat2 = np.deg2rad(pos2_lat)
   lon2 = np.deg2rad(pos2_lon)

   bearing = np.arctan2(np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(lon2 - lon1), np.sin(lon2 - lon1) * np.cos(lat2))

   db = np.rad2deg(bearing)
   return (90.0 - db + 360.0) % 360.0

# =========================================================
def make_map(e, n, t, d, dat_port, dat_star, pix_m, res, cs2cs_args, sonpath, p, dogrid):
   
   trans =  pyproj.Proj(init=cs2cs_args)   
   
   merge = np.vstack((dat_port,dat_star))
   #merge = np.vstack((np.flipud(port_fp[p]),star_fp[p]))
   
   merge[np.isnan(merge)] = 0

   merge = merge[:,:len(n)]

   # get number pixels in scan line
   extent = int(np.shape(merge)[0]/2)

   yvec = np.linspace(pix_m,extent*pix_m,extent)

   print "getting point cloud ..."
   # get the points by rotating the [x,y] vector so it lines up with boat heading, assumed to be the same as the curvature of the [e,n] trace
   X=[]; Y=[];
   for k in range(len(n)): 
      x = np.concatenate((np.tile(e[k],extent) , np.tile(e[k],extent)))
      y = np.concatenate((n[k]+yvec, n[k]-yvec))
      # Rotate line around center point
      xx = e[k] - ((x - e[k]) * np.cos(t[k])) - ((y - n[k]) * np.sin(t[k]))
      yy = n[k] - ((x - e[k]) * np.sin(t[k])) + ((y - n[k]) * np.cos(t[k]))
      xx, yy = calc_beam_pos(d[k], t[k], xx, yy)
      X.append(xx)
      Y.append(yy) 

   del e, n, t, x, y #, X, Y

   # merge flatten and stack
   X = np.asarray(X,'float').T
   X = X.flatten()

   # merge flatten and stack
   Y = np.asarray(Y,'float').T
   Y = Y.flatten()

   # write raw bs to file
   outfile = sonpath+'x_y_ss_raw'+str(p)+'.asc' 
   with open(outfile, 'w') as f:
      np.savetxt(f, np.hstack((humutils.ascol(X.flatten()),humutils.ascol(Y.flatten()), humutils.ascol(merge.flatten()))), delimiter=' ', fmt="%8.6f %8.6f %8.6f")

   humlon, humlat = trans(X, Y, inverse=True)

   if dogrid==1:
      grid_x, grid_y = np.meshgrid( np.arange(np.min(X), np.max(X), res), np.arange(np.min(Y), np.max(Y), res) )  

      dat = griddata(np.c_[X.flatten(),Y.flatten()], merge.flatten(), (grid_x, grid_y), method='nearest') 

      ## create mask for where the data is not
      tree = KDTree(np.c_[X.flatten(),Y.flatten()])
      dist, _ = tree.query(np.c_[grid_x.ravel(), grid_y.ravel()], k=1)
      dist = dist.reshape(grid_x.shape)

   del X, Y #, bearing #, pix_m, yvec

   if dogrid==1:
      ## mask
      dat[dist> np.floor(np.sqrt(1/res))-1 ] = np.nan #np.floor(np.sqrt(1/res))-1 ] = np.nan
      del dist, tree

      dat[dat==0] = np.nan
      dat[np.isinf(dat)] = np.nan
      datm = np.ma.masked_invalid(dat)

      glon, glat = trans(grid_x, grid_y, inverse=True)
      del grid_x, grid_y

   print "drawing and printing map ..."
   fig = plt.figure(frameon=False)
   map = Basemap(projection='merc', epsg=cs2cs_args.split(':')[1], #26949,
    resolution = 'i', #h #f
    llcrnrlon=np.min(humlon)-0.001, llcrnrlat=np.min(humlat)-0.001,
    urcrnrlon=np.max(humlon)+0.001, urcrnrlat=np.max(humlat)+0.001)

   if dogrid==1:
      gx,gy = map.projtran(glon, glat)

   ax = plt.Axes(fig, [0., 0., 1., 1.], )
   ax.set_axis_off()
   fig.add_axes(ax)

   if dogrid==1:
      map.pcolormesh(gx, gy, datm, cmap='gray', vmin=np.nanmin(dat), vmax=np.nanmax(dat))
      del datm, dat
   else: 
      ## draw point cloud
      x,y = map.projtran(humlon, humlat)
      map.scatter(x.flatten(), y.flatten(), 0.5, merge.flatten(), cmap='gray', linewidth = '0')

   custom_save(sonpath,'map'+str(p))
   del fig 

   kml = simplekml.Kml()
   ground = kml.newgroundoverlay(name='GroundOverlay')
   ground.icon.href = sonpath+'map'+str(p)+'.png'
   ground.latlonbox.north = np.min(humlat)-0.001
   ground.latlonbox.south = np.max(humlat)+0.001
   ground.latlonbox.east =  np.max(humlon)+0.001
   ground.latlonbox.west =  np.min(humlon)-0.001
   ground.latlonbox.rotation = 0

   kml.save(sonpath+'GroundOverlay'+str(p)+'.kml')

   del humlat, humlon

