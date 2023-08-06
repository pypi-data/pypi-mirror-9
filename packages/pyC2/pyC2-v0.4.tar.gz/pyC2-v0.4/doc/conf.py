# -------------------------------------------------------------------------
# CWIPI.CGNS - a CGNS/Python module for CWIPI
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------

# to be run with:
# export C2GENDOC
# export PYTHONEXEC=/home/tools/local/tiamat/bin/python
# export CWIPI_INSTALL=/home/cwipi/opt/cwipi-0.6.4/tiamat_dbg
# export PYC2_INSTALL=/tmp_user/tiamat/poinot/I
# export PYTHONPATH=${CWIPI_INSTALL}/lib/python2.7/site-packages:${PYTHONPATH}
# export PYTHONPATH=${PYC2_INSTALL}/lib/python2.7/site-packages:${PYTHONPATH}
# C2GENDOC=1 1 sphinx-build -c doc -b html doc build/html doc/index.txt
# in the parent directory of this file


extensions = ['sphinx.ext.autodoc']
master_doc='index'
project = u'CWIPI.CGNS'
copyright = u'2013-, Marc Poinot'
version = '0'
release = '0.4'
unused_docs = ['license.txt']
source_suffix = '.txt'

pygments_style = 'sphinx'
html_title = "pyC2"
html_use_index = True

latex_paper_size = 'a4'
latex_font_size = '10pt'
latex_documents = [
  ("pyC2",
   'index.tex',
   u'pyC2 - CWIPI.CGNS Manual',
   u'Marc Poinot',
   'manual',False),
]
latex_use_parts = False
latex_use_modindex = True

autodoc_member_order='bysource'
autodoc_default_flags=['members', 'undoc-members']

# --- last line
