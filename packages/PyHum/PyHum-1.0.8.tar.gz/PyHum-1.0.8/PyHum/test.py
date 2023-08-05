"""
Part of PyHum software 

INFO:


Author:    Daniel Buscombe
           Grand Canyon Monitoring and Research Center
           United States Geological Survey
           Flagstaff, AZ 86001
           dbuscombe@usgs.gov
Version: 1.0.8      Revision: Feb, 2015

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

__all__ = [
    'dotest',
    ]

def dotest():
   # general settings
   humfile = PyHum.__path__[0]+os.sep+'test.DAT'
   sonpath = PyHum.__path__[0]
   c = 1450
   t = 0.108
   f = 455
   doplot = 1

   # correction specific settings
   bedpick = 1
   maxW = 1000

   # reading specific settings
   epsg = "epsg:26949"
   draft = 0

   # for texture calcs
   win = 100
   shift = 10
   density = win/2
   numclasses = 4
   maxscale = 20
   notes = 4
   shorepick = 0
   do_two = 0

   PyHum.humread(humfile, sonpath, epsg, c, draft, doplot)

   PyHum.humcorrect(humfile, sonpath, c, t, f, maxW, bedpick, doplot)

   PyHum.humtexture(humfile, sonpath, c, t, f, win, shift, doplot, density, numclasses, maxscale, notes, shorepick, do_two)

if __name__ == '__main__':
   dotest()

