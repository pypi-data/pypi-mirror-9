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

__all__ = ['QTTvec','QTTzerosvec']

import sys
import warnings
import logging 
import operator
import numpy as np
import math
import itertools

from TensorToolbox.core import TTvec, idxfold, idxunfold, TensorWrapper, matkron_to_mattensor
from TensorToolbox import multilinalg as mla

class QTTvec(TTvec):
    """ Constructor of multidimensional tensor in Quantics Tensor Train format
        
    :param ndarray,TensorWrapper,TT A: Available input formats are full tensor in numpy.ndarray, Tensor Wrapper, Tensor Train structure (list of cores)
    :param list global_shape: Argument to be provided if ``A`` is the list of cores of a TT format.
    :param int base: base selected to do the folding

    .. note: In the new version (>0.3.1): the tensor A is extended to the next power of base and then folded.
    .. note: (In the old version (<=0.3.1): The minimum folding base is always used.)
    """

    logger = logging.getLogger(__name__)
    logger.propagate = False
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s %(levelname)s:%(name)s: %(message)s",
                                  "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    def __init__(self,A, global_shape= None, base=2,
                 store_location="",store_object=None,store_freq=1, store_overwrite=False,
                 multidim_point=None):
        
        # Initialize the tensor with the input tensor in TT ([][]numpy.ndarray), tensor(numpy.ndarray)
        # if isinstance(A,Candecomp):
        #     self.TT = A.to_TT()
        
        super(QTTvec,self).__init__(A, 
                                    store_location=store_location,
                                    store_object=store_object,
                                    store_freq=store_freq,
                                    store_overwrite=store_overwrite,
                                    multidim_point=multidim_point)

        ###################################
        # List of attributes
        self.base = None
        self.global_shape = None
        self.q_shape = None
        self.folded_shape = None

        self.serialize_list.extend( ['base','global_shape','q_shape','folded_shape'] )
        # End list of attributes
        ##################################
        
        self.base = base
        
        if isinstance(self.A,np.ndarray) or isinstance(self.A, TensorWrapper):
            if global_shape != None: warnings.warn("TensorToolbox.QTTvec.__init__: shape argument is unnecessary for ndarray and TensorWrapper input", RuntimeWarning)
            
            self.global_shape = self.A.shape
            
            # Construct the base "base" shape
            self.q_shape = tuple( [ self.base**(int(math.log(s-0.5,self.base))+1) for s in self.get_global_shape() ] )
            if isinstance(self.A, np.ndarray):
                # Resize the array and fill the extended dimensions with data on the -1 hyper-faces
                Anew = np.zeros(self.q_shape)
                Anew[ tuple([ slice(0,gs,None) for gs in self.global_shape ]) ] = self.A
                for dcube in range(self.A.ndim):
                    cubes = itertools.combinations(range(self.A.ndim), dcube+1)
                    for cube in cubes:
                        idxs_out = []
                        idxs_in = []
                        for i, gs in enumerate(self.global_shape):
                            if i in cube:
                                idxs_out.append( slice(gs,None,None) )
                                idxs_in.extend( [-1,np.newaxis] )
                            else:
                                idxs_out.append( slice(0,gs,None) )
                                idxs_in.append( slice(0,gs,None) )
                        idxs_out = tuple(idxs_out)
                        idxs_in = tuple(idxs_in)
                        Anew[ idxs_out ] = self.A[ idxs_in ]
                self.A = Anew
            else:
                self.A.set_Q( base )
                
            # Set the folded_shape (list of list) for each dimension
            self.folded_shape = [ [self.base] * int(math.log(self.A.shape[i],self.base)) for i in xrange(len(self.global_shape)) ]
            
            # Folding matrix
            new_shape = [self.base] * int(math.log( self.A.size, self.base ))
            self.A = self.A.reshape(new_shape)
            
            # # Construct the folding shape
            # self.folded_shape = []
            # for sizedim in self.A.shape:
            #     new_subshape = []
            #     if sizedim == 1:
            #         new_subshape.append(sizedim)
            #     else:
            #         div = 1
            #         while sizedim != 1:
            #             div += 1
            #             while sizedim % div == 0:
            #                 sizedim /= div
            #                 new_subshape.append(div)
            #     self.folded_shape.append(new_subshape)
            
            # # Folding matrix
            # new_shape = list(itertools.chain(*self.folded_shape))
            # self.A = self.A.reshape(new_shape)

        elif isinstance(self.A,list):
            if global_shape == None: raise NameError("TensorToolbox.QTTvec.__init__: shape argument is mandatory for TT input")
            self.global_shape = global_shape

    def __getstate__(self):
        return super(QTTvec,self).__getstate__()
    
    def __setstate__(self,state):
        super(QTTvec,self).__setstate__( state )

    def build(self, eps=1e-10, method='svd', rs=None, fix_rank=False, Jinit=None, delta=1e-4, maxit=100, mv_eps=1e-6, mv_maxit=100, kickrank=None):
        """ Common interface for the construction of the approximation.

        :param float eps: [default == 1e-10] For method=='svd': precision with which to approximate the input tensor. For method=='ttcross': TT-rounding tolerance for rank-check.
        :param string method: 'svd' use singular value decomposition to construct the TT representation [1]_, 'ttcross' use low rank skeleton approximation to construct the TT representation [2]_, 'ttdmrg' uses Tensor Train Renormalization Cross to construct the TT representation [3]_ [4]_, 'ttdmrgcross' uses 'ttdmrg' with 'ttcross' approximation of supercores
        :param list rs: list of integer ranks of different cores. If ``None`` then the incremental TTcross approach will be used. (method=='ttcross')
        :param bool fix_rank: determines whether the rank is allowed to be increased (method=='ttcross')
        :param list Jinit: list of list of integers containing the r starting columns in the lowrankapprox routine for each core. If ``None`` then pick them randomly. (method=='ttcross')
        :param float delta: accuracy parameter in the TT-cross routine (method=='ttcross'). It is the relative error in Frobenious norm between two successive iterations.
        :param int maxit: maximum number of iterations in the lowrankapprox routine (method=='ttcross')
        :param float mv_eps: accuracy parameter for each usage of the maxvol algorithm (method=='ttcross')
        :param int mv_maxit: maximum number of iterations in the maxvol routine (method=='ttcross')
        :param bool fix_rank: Whether the rank is allowed to increase
        :param int kickrank: rank overshooting for 'ttdmrg'
        """
        
        if isinstance(self.A,np.ndarray) or isinstance(self.A, TensorWrapper):

            super(QTTvec,self).build( eps, method, rs, fix_rank, Jinit, delta, maxit, mv_eps, mv_maxit, kickrank)
            
        elif isinstance(self.A,list):
            
            super(QTTvec,self).build( eps, method, rs, fix_rank, Jinit, delta, maxit, mv_eps, mv_maxit, kickrank)

            shape = self.shape()

            # Check that the shape is consistent with the global_shape
            # and construct folded_shape
            self.folded_shape = []
            i_fold = 0
            for sizedim in self.global_shape:
                subshape = []
                if sizedim == 1:
                    if shape[i_fold] == 1:
                        subshape.append(1)
                        i_fold += 1
                    else:
                        raise AttributeError("TensorToolbox.QTTvec.__init__: the shape provided is not consistent with the shape of A #1")
                while sizedim != 1:
                    if sizedim % shape[i_fold] != 0:
                        raise AttributeError("TensorToolbox.QTTvec.__init__: the shape provided is not consistent with the shape of A #2")
                    else:
                        subshape.append(shape[i_fold])
                        sizedim /= shape[i_fold]
                        i_fold += 1
                self.folded_shape.append(subshape)
            
        else:
            raise NameError("TensorToolbox.TTvec.__init__: Input type not allowed")
        
        return self

    def copy(self):
        newTT = []
        for TTi in self.TT: newTT.append(TTi.copy())
        return QTTvec(newTT,list(self.global_shape)).build()

    def get_global_shape(self):
        """ Return the shape of the original tensor
        """
        return self.global_shape

    def get_global_ndim(self):
        """ Return the ndim of the original tensor
        """
        return len(self.global_shape)

    def get_folded_shape(self):
        """ Return the shape of the folded tensor (list of lists)
        """
        return self.folded_shape
    
    def get_q_shape(self):
        """ Return the shape of the base "base" shape of the tensor
        """
        if self.q_shape == None:
            return self.get_global_shape()
        else: 
            return self.q_shape

    def to_tensor(self):
        A = super(QTTvec,self).to_tensor()
        return A.reshape(self.get_q_shape())[ tuple([ slice(0,gs,None) for gs in self.get_global_shape() ]) ]
    
    def to_TTvec(self):
        icore = 0
        TTs = []
        for subshape,gs in zip(self.folded_shape,self.get_global_shape()):
            tmpcore = self.TT[icore]
            icore += 1
            for i in xrange(1,len(subshape)):
                tmpcore = np.tensordot( tmpcore, self.TT[icore], ( (tmpcore.ndim-1,),(0,) ) )
                icore += 1
            tmpcore = np.reshape( tmpcore, 
                                  (tmpcore.shape[0], 
                                   np.prod(tmpcore.shape[1:-1]), 
                                   tmpcore.shape[-1]) )
            # Truncate the core mode to the global_shape
            tmpcore = tmpcore[:,:gs,:]
            TTs.append(tmpcore)
        return TTvec(TTs).build()
    
    def q_to_full(self,idxs):
        return idxfold( self.shape(), idxunfold( self.get_q_shape(), idxs ) )
    
    def full_to_q(self,idxs):
        return idxfold( self.get_q_shape(), idxunfold( self.shape(), idxs ) )
    
    def q_to_global(self,idxs):
        """ This is a non-injective function from the q indices to the global indices
        """
        return tuple( [ ( i if i<N else N-1 ) for i,N in zip(idxs,self.get_global_shape()) ] )
    
    def full_to_global(self,idxs):
        return self.q_to_global( self.full_to_q( idxs ) )

    def get_ttdmrg_eval_idxs(self):
        idxs_full = super(QTTvec,self).get_ttdmrg_eval_idxs()
        idxs = [ self.full_to_global( idxs_full[i,:] ) for i in xrange(idxs_full.shape[0]) ]
        return np.asarray(idxs)

    def __getitem__(self,idxs):
        """ Get item function: indexes are entered in with respect to the unfolded mode sizes.
        """
        if not self.init: raise NameError("TensorToolbox.QTTvec.__getitem__: QTT not initialized correctly")
        
        # Check whether index out of bounds
        if any(map(operator.ge,idxs,self.get_global_shape())):
            raise NameError("TensorToolbox.QTTvec.__getitem__: Index out of bounds")

        # Compute the index of the folding representation from the unfolded representation
        return TTvec.__getitem__(self,idxfold(self.shape(),idxunfold(self.get_global_shape(),idxs)))
        
    def kron(self,A):
        if not self.init: raise NameError("TensorToolbox.QTTvec.kron: TT not initialized correctly")
        # Additional tests wrt the extend function of TTvec
        if not isinstance(A,QTTvec): raise NameError("TensorToolbox.QTTvec.kron: A is not of QTTvec type")
        if not A.init: raise NameError("TensorToolbox.QTTvec.kron: input tensor is not initialized correctly")
        
        self.TT.extend(A.TT)
        self.global_shape.extend(A.get_global_shape())
        self.folded_shape.extend(A.get_folded_shape())
    
    def interpolate(self, Ms=None,eps=1e-8,is_sparse=None):
        """ Interpolates the values of the QTTvec at arbitrary points, using the interpolation matrices ``Ms''.
        
        :param list Ms: list of interpolation matrices for each dimension. Ms[i].shape[1] == self.shape()[i]
        :param float eps: tolerance with which to perform the rounding after interpolation
        :param list is_sparse: is_sparse[i] is a bool indicating whether Ms[i] is sparse or not. If 'None' all matrices are non sparse [sparsity is not exploited]
        
        :returns: QTTvec interpolation
        :rtype: QTTvec

        >>> from DABISpectralToolbox import DABISpectral1D as S1D
        >>> Ms = [ S1D.LinearInterpolationMatrix(X[i],XI[i]) for i in range(d) ]
        >>> is_sparse = [True]*d
        >>> TTapproxI = TTapprox.interpolate(Ms,eps=1e-8,is_sparse=is_sparse)
        
        .. note: NOT WORKING! (Transform first to TTvec)
        """
        from TensorToolbox import QTTmat
        
        if not self.init: raise NameError("TensorToolbox.QTTvec.interpolate: QTT not initialized correctly")
        
        if len(Ms) != self.get_global_ndim():
            raise AttributeError("The length of Ms and the dimension of the TTvec must be the same!")

        d = len(Ms)
        for i in range(d):
            if Ms[i].shape[1] != self.get_global_shape()[i]:
                raise AttributeError("The condition  Ms[i].shape[1] == self.shape()[i] must hold.")                        

        # Construct the interpolating TTmat
        Ms0 = matkron_to_mattensor(Ms[0],[Ms[0].shape[0]],[Ms[0].shape[1]])
        TT_MND = QTTmat( Ms0, base=self.base, nrows=[Ms[0].shape[0]],ncols=[Ms[0].shape[1]] ).build()
        for M in Ms[1:]:
            Msi = matkron_to_mattensor(M,[M.shape[0]],[M.shape[1]])
            TT_M = QTTmat( Msi, base=self.base, nrows=[M.shape[0]],ncols=[M.shape[1]] ).build()
            TT_MND.kron( TT_M )
        
        # Perform interpolation
        return mla.dot(TT_MND,self).rounding(eps)

    def project(self, Vs=None, Ws=None, eps=1e-8,is_sparse=None):
        """ Project the QTTvec onto a set of basis provided, using the Generalized Vandermonde matrices ``Vs'' and weights ``Ws''.
        
        :param list Vs: list of generalized Vandermonde matrices for each dimension. Ms[i].shape[1] == self.shape()[i]
        :param list Ws: list of weights for each dimension. Ws[i].shape[0] == self.shape()[i]
        :param float eps: tolerance with which to perform the rounding after interpolation
        :param list is_sparse: is_sparse[i] is a bool indicating whether Ms[i] is sparse or not. If 'None' all matrices are non sparse [sparsity is not exploited]
        
        :returns: TTvec containting the Fourier coefficients
        :rtype: TTvec

        >>> from DABISpectralToolbox import DABISpectral1D as S1D
        >>> P = S1D.Poly1D(S1D.JACOBI,(0,0))
        >>> x,w = S1D.Quadrature(10,S1D.GAUSS)
        >>> X = [x]*d
        >>> W = [w]*d
        >>> # Compute here the TTapprox at points X
        >>> TTapprox = QTTvec(....)
        >>> # Project
        >>> Vs = [ P.GradVandermonde1D(x,10,0,norm=False) ] * d
        >>> is_sparse = [False]*d
        >>> TTfourier = TTapprox.project(Vs,W,eps=1e-8,is_sparse=is_sparse)

        .. note: NOT WORKING! (Transform first to TTvec)
        """
        from TensorToolbox import QTTmat
        
        if not self.init: raise NameError("TensorToolbox.QTTvec.project: QTT not initialized correctly")
        
        if len(Vs) != len(Ws) or len(Ws) != self.get_global_ndim():
            raise AttributeError("The length of Vs, Ms and the dimension of the QTTvec must be the same!")

        d = len(Vs)
        for i in range(d):
            if Vs[i].shape[1] != Ws[i].shape[0] or Ws[i].shape[0] != self.get_global_shape()[i]:
                raise AttributeError("The condition  Vs[i].shape[1] == Ws[i].shape[0] == self.get_global_shape()[i] must hold.")
        
        # Prepare matrices
        VV = [ Vs[i].T * np.tile(Ws[i],(Vs[i].shape[0],1)) for i in range(d) ]

        V0 = matkron_to_mattensor(VV[0], [VV[0].shape[0]], [VV[0].shape[1]])
        TT_MND = QTTmat(V0, base= self.base, nrows=[VV[0].shape[0]],ncols=[VV[0].shape[1]]).build()
        for V in VV[1:]:
            Vi = matkron_to_mattensor(V, [V.shape[0]], [V.shape[1]])
            TT_V = QTTmat(Vi, base= self.base, nrows=[V.shape[0]],ncols=[V.shape[1]]).build()
            TT_MND.kron( TT_V )
        
        # Perform projection
        return mla.dot(TT_MND,self).rounding(eps)
        
##########################################################
# Constructors of frequently used tensor vectors
##########################################################

def QTTzerosvec(d,N,base):
    """ Returns the rank-1 multidimensional vector of zeros in Quantics Tensor Train format
    
    Args:
       d (int): number of dimensions
       N (int or list): If int then uniform sizes are used for all the dimensions, if list of int then len(N) == d and each dimension will use different size
       base (int): QTT base
    
    Returns:
       QTTvec The rank-1 multidim vector of zeros in Tensor Train format
    """
    from TensorToolbox.core import Candecomp
    from TensorToolbox.core import zerosvec

    if isinstance(N,int):
        N = [N for i in range(d)]
    
    for sizedim in N:
        if np.remainder(math.log(sizedim)/math.log(base),1.0) > np.spacing(1):
            raise NameError("TensorToolbox.QTTvec.QTTzerosvec: base is not a valid base of N")
    
    L = int( np.around( math.log(np.prod(N))/math.log(base) ) )

    tt = zerosvec(L,[base for i in range(L)])

    return QTTvec(tt.TT, global_shape=N).build()
