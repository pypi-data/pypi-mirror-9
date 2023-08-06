# -------------------------------------------------------------------------
# CWIPI.CGNS - a CGNS/Python module for CWIPI
# See license.txt file in the root directory of this Python module source  
# -------------------------------------------------------------------------

import CGNS.PAT.cgnsutils as CGU
import CGNS.PAT.cgnskeywords as CGK
import CGNS.PAT.cgnsutils as CGU
import numpy
import error as CWE

try:
  import cwipi

  (STATIC,MOBILE)=(cwipi.STATIC_MESH,cwipi.MOBILE_MESH)
  (CELLCENTER,CELLVERTEX)=(cwipi.SOLVER_CELL_CENTER,cwipi.SOLVER_CELL_VERTEX)
  (PARAPART,PARANOPART,SEQUENTIAL)=\
        (cwipi.COUPLING_PARALLEL_WITH_PARTITIONING,\
         cwipi.COUPLING_PARALLEL_WITHOUT_PARTITIONING,\
         cwipi.COUPLING_SEQUENTIAL)
  MESH_TYPE_L =(STATIC,MOBILE)
  MESH_TYPE_S={'STATIC':STATIC,'MOBILE':MOBILE}
  MESH_TYPE_E={STATIC:'STATIC',MOBILE:'MOBILE'}

  import mpi4py.MPI as MPI

except ImportError:
    import os
    if (not os.environ.has_key('C2GENDOC')):
      raise CWE.C2Error(101)

"""The MESH_TYPE_L is the list of enumerate values for the type of mesh.
   Use this list to check a variable belongs to enumerate. The
   MESH_TYPE_S can be used to get the enumerate from string name of the
   value. The MESH_TYPE_E guives the string from the enumerate::

     if (v in MESH_TYPE_L):
       print MESH_TYPE_E[v]

"""

# ----------------------------------------------------------------------
class Attributes(dict):
  def __init__(self,framework):
    self._framework=framework
    super(Attributes,self).__init__(self)
  def __setitem__(self,att,value):
    if (self.setValue(att,value)):
      super(Attributes,self).__setitem__(att,value)
  def __getattr__(self,att):
    if (att in ['retrieve','publish']):
      return self._framework.updateAttribute
    elif (att in self.keys()): return self[att]
  def __setattr__(self,att,value):
    if (self.setValue(att,value)):
      super(Attributes,self).__setitem__(att,value)
  def setValue(self,att,value):
    if (att in self.keys()): return False
    if (isinstance(value,int)):
      cwipi.add_local_int_control_parameter(att,value)
    elif (isinstance(value,float)):
      cwipi.add_local_double_control_parameter(att,value)
    elif (isinstance(value,str)):
      cwipi.add_local_string_control_parameter(att,value)
    return True

# ----------------------------------------------------------------------
class Framework(object):
  """
  Support object for a CWIPI session or framework. All connections should
  be associated with at least one Framework.

  - Args:
   * `global_communicator`: MPI_COMM_WORLD
   * `framework_name`: Framework nickname, used for later reference

  - Returns:
   * `local_communicator`: the new MPI communicator used for connections
  
  - Remarks
   * Attributes are handled as dictionnary key as well as usual attribute

  .. code-block:: python

    fwk=C2.Framework(MPI.COMM_WORLD, "fake")
    fwk.attribute["path-%.4d"%count]=p
    fwk.attribute["nbzones"]=count

    print fwk.attribute['nbzones']
    print fwk.attribute.nbzones
  
   * `debug` mode can be set to have verbose trace on process.
  
  .. code-block:: python

    import mpi4py
    import CWIPI.CGNS
  
    fwk=CWIPI.CGNS.Framework(mpi4py.MPI_COMM_WORLD,'Fluid/Structure')
    fwk.debug=True
     
  """
  def __init__(self,framework_name,global_communicator=None,debug=False):
    if (not isinstance(framework_name,str)): raise CWE.C2Error(102)
    if (framework_name==''): raise CWE.C2Error(103)
    if (global_communicator is None): global_communicator=MPI.COMM_WORLD
    self._debug=True
    if (not self._debug): CWE.close_std()
    self._wcomm=global_communicator
    self._lcomm=cwipi.init(global_communicator,framework_name)
    self._name=framework_name
    self._attributes=Attributes(self)
  @property
  def name(self):
    """Framework name, as passed as argument at init
    """
    return self._name
  @property
  def rank(self):
    return self._lcomm.Get_rank()
  @property
  def size(self):
    return self._lcomm.Get_size()
  @property
  def local_communicator(self):
    return self._lcomm
  @property
  def debug(self):
    return self._debug
  @debug.setter
  def debug(self,value):
    if (value not in [False,True]): return
    self._debug=value
  @property
  def attribute(self):
    return self._attributes
  def trace(self,p):
    if (not self._debug): print p
    else:
      s="%s%s"%(CWE.TAG,p)
      print s
  def __del__(self):
    pass
    # cwipi.finalize() # perform into Connection object
  def updateAttribute(self,remotename,attribute):
    cwipi.get_local_string_control_parameter(attribute)
    cwipi.synchronize_control_parameter(remotename)

# ----------------------------------------------------------------------
class Connection(object):
  """
  Support object containing the actual CWIPI coupling object

  * Args:
   - framework: cwipi framework object
   - name:     nickname of connection object
   - application:  nickname of target application to be coupled
   - coupling: one of (PARAPART,PARANOPART,SEQUENTIAL)
   - mesh:     one of (STATIC,MOBILE)
   - solver:   one of (CELLCENTER,CELLVERTEX)
   - tolerance :

  * Remarks:
   - Default family name for surface detection is *SurfaceExchange*,
     this should be the name of an `AdditionalFamily_t` in all `BC_t`
     defining the coupling surface.

  """
  def __init__(self,
               framework,
               name,
               application,
               tree,
               basename,
               surfacename="SurfaceExchange",
               mesh=STATIC,
               solver=CELLVERTEX,
               mode=PARAPART,
               zonelist=None):
    if (tree is None): raise CWE.C2Error(200)
    if (not isinstance(name,str)): raise CWE.C2Error(210)
    if (name==''): raise CWE.C2Error(211)
    if (not isinstance(application,str)): raise CWE.C2Error(212)
    if (application==''): raise CWE.C2Error(213)
    if (not isinstance(surfacename,str)): raise CWE.C2Error(214)
    if (surfacename==''): raise CWE.C2Error(215)
    self._framework=framework
    self._name=name
    self._application=application
    self._mesh=mesh
    self._solver=solver
    self._mode=mode
    self._tolerance=0.1
    self._c_coordinates=None
    self._c_strides=None
    self._c_elements=None
    self._basename=basename
    self._family=surfacename
    self._tree=tree
    self._zonelist=zonelist
    self._c_tagcount=0
    cwipi.synchronize_control_parameter(self._application)
    self._proxy=cwipi.Coupling(self._name,self._mode,self._application,
                                2,self._tolerance,  
                                self._mesh,self._solver,
                                1,"EnSight","text")
    self.defineFromFamily(tree,basename,surfacename,zonelist)
    
  # ------------------------------------------------------------
  @property
  def framework(self):
    return self._framework
  @property
  def name(self):
    return self._name
  @property
  def mesh(self):
    """Returns the type of the mesh, one of (STATIC,MOBILE)
    """
    return self._mesh
  @property
  def solver(self):
    """Returns the type of solver, one of (CELLCENTER,CELLVERTEX)
    """
    return self._solver
  @property
  def mode(self):
    """Returns the mode of coupling, one of (PARAPART,PARANOPART,SEQUENTIAL)
    """
    return self._mode
  @property
  def tolerance(self):
    return self._tolerance
  @property
  def debug(self):
    return self._framework.debug()
  @property
  def proxy(self):
    return self._proxy
  @property
  def located(self):
    return self._c_located
  def cgns_to_cwipi(self,zone=None):
    """
    Gives the mapping to/from CGNS/CWIPI.
    Without args you have the full index_cwipi_to_cgns data.
    index_cwipi_to_cgns is a tuple of a list of strings (zone names) and
    a 2 dims ndarray. The first dim gives the zone name index in the list
    of names, the second gives the index of the point in the CGNS zone
    coordinates (as 1D array). For example:
    index_cwipi_to_cgns=(['/B/Z1','/B/Z2'],[ [0,28], [0,29], [1,42] ... ]
    means the point index 2 for cwipi is the point 42 in /B/Z2.flat

    If you give a zone name as arg, you get a 2D array with cwipi index
    as first and cgns index as second for the selected zone.
    """
    if (zone is None): return self._to_cwipi
    else:
      if (zone not in self._to_cwipi[0]): return None
      if (self._to_cwipi[1] is None): return None
      zidx=self._to_cwipi[0].index(zone)
      sdata=(self._to_cwipi[1][0,:]==zidx)
      cindex=numpy.arange(self._to_cwipi[1].shape[1])
      t=numpy.ones((2,sdata.size,),dtype='i')
      t[0,:]=cindex[sdata]
      t[1,:]=self._to_cwipi[1][1,sdata]
      return t

  # ------------------------------------------------------------
  def getDataFromFamily(self,T,basename,familyname):
    """Parse a CGNS/Python tree, returns `DataInput` and `DataOutput`.
    """
    s=[]
    searchpath=[CGK.CGNSTree_ts,basename,familyname]
    flist=CGU.getAllNodesByTypeOrNameList(T,searchpath)
    di=None
    do=None
    if (flist):
      di=CGU.getNodeByPath(T,flist[0]+'/DataInput')
      do=CGU.getNodeByPath(T,flist[0]+'/DataOutput')
    return (di,do)
        
  # ------------------------------------------------------------
  def getSurfaceFromFamily(self,T,basename,familyname,zonelist):
    """Parse a CGNS/Python tree and gather all BC with familyname as
    additionalfamily. Then merges the coordinates and rebuilds the
    element indices to have a single unstructured surface.

    The application has to use
    the index_cwipi_to_cgns to access to actual
    data to/from CGNS and cwipi in the coupling scripts.
    See cgns_to_cwipi
    """
    s=[]
    if (zonelist is None):
      searchpath=[CGK.CGNSTree_ts,basename,CGK.Zone_ts,
                  CGK.ZoneBC_ts,CGK.BC_ts,CGK.AdditionalFamilyName_ts]
      plist=CGU.getAllNodesByTypeOrNameList(T,searchpath)
    else:
      plist=[]
      for zname in zonelist:
        searchpath=[CGK.CGNSTree_ts,basename,zname,
                    CGK.ZoneBC_ts,CGK.BC_ts,CGK.AdditionalFamilyName_ts]
        plist+=CGU.getAllNodesByTypeOrNameList(T,searchpath)
    if (not plist): return None
    for p in plist:
        zn=CGU.getPathAncestor(p,level=3)
        zt=CGU.getPathAncestor(p,level=3)+'/'+CGK.ZoneType_s
        gr=CGU.getPathAncestor(p,level=3)+'/'+CGK.GridCoordinates_s
        pr=CGU.getPathAncestor(p,level=1)+'/'+CGK.PointRange_s
        pl=CGU.getPathAncestor(p,level=1)+'/'+CGK.PointList_s
        cx=gr+'/'+CGK.CoordinateX_s
        cy=gr+'/'+CGK.CoordinateY_s
        cz=gr+'/'+CGK.CoordinateZ_s
        n=CGU.getNodeByPath(T,pr)
        p=True
        if (n is None):
          n=CGU.getNodeByPath(T,pl)
          p=False
        x=CGU.getNodeByPath(T,cx)
        y=CGU.getNodeByPath(T,cy)
        z=CGU.getNodeByPath(T,cz)
        t=CGU.getNodeByPath(T,zt)
        if (CGU.stringValueMatches(t,CGK.Structured_s)):
          if (not p): # structured/pointlist
            pass 
          else:       # structured/pointrange
            ix=n[1]
          s+=[self.getSurfaceAsUnstructured(x[1],y[1],z[1],ix,zn)]
        else:
          searchpath=[CGK.CGNSTree_ts,basename,CGK.Zone_ts,CGK.Elements_ts]
          enlist=CGU.getAllNodesByTypeOrNameList(T,searchpath)
          el=[]
          for en in enlist:
            ee=CGU.getNodeByPath(T,en)
            er=CGU.hasChildName(ee,CGK.ElementRange_s)[1]
            ec=CGU.hasChildName(ee,CGK.ElementConnectivity_s)[1]
            el+=[(er,ec)]
          if (not p):  # unstructured/pointlist
            ix=n[1] 
          else:        # unstructured/pointrange
            ix=numpy.arange(n[1][0],n[1][1]+1) 
          s+=[self.getSurface(x[1],y[1],z[1],ix,el,zn)]
    return self.mergeAndReindex(s)
  # ------------------------------------------------------------
  def getSurface(self,acx,acy,acz,plist,el,zname):
    """Uses a BC on unstructured grid to build a surface, extract
    corresponding coordinates for x,y and z arrays. there is a re-indexing
    so that a correspondance index is returned. 
    """
    sz=plist.size*4
    ex=0
    x=[]
    y=[]
    z=[]
    q=[]
    index_cwipi_to_cgns={zname:numpy.zeros((2,plist.size),dtype='i')}
    for p in plist[0]:
      for e in el:
        if ((p>=e[0][0]) or (p<=e[0][1])): # only QUADs
          ei=p-e[0][0]+1
          pt=e[1][ei*4:(ei+1)*4]
          x+=list(acx[pt])
          y+=list(acy[pt])
          z+=list(acz[pt])
          q+=list(pt)
          index_cwipi_to_cgns[zname][1,ex]=pt
          ex+=1
          break
    cx=numpy.array(x)
    cy=numpy.array(y)
    cz=numpy.array(z)
    ct=numpy.array(q)
    nodelist=numpy.concatenate([cx,cy,cz])
    nodelist.reshape((3,sz)).T.reshape((sz*3,))
    return (nodelist,ct,index_cwipi_to_cgns)
    
  # ------------------------------------------------------------
  def getSurfaceAsUnstructured(self,acx,acy,acz,plist,zname): 
    """Uses a BC on structured grid to build a surface, extract
    corresponding coordinates for x,y and z arrays. Add a QUAD elements index.
    The result, points and elements, is used as the exchange basis for
    CWIPI, the input/ouput arrays should use this result index to
    read/write data.
    """
    (ri1,ri2)=(plist[0][0],plist[0][1])
    (rj1,rj2)=(plist[1][0],plist[1][1])
    (rk1,rk2)=(plist[2][0],plist[2][1])
    imax=ri2-ri1+1
    jmax=rj2-rj1+1
    kmax=rk2-rk1+1
    if (not numpy.isfortran(acx)): return (None,None)
    shp=acx.shape
    cx=acx
    cy=acy
    cz=acz
    itmax=shp[0]
    jtmax=shp[1]
    ktmax=shp[2]
    idx=numpy.arange(itmax*jtmax*ktmax).reshape(itmax,jtmax,ktmax)
    if (not (ri2-ri1)):
      bcx=cx[ri1-1,rj1-1:rj2,rk1-1:rk2]
      bcy=cy[ri1-1,rj1-1:rj2,rk1-1:rk2]
      bcz=cz[ri1-1,rj1-1:rj2,rk1-1:rk2]
      amax=jmax
      bmax=kmax
      index=idx[ri1-1,rj1-1:rj2,rk1-1:rk2].ravel()
    if (not (rj2-rj1)):
      bcx=cx[ri1-1:ri2,rj1-1,rk1-1:rk2]
      bcy=cy[ri1-1:ri2,rj1-1,rk1-1:rk2]
      bcz=cz[ri1-1:ri2,rj1-1,rk1-1:rk2]
      amax=imax
      bmax=kmax
      index=idx[ri1-1:ri2,rj1-1,rk1-1:rk2].ravel()
    if (not (rk2-rk1)):
      bcx=cx[ri1-1:ri2,rj1-1:rj2,rk1-1]
      bcy=cy[ri1-1:ri2,rj1-1:rj2,rk1-1]
      bcz=cz[ri1-1:ri2,rj1-1:rj2,rk1-1]
      amax=imax
      bmax=jmax
      index=idx[ri1-1:ri2,rj1-1:rj2,rk1-1].ravel()
    nodelist=numpy.zeros(amax*bmax*3,dtype='d')
    elemlist=numpy.zeros((amax-1)*(bmax-1)*4,dtype='i')
    index_cwipi_to_cgns={zname:numpy.zeros((2,amax*bmax),dtype='i')}
    for a in xrange(0,amax):
      for b in xrange(0,bmax):
         nodelist[(a*bmax+b)*3+0]=bcx[a,b]
         nodelist[(a*bmax+b)*3+1]=bcy[a,b]
         nodelist[(a*bmax+b)*3+2]=bcz[a,b]
         index_cwipi_to_cgns[zname][1,a*bmax+b]=index[a*bmax+b]
    for a in xrange(0,amax-1):
      for b in xrange(0,bmax-1):
         (n1,n2,n3,n4)=self.topoIndex2D(amax,bmax,a+1,b+1)
         elemlist[(a*(bmax-1)+b)*4+0]=n1
         elemlist[(a*(bmax-1)+b)*4+1]=n2
         elemlist[(a*(bmax-1)+b)*4+2]=n3
         elemlist[(a*(bmax-1)+b)*4+3]=n4
    return (nodelist,elemlist,index_cwipi_to_cgns)

  # ------------------------------------------------------------
  def mergeAndReindex(self,surface):
    """Add the offset to elements index in the case of multiple BC surface.
    """
    scoords=[]
    sindex=[]
    zlist=[]
    tindex=[]
    eoffset=0
    for s in surface:
      zname=s[2].keys()[0]
      if (zname not in zlist): zlist.append(zname)
      zidx=zlist.index(zname)
      s[2][zname][0,:]=zidx
      scoords.append(s[0])
      sindex.append(s[1]+eoffset)
      tindex.append(s[2][zname])
      eoffset=max(s[1])
    index_cwipi_to_cgns=(zlist,numpy.concatenate(tindex,axis=1))
    return (numpy.concatenate(scoords),
            numpy.concatenate(sindex),
            index_cwipi_to_cgns)

  # ------------------------------------------------------------
  def topoIndex2D(self,imax,jmax,a,b):
    """Return the QUAD element index from structured index
    """
    n1=(a-1)*jmax +1 +(b-1)
    n2=(a-1)*jmax +1 + b
    n3= a   *jmax +1 + b
    n4= a   *jmax +1 +(b-1)
    return (n1,n2,n3,n4)

  # ------------------------------------------------------------
  def defineFromFamily(self,T,basename,surfacename=None,zonelist=None):
    """Parse the CGNS/Python tree to get the coupling surface, call
    CWIPI definition function on this surface.
    If zonelist is not None, then only use surfaces defined for set of zone
    (zone name only).
    """
    dist=self._framework.attribute.distribution
    if ((zonelist is None) and (dist is not None)):
      zonelist=['/'+z for z in dist if dist[z]==self._framework.rank]
    s=self.getSurfaceFromFamily(T,basename,surfacename,zonelist)
    if (s is None):
      coords=numpy.zeros((0,))
      constp=numpy.zeros((1,),dtype='i')
      conelt=numpy.zeros((0,),dtype='i')
      self._to_cwipi=(zonelist,None)
      self._proxy.define_mesh(0,0,coords,constp,conelt)
    else:
      d=self.getDataFromFamily(T,basename,surfacename)
      self._to_cwipi=s[2]
      coords=numpy.copy(s[0])
      constp=numpy.arange(s[1].size+1,step=4,dtype='i')
      conelt=s[1]
      self._proxy.define_mesh(coords.size/3,# number of vertices (nodes)
                               conelt.size/4,# number of elements
                               coords,       # coords as interlaced pattern
                               constp,       # vertices index range 
                               conelt)       # points connectivity/elt
    self._proxy.locate()
    self._c_coordinates=coords
    self._c_strides=constp
    self._c_elements=conelt
    self._c_located=self._proxy.get_n_located_points()
    self._c_unlocated=self._proxy.get_n_not_located_points()
    return (self._c_located,self._c_unlocated)

  # ------------------------------------------------------------
  def publishAndRetrieve(self,send_array,iteration=1,time=1.0):
    sz=self._proxy.get_n_located_points()
    recv_array=numpy.ones((sz,),dtype='d')
    r=self._proxy.exchange(self._family,
                            1,iteration,time,
                            "field_s",send_array,
                            "field_r",recv_array)
    return recv_array
  
  # ------------------------------------------------------------
  def publish(self,send_array,tag=None,iteration=1,time=1.0):
    sz=self._proxy.get_n_located_points()
    recv_array=numpy.ones((sz,),dtype='d')
    if (tag is None):
      tag=self._c_tagcount
    r=self._proxy.issend(self._family,tag,1,iteration,time,"field_s",send_array)
    self._proxy.wait_irecv(r['request'])
    return recv_array
  
  # ------------------------------------------------------------
  def retrieve(self,tag=None,iteration=1,time=1.0):
    sz=self._proxy.get_n_located_points()
    recv_array=numpy.ones((sz,),dtype='d')
    if (tag is None):
      tag=self._c_tagcount
      self._c_tagcount+=1
    r=self._proxy.irecv(self._family,tag,1,iteration,time,"field_r",recv_array)
    self._proxy.wait_issend(r['request'])
    return recv_array
  # ------------------------------------------------------------
  def __del__(self):
    pass
    #cwipi.finalize()

# --- last line
