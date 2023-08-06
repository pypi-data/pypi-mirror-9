The chopthin resampler
======================

This gives an implementation of the chopthin algorithm for Python. Not much error checking is happening.


Some example code
-----------------
::

   import chopthin
   from numpy import *
   w = array([1,3.4,2,0.1,0.1,0.1,0.1]);
   chopthin.chopthin(w,5,5.8)


