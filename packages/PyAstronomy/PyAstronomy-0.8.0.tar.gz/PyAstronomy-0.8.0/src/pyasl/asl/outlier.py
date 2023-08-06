from PyAstronomy.pyaC import pyaErrors as PE
from PyAstronomy import pyaC
import numpy as np
from PyAstronomy.pyaC import ImportCheck


def generalizedESD(x, maxOLs, alpha=0.05, fullOutput=False):
  """
    Carry out a Generalized ESD Test for Outliers.
    
    The Generalized Extreme Studentized Deviate (ESD) test for
    outliers can be used to search for outliers in a univariate
    data set, which approximately follows a normal distribution.
    A description of the algorithm is, e.g., given at
    `Nist <http://www.itl.nist.gov/div898/handbook/eda/section3/eda35h3.htm>`_
    or [Rosner1983]_.
    
    Parameters
    ----------
    maxOLs : int
        Maximum number of outliers in the data set.
    alpha : float, optional
        Significance (default is 0.05).
    fullOutput : boolean, optional
        Determines whether additional return values
        are provided. Default is False.
    
    Returns
    -------
    Number of outliers : int
        The number of data points characterized as
        outliers by the test.
    Indices : list of ints
        The indices of the data points found to
        be outliers.
    R : list of floats, optional
        The values of the "R statistics". Only provided
        if `fullOutput` is set to True.
    L : list of floats, optional
        The lambda values needed to test whether a point
        should be regarded an outlier. Only provided
        if `fullOutput` is set to True.  
    
  """
  ImportCheck(["scipy"], required=["scipy"])
  from scipy.stats import t
  if maxOLs < 1:
    raise(PE.PyAValError("Maximum number of outliers, `maxOLs`, must be > 1.", \
          solution="Specify, e.g., maxOLs = 2"))
  import numpy.ma as ma
  xm = ma.array(x)
  n = len(xm)
  # Compute R-values
  R = []
  L = []
  minds = []
  for i in xrange(maxOLs + 1):
    # Compute mean and std of x
    xmean = xm.mean()
    xstd = xm.std()
    # Find maximum deviation
    rr = np.abs((xm - xmean)/xstd)
    minds.append(np.argmax(rr))
    R.append(rr[minds[-1]])
    if i >= 1:
      p = 1.0 - alpha/(2.0*(n - i + 1))
      perPoint = t.ppf(p, n-i-1)
      L.append((n-i)*perPoint / np.sqrt((n-i-1+perPoint**2) * (n-i+1)))
    # Mask that value and proceed
    xm[minds[-1]] = ma.masked
  # Remove the first entry from R, which is of
  # no meaning for the test
  R.pop(-1)
  # Find the number of outliers
  ofound = False
  for i in xrange(maxOLs-1, -1, -1):
    if R[i] > L[i]:
      ofound = True
      break
  # Prepare return value
  if ofound:
    if not fullOutput:
      # There are outliers
      return i+1, minds[0:i+1]
    else:
      return i+1, minds[0:i+1], R, L, minds
  else:
    # No outliers could be detected
    if not fullOutput:
      # There are outliers
      return 0, []
    else:
      return 0, [], R, L, minds
    

def pointDistGESD(x, maxOLs, alpha=0.05):
  """
    Search for outliers by comparing distance of adjacent points.
    
    This method computes the "distance" between adjacent points, e.g.,
    d = x[i+1] - x[i]. It then uses :py:func:`PyAstronomy.pyasl.generalizedESD`
    to search for outliers in the list of distances. A point will be
    characterized as being an outlier, if (and only if) the distance
    to its left *and* right neighbor are abnormal.
    
    Parameters
    ----------
    x : array
        The data set to be searched for outliers.
    maxOLs : int
        The number of outliers. Note that the number
        passed to `generalizedESD` is actually 2*`maxOLs`.
    alpha : float, optional
        The significance level to be used in applying
        `generalizedESD`. The default is 0.05.
    
    Returns
    -------
    n : int
        The number of outliers detected.
    Indices : list of ints
        The indices of the points found to
        be outliers.
  """
  # Get the distances
  ds = x[1:] - x[0:-1]
  # Apply the generalized ESD to the distances
  r = generalizedESD(ds, maxOLs=maxOLs*2, alpha=alpha, fullOutput=False)
  # Detect outliers (distance to left AND right should
  # be abnormal).
  oll = []
  for i in range(len(r[1])):
    # Check whether also the distance to the right
    # if the current point is abnormal
    if r[1][i] + 1 in r[1]:
      oll.append(r[1][i]+1)
  return len(oll), oll
  
  
def polyResOutlier(x, y, deg=0, stdlim=3.0, controlPlot=False, fullOutput=False):
  """
    Simple outlier detection based on residuals.
    
    This algorithm fits a polynomial of the specified degree
    to the data, subtracts it to find the residuals, determines the
    standard deviations of the residuals, and, finally,
    identifies all points with residuals further than the
    specified number of standard deviations from the fit.
    
    Parameters
    ----------
    x, y : arrays
        The abscissa and ordinate of the data.
    deg : int, optional
        The degree of the polynomial to be fitted.
        The default is 0, i.e., a constant.
    stdlim : float, optional
        The number of standard deviations acceptable
        for points not categorized as outliers.
    controlPlot : boolean, optional
        If True, a control plot will be generated
        showing the location of outliers (default is
        False).
    fullOutput : boolean, optional
        If True, the fitted polynomial and the resulting
        model will be returned.
    
    Returns
    -------
    indiin : array
        The indices of the points *not* being categorized
        as outliers.
    indiout : array
        Indices of the oulier points.
    p : array, optional
        Coefficients of the fitted polynomial (only returned if
        `fullOutput` is True).
    model : array, optional
        The polynomial model (only returned if
        `fullOutput` is True).
  """
  if len(x) < deg + 1:
    raise(PE.PyAValError("Only " + str(len(x)) + " points given to fit a polynomial of degree " + str(deg) + ".", \
                         solution="Use more points and/or change degree of polynomial.", \
                         where="polyResOutlier"))
  if len(x) != len(y):
    raise(PE.PyAValError("x and y need to have the same length.", \
                         solution="Check the lengths of the input arrays.", \
                         where="polyResOutlier"))
  if deg < 0:
    raise(PE.PyAValError("Polynomial degree must be > 0.",
                         where="polyResOutlier"))
  
  p = np.polyfit(x, y, deg)
  model = np.polyval(p, x)
  residuals = y - model
  
  std = np.std(residuals)
  # Find points too far off
  indi = np.where(np.abs(residuals) >= stdlim*std)[0]
  indiin = pyaC.invertIndexSelection(residuals, indi)
  if controlPlot:
    # Produce control plot
    import matplotlib.pylab as plt
    plt.title("polyResOutlier control plot (red: potential outliers, green: polynomial model)")
    plt.plot(x, y, 'b.')
    s = np.argsort(x)
    plt.plot(x[s], model[s], 'g--')
    plt.plot(x[indi], y[indi], 'rp')
    plt.show()
  
  if fullOutput:
    return indiin, indi, p, model
  return indiin, indi