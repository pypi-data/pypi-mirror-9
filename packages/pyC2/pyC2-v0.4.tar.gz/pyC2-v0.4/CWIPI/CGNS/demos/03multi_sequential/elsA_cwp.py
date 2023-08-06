#!/usr/bin/env python
# -------------------------------------------------------------------------
# CWIPI.CGNS - a CGNS/Python module for CWIPI
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
import numpy
import CWIPI.CGNS as C2
from CWIPI.CGNS.demos.data import T
from mpi4py import MPI

# to be run on 4 procs
#
# distribution is
# proc 0 : 01A
# proc 1 : 01B
# proc 2 : 01C
# proc 3 : 02A, 03A
#
distribution={ # elsA-like distribution of zones
  'Block:01:A':0,
  'Block:01:B':1,
  'Block:01:C':2,
  'Block:02:A':3,
  'Block:02:B':3
}

class elsA(object):
  def initialize(self,comm,n=None):
    if (n is not None):
      self.data=numpy.ones((n,),dtype='d')*2.4
    else:
      self.data=None
  def computeStep(self,input):
    if (self.data is not None):
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
cpl=C2.Connection(fwk,"IsothermalWall",'fake',T,
                  baseName,surfaceName,mode=C2.SEQUENTIAL)
psize=cpl.located

e.initialize(fwk.local_communicator,psize)

for i in range(10):
  print 'RANK ',fwk.local_communicator.rank
  if (fwk.local_communicator.rank==0):
    fwk.trace('enter elsA loop step:%d send'%i)
    remote_data=cpl.publishAndRetrieve(e.data,iteration=i)
  else:
    fwk.trace('enter elsA loop step:%d skip'%i)
    remote_data=None
  local_data=e.computeStep(remote_data)
  if ((not i%2) and (fwk.local_communicator.rank==0)):
    fwk.trace('elsA total: %.3d=%e'%(i,local_data.sum()))
    fwk.attribute.retrieve('fake','local_delta')
    fwk.trace('elsA remote delta from fake: %e'%fwk.attribute.local_delta)
    
fwk.trace('leave elsA')
e.finalize()

# --- last line

