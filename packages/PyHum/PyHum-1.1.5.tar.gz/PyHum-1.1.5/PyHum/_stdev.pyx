from __future__ import division
import numpy as np
cimport numpy as np
cimport cython

import RunningStats

# =========================================================
cdef class proc:
   """
   Returns an instance.
   """
   cdef object data

   @cython.boundscheck(False)
   @cython.cdivision(True)
   @cython.wraparound(False)
   @cython.nonecheck(False)
   # =========================================================
   def __init__(self, np.ndarray[np.float64_t, ndim=1] points): 

      # pre-allocate arrays
      cdef list filled

      rs1 = RunningStats.RunningStats()
      # global stats, not detrended
      for k in points:
         rs1.Push(k)
 
      # compile all parameters into a list
      filled = [rs1.Mean(), rs1.StandardDeviation()]

      self.data = filled

      rs1.Clear()

      return

   # =========================================================
   @cython.boundscheck(False)
   @cython.cdivision(True)
   @cython.wraparound(False)
   @cython.nonecheck(False)
   cpdef list getdata(self):
      return self.data


