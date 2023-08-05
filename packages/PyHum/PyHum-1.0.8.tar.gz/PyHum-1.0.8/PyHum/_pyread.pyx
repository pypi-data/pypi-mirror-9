# cython module for reading binary humminbird files
# Daniel Buscombe, June 2014 - Feb 2015
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

from __future__ import generators
from __future__ import division
import numpy as np
cimport numpy as np
from array import array as arr
import pyproj
import os, struct

# =========================================================
cdef class pyread:
    """
    read a humminbird file
    """
    cdef object trans
    cdef object transWGS84
    cdef object data
    cdef object humdat
    
    # =========================================================
    def __init__(self, list sonfiles, str humfile, float c, int headbytes=67, str cs2cs_args1="epsg:26949"):
       """
       PyRead

       sonfile:     blah blah blah
       headbytes:   blah blah blah
       cs2cs_args1: blah blah blah
       """

       trans =  pyproj.Proj(init=cs2cs_args1)

       # world mercator
       cdef str cs2cs_args2 = '+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs +proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
       transWGS84 =  pyproj.Proj(cs2cs_args2)
       
       fid2 = open(humfile,'rb')
       humdat = self._decode_humdat(fid2, trans, transWGS84)
       self.humdat = humdat

       cdef list dat = []       
       cdef list data = [] 
       cdef list dfbreak = []  
       cdef list ints_list = []   
       cdef list int_list = [] 
       cdef list fbreak=[]
       cdef list tmpdata = [] 
              
       for sonfile in sonfiles:
          fid = open(sonfile,'rb')
          dat = self._fread(fid,os.path.getsize(sonfile), 'c')
          fid.close()

          # unpack into integers
          for i from 0 <= i < len(dat):
             int_list.append(struct.unpack('>B', dat[i])[0])
          dat = [] 

          # find the start sequences in the list of integers
          for s in self._KnuthMorrisPratt(int_list, [192,222,171,33,128]): 
             fbreak.append(s)
          int_list = [] 
          
          dfbreak = [ x-y for (x,y) in zip(fbreak[1:],fbreak[:-1]) ]
          fbreak = []
     
          fid = open(sonfile,'rb')
          for i from 0 <= i < len(dfbreak):              
             tmpdata.append(self._gethead(fid,trans,transWGS84, c)) # get header for packet
             ints_list = []
             for j from 0 <= j < dfbreak[i]-headbytes:                 
                ints_list.append(struct.unpack('>B', ''.join(self._fread(fid,1,'c')) )[0])
             tmpdata.append(ints_list) # grab the sonar data     
          dfbreak = [] 
          data.append(tmpdata)  
          tmpdata = []   
     
          fid.close()
          
       self.data = data
       return

    # internal functions ======================================


    # =========================================================
    def _calc_beam_pos(self, float dist, float bearing, tuple point):

       cdef float dist_x, dist_y, x_final, y_final
       dist_x, dist_y = (dist*np.sin(bearing), dist*np.cos(bearing))
       xfinal, yfinal = (point[0] + dist_x, point[1] + dist_y)
       return (xfinal, yfinal)

    # =========================================================
    def _KnuthMorrisPratt(self, list text, list pattern):
       # Knuth-Morris-Pratt string matching
       # David Eppstein, UC Irvine, 1 Mar 2002
       # http://code.activestate.com/recipes/117214/

       '''Yields all starting positions of copies of the pattern in the text.
       Calling conventions are similar to string.find, but its arguments can be
       lists or iterators, not just strings, it returns all matches, not just
       the first one, and it does not need the whole text in memory at once. 
       Whenever it yields, it will have read the text exactly up to and including
       the match that caused the yield.'''

       # build table of shift amounts
       cdef list shifts = [1] * (len(pattern) + 1)
       cdef int shift = 1
       for pos from 0 <= pos < len(pattern):       
          while shift <= pos and pattern[pos] != pattern[pos-shift]:
             shift += shifts[pos-shift]
          shifts[pos+1] = shift

       # do the actual search
       cdef int startPos = 0
       cdef int matchLen = 0
       for c in text:
          while matchLen == len(pattern) or \
                matchLen >= 0 and pattern[matchLen] != c:
              startPos += shifts[matchLen]
              matchLen -= shifts[matchLen]
          matchLen += 1
          if matchLen == len(pattern):
             yield startPos

    # =========================================================
    def _fread(self, infile, int num, str typ):
       dat = arr(typ)
       dat.fromfile(infile, num)
       if typ == 'c': #character
          return(list(dat)) #''.join(dat.tolist())))
       elif num == 1: # only 1 byte
          return(list(dat))
       else: 
          return(list(dat))

    # =========================================================
    def _gethead(self, fid, trans, transWGS84, float c):
       cdef list hd = self._fread(fid, 3, 'B')
       cdef list head=[] #pre-allocate list
       cdef int flag

       # error catches - if headers not in right place, roll back
       if hd[0]=='222':
          fid.seek(fid,-4, 1) #'cof')
          hd = self._fread(fid, 3, 'B')
       elif hd[0]=='171':
          fid.seek(fid,-5, 1) #'cof')
          hd = self._fread(fid, 3, 'B')
       elif hd[0]=='33':
          fid.seek(fid,-6, 1) #'cof')
          hd = self._fread(fid, 3, 'B')

       if hd[0]!=192 & hd[1]!=222 & hd[2]!=171:
          flag=1
       else:
          flag=0
          
       cdef list spacer = self._fread(fid, 1, 'B')
       spacer = self._fread(fid, 1, 'B')
       head.append(struct.unpack('>i', ''.join(self._fread(fid,4,'c')) )[0]) #recnum       
       spacer = self._fread(fid, 1, 'B')
       head.append(struct.unpack('>i', ''.join(self._fread(fid,4,'c')) )[0]) #time_ms
       spacer = self._fread(fid, 1, 'B')
       head.append(struct.unpack('>i', ''.join(self._fread(fid,4,'c')) )[0]) # x_utm
       spacer = self._fread(fid, 1, 'B')
       head.append(struct.unpack('>i', ''.join(self._fread(fid,4,'c')) )[0]) # y_utm
       spacer = self._fread(fid, 1, 'B')
       head.append(struct.unpack('>h', ''.join(self._fread(fid,2,'c')) )[0]) # gps1
       head.append(float(struct.unpack('>h', ''.join(self._fread(fid,2,'c')) )[0])/10) # heading_deg    

       spacer = self._fread(fid, 1, 'B')
       head.append(struct.unpack('>h', ''.join(self._fread(fid,2,'c')) )[0]) # gps2
       head.append(float(struct.unpack('>h', ''.join(self._fread(fid,2,'c')) )[0])/10) # speed_ms
       spacer = self._fread(fid, 1, 'B')
       head.append(float(struct.unpack('>i', ''.join(self._fread(fid,4,'c')) )[0])/10) # depth_m
       spacer = self._fread(fid, 1, 'B')
       #%0 (50 or 83 kHz), 1 (200 kHz), 2 (SI Poort), 3 (SI Starboard)
       head.append(self._fread(fid, 1, 'B')[0]) #beam
       spacer = self._fread(fid, 1, 'B')
       head.append(self._fread(fid, 1, 'B')[0]) #voltscale
       spacer = self._fread(fid, 1, 'B')
       head.append(struct.unpack('>i', ''.join(self._fread(fid,4,'c')) )[0]/1000) # freq_khz
       spacer = self._fread(fid, 5, 'B')
       spacer = self._fread(fid,4,'c')
       spacer = self._fread(fid, 5, 'B')
       head.append(struct.unpack('>i', ''.join(self._fread(fid,4,'c')) )[0]) #sentlen
       spacer = self._fread(fid, 1, 'B')          
       
       # channel name
       if head[9]==0:
          head.append('down_lowfreq')
       elif head[9]==1:
          head.append('down_highfreq')
       elif head[9]==2:
          head.append('sidescan_port')
       elif head[9]==3:
          head.append('sidescan_starboard')
       else:
          head.append('unknown')

       cdef float lon, lat
       cdef float dist, bearing

       cdef float tvg = ((8.5*10**-5)+(3/76923)+((8.5*10**-5)/4))*c
        
       if head[9]==3 or head[9]==2: #starboard or port
          dist = ((np.tan(np.radians(25)))*head[8])-(tvg) #depth
          bearing = np.radians(head[5]) - (np.pi/2) #heading_deg
          x_utm, y_utm = self._calc_beam_pos(dist, bearing, (head[2],head[3]))
          lon, lat = transWGS84(x_utm,y_utm, inverse=True)
          head.append(lat)
          head.append(lon)
          lon, lat = trans(lon, lat)
          head.append(lat)
          head.append(lon)     
       
       return head

    # =========================================================
    def _decode_humdat(self, fid2, trans, transWGS84): 
       """
       returns data from .DAT file
       """
       cdef list humdat=[] #pre-allocate list

       cdef list dummy = self._fread(fid2, 1, 'B')
       humdat.append(self._fread(fid2,1,'B')[0]) # water
       dummy = self._fread(fid2,2,'B')
       humdat.append(str(struct.unpack('>i', ''.join(self._fread(fid2,4,'c')) )[0])) #sonar_name
       dummy = list(struct.unpack('>iii', ''.join(self._fread(fid2,3*4,'c')) ))
       humdat.append(struct.unpack('>i', ''.join(self._fread(fid2,4,'c')) )[0]) # unix time
       humdat.append(struct.unpack('>i', ''.join(self._fread(fid2,4,'c')) )[0]) # utm x 
       humdat.append(struct.unpack('>i', ''.join(self._fread(fid2,4,'c')) )[0]) # utm y
       humdat.append(''.join(self._fread(fid2,10,'c'))) #filename
       dummy = self._fread(fid2,2,'B')
       humdat.append(struct.unpack('>i', ''.join(self._fread(fid2,4,'c')) )[0]) #numrecords
       humdat.append(struct.unpack('>i', ''.join(self._fread(fid2,4,'c')) )[0]) #recordlen_ms
       humdat.append(struct.unpack('>i', ''.join(self._fread(fid2,4,'c')) )[0]) #linesize
       dummy = self._fread(fid2,1,'i')
       dummy = self._fread(fid2,4,'B')

       fid2.close()

       # water type
       if humdat[0]==0:
          humdat.append('fresh')
       elif humdat[0]==1:
          humdat.append('deep salt')
       elif humdat[0]==2:
          humdat.append('shallow salt')
       else:
          humdat.append('unknown')

       cdef float humlon
       cdef float humlat
       humlon, humlat = transWGS84(humdat[3],humdat[4], inverse=True)

       humlon, humlat = trans(humlon, humlat)
       humdat.append(humlat)
       humdat.append(humlon)

       cdef dict headdict={'water_code': humdat[0], 'sonar_name': humdat[1], 'unix_time': humdat[2], 'utm_x': humdat[3], 'utm_y': humdat[4], 'filename': humdat[5], 'numrecords': humdat[6], 'recordlens_ms': humdat[7], 'linesize': humdat[8], 'water_type': humdat[9], 'lat': humdat[10], 'lon': humdat[11] } 
       return headdict


    # =========================================================
    def _getsonar(self, str sonarstring):
        """
        returns sonar data
        """
        dat = self.data
        for k in dat:
           if k[0][13] == sonarstring:
              return k  
                 
    # =========================================================
    def _get_scans(self, list scan, int packet):
        """
        returns an individual scan
        """ 
        cdef np.ndarray d = np.zeros( (packet,) )
        cdef np.ndarray tmp = np.squeeze(scan) 
        d[:len(tmp)] = tmp[:packet]
        return d[:packet]                    
                   
    # external functions ======================================                        
    # =========================================================
    def gethumdat(self):
        """
        returns data in .DAT file
        """  
        return self.humdat

    # =========================================================
    def getportscans(self):
        """
        returns compiled scans
        """       
        cdef list data_port = self._getsonar('sidescan_port')
        cdef int packet = data_port[0][12]
        cdef list ind = range(0,len(data_port))
        ind = ind[1::2]

        cdef list c_port = []
        for i in ind:
           c_port.append(self._get_scans(data_port[i], packet))
        return np.asarray(c_port,'float16').T

    # =========================================================
    def getstarscans(self):
        """
        returns compiled scans
        """       
        cdef list data_star = self._getsonar('sidescan_starboard')
        cdef int packet = data_star[0][12]
        cdef list ind = range(0,len(data_star))
        ind = ind[1::2]

        cdef list c_star = []
        for i in ind:
           c_star.append(self._get_scans(data_star[i], packet))
        return np.asarray(c_star,'float16').T

    # =========================================================
    def getlowscans(self):
        """
        returns compiled scans
        """       
        cdef list data_lo = self._getsonar('down_lowfreq')
        cdef int packet = data_lo[0][12]
        cdef list ind = range(0,len(data_lo))
        ind = ind[1::2]

        cdef list c_lo = []
        for i in ind:
           c_lo.append(self._get_scans(data_lo[i], packet))
        return np.asarray(c_lo,'float16').T

    # =========================================================
    def gethiscans(self):
        """
        returns compiled scans
        """       
        cdef list data_hi = self._getsonar('down_highfreq')
        cdef int packet = data_hi[0][12]
        cdef list ind = range(0,len(data_hi))
        ind = ind[1::2]

        cdef list c_hi = []
        for i in ind:
           c_hi.append(self._get_scans(data_hi[i], packet))
        return np.asarray(c_hi,'float16').T

    # =========================================================
    def getmetadata(self):
        """
        returns meta data
        """  
        cdef list data_port = self._getsonar('sidescan_port')
        cdef int packet = data_port[0][12]
        cdef list ind = range(0,len(data_port))
        ind = ind[1::2]        
        
        cdef np.ndarray tmp = np.squeeze(data_port)

        cdef list hdg = []        
        cdef list lon = []
        cdef list lat = []
        cdef list spd = []
        cdef list time_s = []
        cdef list dep_m = []
        cdef list e = []
        cdef list n = []
        for i in ind:
           lon.append(float(tmp[i-1][15]) )
           lat.append(float(tmp[i-1][14]) )
           spd.append(float(tmp[i-1][7]) )
           time_s.append(float(tmp[i-1][1])/1000 )
           dep_m.append(float(tmp[i-1][8]) )
           e.append(float(tmp[i-1][17]) )
           n.append(float(tmp[i-1][16]) )
           hdg.append(float(tmp[i-1][5]) )

        cdef np.ndarray starttime = np.asarray(self.humdat['unix_time'], 'float')
        cdef np.ndarray caltime = np.asarray(starttime + time_s, 'float')

        cdef dict metadict={'lat': np.asarray(lat), 'lon': np.asarray(lon), 'spd': np.asarray(spd), 'time_s': np.asarray(time_s), 'e': np.asarray(e), 'n': np.asarray(n), 'dep_m': np.asarray(dep_m), 'caltime': np.asarray(caltime), 'heading': np.asarray(hdg) }
        return metadict

# cython pyread.pyx
# gcc -c -fPIC -I/usr/include/python2.7/ pyread.c; gcc -shared pyread.o -o pyread.so


