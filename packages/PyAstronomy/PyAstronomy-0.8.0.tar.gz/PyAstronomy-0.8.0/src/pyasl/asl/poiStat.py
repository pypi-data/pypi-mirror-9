from PyAstronomy.pyaC import pyaErrors as PE
from PyAstronomy.pyasl import _ic

def upperLimitPoisson(csrc, cbg, backscale=1.0, conf=0.95, verbose=False):
  """
    Compute Poisson statistics.
    
    Parameters
    ----------
    csrc : int
        Source counts.
    cbg : int
        Background counts.
    backscale : float
        Ratio between source and background region.
        This number is larger one, if the background
        region is larger than the source region.
    conf : float, optional
        Confidence level used in calculations. The
        default is 0.95.
    verbose : boolean, optional
        If True, the results will be printed to
        screen. The default is False.
    
    Returns
    -------
    Poisson statistics : dictionary
        A dictionary containing the following entries:
          - mubg : The background expectation value in the
            source region.
          - pbgfluc : The probability to obtain the observed
            number or a higher number of counts in the source
            region. A small number indicates that a background
            fluctuation is an unlikely explanation for the
            observation.
          - ul : The expected number of source counts
            required to make the probability to obtain more
            than the observed number of counts in the source
            region, `csrc`, be equal to `conf`. This number
            is an upper limit for the source strength at the
            specified confidence level. Note that it is
            calculated no matter what the value of `pbgfluc`
            is. 
             
  """
  if not _ic.check["scipy"]:
    raise(PE.PyARequiredImport("scipy is not installed.", \
          where="upperLimitPoisson", \
          solution="Install scipy (http://www.scipy.org/)"))
  
  from scipy import stats
  from scipy import optimize
  # Estimate bg expectation value in source region
  mubg = cbg * backscale
  
  # The probability to obtain `csrc` or more counts
  # as a result of background fluctuation
  pbgfluc = 1.0 - stats.poisson.cdf(csrc-1, mubg)
  
  # Calculate the maximum source-count expectation value
  # for which the probability to obtain more than `csrc`
  # counts amounts to `conf`.
  f = lambda musrc : stats.poisson.cdf(csrc, mubg+musrc) - (1.0 - conf)

  print f(0), stats.poisson.cdf(csrc, mubg+0)
  print f(20.0*(csrc+1)), stats.poisson.cdf(csrc, mubg+(20.0*(csrc+1)))
  
  if f(0) < 0.0:
    limit = None
  else:
    limit = optimize.brentq(f, 0, 20.0*(csrc+1))
  
  if verbose:
    print "Poisson statistics"
    print "         INPUT"
    print "  Counts in source region: ", csrc
    print "  Counts in bg region    : ", cbg
    print "  Background scaling     : ", backscale
    print "  Confidence level       : ", conf
    print "         OUTPUT"
    print "  Bg counts expected in source region: ", mubg
    print "  p(bg fluctuation) : ", pbgfluc
    print "  upper limit       : ", limit
  
  return {"ul":limit, "mubg":mubg, "pbgfluc":pbgfluc}
  