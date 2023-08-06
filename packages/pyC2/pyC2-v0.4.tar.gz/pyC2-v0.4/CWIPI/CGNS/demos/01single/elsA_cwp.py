#!/usr/bin/env python
# -------------------------------------------------------------------------
# CWIPI.CGNS - a CGNS/Python module for CWIPI
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
import numpy
import CWIPI.CGNS as C2
from CWIPI.CGNS.demos.data import T

class elsA(object):
  def initialize(self,comm,n):
    self.data=numpy.ones((n,),dtype='d')*2.4
  def computeStep(self,input):
   self.data+=remote_data
   return self.data
  def finalize(self):
    pass
  
baseName='Blocks:S'
surfaceName='SurfaceOtherName'# struct/struct
#surfaceName='SurfaceName' # struct/unstruct
count=0

e=elsA()

fwk=C2.Framework("elsA",debug=True)
fwk.attribute.tol=1e-12
fwk.trace('init elsA connexion (to fake)')
cpl=C2.Connection(fwk,"IsothermalWall",'fake',T,baseName,surfaceName)
e.initialize(fwk.local_communicator,cpl.located)
for i in range(100):
  remote_data=cpl.publishAndRetrieve(e.data,iteration=i)
  local_data=e.computeStep(remote_data)
  if (not i%20):
    fwk.trace('elsA total: %.3d=%e'%(i,local_data.sum()))
    #fwk.attribute.retrieve('fake','local_delta')
    #fwk.trace('elsA remote delta from fake: %e'%fwk.attribute.local_delta)
    
fwk.trace('leave elsA')
e.finalize()

# --- last line

