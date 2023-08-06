# distutils: language = c++
# cython: embedsignature = True

from libc.stdint cimport (uint8_t, uint16_t, uint32_t, uint64_t, int8_t,
                          int16_t, int32_t, int64_t)
from cythrust.thrust.device_vector cimport device_vector
from cythrust.thrust.reduce cimport accumulate_by_key
from cythrust.thrust.iterator.constant_iterator cimport make_constant_iterator

from cythrust.device_vector cimport DeviceVectorViewInt8
from cythrust.device_vector cimport DeviceVectorViewUint8
from cythrust.device_vector cimport DeviceVectorViewInt16
from cythrust.device_vector cimport DeviceVectorViewUint16
from cythrust.device_vector cimport DeviceVectorViewInt32
from cythrust.device_vector cimport DeviceVectorViewUint32
from cythrust.device_vector cimport DeviceVectorViewInt64
from cythrust.device_vector cimport DeviceVectorViewUint64
from cythrust.device_vector cimport DeviceVectorViewFloat32
from cythrust.device_vector cimport DeviceVectorViewFloat64




cpdef count_int8_key(DeviceVectorViewInt8 keys,
                                DeviceVectorViewInt8 reduced_keys,
                                DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[int8_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        make_constant_iterator(1), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count

cpdef count_uint8_key(DeviceVectorViewUint8 keys,
                                DeviceVectorViewUint8 reduced_keys,
                                DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[uint8_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        make_constant_iterator(1), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count

cpdef count_int16_key(DeviceVectorViewInt16 keys,
                                DeviceVectorViewInt16 reduced_keys,
                                DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[int16_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        make_constant_iterator(1), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count

cpdef count_uint16_key(DeviceVectorViewUint16 keys,
                                DeviceVectorViewUint16 reduced_keys,
                                DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[uint16_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        make_constant_iterator(1), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count

cpdef count_int32_key(DeviceVectorViewInt32 keys,
                                DeviceVectorViewInt32 reduced_keys,
                                DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[int32_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        make_constant_iterator(1), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count

cpdef count_uint32_key(DeviceVectorViewUint32 keys,
                                DeviceVectorViewUint32 reduced_keys,
                                DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[uint32_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        make_constant_iterator(1), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count

cpdef count_int64_key(DeviceVectorViewInt64 keys,
                                DeviceVectorViewInt64 reduced_keys,
                                DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[int64_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        make_constant_iterator(1), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count

cpdef count_uint64_key(DeviceVectorViewUint64 keys,
                                DeviceVectorViewUint64 reduced_keys,
                                DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[uint64_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        make_constant_iterator(1), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
