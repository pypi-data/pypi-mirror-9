Binning algorithms
===================

Create binned data sets.

Constant bin width
------------------

.. currentmodule:: PyAstronomy.pyasl
.. autofunction:: binningx0dt

Examples
---------

Basic binning
~~~~~~~~~~~~~~~

::

  import numpy as np
  import matplotlib.pylab as plt
  from PyAstronomy.pyasl import binningx0dt
  
  # Generate some data
  x = np.arange(999)
  y = np.sin(x/100.)
  y += np.random.normal(0,0.1,len(x))
  
  # Bin using fixed number of bins and start at x0 = -10.
  # Use beginning of bin as starting value.
  r1, dt1 = binningx0dt(x, y, nbins=50, x0=-10, useBinCenter=False)
  # Use fixed bin width. Specify another (wrong) error estimate and
  # use bin center.
  r2, dt2 = binningx0dt(x, y, yerr=np.ones(len(x))*0.2, dt=dt1, \
                        x0=-10, useBinCenter=True, removeNoError=True)
  
  print "dt1, dt2: ", dt1, dt2
  print "Input data points in last bin: ", r2[-1,3]
  
  # Use the reducedBy flag to indicate the binning. In this case, x0
  # will be set to the lowest x value in the data, and the number of
  # bins will be calculated as: int(round(len(x)/float(reduceBy))).
  # Here, we will, thus, obtain 100 bins.
  r3, dt3 = binningx0dt(x, y, \
                        useBinCenter=True, removeNoError=True, reduceBy=10)
  
  print "dt3: ", dt3
  print "Number of bins in third version: ", len(r3[::,0])
  
  
  # Plot the output
  plt.plot(x,y)
  plt.errorbar(r1[::,0], r1[::,1], yerr=r1[::,2], fmt='kp--')
  plt.errorbar(r2[::,0], r2[::,1], yerr=r2[::,2], fmt='rp--')
  plt.errorbar(r3[::,0], r3[::,1], yerr=r3[::,2], fmt='gp--')
  plt.show()



Data gaps and time bins at barycenter of binned points
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  import numpy as np
  import matplotlib.pylab as plt
  from PyAstronomy.pyasl import binningx0dt
  
  # Generate some data
  x = np.arange(-100,999)
  # Create some holes in the data
  x = np.delete(x, range(340,490))
  x = np.delete(x, range(670,685))
  x = np.delete(x, range(771,779))
  y = np.sin(x/100.)
  y += np.random.normal(0,0.1,len(x))
  
  
  # Bin using bin width of 27 and starting at minimum x-value.
  # Use beginning of bin as starting value.
  r1, dt1 = binningx0dt(x, y, dt=27, x0=min(x), useBinCenter=True)
  
  # As previously, but use the mean x-value in the bins to produce the
  # rebinned time axis.
  r2, dt2 = binningx0dt(x, y, dt=27, x0=min(x), useMeanX=True)
  
  print "Median shift between the time axes: ", np.median(r1[::,0] - r2[::,0])
  print " -> Time bins are not aligned due to 'forced' positioning of"
  print "    the first axis."
  
  # Plot the output
  plt.plot(x,y, 'b.-')
  plt.errorbar(r1[::,0], r1[::,1], yerr=r1[::,2], fmt='kp--')
  plt.errorbar(r2[::,0], r2[::,1], yerr=r2[::,2], fmt='rp--')
  plt.show()