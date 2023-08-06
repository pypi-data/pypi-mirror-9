# -------------------------------------------------------------------------
# CWIPI.CGNS - a CGNS/Python module for CWIPI
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------

import sys
import os
import string

# -----------------------------------------------------------------------------
try:
  import mpi4py.MPI as MPI

  rs=MPI.COMM_WORLD.rank
  ss=MPI.COMM_WORLD.size

except ImportError:
  if (not os.environ.has_key('C2GENDOC')):
    print 'FATAL: Cannot import MPI4py'
    sys.exit()

TAG="### CWIPI.CGNS [%.2d:%.2d]:"%(rs+1,ss)
TAG_ERROR=" ERROR "

# ----------------------------------------------------------------------
def perr(id, *tp):
  try:
    msg=TAG+TAG_ERROR+"[%.3d] %s"%(id,errorTable[id])
  except TypeError,KeyError:
    msg=TAG+TAG_ERROR+"[%.3d] %s"%(id,errorTable[999])
  ret=msg
  if tp:
    ret=msg%tp
  return ret

# ----------------------------------------------------------------------
class C2Error(Exception):
  """Error support object
  """
  def __init__(self,code,*args):
    self.code=code
    self.value=args
  def __str__(self):
    if (self.value is not None): ret=perr(self.code,*self.value)
    else:                        ret=perr(self.code)
    return ret

# ----------------------------------------------------------------------
class C2Log(object):
  def __init__(self,prefix,std_out):
    self.prefix=prefix
    self.std_out=std_out
  def write(self,msg):
    if (msg in ['\n','\r']):
      self.std_out.write(msg+self.prefix)
    else: self.std_out.write(msg)

def close_std():
  sys.stdout.flush()
  newstdout=os.dup(1)
  devnull=os.open(os.devnull, os.O_WRONLY)
  os.dup2(devnull, 1)
  os.close(devnull)
  sys.stdout=os.fdopen(newstdout, 'w')
  sys.stderr.close()
  sys.stdout=C2Log(TAG,sys.stdout)
  sys.stderr=sys.stdout

# -----------------------------------------------------------------------------
from CWIPI.CGNS.messages import messageTable
errorTable=messageTable

# --- last line
