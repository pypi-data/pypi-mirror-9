"""
Part of PyHum software 

INFO:


Author:    Daniel Buscombe
           Grand Canyon Monitoring and Research Center
           United States Geological Survey
           Flagstaff, AZ 86001
           dbuscombe@usgs.gov
Version: 1.2.1      Revision: Mar, 2015

For latest code version please visit:
https://github.com/dbuscombe-usgs

This function is part of 'PyHum' software
This software is in the public domain because it contains materials that originally came from the United States Geological Survey, an agency of the United States Department of Interior. 
For more information, see the official USGS copyright policy at 
http://www.usgs.gov/visual-id/credit_usgs.html#copyright
    
"""
#python -c "import PyHum; PyHum.test.dotest()"

import PyHum
import os
import shutil
import errno
 
def dircopy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            print('Directory not copied. Error: %s' % e)

__all__ = [
    'dotest',
    ]

def dotest():

   # copy files over to somewhere read/writeable
   dircopy(PyHum.__path__[0], os.path.expanduser("~")+os.sep+'pyhum_test')
   shutil.copy(PyHum.__path__[0]+os.sep+'test.DAT', os.path.expanduser("~")+os.sep+'pyhum_test'+os.sep+'test.DAT')

   # general settings   
   humfile = os.path.expanduser("~")+os.sep+'pyhum_test'+os.sep+'test.DAT' #PyHum.__path__[0]+os.sep+'test.DAT'
   sonpath = os.path.expanduser("~")+os.sep+'pyhum_test' #PyHum.__path__[0]
   doplot = 1 #yes

   # reading specific settings
   cs2cs_args = "epsg:26949" #arizona central state plane
   bedpick = 1 # auto bed pick
   c = 1450 # speed of sound fresh water
   t = 0.108 # length of transducer
   f = 455 # frequency kHz
   draft = 0.3 # draft in metres
   flip_lr = 1 # flip port and starboard

   # correction specific settings
   maxW = 1000 # rms output wattage

   # for texture calcs
   win = 100 # pixel window
   shift = 10 # pixel shift
   density = win/2 
   numclasses = 4 # number of discrete classes for contouring and k-means
   maxscale = 20 # Max scale as inverse fraction of data length (for wavelet analysis)
   notes = 4 # Notes per octave (for wavelet analysis)

   # for mapping
   #imagery = 1 # server='http://server.arcgisonline.com/ArcGIS', service='World_Imagery'
   dogrid = 0 # no
   calc_bearing = 0 #no
   filt_bearing = 1 #yes
   res = 0.05 # grid resolution in metres

   PyHum.humread(humfile, sonpath, cs2cs_args, c, draft, doplot, t, f, bedpick, flip_lr)

   PyHum.humcorrect(humfile, sonpath, maxW, doplot)

   PyHum.humtexture(humfile, sonpath, win, shift, doplot, density, numclasses, maxscale, notes)

   PyHum.domap(humfile, sonpath, cs2cs_args, dogrid, calc_bearing, filt_bearing, res)

   PyHum.domap_texture(humfile, sonpath, cs2cs_args, dogrid, calc_bearing, filt_bearing, res)

if __name__ == '__main__':
   dotest()

