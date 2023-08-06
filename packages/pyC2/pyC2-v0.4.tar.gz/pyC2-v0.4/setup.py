# -------------------------------------------------------------------------
# CWIPI.CGNS - a CGNS/Python module for CWIPI
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
from distutils.core import setup, Extension
import sys

try:
    import cwipi
except ImportError:
    pass
#   print "### pyC2: FATAL: cannot find cwipi..."

# -------------------------------------------------------------------------
setup (
name         = "CWIPI.CGNS",
description  = "CGNS/Python interface to CWIPI",
author       = "marc Poinot",
author_email = "marc.poinot@onera.fr",
license      = "LGPL 2",
packages     = ['CWIPI','CWIPI.CGNS','CWIPI.CGNS.demos'],
)

# --- last line
