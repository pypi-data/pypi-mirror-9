# distutils: language = c++
# cython: embedsignature = True

import sys
from cython.operator cimport dereference as deref
import numpy as np
cimport numpy as np
from libc.stdint cimport (
    int8_t, uint8_t,
    int16_t, uint16_t,
    int32_t, uint32_t,
    int64_t, uint64_t)

from cythrust.thrust.copy cimport copy_n
from cythrust.thrust.fill cimport fill_n


CTYPE = 'uint16_t'
DTYPE = np.uint16


cdef class DeviceVector:
    def __cinit__(self, size_t size=0):
        self._vector = new device_vector[uint16_t](size)
        self.dtype = DTYPE
        self.ctype = CTYPE

    @classmethod
    def from_array(cls, np.ndarray a):
        cdef np.ndarray _a = np.ascontiguousarray(a, dtype=np.uint16)
        cdef size_t N = _a.size
        cdef DeviceVector vector = DeviceVector(N)
        cdef uint16_t *data = <uint16_t*>&_a.data[0]
        copy_n(data, N, vector._vector.begin())
        return vector

    def resize(self, size_t size):
        '''
        Resize the device vector to `size`.
        '''
        self._vector.resize(size)

    def astype(self, dtype):
        '''
        Return a _copy_ of the device vector as a `numpy` array of type
        `dtype`.
        '''
        return self.asarray().astype(dtype)

    def asarray(self):
        '''
        Return a _copy_ of the device vector as a `numpy` array.
        '''
        return self[:]

    def __dealloc__(self):
        del self._vector

    def __getitem__(self, i):
        return deref(self._vector)[i]

    def __getslice__(self, i, j):
        if i < 0:
            i = self.size + i
        if j < 0:
            j = self.size + j
        elif j == sys.maxint:
            j = self.size
        assert(i <= j)
        cdef int N = j - i
        cdef np.ndarray result = np.empty(N, dtype=np.uint16)
        copy_n(self._vector.begin() + <size_t>i, N,
               <uint16_t*>result.data)
        return result

    def __setitem__(self, key_or_slice, value):
        cdef int N
        cdef np.ndarray _values
        if isinstance(key_or_slice, slice):
            if key_or_slice.step is not None:
                raise ValueError('Step other than one is not supported.')
            i = key_or_slice.start
            j = key_or_slice.stop
            if i is None:
                i = 0
            elif i < 0:
                i = self.size + i
            if j is None:
                j = self.size
            elif j < 0:
                j = self.size + j
            elif j == sys.maxint:
                j = self.size
            assert(i <= j)
            N = j - i
            assert(N <= self.size)
            _values = np.ascontiguousarray(value, dtype=np.uint16)
            if _values.size == 1:
                # Input was a single value.
                fill_n(self._vector.begin() + <size_t>i, N, <uint16_t>_values[0])
            elif _values.size == N:
                copy_n(<uint16_t*>_values.data, N, self._vector.begin() +
                       <size_t>i)
            else:
                raise ValueError('Incorrect slice length.  Expected %d, but got %d'
                                % (N, _values.size))
        else:
            fill_n(self._vector.begin() + <size_t>key_or_slice, 1, <uint16_t>value)

    def __str__(self):
        return str(self[:])

    def __repr__(self):
        return repr(self[:])

    property dtype:
        def __get__(self):
            return self.dtype

    property ctype:
        def __get__(self):
            return self.ctype

    property size:
        def __get__(self):
            return self._vector.size()

        def __set__(self, value):
            self._vector.resize(value)


cdef class DeviceVectorView:
    def __cinit__(self, DeviceVector vector, first_i=0, last_i=-1):
        self.dtype = DTYPE
        self.ctype = CTYPE
        self._vector = vector._vector
        self.first_i = first_i
        self.last_i = last_i

    def reset(self):
        self._begin = self._vector.begin()
        self._end = self._vector.end()

    property first_i:
        def __get__(self):
            return self._begin - self._vector.begin()

        def __set__(self, value):
            if value < 0:
                value += self._vector.size()
            cdef device_vector[uint16_t].iterator begin
            begin = self._begin = self._vector.begin() + <size_t>value
            cdef int64_t size = (begin - self._vector.begin())
            if size < 0 or size > self._vector.size():
                raise ValueError('Out of range: i = %d.')
            else:
                self._begin = begin

    property last_i:
        def __get__(self):
            return self._end - self._vector.begin() - 1

        def __set__(self, int64_t value):
            if value < 0:
                value += self._vector.size()
            cdef device_vector[uint16_t].iterator end
            end = self._vector.begin() + <size_t>value + 1
            cdef int64_t size = (end - self._vector.begin())
            if size < 0 or size > self._vector.size():
                raise ValueError('Out of range: i = %d.')
            else:
                self._end = end

    def astype(self, dtype):
        '''
        Return a _copy_ of the device vector view as a `numpy` array of type
        `dtype`.
        '''
        return self.asarray().astype(dtype)

    def asarray(self):
        '''
        Return a _copy_ of the device vector view as a `numpy` array.
        '''
        return self[:]

    def __getitem__(self, size_t i):
        return deref(self._begin + i)

    def __setitem__(self, key_or_slice, value):
        cdef int N
        cdef np.ndarray _values
        if isinstance(key_or_slice, slice):
            if key_or_slice.step is not None:
                raise ValueError('Step other than one is not supported.')
            i = key_or_slice.start
            j = key_or_slice.stop
            if i is None:
                i = 0
            elif i < 0:
                i = self.size + i
            if j is None:
                j = self.size
            elif j < 0:
                j = self.size + j
            elif j == sys.maxint:
                j = self.size
            assert(i <= j)
            N = j - i
            assert(N <= self.size)
            _values = np.ascontiguousarray(value, dtype=np.uint16)
            if _values.size == 1:
                # Input was a single value.
                fill_n(self._begin + <size_t>i, N, <uint16_t>_values[0])
            elif _values.size == N:
                copy_n(<uint16_t*>_values.data, N,
                    self._begin + <size_t>i)
            else:
                raise ValueError('Incorrect slice length.  Expected %d, but got %d'
                                % (N, _values.size))
        else:
            fill_n(self._begin + <size_t>key_or_slice, 1, <uint16_t>value)

    def __getslice__(self, i, j):
        if i < 0:
            i = self.size + i
        if j < 0:
            j = self.size + j
        elif j == sys.maxint:
            j = self.size
        assert(i <= j)
        cdef int N = j - i
        cdef np.ndarray result = np.empty(N, dtype=np.uint16)
        copy_n(self._begin + <size_t>i, N, <uint16_t*>result.data)
        return result

    def __str__(self):
        return str(self[:])

    def __repr__(self):
        return repr(self[:])

    property dtype:
        def __get__(self):
            return self.dtype

    property ctype:
        def __get__(self):
            return self.ctype

    property size:
        def __get__(self):
            return self._end - self._begin