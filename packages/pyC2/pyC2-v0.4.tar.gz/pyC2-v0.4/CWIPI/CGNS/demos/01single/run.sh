# set your own env here
#
export PYTHONEXEC=/home/tools/local/tiamat/bin/python
export CWIPI_INSTALL=/home/cwipi/opt/cwipi-0.6.4/tiamat_dbg
export PYC2_INSTALL=/tmp_user/tiamat/poinot/I
export PYTHONPATH=${CWIPI_INSTALL}/lib/python2.7/site-packages:${PYTHONPATH}
export PYTHONPATH=${PYC2_INSTALL}/lib/python2.7/site-packages:${PYTHONPATH}

mpirun \
-np 1 ${PYTHONEXEC} elsA_cwp.py : \
-np 1 ${PYTHONEXEC} fake_cwp.py


