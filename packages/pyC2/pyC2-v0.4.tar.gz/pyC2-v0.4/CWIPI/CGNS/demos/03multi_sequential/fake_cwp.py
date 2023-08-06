#!/usr/bin/env python
# -------------------------------------------------------------------------
# CWIPI.CGNS - a CGNS/Python module for CWIPI
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
import CWIPI.CGNS as C2
import numpy 
from CWIPI.CGNS.demos.data import T

baseName='Blocks:S'
#baseName='Blocks:U'
surfaceName='SurfaceOtherName'
#surfaceName='SurfaceName'
count=0

fwk=C2.Framework("fake")
fwk.attribute.tol=1e-12

fwk.trace('init fake connexion (to elsA)')
cpl=C2.Connection(fwk,"IsothermalWall",'elsA',T,baseName,surfaceName)

local_data=numpy.ones((cpl.located,),dtype='d')*1.3
first_data=numpy.copy(local_data)

for i in range(10):
  fwk.trace('enter fake loop')
  remote_data=cpl.publishAndRetrieve(local_data,iteration=i)
  local_data+=remote_data*.5
  if (not i%2):
    fwk.trace('fake total: %.3d=%e'%(i,local_data.sum()))
    local_delta=local_data-first_data
    fwk.attribute.local_delta=local_delta.max()
    fwk.attribute.publish('elsA','local_delta')
    
    
fwk.trace('leave fake')
del cpl

# --- last line
