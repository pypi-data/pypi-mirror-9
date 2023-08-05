#
# This file is part of TensorToolbox.
#
# TensorToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TensorToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with TensorToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

__all__ = ['TensorWrapper']

import sys
import time
import datetime
import logging
import operator
import itertools
import random
import shutil
import os.path
import numpy as np
import numpy.linalg as npla
import math
import scipy.linalg as scla
import marshal, types
import warnings
import h5py
try:
    import mpi_map
    MPI_SUPPORT = True
except ImportError:
    MPI_SUPPORT = False

from TensorToolbox.core import idxunfold, idxfold, storable_object

class TensorWrapper(storable_object):
    """ A tensor wrapper is a data structure W that given a multi-dimensional scalar function f(X,params), and a set of coordinates {{x1}_i1,{x2}_i2,..,{xd}_id} indexed by the multi index {i1,..,id}, let you access f(x1_i1,..,xd_id) by W[i1,..,id]. The function evaluations are performed "as needed" and stored for future accesses.

    :param f: multi-dimensional scalar function of type f(x,params), x being a list.
    :param list X: list of arrays with coordinates for each dimension
    :param tuple params: parameters to be passed to function f
    :param int Q: power to which round all the dimensions to.
    :param string twtype: 'array' values are stored whenever computed, 'view' values are never stored and function f is always called
    :param dict data: initialization data of the Tensor Wrapper (already computed entries)
    :param type dtype: type of output to be expected from f
    :param str store_file: file where to store the data
    :param object store_object: a storable object that must be stored in place of the TensorWrapper
    :param bool store_freq: how frequently to store the TensorWrapper (seconds)
    :param bool store_overwrite: whether to overwrite pre-existing files.
    :param bool empty: Creates an instance without initializing it. All the content can be initialized using the ``setstate()`` function.
    :param int maxprocs: Number of processors to be used in the function evaluation (MPI)
    :param bool marshal_f: whether to marshal the function or not

    """
    
    logger = logging.getLogger(__name__)
    logger.propagate = False
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s %(levelname)s:%(name)s: %(message)s",
                                  "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    def __init__(self, f, X, params=None, Q=None, twtype='array', data=None, dtype=object,
                 store_file = "", store_object = None, store_freq=None, store_overwrite=False,
                 empty=False,
                 maxprocs=None,
                 marshal_f=True):

        super(TensorWrapper,self).__init__(store_file, 
                                           store_freq=store_freq, 
                                           store_overwrite=store_overwrite)

        #######################################
        # List of attributes
        self.f_code = None               # Marshal string of the function f
        self.X = None
        self.params = None
        self.Q = None
        self.dtype = object
        self.shape = None
        self.ndim = None
        self.size = None
        self.twtype = None
        self.data = None

        self.serialize_list.extend( ['X', 'dtype', 'params', 'Q', 'shape', 'ndim', 'size', 'twtype', 'f_code'] )
        self.subserialize_list.extend( [] )

        # Attributes which are not serialized and need to be reset on reload
        self.__ghost_shape = None
        self.f = None
        self.store_object = None
        self.__maxprocs = None             # Number of processors to be used (MPI)

        self.fix_idxs = []
        self.fix_dims = []

        self.stored_keys = None # Set of stored keys (to improve the saving speed)
        # End list of attributes
        #################################
        
        self.stored_keys = set()
        if not empty: 
            self.set_f(f,marshal_f)
            self.params = params
            self.X = X
            self.Q = Q
            self.shape = self.get_shape()
            self.ndim = len(self.shape)
            self.size = self.get_size()
            self.twtype = twtype
            self.dtype = dtype

            self.set_store_object(store_object)

            self.set_maxprocs(maxprocs)
            if self.twtype == 'array':
                if data == None:
                    self.data = {} # Dictionary in python behave as a hash-table
                else:
                    self.data = data
            elif self.twtype != 'view':
                raise ValueError("Tensor Wrapper type not existent. Use 'array' or 'view'")
    
    def __getstate__(self):
        return super(TensorWrapper,self).__getstate__()
        
    def __setstate__(self,state,f = None, store_object = None):
        super(TensorWrapper,self).__setstate__( state, store_object )
        # Reset parameters
        if f == None: self.reset_f_marshal()
        else: self.set_f(f)
        self.set_store_object( store_object )
        self.fix_idxs = []
        self.fix_dims = []
        self.__maxprocs = None
        self.reset_shape()

    def getstate(self):
        return self.__getstate__();
    
    def setstate(self,state,f = None, store_object = None):
        return self.__setstate__(state, f, store_object)

    def h5store(self, h5file):
        # Store the data table in the h5 file. Update if possible.
        try:
            tw_grp = h5file['TW']
        except KeyError:
            # Create the group, the data structure and dump data
            if len(self.data) > 0:
                tw_grp = h5file.create_group('TW')
                tw_grp.create_dataset("keys", data=self.data.keys(), maxshape=(None,self.get_ndim()) )
                tw_grp.create_dataset("values", data=self.data.values(), maxshape=(None,)+self.data[self.data.keys()[0]].shape )
                self.stored_keys = set( self.data.keys() )
        else:
            # Increase the shape of the datasets to accommodate for the new data
            tw_grp["keys"].resize(len(self.data),axis=0)
            tw_grp["values"].resize(len(self.data),axis=0)

            # Store by data chunk
            N = 100000
            it = 0
            dvals = len(tw_grp["values"].shape)
            while len(self.stored_keys) < len(self.data):
                # Get the missing data
                new_data = dict(itertools.ifilter(lambda i:i[0] not in self.stored_keys, 
                                                  itertools.islice( self.data.iteritems(), 
                                                                    it*N, 
                                                                    min((it+1)*N,len(self.data)) 
                                                                    ) 
                                                  ))
                it += 1
                # Assign new values to the datasets
                tw_grp["keys"][len(self.stored_keys):len(self.stored_keys)+len(new_data),:] = new_data.keys()
                tw_grp["values"][ (slice(len(self.stored_keys),len(self.stored_keys)+len(new_data),None),) + tuple([slice(None,None,None)]*(dvals-1)) ] = new_data.values()
                self.stored_keys |= set( new_data.keys() )

    def h5load(self, h5file):
        try:
            tw_grp = h5file['TW']
        except KeyError:
            # The data structure is empty. Do nothing.
            pass
        else:
            # Load by data chunk
            N = 100000
            it = 0
            dvals = len(tw_grp["values"].shape)
            Ndata = tw_grp["keys"].shape[0]
            self.data = {}
            while len(self.data) < Ndata:
                keys = tw_grp["keys"][it*N:min((it+1)*N,Ndata), :]
                values = tw_grp["values"][ (slice(it*N, min((it+1)*N,Ndata),None),) + tuple([slice(None,None,None)]*(dvals-1))]
                def f(i,dvals=dvals):
                    return ( tuple(keys[i,:]), values[(i,) + tuple([slice(None,None,None)]*(dvals-1))] )
                self.data.update( itertools.imap( f, xrange(keys.shape[0]) ) )
                it += 1
            self.stored_keys = set( self.data.keys() )
    
    def to_v_0_3_0(self, store_location):
        """ Upgrade to v0.3.0
        
        :param string filename: path to the filename. This must be the main filename with no extension.
        """
        super(TensorWrapper,self).to_v_0_3_0(store_location)
        # Upgrade serialize list
        self.serialize_list.remove( 'data' )

    def copy(self):
        return TensorWrapper(self.f, self.X, params=self.params, twtype=self.twtype, data=self.data.copy())

    def set_Q(self, Q):
        self.Q = Q
        self.__ghost_shape = self.get_q_shape()
        self.update_shape()

    def get_size(self):
        """ Always returns the size of the tensor view
        
        .. note: use :py:meth:`TensorWrapper.get_global_size` to get the size of the original tensor
        """
        return reduce(operator.mul, self.get_shape(), 1)
    
    def get_ndim(self):
        """ Always returns the number of dimensions of the tensor view
        
        .. note: use :py:meth:`TensorWrapper.get_global_ndim` to get the number of dimensions of the original tensor
        """
        return len(self.get_shape())

    def get_shape(self):
        """ Always returns the shape of the actual tensor view
        
        .. note: use :py:meth:`TensorWrapper.get_global_shape` to get the shape of the original tensor
        """
        if self.__ghost_shape == None:
            dim = [ len(coord) for dim,coord in enumerate(self.X) if not (dim in self.fix_dims) ]
        else: 
            dim = [ s for dim,s in enumerate(self.__ghost_shape) if not (dim in self.fix_dims) ]
        return tuple(dim)
    
    def get_full_shape(self):
        """ Always returns the shape of the reshaped tensor tensor with no fixed indices
        """
        if self.__ghost_shape == None:
            dim = self.get_q_shape()
        else:
            dim = self.__ghost_shape
        return tuple(dim)

    def get_full_ndim(self):
        """ Always returns the ndim of the reshaped tensor tensor with no fixed indices
        """
        return len(self.get_full_shape())
    
    def get_full_size(self):
        """ Always returns the size of the reshaped tensor tensor with no fixed indices
        """
        return reduce(operator.mul, self.get_full_shape(), 1)

    def get_q_shape(self):
        """ Always returns the shape of the tensor rounded to the next power of Q if Q!=None. Otherwise returns the shape of the underlying tensor.
        """
        if self.Q == None:
            dim = self.get_global_shape()
        else:
            dim = [ self.Q**(int(math.log(s-0.5,self.Q))+1) for s in self.get_global_shape() ]
        return tuple( dim )
    
    def get_q_size(self):
        """Always returns the size of the tensor rounded to the next power of Q
        """
        return reduce(operator.mul, self.get_q_shape(), 1)
    
    def get_global_shape(self):
        """ Always returns the shape of the underlying tensor
        """
        dim = [ len(coord) for coord in self.X ]
        return tuple(dim)
    
    def get_global_ndim(self):
        """ Always returns the ndim of the underlying tensor
        """
        return len(self.get_global_shape())
    
    def get_global_size(self):
        """ Always returns the size of the underlying tensor
        """
        return reduce(operator.mul, self.get_global_shape(), 1)

    def get_fill_level(self):
        if self.twtype == 'view': return 0
        else: return len(self.data)

    def fix_indices(self, idxs, dims):
        """ Fix some of the indices in the tensor wrapper and reshape/resize it accordingly. The internal storage of the data is still done with respect to the global indices, but once some indices are fixed, the TensorWrapper can be accessed using just the remaining free indices.
        
        :param list idxs: list of indices to be fixed
        :param list dims: list of dimensions to which the indices refer to
        
        .. note: ``len(idxs) == len(dims)``
        """
        if len(idxs) != len(dims):
            raise AttributeError("TensorToolbox.TensorWrapper.fix_indices: len(idxs) == len(dims) violated")
        if len(dims) != len(set(dims)):
            raise AttributeError("TensorToolbox.TensorWrapper.fix_indices: the list of dimensions must contain unique entries only.")
        
        # Reorder the lists
        i_ord = sorted(range(len(dims)), key=dims.__getitem__)
        self.fix_idxs = [ idxs[i] for i in i_ord ]
        self.fix_dims = [ dims[i] for i in i_ord ]
        
        # Update shape, ndim and size
        self.update_shape()
    
    def release_indices(self):
        self.fix_idxs = []
        self.fix_dims = []
        self.update_shape()
    
    def update_shape(self):
        self.shape = self.get_shape()
        self.size = self.get_size()
        self.ndim = self.get_ndim()
    
    def reshape(self,newshape):
        if reduce(operator.mul, newshape, 1) == self.get_q_size():
            self.__ghost_shape = tuple(newshape)
        self.update_shape()
        return self
    
    def reset_shape(self):
        self.__ghost_shape = None
        self.update_shape()
    
    def full_to_q(self,idxs):
        return idxfold( self.get_q_shape(), idxunfold( self.get_full_shape(), idxs ) )
    
    def q_to_full(self,idxs):
        return idxfold( self.get_full_shape(), idxunfold( self.get_q_shape(), idxs ) )
    
    def q_to_global(self,idxs):
        """ This is a non-injective function from the q indices to the global indices
        """
        return tuple( [ ( i if i<N else N-1 ) for i,N in zip(idxs,self.get_global_shape()) ] )
    
    def global_to_q(self,idxs):
        """ This operation is undefined because one global idx can point to many q indices
        """
        if self.Q != None:
            raise NotImplemented("This operation is undefined because one global idx can point to many q indices")
        else:
            return idxs

    def global_to_full(self,idxs):
        return self.q_to_full( self.global_to_q( idxs ) )
    
    def full_to_global(self,idxs):
        return self.q_to_global( self.full_to_q( idxs ) )
    
    def get_fill_idxs(self):
        return self.data.keys()
    
    def get_data(self):
        return self.data
    
    def get_X(self):
        return self.X

    def get_params(self):
        return self.params
    
    def set_f(self,f,marshal_f=True):
        self.f = f
        if self.f != None and marshal_f:
            self.f_code = marshal.dumps(self.f.func_code)
    
    def reset_f_marshal(self):
        if self.f_code != None:
            code = marshal.loads(self.f_code)
            self.f = types.FunctionType(code, globals(), "f")
        else:
            warnings.warn("TensorToolbox.TensorWrapper: The tensor wrapper has not function code to un-marshal. The function is undefined. Define it using TensorToolbox.TensorWrapper.set_f", RuntimeWarning)
    
    def set_params(self, params):
        self.params = params
    
    def set_maxprocs(self,maxprocs):
        self.__maxprocs = maxprocs
        try:
            import mpi_map
            MPI_SUPPORT = True
        except ImportError:
            MPI_SUPPORT = False
        
        if self.__maxprocs != None and not MPI_SUPPORT:
            warnings.warn("TensorToolbox.TensorWrapper: MPI is not supported on this machine. The program will run without it.", RuntimeWarning)
        
    def set_store_object(self, store_object):
        self.store_object = store_object

    def __getitem__(self,idxs_in):
        # Transform the tuple to a list for convinience
        idxs_in = list(idxs_in)
        
        # Slice notation can be used. Remember: slice(start:stop:step)
        if len(idxs_in) != len(self.shape):
            raise IndexError('wrong number of indices')
        
        # Check that all the lists are of the same length
        int_idx = []
        llen = None
        for i,idx in enumerate(idxs_in):
            if isinstance(idx, int):
                int_idx.append(i)
            if isinstance(idx, list) or isinstance(idx,tuple):
                idxs_in[i] = list(idx)
                if llen == None:
                    llen = len(idx)
                elif llen != len(idx):
                    raise IndexError('List of indices must have the same length.')
        
        if llen == None: llen = 1

        # Expand single indices in idxs_in to llen
        for i in int_idx: idxs_in[i] = [idxs_in[i]] * llen

        # Update input indices of slices and lists
        list_idx_in = []
        slice_idx_in = []
        for i,idx in enumerate(idxs_in):
            if isinstance(idx, list) or isinstance(idx,tuple):
                list_idx_in.append(i)
            if isinstance(idx, slice):
                slice_idx_in.append(i)
        
        # Insert fixed indices
        for i in self.fix_dims:
            idxs_in.insert(i, [self.fix_idxs[self.fix_dims.index(i)]] * llen)

        # Construct list of indices which are lists and slices
        list_idx = []
        list_IDXs = []
        slice_idx = []
        slice_IDXs = []
        out_shape = []
        for i,idx in enumerate(idxs_in):
            if isinstance(idx, list) or isinstance(idx,tuple):
                list_idx.append(i)
                list_IDXs.append( idx )
            if isinstance(idx, slice):
                slice_idx.append(i)
                IDXs = range(idx.start if idx.start != None else 0,
                                 idx.stop  if idx.stop  != None else self.get_full_shape()[i],
                                 idx.step  if idx.step  != None else 1)
                slice_IDXs.append( IDXs )
                out_shape.append(len(IDXs))
        
        if len(list_idx) == 0: list_IDXs.append( [-1] ) # Ghost element added to make the full slicing work
        unlistIdxs = itertools.izip(*list_IDXs)

        transpose_list_shape = False
        if llen > 1: 
            out_shape.insert(0,llen)
            if len(slice_idx_in) > 0 and len(list_idx_in) > 0 and min(list_idx_in) > max(slice_idx_in):
                transpose_list_shape = True
        
        # Un-slice sliced idxs
        unslicedIdxs = itertools.product(*slice_IDXs)

        # Final list of indices (iterator)
        lidxs = itertools.product(unlistIdxs, unslicedIdxs)
        
        # Allocate output array
        if len(out_shape) > 0:
            out = np.empty(out_shape, dtype=self.dtype)
            
            # MPI code
            eval_is =[]
            eval_idxs = []
            eval_xx = []
            # End MPI code

            for i,(lidx,sidx) in enumerate(lidxs):
                # Reorder the idxs
                idxs = [None for j in range(len(idxs_in))]
                for j,jj in enumerate(list_idx): idxs[jj] = lidx[j]
                for j,jj in enumerate(slice_idx): idxs[jj] = sidx[j]
                idxs = tuple(idxs)

                # Map ghost indices to global indices
                idxs = self.full_to_global( idxs )
                
                # Separate field idxs from parameter idxs                
                if self.twtype == 'array':
                    # Check whether the value has already been computed
                    try:
                        out[idxfold(out_shape,i)] = self.data[idxs]
                    except KeyError:
                        if idxs not in eval_idxs:
                            # Evaluate function
                            xx = np.array( [self.X[ii][idx] for ii,idx in enumerate(idxs)] )
                            # MPI code
                            eval_is.append([i])
                            eval_idxs.append(idxs)
                            eval_xx.append(xx)
                            # End MPI code
                        else:
                            pos = eval_idxs.index(idxs)
                            eval_is[pos].append(i)

                else:
                    # Evaluate function
                    xx = np.array([self.X[ii][idx] for ii,idx in enumerate(idxs)])
                    out[idxfold(out_shape,i)] = self.f(xx,self.params)
            
            # Evaluate missing values
            if len(eval_xx) > 0:
                self.logger.debug(" [START] Num. of func. eval.: %d " % len(eval_xx))
                start_eval = time.time()
                if self.__maxprocs == None or not MPI_SUPPORT:
                    # Serial evaluation
                    for (ii,idxs,xx) in zip(eval_is, eval_idxs, eval_xx):
                        self.data[idxs] = self.f(xx,self.params)
                        self.store()
                        for i in ii:
                            out[idxfold(out_shape,i)] = self.data[idxs]
                else:
                    # MPI code
                    eval_res = mpi_map.mpi_map_code( self.f_code, eval_xx, self.params, self.__maxprocs )
                    for (ii,idxs,res) in zip(eval_is, eval_idxs, eval_res):
                        self.data[idxs] = res
                        for i in ii:
                            out[idxfold(out_shape,i)] = self.data[idxs]
                    self.store()
                    # End MPI code
                stop_eval = time.time()
                self.logger.debug(" [DONE] Num. of func. eval.: %d - Avg. time of func. eval.: %fs - Tot. time: %s" % (len(eval_xx),(stop_eval-start_eval)/len(eval_xx)*(min(self.__maxprocs,len(eval_xx)) if self.__maxprocs != None else 1), str(datetime.timedelta(seconds=(stop_eval-start_eval))) ))
            
            if transpose_list_shape:
                out = np.transpose( out , tuple( range(1,len(out_shape)) + [0] ) )
            
        else:
            idxs = tuple(itertools.chain(*lidxs.next()))
            # Map ghost indices to global indices
            idxs = self.full_to_global( idxs )
            if self.twtype == 'array':
                try:
                    out = self.data[idxs]
                except KeyError:
                    # Evaluate function
                    xx = np.array([self.X[ii][idx] for ii,idx in enumerate(idxs)])
                    self.data[idxs] = self.f(xx,self.params)
                    self.store()
                    out = self.data[idxs]
            else:
                out = self.f(np.array([self.X[ii][idx] for ii,idx in enumerate(idxs)]),self.params)
            return out
        
        return out
