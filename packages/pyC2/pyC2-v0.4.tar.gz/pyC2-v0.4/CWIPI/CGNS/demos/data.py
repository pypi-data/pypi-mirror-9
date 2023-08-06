# -------------------------------------------------------------------------
# CWIPI.CGNS - a CGNS/Python module for CWIPI
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------
import CGNS.PAT.cgnslib as CGL
import CGNS.PAT.cgnskeywords as CGK
import CGNS.PAT.cgnsutils as CGU
import CGNS.MAP
import numpy
import mpi4py.MPI as MPI

# ---
# this is a test case, all blocks have BC instead of BC & connectivities
# each block has 6 BCs, there is a base with only structured blocks and
# a base with unstructured blocks
# again, this is a test tree, this is not a usual CGNS pattern
#
SAVE=True

# ------------------------------------------------------------
imax=3
jmax=5
kmax=7

x=numpy.ones((imax,jmax,kmax),dtype='d',order='F')
y=numpy.ones((imax,jmax,kmax),dtype='d',order='F')
z=numpy.ones((imax,jmax,kmax),dtype='d',order='F')+2

for i in range(imax):
  for j in range(jmax):
    for k in range(kmax):
      x[i,j,k]=i
      y[i,j,k]=j
      z[i,j,k]=k

zsize=numpy.array([[imax,imax-1,0],[jmax,jmax-1,0],[kmax,kmax-1,0]],dtype='i',order='F')

T =CGL.newCGNSTree()
Tb=CGL.newCGNSBase(T,'Blocks:S',3,3)
Tf=CGL.newFamily(Tb,'ExchangeSurface')
Tu=CGL.newUserDefinedData(Tf,'DataInput')
Td=CGL.newDataArray(Tu,'Temperature')
Tu=CGL.newUserDefinedData(Tf,'DataOutput')
Td=CGL.newDataArray(Tu,'HeatFlux')
Tu=CGL.newUserDefinedData(Tf,'Mode')
Tf=CGL.newFamily(Tb,'ExchangeSurfaceStructured')
Tu=CGL.newUserDefinedData(Tf,'DataInput')
Td=CGL.newDataArray(Tu,'Temperature')
Tu=CGL.newUserDefinedData(Tf,'DataOutput')
Td=CGL.newDataArray(Tu,'HeatFlux')
Tu=CGL.newUserDefinedData(Tf,'Mode')
Tf=CGL.newFamily(Tb,'DOWN')
Tu=CGL.newFamilyBC(Tf,CGK.UserDefined_s)
Tf=CGL.newFamily(Tb,'EAST')
Tu=CGL.newFamilyBC(Tf,CGK.BCWallViscousIsothermal_s)
Tf=CGL.newFamily(Tb,'NORTH')
Tu=CGL.newFamilyBC(Tf,CGK.UserDefined_s)
Tf=CGL.newFamily(Tb,'WEST')
Tu=CGL.newFamilyBC(Tf,CGK.UserDefined_s)
Tf=CGL.newFamily(Tb,'SOUTH')
Tu=CGL.newFamilyBC(Tf,CGK.UserDefined_s)
Tf=CGL.newFamily(Tb,'UP')
Tu=CGL.newFamilyBC(Tf,CGK.UserDefined_s)

# ------------------------------------------------------------
Tn=CGL.newZone(Tb,'Block:01:A',zsize)
Tg=CGL.newGridCoordinates(Tn,CGK.GridCoordinates_s)
Tx=CGL.newDataArray(Tg,CGK.CoordinateX_s,x/11.)
Ty=CGL.newDataArray(Tg,CGK.CoordinateY_s,y/11.)
Tz=CGL.newDataArray(Tg,CGK.CoordinateZ_s,z/11.)
Tq=CGL.newZoneBC(Tn)
T1=CGL.newBC(Tq,'D',numpy.array([[1,   imax],[1,   jmax],[1,   1   ]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='DOWN')
T2=CGL.newBC(Tq,'E',numpy.array([[imax,imax],[1,   jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='EAST')
T3=CGL.newBC(Tq,'N',numpy.array([[1,   imax],[jmax,jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='NORTH')
CGU.newNode('SurfaceName',CGU.setStringAsArray('ExchangeSurface'),[],CGK.AdditionalFamilyName_ts,T3)
T4=CGL.newBC(Tq,'W',numpy.array([[1,   1,  ],[1,   jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='WEST')
T5=CGL.newBC(Tq,'S',numpy.array([[1,   imax],[1,   1   ],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='SOUTH')
T6=CGL.newBC(Tq,'U',numpy.array([[1,   imax],[1,   jmax],[kmax,kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='UP')
CGU.newNode('SurfaceOtherName',CGU.setStringAsArray('ExchangeSurfaceStructured'),[],CGK.AdditionalFamilyName_ts,T6)

# ------------------------------------------------------------
Tn=CGL.newZone(Tb,'Block:01:B',zsize)
Tg=CGL.newGridCoordinates(Tn,CGK.GridCoordinates_s)
Tx=CGL.newDataArray(Tg,CGK.CoordinateX_s,(x+imax-1)/11.)
Ty=CGL.newDataArray(Tg,CGK.CoordinateY_s,y/11.)
Tz=CGL.newDataArray(Tg,CGK.CoordinateZ_s,z/11.)
Tq=CGL.newZoneBC(Tn)
T1=CGL.newBC(Tq,'D',numpy.array([[1,   imax],[1,   jmax],[1,   1   ]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='DOWN')
T2=CGL.newBC(Tq,'E',numpy.array([[imax,imax],[1,   jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='EAST')
T3=CGL.newBC(Tq,'N',numpy.array([[1,   imax],[jmax,jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='NORTH')
CGU.newNode('SurfaceName',CGU.setStringAsArray('ExchangeSurface'),[],CGK.AdditionalFamilyName_ts,T3)
T4=CGL.newBC(Tq,'W',numpy.array([[1,   1,  ],[1,   jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='WEST')
CGU.newNode('SurfaceName',CGU.setStringAsArray('ExchangeSurface'),[],CGK.AdditionalFamilyName_ts,T4)
T5=CGL.newBC(Tq,'S',numpy.array([[1,   imax],[1,   1   ],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='SOUTH')
T6=CGL.newBC(Tq,'U',numpy.array([[1,   imax],[1,   jmax],[kmax,kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='UP')

# ------------------------------------------------------------
Tn=CGL.newZone(Tb,'Block:01:C',zsize)
Tg=CGL.newGridCoordinates(Tn,CGK.GridCoordinates_s)
Tx=CGL.newDataArray(Tg,CGK.CoordinateX_s,(x+2*(imax-1))/11.)
Ty=CGL.newDataArray(Tg,CGK.CoordinateY_s,y/11.)
Tz=CGL.newDataArray(Tg,CGK.CoordinateZ_s,z/11.)
Tq=CGL.newZoneBC(Tn)
T1=CGL.newBC(Tq,'D',numpy.array([[1,   imax],[1,   jmax],[1,   1   ]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='DOWN')
T2=CGL.newBC(Tq,'E',numpy.array([[imax,imax],[1,   jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='EAST')
T3=CGL.newBC(Tq,'N',numpy.array([[1,   imax],[jmax,jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='NORTH')
CGU.newNode('SurfaceName',CGU.setStringAsArray('ExchangeSurface'),[],CGK.AdditionalFamilyName_ts,T3)
T4=CGL.newBC(Tq,'W',numpy.array([[1,   1,  ],[1,   jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='WEST')
T5=CGL.newBC(Tq,'S',numpy.array([[1,   imax],[1,   1   ],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='SOUTH')
T6=CGL.newBC(Tq,'U',numpy.array([[1,   imax],[1,   jmax],[kmax,kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='UP')

# ------------------------------------------------------------
imax=7
jmax=5
kmax=3

x=numpy.ones((imax,jmax,kmax),dtype='d',order='F')
y=numpy.ones((imax,jmax,kmax),dtype='d',order='F')
z=numpy.ones((imax,jmax,kmax),dtype='d',order='F')+2

for i in range(imax):
  for j in range(jmax):
    for k in range(kmax):
      x[i,j,k]=i
      y[i,j,k]=j
      z[i,j,k]=k+imax-1

zsize=numpy.array([[imax,imax-1,0],[jmax,jmax-1,0],[kmax,kmax-1,0]],dtype='i',order='F')

Tn=CGL.newZone(Tb,'Block:02:A',zsize)
Tg=CGL.newGridCoordinates(Tn,CGK.GridCoordinates_s)
Tx=CGL.newDataArray(Tg,CGK.CoordinateX_s,x/11.)
Ty=CGL.newDataArray(Tg,CGK.CoordinateY_s,y/11.)
Tz=CGL.newDataArray(Tg,CGK.CoordinateZ_s,z/11.)
Tq=CGL.newZoneBC(Tn)
T1=CGL.newBC(Tq,'D',numpy.array([[1,   imax],[1,   jmax],[1,   1   ]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='DOWN')
CGU.newNode('SurfaceOtherName',CGU.setStringAsArray('ExchangeSurfaceStructured'),[],CGK.AdditionalFamilyName_ts,T1)
T2=CGL.newBC(Tq,'E',numpy.array([[imax,imax],[1,   jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='EAST')
T3=CGL.newBC(Tq,'N',numpy.array([[1,   imax],[jmax,jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='NORTH')
CGU.newNode('SurfaceName',CGU.setStringAsArray('ExchangeSurface'),[],CGK.AdditionalFamilyName_ts,T3)
T4=CGL.newBC(Tq,'W',numpy.array([[1,   1,  ],[1,   jmax],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='WEST')
T5=CGL.newBC(Tq,'S',numpy.array([[1,   imax],[1,   1   ],[1,   kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='SOUTH')
T6=CGL.newBC(Tq,'U',numpy.array([[1,   imax],[1,   jmax],[kmax,kmax]],dtype='i',order='F'),btype=CGK.FamilySpecified_s,family='UP')

# ------------------------------------------------------------
x=numpy.ones((imax,jmax,kmax),dtype='d',order='F')
y=numpy.ones((imax,jmax,kmax),dtype='d',order='F')
z=numpy.ones((imax,jmax,kmax),dtype='d',order='F')

for i in range(imax):
  for j in range(jmax):
    for k in range(kmax):
      x[i,j,k]=i
      y[i,j,k]=j
      z[i,j,k]=k-kmax+1

Tn=CGL.newZone(Tb,'Block:03:A',zsize)
Tg=CGL.newGridCoordinates(Tn,CGK.GridCoordinates_s)
Tx=CGL.newDataArray(Tg,CGK.CoordinateX_s,x/11.)
Ty=CGL.newDataArray(Tg,CGK.CoordinateY_s,y/11.)
Tz=CGL.newDataArray(Tg,CGK.CoordinateZ_s,z/11.)
Tq=CGL.newZoneBC(Tn)
T1=CGL.newBC(Tq,'D',numpy.array([[1,   imax],[1,   jmax],[1,   1   ]],
                                dtype='i',order='F'),
             btype=CGK.FamilySpecified_s,family='DOWN')
T2=CGL.newBC(Tq,'E',numpy.array([[imax,imax],[1,   jmax],[1,   kmax]],
                                dtype='i',order='F'),
             btype=CGK.FamilySpecified_s,family='EAST')
T3=CGL.newBC(Tq,'N',numpy.array([[1,   imax],[jmax,jmax],[1,   kmax]],
                                dtype='i',order='F'),
             btype=CGK.FamilySpecified_s,family='NORTH')
CGU.newNode('SurfaceName',CGU.setStringAsArray('ExchangeSurface'),[],CGK.AdditionalFamilyName_ts,T3)
T4=CGL.newBC(Tq,'W',numpy.array([[1,   1,  ],[1,   jmax],[1,   kmax]],
                                dtype='i',order='F'),
             btype=CGK.FamilySpecified_s,family='WEST')
T5=CGL.newBC(Tq,'S',numpy.array([[1,   imax],[1,   1   ],[1,   kmax]],
                                dtype='i',order='F'),
             btype=CGK.FamilySpecified_s,family='SOUTH')
T6=CGL.newBC(Tq,'U',numpy.array([[1,   imax],[1,   jmax],[kmax,kmax]],
                                dtype='i',order='F'),
             btype=CGK.FamilySpecified_s,family='UP')

# ------------------------------------------------------------
imax=7
jmax=5
kmax=11

# add some random delta to coords in order to force interpolation
def dc():
    return (0.5-numpy.random.random())/10.

x=numpy.ones((imax,jmax,kmax),dtype='d',order='F')
y=numpy.ones((imax,jmax,kmax),dtype='d',order='F')
z=numpy.ones((imax,jmax,kmax),dtype='d',order='F')+2

for i in range(imax):
  for j in range(jmax):
    for k in range(kmax):
      x[i,j,k]=i+dc()
      y[i,j,k]=j+jmax-1+dc()
      z[i,j,k]=k-2+dc()

# gets hexa index from structured
def topoIndex2D(imax,jmax,kmax,i,j,k,p=0):
  n1=(imax*jmax*(k+p))  +(imax*(j+p))  +i   +p+1
  n2=(imax*jmax*(k+p))  +(imax*(j+p))  +i+1 +p+1
  n3=(imax*jmax*(k+p))  +(imax*(j+1+p))+i+1 +p+1
  n4=(imax*jmax*(k+p))  +(imax*(j+1+p))+i   +p+1
  n5=(imax*jmax*(k+p+1))+(imax*(j+p))  +i   +p+1
  n6=(imax*jmax*(k+p+1))+(imax*(j+p))  +i+1 +p+1
  n7=(imax*jmax*(k+p+1))+(imax*(j+1+p))+i+1 +p+1
  n8=(imax*jmax*(k+p+1))+(imax*(j+1+p))+i   +p+1
  return (n1,n2,n3,n4,n5,n6,n7,n8)

hexa=[]
quad={'W':[],'E':[],'S':[],'N':[],'D':[],'U':[]}
n_hexas=0
n_quads=0
for i in range(imax-1):
  for j in range(jmax-1):
    for k in range(kmax-1):
      (n1,n2,n3,n4,n5,n6,n7,n8)=topoIndex2D(imax,jmax,kmax,i,j,k)
      hexa+=[n1,n2,n3,n4,n5,n6,n7,n8]
      n_hexas+=1
      if (i==0):
        quad['W']+=[n1,n5,n8,n4]
      if (i==imax-2):
        quad['E']+=[n2,n3,n7,n6]
      if (j==0):
        quad['S']+=[n1,n2,n6,n5]
      if (j==jmax-2):
        quad['N']+=[n3,n4,n8,n7]
      if (k==0):
        quad['D']+=[n1,n4,n3,n2]
      if (k==kmax-2):
        quad['U']+=[n5,n6,n7,n8]
      n_quads+=1

e=numpy.array(hexa,dtype='i')
n_points=imax*jmax*kmax
n_elems=n_hexas+n_quads

zsize=numpy.array([[n_points,n_elems,0]],dtype='i',order='F')
x=x.ravel(order='F')
y=y.ravel(order='F')
z=z.ravel(order='F')

Tb=CGL.newCGNSBase(T,'Blocks:U',3,3)
Tf=CGL.newFamily(Tb,'ExchangeSurface')
Tu=CGL.newUserDefinedData(Tf,'DataOutput')
Td=CGL.newDataArray(Tu,'Temperature')
Tu=CGL.newUserDefinedData(Tf,'DataIntput')
Td=CGL.newDataArray(Tu,'HeatFlux')
Tu=CGL.newUserDefinedData(Tf,'Mode')
Tf=CGL.newFamily(Tb,'DOWN')
Tu=CGL.newFamilyBC(Tf,CGK.UserDefined_s)
Tf=CGL.newFamily(Tb,'EAST')
Tu=CGL.newFamilyBC(Tf,CGK.BCWallViscousIsothermal_s)
Tf=CGL.newFamily(Tb,'NORTH')
Tu=CGL.newFamilyBC(Tf,CGK.UserDefined_s)
Tf=CGL.newFamily(Tb,'WEST')
Tu=CGL.newFamilyBC(Tf,CGK.UserDefined_s)
Tf=CGL.newFamily(Tb,'SOUTH')
Tu=CGL.newFamilyBC(Tf,CGK.UserDefined_s)
Tf=CGL.newFamily(Tb,'UP')
Tu=CGL.newFamilyBC(Tf,CGK.UserDefined_s)
Tn=CGL.newZone(Tb,'Block:04:A',zsize,ztype=CGK.Unstructured_s)
Tq=CGL.newZoneBC(Tn)
Tg=CGL.newGridCoordinates(Tn,CGK.GridCoordinates_s)
Tx=CGL.newDataArray(Tg,CGK.CoordinateX_s,x/11.)
Ty=CGL.newDataArray(Tg,CGK.CoordinateY_s,y/11.)
Tz=CGL.newDataArray(Tg,CGK.CoordinateZ_s,z/11.)
Te=CGL.newElements(Tn,'HEXA',CGK.HEXA_8,e,
                   erange=numpy.array([1,n_hexas],dtype='i'))

last_index=n_hexas+1
for n in ['WEST','EAST','NORTH','SOUTH','DOWN','UP']:
  e=numpy.array(quad[n[0]],dtype='i')
  n_quads=e.size/4
  erange=numpy.array([last_index,last_index+n_quads-1],dtype='i')
  last_index+=n_quads
  Te=CGL.newElements(Tn,'QUAD_%s'%n[0],CGK.QUAD_4_s,e,erange,eboundary=0)
  Tm=CGL.newBC(Tq,n[0],
               numpy.array([numpy.arange(erange[0],erange[1]+1)],dtype='i'),
               btype=CGK.FamilySpecified_s,
               pttype=CGK.PointList,
               family=n)
  if (n=='SOUTH'):
    CGU.newNode('SurfaceName',
                CGU.setStringAsArray('ExchangeSurface'),[],
                CGK.AdditionalFamilyName_ts,Tm)
  CGL.newGridLocation(Tm,CGK.FaceCenter_s)

bclist=[
  (1,   imax,1,   jmax,1,   1,   'DOWN'),
  (imax,imax,1,   jmax,1,   kmax,'EAST'),
  (1,   imax,jmax,jmax,1,   kmax,'NORTH'),
  (1,   1,   1,   jmax,1,   kmax,'WEST'),
  (1,   imax,1,   1,   1,   kmax,'SOUTH'),
  (1,   imax,1,   jmax,kmax,kmax,'UP')
  ]

if 0:
  last_index=n_hexas+1
  for (i1,i2,j1,j2,k1,k2,n) in bclist:
    quad=[]
    n_quads=0
    i2_=i2
    j2_=j2
    k2_=k2
    if (i1==i2): i2_=i2+1
    if (j1==j2): j2_=j2+1
    if (k1==k2): k2_=k2+1    
    for i in range(i1,i2_):
      for j in range(j1,j2_):
        for k in range(k1,k2_):
          (n1,n2,n3,n4,n5,n6,n7,n8)=topoIndex2D(imax,jmax,kmax,i-1,j-1,k-1)
          if ((i1==i2) and (i1==1)):    quad+=[n3,n4,n8,n7]
          if ((i1==i2) and (i1==imax)): quad+=[n1,n2,n6,n5]
          if ((j1==j2) and (j1==1)):    quad+=[n1,n5,n8,n4]
          if ((j1==j2) and (j1==jmax)): quad+=[n2,n3,n7,n6]
          if ((k1==k2) and (k1==1)):    quad+=[n1,n4,n3,n2]
          if ((k1==k2) and (k1==kmax)): quad+=[n5,n6,n7,n8]
          n_quads+=1
    e=numpy.array(quad,dtype='i')
    erange=numpy.array([last_index,last_index+n_quads-1],dtype='i')
    last_index+=n_quads
    Te=CGL.newElements(Tn,'QUAD_%s'%n[0],CGK.QUAD_4,e,erange,eboundary=0)
    Tm=CGL.newBC(Tq,n[0],
                 numpy.array([numpy.arange(erange[0],erange[1]+1)],dtype='i'),
                 btype=CGK.FamilySpecified_s,
                 pttype=CGK.PointList,
                 family=n)
    CGL.newGridLocation(Tm,CGK.FaceCenter_s)

# ------------------------------------------------------------
if (SAVE and not MPI.COMM_WORLD.rank):
  import os
  filename='blocks.hdf'
  if (os.path.exists(filename)): os.unlink(filename)
  CGNS.MAP.save(filename,T)

# --- last line
