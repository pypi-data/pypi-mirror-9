# Copyright (C) 2015  Randy Direen <spherepy@direentech.com>
#
# This file is part of SpherePy.
#
# SpherePy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SpherePy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SpherePy.  If not, see <http://www.gnu.org/licenses/>

import numpy as np
import numbers
import pysphi
from functools import wraps



"""***************************************************************************
                            Objects
***************************************************************************"""

scalar = 0
vector = 1

class SpherePyError(Exception):
    pass

class ScalarCoefs:
    """Holds the scalar coefficients that represent a spherical pattern the 
    function spht returns this object"""
    def __init__(self,vec,nmax,mmax):

        self._vec = vec
        self._nmax = nmax
        self._mmax = mmax

    @property
    def nmax(self):
        return self._nmax

    @property
    def mmax(self):
        return self._mmax

    def _array_2d_repr(self):
        """creates a 2D array that has nmax + 1 rows and 2*mmax + 1 columns
        and provides a representation for the coefficients that makes 
        plotting easier"""

        sc_array = np.zeros((self.nmax + 1,2*self.mmax + 1),
                            dtype = np.complex128)

        lst = self._reshape_n_vecs()
        sc_array[0:self.nmax + 1,self.mmax] = lst[0]
        for m in xrange(1,self.mmax + 1):
            sc_array[m:self.nmax + 1,self.mmax - m] = lst[2*m - 1]
            sc_array[m:self.nmax + 1,self.mmax + m] = lst[2*m]

        return sc_array

    def _reshape_n_vecs(self):
        """return list of arrays, each array represents a different m mode"""

        lst = []
        sl = slice(None,None,None)
        lst.append(self.__getitem__((sl,0)))
        for m in xrange(1,self.mmax +1):
            lst.append(self.__getitem__((sl,-m)))
            lst.append(self.__getitem__((sl,m)))
        return lst

    def _reshape_m_vecs(self):
        """return list of arrays, each array represents a different n mode"""
        
        lst = []
        for n in xrange(0,self.nmax+1):
            mlst = []
            if n <= self.mmax:
                nn = n
            else:
                nn = self.mmax            
            for m in xrange(-nn,nn+1):
                mlst.append(self.__getitem__((n,m)))
            lst.append(mlst)
        return lst

    def __repr__(self):
        rs = self._reshape_m_vecs()
        return "scalar_coef((nmax = %d, mmax = %d) , %s )" % (self.nmax,
                                                            self.mmax,
                                                            str(rs))

    def __str__(self):
        rs = self._reshape_m_vecs()
        st = "scalar_coef(nmax = %d, mmax = %d):" % (self.nmax,
                                                      self.mmax)
        st += "\n"
        for n,x in enumerate(rs):
            st += "n = "+ str(n) +" :: " + str(x)
            st +="\n"
        return st

    def __setitem__(self,arg,val):
        if len(arg) == 2:

            if (type(arg[0]) is slice) and (type(arg[1]) is int):

                m = arg[1]

                if (arg[0].start == None) and   \
                   (arg[0].step == None) and    \
                   (arg[0].stop == None):

                    if np.abs(m) > self._mmax:
                        raise AttributeError("m value out of bounds")

                    idx_start = pysphi.mindx(m,self.nmax,self.mmax)
                    idx_stop = idx_start + self.nmax - np.abs(m) + 1

                    L = len(self._vec[idx_start:idx_stop])
                    if len(val) != L:
                        raise AttributeError("dimension mismatch")
                    else:
                        self._vec[idx_start:idx_stop] = val
                else:
                    raise AttributeError("slicing operation not permitted")

            elif (type(arg[0]) is int) and (type(arg[1]) is slice):
                
                n = arg[0]

                if (arg[1].start == None) and   \
                   (arg[1].step == None) and    \
                   (arg[1].stop == None):

                    if (n > self.nmax) or (n < 0):
                        raise AttributeError("n value out of bounds")

                    if (len(val) != 2*n + 1):
                        raise ArithmeticError("dimension mismatch")

                    if n <= self.mmax:
                        nn = n
                    else:
                        nn = self.mmax            
                    for k,m in enumerate(xrange(-nn,nn+1)):
                        self.__setitem__((n,m),val[k])

                else:
                    raise AttributeError("slicing operation not permitted")

            elif (type(arg[0]) is int) and (type(arg[1]) is int):

                n = arg[0]
                m = arg[1]

                if (n < 0) or (n > self._nmax):
                    raise AttributeError("n value out of bounds")

                if (np.abs(m) > n) or (np.abs(m) > self._mmax):
                    raise AttributeError("m value out of bounds")

                idx = pysphi.mindx(m,self.nmax,self.mmax) + n - np.abs(m)

                self._vec[idx] = val

            else:
                raise AttributeError("what?, indexing method not recognized")

        else:
            raise AttributeError("tuple must have 2 elements")

    def __getitem__(self,arg):

        if len(arg) == 2:

            if (type(arg[0]) is slice) and (type(arg[1]) is int):

                m = arg[1]

                if (arg[0].start == None) and   \
                   (arg[0].step == None) and    \
                   (arg[0].stop == None):

                    if np.abs(m) > self._mmax:
                        raise AttributeError("m value out of bounds")

                    idx_start = pysphi.mindx(m,self.nmax,self.mmax)
                    idx_stop = idx_start + self.nmax - np.abs(m) + 1

                    return self._vec[idx_start:idx_stop]
                else:
                    raise AttributeError("slicing operation not permitted")

            elif (type(arg[0]) is int) and (type(arg[1]) is slice):
                
                n = arg[0]

                if (arg[1].start == None) and   \
                   (arg[1].step == None) and    \
                   (arg[1].stop == None):

                    if (n > self.nmax) or (n < 0):
                        raise AttributeError("n value out of bounds")

                    mlst = []
                    if n <= self.mmax:
                        nn = n
                    else:
                        nn = self.mmax            
                    for m in xrange(-nn,nn+1):
                        mlst.append(self.__getitem__((n,m)))

                    return np.array(mlst,dtype=np.complex128)
                else:
                    raise AttributeError("slicing operation not permitted")

            elif (type(arg[0]) is int) and (type(arg[1]) is int):

                n = arg[0]
                m = arg[1]

                if (n < 0) or (n > self._nmax):
                    raise AttributeError("n value out of bounds")

                if (np.abs(m) > n) or (np.abs(m) > self._mmax):
                    raise AttributeError("m value out of bounds")

                idx = pysphi.mindx(m,self.nmax,self.mmax) + n - np.abs(m)

                return self._vec[idx]

            else:
                raise AttributeError("what?, indexing method not recognized")

        else:
            raise AttributeError("tuple must have 2 elements")

    def _scalar_coef_op_left(func):
        """decorator for operator overloading when ScalarCoef is on the
        left"""
        @wraps(func)
        def verif(self,scoef):
            if isinstance(scoef,ScalarCoefs):
                if len(self._vec) == len(scoef._vec):
                    return ScalarCoefs(func(self,self._vec, scoef._vec),
                                        self.nmax,
                                        self.mmax)
                else:
                    raise SpherePyError("ScalarCoefs could not be combined" +
                                    " with sizes (%d,%d) and (%d,%d)" % \
                                    (self.nmax,self.mmax,
                                     scoef.nmax,scoef.mmax))
        
            elif isinstance(scoef, numbers.Number):
                return ScalarCoefs(func(self,self._vec, scoef),self.nmax,
                                   self.mmax)
            else:
                raise SpherePyError("cannot combine type with ScalarCoefs")
        return verif

    def _scalar_coef_op_right(func):
        """decorator for operator overloading when ScalarCoef is on the
        right"""
        @wraps(func)
        def verif(self,scoef):
            if isinstance(scoef, numbers.Number):
                return ScalarCoefs(func(self,self._vec,scoef),
                                   self.nmax,self.mmax)
            else:
                raise SpherePyError("cannot add type to ScalarCoefs")
        return verif

    @_scalar_coef_op_left
    def __add__(self,a,b):
        return a + b

    @_scalar_coef_op_right
    def __radd__(self,a,b):
        return  b + a

    @_scalar_coef_op_left
    def __sub__(self,a,b):
        return a - b

    @_scalar_coef_op_right
    def __rsub__(self,a,b):
        return b - a

    @_scalar_coef_op_left
    def __mul__(self,a,b):
        return a * b

    @_scalar_coef_op_right
    def __rmul__(self,a,b):
        return b * a

    @_scalar_coef_op_left
    def __div__(self,a,b):
        return a / b

    @_scalar_coef_op_right
    def __rdiv__(self,a,b):
        return b / a  


class VectorCoefs:
    pass

class ScalarPatternUniform:

    def __init__(self,cdata,doublesphere = False):

        if( doublesphere == False):
            self._dsphere = continue_sphere(cdata,1)
        else:
            self._dsphere = cdata

    def __repr__(self):

        return self.array.__repr__()

    @property
    def nrows(self):
        return self._dsphere.shape[0] / 2 + 1 

    @property
    def ncols(self):
        return self._dsphere.shape[1]

    @property
    def shape(self):
        return (self.nrows,self.ncols)

    @property
    def doublesphere(self):
        return self._dsphere

    @property
    def array(self):
        return self._dsphere[0:self.nrows,:]

    @property
    def is_symmetric(self):
        """return true if the data is symmetric"""
        if self.single_val < 1e-14:
            return True 
        else:
            return False

    @property
    def single_val(self):
        """return relative error of worst point that might make the data none
        symmetric.
        """
        nrows = self._dsphere.shape[0]
        ncols = self._dsphere.shape[1]

        sv = 0.0
        for n in xrange(0,nrows):
            for m in xrange(0,ncols):
                s = self._dsphere[np.mod(nrows-n,nrows),
                              np.mod(int(np.floor(ncols/2))+m,ncols)]
                t = self._dsphere[n,m]

                if s != 0:
                    sabs = np.abs((s - t)/s)
                    if sabs >= sv:
                        sv = sabs
                elif t != 0:
                    sabs = 1.0
                    if sabs >= sv:
                        sv = sabs

        return sv

    def _scalar_pattern_uniform_op_left(func):
        """decorator for operator overloading when ScalarPatternUniform is on 
        the left"""
        @wraps(func)
        def verif(self,patt):
            if isinstance(patt,ScalarPatternUniform):
                if len(self._dsphere.shape) == len(patt._dsphere.shape):
                    return ScalarPatternUniform(func(self,self._dsphere,
                                                     patt._dsphere),
                                                doublesphere = True)
                else:
                    raise SpherePyError("ScalarPatternUniform could not be" + 
                                        " combined with sizes (%d,%d) and "
                                        + "(%d,%d)" % \
                                            (self.nrows,self.ncols,
                                            patt.nrows,patt.ncols))
        
            elif isinstance(patt, numbers.Number):
                return ScalarPatternUniform(func(self,self._dsphere, patt),
                                            doublesphere = True)
            else:
                raise SpherePyError("cannot combine type with" +
                                   " ScalarPatternUniform")
        return verif

    def _scalar_pattern_uniform_op_right(func):
        """decorator for operator overloading when ScalarPatternUniform is on
        the right"""
        @wraps(func)
        def verif(self,patt):
            if isinstance(patt, numbers.Number):
                return ScalarPatternUniform(func(self,self._dsphere,patt),
                                   doublesphere = True)
            else:
                raise SpherePyError("cannot add type to ScalarPatternUniform")
        return verif

    @_scalar_pattern_uniform_op_left
    def __add__(self,a,b):
        return a + b

    @_scalar_pattern_uniform_op_right
    def __radd__(self,a,b):
        return  b + a

    @_scalar_pattern_uniform_op_left
    def __sub__(self,a,b):
        return a - b

    @_scalar_pattern_uniform_op_right
    def __rsub__(self,a,b):
        return b - a

    @_scalar_pattern_uniform_op_left
    def __mul__(self,a,b):
        return a * b

    @_scalar_pattern_uniform_op_right
    def __rmul__(self,a,b):
        return b * a

    @_scalar_pattern_uniform_op_left
    def __div__(self,a,b):
        return a / b

    @_scalar_pattern_uniform_op_right
    def __rdiv__(self,a,b):
        return b / a  


class ScalarPatternNonUniform:
    pass

class VectorPatternUniform:
    pass

class VectorPatternNonUniform:
    pass

"""***************************************************************************
                              Factories
***************************************************************************"""

def zeros_coefs(nmax,mmax,coef_type = scalar):
    """return ScalarCoefs with all coefficients set to zeros"""

    if(mmax > nmax):
        raise SpherePyError("mmax must be less than nmax")

    if(coef_type == scalar):
        L = (nmax + 1) + mmax*(2*nmax - mmax + 1)
        vec = np.zeros(L,dtype=np.complex128)
        return  ScalarCoefs(vec,nmax,mmax)
    elif(coef_type == vector):
        raise NotImplementedError()
    else:
        raise SpherePyError("unknown coefficient type")

def ones_coefs(nmax,mmax, coef_type = scalar):
    """return ScalarCoefs with all coefficients set to ones"""

    if(mmax > nmax):
        raise SpherePyError("mmax must be less than nmax")
    
    if(coef_type == scalar):
        L = (nmax + 1) + mmax*(2*nmax - mmax + 1)
        vec = np.ones(L,dtype=np.complex128)
        return  ScalarCoefs(vec,nmax,mmax)
    elif(coef_type == vector):
        raise NotImplementedError()
    else:
        raise SpherePyError("unknown coefficient type")

def random_coefs(nmax,mmax,mu = 0.0,sigma = 1.0, coef_type = scalar):
    """return ScalarCoefs with all coefficients random normal variables"""

    if(mmax > nmax):
        raise SpherePyError("mmax must be less than nmax")

    if(coef_type == scalar):
        L = (nmax + 1) + mmax*(2*nmax - mmax + 1)
        vec = np.random.normal(mu, sigma, L)
        return  ScalarCoefs(vec,nmax,mmax)
    elif(coef_type == vector):
        raise NotImplementedError()
    else:
        raise SpherePyError("unknown coefficient type")

def zeros_patt_uniform(nrows, ncols, patt_type = scalar):
    
    if np.mod(ncols,2) == 1:
        raise SpherePyError("ncols must be even")

    if(patt_type == scalar):
        cdata = np.zeros((2*nrows + 2, ncols), dtype = np.complex128)
        return ScalarPatternUniform(cdata, doublesphere = True)

    elif(patt_type == vector):
        raise NotImplementedError()

    else:
        raise SpherePyError("unrecognized pattern type")

def ones_patt_uniform(nrows, ncols, patt_type = scalar):
    if np.mod(ncols,2) == 1:
        raise SpherePyError("ncols must be even")

    if(patt_type == scalar):
        cdata = np.ones((nrows, ncols), dtype = np.complex128)
        return ScalarPatternUniform(cdata, doublesphere = False)

    elif(patt_type == vector):
        raise NotImplementedError()

    else:
        raise SpherePyError("unrecognized pattern type")

def random_patt_uniform(nrows, ncols, patt_type = scalar):

    if np.mod(ncols,2) == 1:
        raise SpherePyError("ncols must be even")

    if(patt_type == scalar):
        vec = np.random.normal(0.0, 1.0, nrows*ncols)
        return ScalarPatternUniform(vec.reshape((nrows,ncols)), 
                                    doublesphere = False)

    elif(patt_type == vector):
        raise NotImplementedError()

    else:
        raise SpherePyError("unrecognized pattern type")

def zeros_patt_nonuniform(theta_phi, patt_type = scalar):
    raise NotImplementedError()

def ones_patt_nonuniform(theta_phi, patt_type = scalar):
    raise NotImplementedError()

def random_patt_nonuniform(theta_phi, ncols, patt_type = scalar):
    raise NotImplementedError()

"""***************************************************************************
                              Functions
***************************************************************************"""   

def array(patt):

    if isinstance(patt,ScalarPatternUniform):
        return patt.array
    elif isinstance(patt,VectorPatternUniform):
        return patt.array
    else:
        raise SpherePyError("unrecognized type")


def continue_sphere(cdata,sym):
    
    nrows = cdata.shape[0]
    ncols = cdata.shape[1]

    zdata = np.zeros([nrows-2,ncols],dtype=np.complex128)
    ddata = np.concatenate([cdata,zdata])
    return double_sphere(ddata,sym)
    
def double_sphere(cdata,sym):
    
    nrows = cdata.shape[0]
    ncols = cdata.shape[1]

    ddata = np.zeros([nrows,ncols],dtype=np.complex128)

    for n in xrange(0,nrows):
        for m in xrange(0,ncols):
            s = sym*cdata[np.mod(nrows-n,nrows),
                          np.mod(int(np.floor(ncols/2))+m,ncols)]
            t = cdata[n,m]

            if s*t == 0:
                ddata[n,m] = s + t
            else:
                ddata[n,m] = (s + t) / 2

    return ddata

def spht(ssphere,nmax,mmax):
    """Returns a ScalarCoefs object containing the spherical harmonic 
    coefficients of the ssphere object"""

    if mmax > nmax:
        raise Exception("Mmax must be less than or equal to Nmax")

    nrows = ssphere._dsphere.shape[0]
    ncols = ssphere._dsphere.shape[1]

    if np.mod(nrows,2) == 1 or np.mod(ncols,2) == 1:
        raise Exception("number of rows and columns in continued sphere" + 
                        " object must be even")

    fdata = np.fft.fft2(ssphere._dsphere) /(nrows * ncols)
    pysphi.fix_even_row_data_fc(fdata)
    
    fdata_extended = np.zeros([nrows+2,ncols],dtype=np.complex128)

    pysphi.pad_rows_fdata(fdata,fdata_extended)

    pysphi.sin_fc(fdata_extended)

    #work = np.zeros(nmax + 1, dtype = np.float64) 
                                  
    c = pysphi.fc_to_sc(fdata_extended, nmax, mmax)

    return ScalarCoefs(c,nmax,mmax)


def ispht(scoefs,nrows,ncols):

    if np.mod(ncols,2) == 1:
        raise Exception("For consistency purposes, make sure Ncols is even.")

    #work = np.zeros(nrows + 1, dtype=np.float64)
    
    fdata = pysphi.sc_to_fc(scoefs._vec,
                            scoefs._nmax,
                            scoefs._mmax,
                            nrows,ncols)

    ds = np.fft.ifft2(fdata) * nrows * ncols

    return ScalarPatternUniform(ds,doublesphere = True)

def L2_coef(scoef):

    return np.sqrt(np.sum(np.abs(scoef._vec)**2))





