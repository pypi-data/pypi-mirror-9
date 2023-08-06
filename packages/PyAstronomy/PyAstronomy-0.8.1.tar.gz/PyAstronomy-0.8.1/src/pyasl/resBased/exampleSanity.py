import unittest

class SanityOfBaraffe98Tracks(unittest.TestCase):
  
  def setUp(self):
    pass
  
  def tearDown(self):
    pass
  
  def sanity_example(self):
    from PyAstronomy.pyasl import resBased as rb
    import matplotlib.pylab as plt
    import numpy as np
    
    bt = rb.Baraffe98Tracks()
    
    print "Unique metallicity values: ", bt.getUniqueValues("Met")
    print "Unique Y values: ", bt.getUniqueValues("Y")
    print "Unique Lmix values: ", bt.getUniqueValues("Lmix")
    print "Unique mass values: ", bt.getUniqueValues("Mass")
    
    # Get model data and plot log10(age) versus effective temperature
    m = bt.getModelData((0.0, 0.275, 1.0, 0.3))
    plt.plot(np.log10(m.Age*1e9), m.Teff, 'b.-')
    
    # Find all models with metallicity 0.0, Y 0.275, Lmix 0.0,
    # and any mass.
    models = bt.findModels(Met=0.0, Mass=None, Y=0.275, Lmix=1.0)
    # Print out the model parameters.
    print
    print "Number of models found: ", len(models)
    for i, model in enumerate(models):
      print "Model no. %3d : Met = %3.1f, Y = %5.3f, Lmix = %3.1f, Mass = %4.2f" \
            % ((i+1,) + model)
    
    # Finally, show the plot
#    plt.show()

class SanityOfNasaExoplanetArchive(unittest.TestCase):
  
  def setUp(self):
    pass
  
  def tearDown(self):
    pass
  
  def sanity_example(self):
    from PyAstronomy import pyasl
    import matplotlib.pylab as plt
    
    nexa = pyasl.NasaExoplanetArchive()
    
    # See what information is available
    cols = nexa.availableColumns()
    print
    
    # Get all information for planet 'wasp-12 b'
    # By default, the search is case-insensitive
    print "Entry of Wasp-12 b"
    print nexa.selectByPlanetName("Wasp-12 b")
    
    print
    # Get all data and plot ra vs. dec
    dat = nexa.getAllData()
    plt.plot(dat.ra, dat.dec, 'b.')
#    plt.show()


class SanityOfNasaExoplanetEU(unittest.TestCase):
  
  def setUp(self):
    pass
  
  def tearDown(self):
    pass
  
  def sanity_example(self):
    """
      Exoplanet EU example
    """
    from PyAstronomy import pyasl
    import matplotlib.pylab as plt
    
    eu = pyasl.ExoplanetEU()
    
    # See what information is available
    cols = eu.availableColumns()
    print cols
    
    print
    # Get all data and plot planet Mass vs.
    # semi-major axis in log-log plot
    dat = eu.getAllData()
    plt.xlabel("Planet Mass [RJ]")
    plt.ylabel("Semi-major axis [AU]")
    plt.loglog(dat.plMass, dat.sma, 'b.')
#    plt.show()

class SanityOfNasaExoplanetsOrg(unittest.TestCase):
  
  def setUp(self):
    pass
  
  def tearDown(self):
    pass
  
  def sanity_example(self):
    """
      Exoplanets ORG example
    """
    from PyAstronomy import pyasl
    
    # Instantiate the access class
    epl = pyasl.ExoplanetsOrg()
    
    # Show the available columns
    epl.availableColumns()
    
    # Get information in Kepler-5 b
    d = epl.selectByPlanetName("kepler-5 b")
    
    # Print whatever information has been received
    print
    print "Information on Kepler-5 b"
    print
    for k, v in d.items():
      print "%12s  %12s" % (k,str(v))
      
class SanityOfFIP(unittest.TestCase):
  
  def setUp(self):
    pass
  
  def tearDown(self):
    pass
  
  def sanity_example(self):
    """
      Checking example of FIP.
    """
    from PyAstronomy import pyasl
  
    fip = pyasl.FirstIonizationPot()
    
    print "First ionization energy of Li = %4.2e +/- %4.2e eV" % fip.getFIP(3)
    print "First ionization energy of Protactinium = %4.2e +/- %4.2e eV" % fip.getFIP(91)
    
    # And the same using elemental symbols
    print
    print "First ionization energy of Li = %4.2e +/- %4.2e eV" % fip.getFIP("Li")
    print "First ionization energy of Protactinium = %4.2e +/- %4.2e eV" % fip.getFIP("Pa")
    
    # Plot the first ionization energy as a function of atomic number
#    pyasl.plotFIP()

  def sanity_FIP(self):
    """
      Checking sanity of FIP.
    """
    from PyAstronomy import pyasl
  
    fip = pyasl.FirstIonizationPot()
    self.assertAlmostEqual(10.451260, fip.getFIP(53)[0], 6, msg="FIP for iodine does not match (an).")
    self.assertAlmostEqual(10.451260, fip.getFIP("I")[0], 6, msg="FIP for iodine does not match (sym).")
    
    self.assertAlmostEqual(25e-6, fip.getFIP(53)[1], 6, msg="FIP for iodine does not match (an).")
    self.assertAlmostEqual(25e-6, fip.getFIP("I")[1], 6, msg="FIP for iodine does not match (sym).")