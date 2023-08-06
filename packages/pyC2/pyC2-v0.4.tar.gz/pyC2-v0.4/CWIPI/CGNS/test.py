# -------------------------------------------------------------------------
# CWIPI.CGNS - a CGNS/Python module for CWIPI
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
import unittest
import re

# --------------------------------------------------
# Tests should be run with mpi, example:
#    mpirun -np 1 python test.py
# Make sure the python you are running is the same used for build
# --------------------------------------------------
# should not be documented with docstrings
class C2TestCase(unittest.TestCase):
  def setUp(self):
    self.T=None
  def eStr(self,code):
    import CWIPI.CGNS.error as CWE
    r1=re.compile(re.escape(CWE.TAG+CWE.TAG_ERROR+"[%.3d]"%code))
    return r1
  def getCGNStree(self):
    from CWIPI.CGNS.demo.data import T
    return T
  def test_00Module(self):
    import CWIPI
    import CWIPI.CGNS
    import CGNS
    import CGNS.PAT
    import CGNS.MAP
    import mpi4py
    import numpy
  def test_01Framework(self):
    import mpi4py.MPI as MPI
    import CWIPI.CGNS as C2
    import CWIPI.CGNS.error as CWE
    ex=CWE.C2Error
    fwk=C2.Framework("elsA")
    self.assertIsInstance(fwk,C2.Framework)
    self.assertRaisesRegexp(ex,self.eStr(102),C2.Framework(3))
    self.assertRaisesRegexp(ex,self.eStr(103),C2.Framework(""))
  def test_03Attributes(self):
    import mpi4py.MPI as MPI
    import CWIPI.CGNS as C2
    import CWIPI.CGNS.error as CWE
    ex=CWE.C2Error
    fwk=C2.Framework("elsA")
    fwk.attribute.nbzones=4
    self.assertEqual(fwk.attribute.nbzones,4)
    self.assertEqual(fwk.attribute['nbzones'],4)
    fwk.attribute.tolerance=1e-12
    self.assertEqual(fwk.attribute.tolerance,1e-12)
    self.assertEqual(fwk.attribute['tolerance'],1e-12)
  def test_04Connection(self):
    import mpi4py.MPI as MPI
    import CWIPI.CGNS as C2
    import CWIPI.CGNS.error as CWE
    T=self.getCGNStree()
    ex=CWE.C2Error
    fwk=C2.Framework("elsA")
    self.assertRaisesRegexp(ex,self.eStr(200),C2.Connection(fwk,"Fluid/Structure",'zebulon',None,'FSI-surface'))
    self.assertRaisesRegexp(ex,self.eStr(210),C2.Connection(fwk,2,'zebulon',T,'FSI-surface'))
    self.assertRaisesRegexp(ex,self.eStr(211),C2.Connection(fwk,"",'zebulon',T,'FSI-surface'))
    self.assertRaisesRegexp(ex,self.eStr(212),C2.Connection(fwk,"Fluid/Structure",2,T,'FSI-surface'))
    self.assertRaisesRegexp(ex,self.eStr(213),C2.Connection(fwk,"Fluid/Structure",'',T,'FSI-surface'))
    self.assertRaisesRegexp(ex,self.eStr(214),C2.Connection(fwk,"Fluid/Structure",'zebulon',T,3))
    self.assertRaisesRegexp(ex,self.eStr(215),C2.Connection(fwk,"Fluid/Structure",'zebulon',T,''))
    #self.assertIsInstance(C2.Connection(fwk,"Fluid/Structure",'zebulon',T,'FSI-surface'),C2.Connection)
    if (MPI.COMM_WORLD.rank==1):
      fwk=C2.Framework("elsA")
      self.assertRaiseRegexp(ex,self.eStr(300),C2.Connection(fwk,"Fluid/Structure",'elsA',T,'FSI-surface'),C2.Connection)
    else:
      fwk=C2.Framework("zebulon")
      self.assertRaiseRegexp(ex,self.eStr(300),C2.Connection(fwk,"Fluid/Structure",'elsA',T,'FSI-surface'),C2.Connection)

suite = unittest.TestLoader().loadTestsFromTestCase(C2TestCase)
unittest.TextTestRunner(verbosity=1).run(suite)

# --- last line

