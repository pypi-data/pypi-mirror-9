from scipy import optimize as sco

class Fitter_fmin:
  
  def __init__(self, requires):
    """
    """
    self._required = requires
  
  def _inspectFunc(self):
    """
    """
  
  def _checkArgs(self, args):
    """
    """
    pass
  
  def __call__(self, **kw):
    """
    """
    self._checkArgs(kw)
    self.fitResult =  sco.fmin(kw["minifunc"], kw["x0"], args, xtol, ftol, maxiter, maxfun, full_output, disp, retall, callback) (self.miniFunc, self.pars.getFreeParams(), *self.fminPars, \
                             full_output=True, **self.fminArgs)
    
  