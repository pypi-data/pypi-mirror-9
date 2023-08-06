from PyA_Version import PyA_Version 
import os

class PyAIS:
  """
    PyAstronomy Import Status
  """
  
  def findpackages(self):
    for root, dirs, fns in os.walk(__path__[0]):
      for dir in dirs:
        if os.path.isfile(os.path.join(__path__[0], dir, "__init__.py")):
          self.packages.append(dir)
      break;
    
  def showStatus(self):
    print 
    print "        Results of PyAIS import check:"
    print "-----------------------------------------------------"
    print "%20s  |  %5s" % ("Package Name", "Import Status")
    print "-----------------------------------------------------"
    for m, v in self.importStatus.iteritems():
      print "%20s  |  %5s" % (m, v)
      
  def __init__(self):
    """
      Try to import all packages contained in self.packages and save status.
    """
    
    self.packages = []
    self.findpackages()
    
    self.importStatus = {}
    for m in self.packages:
      try:
        __import__(m, globals(), locals())
        self.importStatus[m] = True
      except ImportError:
        self.importStatus[m] = False


def importCheck():
  p = PyAIS()
  p.showStatus()


# The version Tag for PyAstronomy
__version__ = PyA_Version()