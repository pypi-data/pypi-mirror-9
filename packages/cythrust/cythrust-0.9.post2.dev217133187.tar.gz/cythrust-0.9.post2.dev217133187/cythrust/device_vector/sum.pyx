# distutils: language = c++
# cython: embedsignature = True

from libc.stdint cimport (uint8_t, uint16_t, uint32_t, uint64_t, int8_t,
                          int16_t, int32_t, int64_t)
from cythrust.thrust.device_vector cimport device_vector
from cythrust.thrust.functional cimport plus, minus
from cythrust.thrust.transform cimport transform2
from cythrust.thrust.reduce cimport accumulate_by_key
from cythrust.thrust.iterator.permutation_iterator cimport \
    make_permutation_iterator

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




    
cpdef sum_int32_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewInt32 values,
                            DeviceVectorViewInt8 reduced_keys,
                            DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[int8_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_uint32_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewUint32 values,
                            DeviceVectorViewInt8 reduced_keys,
                            DeviceVectorViewUint32 reduced_values):
    cdef size_t count = (<device_vector[int8_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_float32_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewFloat32 values,
                            DeviceVectorViewInt8 reduced_keys,
                            DeviceVectorViewFloat32 reduced_values):
    cdef size_t count = (<device_vector[int8_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    

    
cpdef sum_int32_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewInt32 values,
                            DeviceVectorViewUint8 reduced_keys,
                            DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[uint8_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_uint32_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewUint32 values,
                            DeviceVectorViewUint8 reduced_keys,
                            DeviceVectorViewUint32 reduced_values):
    cdef size_t count = (<device_vector[uint8_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_float32_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewFloat32 values,
                            DeviceVectorViewUint8 reduced_keys,
                            DeviceVectorViewFloat32 reduced_values):
    cdef size_t count = (<device_vector[uint8_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    

    
cpdef sum_int32_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewInt32 values,
                            DeviceVectorViewInt16 reduced_keys,
                            DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[int16_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_uint32_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewUint32 values,
                            DeviceVectorViewInt16 reduced_keys,
                            DeviceVectorViewUint32 reduced_values):
    cdef size_t count = (<device_vector[int16_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_float32_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewFloat32 values,
                            DeviceVectorViewInt16 reduced_keys,
                            DeviceVectorViewFloat32 reduced_values):
    cdef size_t count = (<device_vector[int16_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    

    
cpdef sum_int32_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewInt32 values,
                            DeviceVectorViewUint16 reduced_keys,
                            DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[uint16_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_uint32_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewUint32 values,
                            DeviceVectorViewUint16 reduced_keys,
                            DeviceVectorViewUint32 reduced_values):
    cdef size_t count = (<device_vector[uint16_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_float32_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewFloat32 values,
                            DeviceVectorViewUint16 reduced_keys,
                            DeviceVectorViewFloat32 reduced_values):
    cdef size_t count = (<device_vector[uint16_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    

    
cpdef sum_int32_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewInt32 values,
                            DeviceVectorViewInt32 reduced_keys,
                            DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[int32_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_uint32_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewUint32 values,
                            DeviceVectorViewInt32 reduced_keys,
                            DeviceVectorViewUint32 reduced_values):
    cdef size_t count = (<device_vector[int32_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_float32_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewFloat32 values,
                            DeviceVectorViewInt32 reduced_keys,
                            DeviceVectorViewFloat32 reduced_values):
    cdef size_t count = (<device_vector[int32_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    

    
cpdef sum_int32_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewInt32 values,
                            DeviceVectorViewUint32 reduced_keys,
                            DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[uint32_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_uint32_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewUint32 values,
                            DeviceVectorViewUint32 reduced_keys,
                            DeviceVectorViewUint32 reduced_values):
    cdef size_t count = (<device_vector[uint32_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_float32_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewFloat32 values,
                            DeviceVectorViewUint32 reduced_keys,
                            DeviceVectorViewFloat32 reduced_values):
    cdef size_t count = (<device_vector[uint32_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    

    
cpdef sum_int32_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewInt32 values,
                            DeviceVectorViewInt64 reduced_keys,
                            DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[int64_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_uint32_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewUint32 values,
                            DeviceVectorViewInt64 reduced_keys,
                            DeviceVectorViewUint32 reduced_values):
    cdef size_t count = (<device_vector[int64_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_float32_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewFloat32 values,
                            DeviceVectorViewInt64 reduced_keys,
                            DeviceVectorViewFloat32 reduced_values):
    cdef size_t count = (<device_vector[int64_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    

    
cpdef sum_int32_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewInt32 values,
                            DeviceVectorViewUint64 reduced_keys,
                            DeviceVectorViewInt32 reduced_values):
    cdef size_t count = (<device_vector[uint64_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_uint32_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewUint32 values,
                            DeviceVectorViewUint64 reduced_keys,
                            DeviceVectorViewUint32 reduced_values):
    cdef size_t count = (<device_vector[uint64_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    
cpdef sum_float32_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewFloat32 values,
                            DeviceVectorViewUint64 reduced_keys,
                            DeviceVectorViewFloat32 reduced_values):
    cdef size_t count = (<device_vector[uint64_t].iterator>accumulate_by_key(
        keys._vector.begin(), keys._vector.begin() + <size_t>keys.size,
        values._vector.begin(), reduced_keys._vector.begin(),
        reduced_values._vector.begin()).first - reduced_keys._vector.begin())
    return count
    




    
cpdef sum_int32_int32(DeviceVectorViewInt32 a,
                                              DeviceVectorViewInt32 b,
                                              DeviceVectorViewInt32 output):
    cdef plus[int32_t] plus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), plus_f)
    
cpdef sum_int32_uint32(DeviceVectorViewInt32 a,
                                              DeviceVectorViewUint32 b,
                                              DeviceVectorViewInt32 output):
    cdef plus[int32_t] plus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), plus_f)
    
cpdef sum_int32_float32(DeviceVectorViewInt32 a,
                                              DeviceVectorViewFloat32 b,
                                              DeviceVectorViewInt32 output):
    cdef plus[int32_t] plus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), plus_f)
    

    
cpdef sum_uint32_int32(DeviceVectorViewUint32 a,
                                              DeviceVectorViewInt32 b,
                                              DeviceVectorViewUint32 output):
    cdef plus[uint32_t] plus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), plus_f)
    
cpdef sum_uint32_uint32(DeviceVectorViewUint32 a,
                                              DeviceVectorViewUint32 b,
                                              DeviceVectorViewUint32 output):
    cdef plus[uint32_t] plus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), plus_f)
    
cpdef sum_uint32_float32(DeviceVectorViewUint32 a,
                                              DeviceVectorViewFloat32 b,
                                              DeviceVectorViewUint32 output):
    cdef plus[uint32_t] plus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), plus_f)
    

    
cpdef sum_float32_int32(DeviceVectorViewFloat32 a,
                                              DeviceVectorViewInt32 b,
                                              DeviceVectorViewFloat32 output):
    cdef plus[float] plus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), plus_f)
    
cpdef sum_float32_uint32(DeviceVectorViewFloat32 a,
                                              DeviceVectorViewUint32 b,
                                              DeviceVectorViewFloat32 output):
    cdef plus[float] plus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), plus_f)
    
cpdef sum_float32_float32(DeviceVectorViewFloat32 a,
                                              DeviceVectorViewFloat32 b,
                                              DeviceVectorViewFloat32 output):
    cdef plus[float] plus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), plus_f)
    




    
cpdef sub_int8_int8(DeviceVectorViewInt8 a,
                                              DeviceVectorViewInt8 b,
                                              DeviceVectorViewInt8 output):
    cdef minus[int8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int8_uint8(DeviceVectorViewInt8 a,
                                              DeviceVectorViewUint8 b,
                                              DeviceVectorViewInt8 output):
    cdef minus[int8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int8_int16(DeviceVectorViewInt8 a,
                                              DeviceVectorViewInt16 b,
                                              DeviceVectorViewInt8 output):
    cdef minus[int8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int8_uint16(DeviceVectorViewInt8 a,
                                              DeviceVectorViewUint16 b,
                                              DeviceVectorViewInt8 output):
    cdef minus[int8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int8_int32(DeviceVectorViewInt8 a,
                                              DeviceVectorViewInt32 b,
                                              DeviceVectorViewInt8 output):
    cdef minus[int8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int8_uint32(DeviceVectorViewInt8 a,
                                              DeviceVectorViewUint32 b,
                                              DeviceVectorViewInt8 output):
    cdef minus[int8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int8_int64(DeviceVectorViewInt8 a,
                                              DeviceVectorViewInt64 b,
                                              DeviceVectorViewInt8 output):
    cdef minus[int8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int8_uint64(DeviceVectorViewInt8 a,
                                              DeviceVectorViewUint64 b,
                                              DeviceVectorViewInt8 output):
    cdef minus[int8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int8_float32(DeviceVectorViewInt8 a,
                                              DeviceVectorViewFloat32 b,
                                              DeviceVectorViewInt8 output):
    cdef minus[int8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int8_float64(DeviceVectorViewInt8 a,
                                              DeviceVectorViewFloat64 b,
                                              DeviceVectorViewInt8 output):
    cdef minus[int8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    

    
cpdef sub_uint8_int8(DeviceVectorViewUint8 a,
                                              DeviceVectorViewInt8 b,
                                              DeviceVectorViewUint8 output):
    cdef minus[uint8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint8_uint8(DeviceVectorViewUint8 a,
                                              DeviceVectorViewUint8 b,
                                              DeviceVectorViewUint8 output):
    cdef minus[uint8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint8_int16(DeviceVectorViewUint8 a,
                                              DeviceVectorViewInt16 b,
                                              DeviceVectorViewUint8 output):
    cdef minus[uint8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint8_uint16(DeviceVectorViewUint8 a,
                                              DeviceVectorViewUint16 b,
                                              DeviceVectorViewUint8 output):
    cdef minus[uint8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint8_int32(DeviceVectorViewUint8 a,
                                              DeviceVectorViewInt32 b,
                                              DeviceVectorViewUint8 output):
    cdef minus[uint8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint8_uint32(DeviceVectorViewUint8 a,
                                              DeviceVectorViewUint32 b,
                                              DeviceVectorViewUint8 output):
    cdef minus[uint8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint8_int64(DeviceVectorViewUint8 a,
                                              DeviceVectorViewInt64 b,
                                              DeviceVectorViewUint8 output):
    cdef minus[uint8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint8_uint64(DeviceVectorViewUint8 a,
                                              DeviceVectorViewUint64 b,
                                              DeviceVectorViewUint8 output):
    cdef minus[uint8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint8_float32(DeviceVectorViewUint8 a,
                                              DeviceVectorViewFloat32 b,
                                              DeviceVectorViewUint8 output):
    cdef minus[uint8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint8_float64(DeviceVectorViewUint8 a,
                                              DeviceVectorViewFloat64 b,
                                              DeviceVectorViewUint8 output):
    cdef minus[uint8_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    

    
cpdef sub_int16_int8(DeviceVectorViewInt16 a,
                                              DeviceVectorViewInt8 b,
                                              DeviceVectorViewInt16 output):
    cdef minus[int16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int16_uint8(DeviceVectorViewInt16 a,
                                              DeviceVectorViewUint8 b,
                                              DeviceVectorViewInt16 output):
    cdef minus[int16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int16_int16(DeviceVectorViewInt16 a,
                                              DeviceVectorViewInt16 b,
                                              DeviceVectorViewInt16 output):
    cdef minus[int16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int16_uint16(DeviceVectorViewInt16 a,
                                              DeviceVectorViewUint16 b,
                                              DeviceVectorViewInt16 output):
    cdef minus[int16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int16_int32(DeviceVectorViewInt16 a,
                                              DeviceVectorViewInt32 b,
                                              DeviceVectorViewInt16 output):
    cdef minus[int16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int16_uint32(DeviceVectorViewInt16 a,
                                              DeviceVectorViewUint32 b,
                                              DeviceVectorViewInt16 output):
    cdef minus[int16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int16_int64(DeviceVectorViewInt16 a,
                                              DeviceVectorViewInt64 b,
                                              DeviceVectorViewInt16 output):
    cdef minus[int16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int16_uint64(DeviceVectorViewInt16 a,
                                              DeviceVectorViewUint64 b,
                                              DeviceVectorViewInt16 output):
    cdef minus[int16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int16_float32(DeviceVectorViewInt16 a,
                                              DeviceVectorViewFloat32 b,
                                              DeviceVectorViewInt16 output):
    cdef minus[int16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int16_float64(DeviceVectorViewInt16 a,
                                              DeviceVectorViewFloat64 b,
                                              DeviceVectorViewInt16 output):
    cdef minus[int16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    

    
cpdef sub_uint16_int8(DeviceVectorViewUint16 a,
                                              DeviceVectorViewInt8 b,
                                              DeviceVectorViewUint16 output):
    cdef minus[uint16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint16_uint8(DeviceVectorViewUint16 a,
                                              DeviceVectorViewUint8 b,
                                              DeviceVectorViewUint16 output):
    cdef minus[uint16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint16_int16(DeviceVectorViewUint16 a,
                                              DeviceVectorViewInt16 b,
                                              DeviceVectorViewUint16 output):
    cdef minus[uint16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint16_uint16(DeviceVectorViewUint16 a,
                                              DeviceVectorViewUint16 b,
                                              DeviceVectorViewUint16 output):
    cdef minus[uint16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint16_int32(DeviceVectorViewUint16 a,
                                              DeviceVectorViewInt32 b,
                                              DeviceVectorViewUint16 output):
    cdef minus[uint16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint16_uint32(DeviceVectorViewUint16 a,
                                              DeviceVectorViewUint32 b,
                                              DeviceVectorViewUint16 output):
    cdef minus[uint16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint16_int64(DeviceVectorViewUint16 a,
                                              DeviceVectorViewInt64 b,
                                              DeviceVectorViewUint16 output):
    cdef minus[uint16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint16_uint64(DeviceVectorViewUint16 a,
                                              DeviceVectorViewUint64 b,
                                              DeviceVectorViewUint16 output):
    cdef minus[uint16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint16_float32(DeviceVectorViewUint16 a,
                                              DeviceVectorViewFloat32 b,
                                              DeviceVectorViewUint16 output):
    cdef minus[uint16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint16_float64(DeviceVectorViewUint16 a,
                                              DeviceVectorViewFloat64 b,
                                              DeviceVectorViewUint16 output):
    cdef minus[uint16_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    

    
cpdef sub_int32_int8(DeviceVectorViewInt32 a,
                                              DeviceVectorViewInt8 b,
                                              DeviceVectorViewInt32 output):
    cdef minus[int32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int32_uint8(DeviceVectorViewInt32 a,
                                              DeviceVectorViewUint8 b,
                                              DeviceVectorViewInt32 output):
    cdef minus[int32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int32_int16(DeviceVectorViewInt32 a,
                                              DeviceVectorViewInt16 b,
                                              DeviceVectorViewInt32 output):
    cdef minus[int32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int32_uint16(DeviceVectorViewInt32 a,
                                              DeviceVectorViewUint16 b,
                                              DeviceVectorViewInt32 output):
    cdef minus[int32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int32_int32(DeviceVectorViewInt32 a,
                                              DeviceVectorViewInt32 b,
                                              DeviceVectorViewInt32 output):
    cdef minus[int32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int32_uint32(DeviceVectorViewInt32 a,
                                              DeviceVectorViewUint32 b,
                                              DeviceVectorViewInt32 output):
    cdef minus[int32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int32_int64(DeviceVectorViewInt32 a,
                                              DeviceVectorViewInt64 b,
                                              DeviceVectorViewInt32 output):
    cdef minus[int32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int32_uint64(DeviceVectorViewInt32 a,
                                              DeviceVectorViewUint64 b,
                                              DeviceVectorViewInt32 output):
    cdef minus[int32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int32_float32(DeviceVectorViewInt32 a,
                                              DeviceVectorViewFloat32 b,
                                              DeviceVectorViewInt32 output):
    cdef minus[int32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int32_float64(DeviceVectorViewInt32 a,
                                              DeviceVectorViewFloat64 b,
                                              DeviceVectorViewInt32 output):
    cdef minus[int32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    

    
cpdef sub_uint32_int8(DeviceVectorViewUint32 a,
                                              DeviceVectorViewInt8 b,
                                              DeviceVectorViewUint32 output):
    cdef minus[uint32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint32_uint8(DeviceVectorViewUint32 a,
                                              DeviceVectorViewUint8 b,
                                              DeviceVectorViewUint32 output):
    cdef minus[uint32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint32_int16(DeviceVectorViewUint32 a,
                                              DeviceVectorViewInt16 b,
                                              DeviceVectorViewUint32 output):
    cdef minus[uint32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint32_uint16(DeviceVectorViewUint32 a,
                                              DeviceVectorViewUint16 b,
                                              DeviceVectorViewUint32 output):
    cdef minus[uint32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint32_int32(DeviceVectorViewUint32 a,
                                              DeviceVectorViewInt32 b,
                                              DeviceVectorViewUint32 output):
    cdef minus[uint32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint32_uint32(DeviceVectorViewUint32 a,
                                              DeviceVectorViewUint32 b,
                                              DeviceVectorViewUint32 output):
    cdef minus[uint32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint32_int64(DeviceVectorViewUint32 a,
                                              DeviceVectorViewInt64 b,
                                              DeviceVectorViewUint32 output):
    cdef minus[uint32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint32_uint64(DeviceVectorViewUint32 a,
                                              DeviceVectorViewUint64 b,
                                              DeviceVectorViewUint32 output):
    cdef minus[uint32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint32_float32(DeviceVectorViewUint32 a,
                                              DeviceVectorViewFloat32 b,
                                              DeviceVectorViewUint32 output):
    cdef minus[uint32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint32_float64(DeviceVectorViewUint32 a,
                                              DeviceVectorViewFloat64 b,
                                              DeviceVectorViewUint32 output):
    cdef minus[uint32_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    

    
cpdef sub_int64_int8(DeviceVectorViewInt64 a,
                                              DeviceVectorViewInt8 b,
                                              DeviceVectorViewInt64 output):
    cdef minus[int64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int64_uint8(DeviceVectorViewInt64 a,
                                              DeviceVectorViewUint8 b,
                                              DeviceVectorViewInt64 output):
    cdef minus[int64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int64_int16(DeviceVectorViewInt64 a,
                                              DeviceVectorViewInt16 b,
                                              DeviceVectorViewInt64 output):
    cdef minus[int64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int64_uint16(DeviceVectorViewInt64 a,
                                              DeviceVectorViewUint16 b,
                                              DeviceVectorViewInt64 output):
    cdef minus[int64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int64_int32(DeviceVectorViewInt64 a,
                                              DeviceVectorViewInt32 b,
                                              DeviceVectorViewInt64 output):
    cdef minus[int64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int64_uint32(DeviceVectorViewInt64 a,
                                              DeviceVectorViewUint32 b,
                                              DeviceVectorViewInt64 output):
    cdef minus[int64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int64_int64(DeviceVectorViewInt64 a,
                                              DeviceVectorViewInt64 b,
                                              DeviceVectorViewInt64 output):
    cdef minus[int64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int64_uint64(DeviceVectorViewInt64 a,
                                              DeviceVectorViewUint64 b,
                                              DeviceVectorViewInt64 output):
    cdef minus[int64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int64_float32(DeviceVectorViewInt64 a,
                                              DeviceVectorViewFloat32 b,
                                              DeviceVectorViewInt64 output):
    cdef minus[int64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_int64_float64(DeviceVectorViewInt64 a,
                                              DeviceVectorViewFloat64 b,
                                              DeviceVectorViewInt64 output):
    cdef minus[int64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    

    
cpdef sub_uint64_int8(DeviceVectorViewUint64 a,
                                              DeviceVectorViewInt8 b,
                                              DeviceVectorViewUint64 output):
    cdef minus[uint64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint64_uint8(DeviceVectorViewUint64 a,
                                              DeviceVectorViewUint8 b,
                                              DeviceVectorViewUint64 output):
    cdef minus[uint64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint64_int16(DeviceVectorViewUint64 a,
                                              DeviceVectorViewInt16 b,
                                              DeviceVectorViewUint64 output):
    cdef minus[uint64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint64_uint16(DeviceVectorViewUint64 a,
                                              DeviceVectorViewUint16 b,
                                              DeviceVectorViewUint64 output):
    cdef minus[uint64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint64_int32(DeviceVectorViewUint64 a,
                                              DeviceVectorViewInt32 b,
                                              DeviceVectorViewUint64 output):
    cdef minus[uint64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint64_uint32(DeviceVectorViewUint64 a,
                                              DeviceVectorViewUint32 b,
                                              DeviceVectorViewUint64 output):
    cdef minus[uint64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint64_int64(DeviceVectorViewUint64 a,
                                              DeviceVectorViewInt64 b,
                                              DeviceVectorViewUint64 output):
    cdef minus[uint64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint64_uint64(DeviceVectorViewUint64 a,
                                              DeviceVectorViewUint64 b,
                                              DeviceVectorViewUint64 output):
    cdef minus[uint64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint64_float32(DeviceVectorViewUint64 a,
                                              DeviceVectorViewFloat32 b,
                                              DeviceVectorViewUint64 output):
    cdef minus[uint64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    
cpdef sub_uint64_float64(DeviceVectorViewUint64 a,
                                              DeviceVectorViewFloat64 b,
                                              DeviceVectorViewUint64 output):
    cdef minus[uint64_t] minus_f

    transform2(a._vector.begin(), a._vector.end(), b._vector.begin(),
               output._vector.begin(), minus_f)
    




    
cpdef sum_int32_int32_stencil(
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewInt32 a,
        DeviceVectorViewInt32 b,
        DeviceVectorViewInt32 output):
    cdef plus[int32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(), stencil._vector.end()),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_int32_uint32_stencil(
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewInt32 a,
        DeviceVectorViewUint32 b,
        DeviceVectorViewInt32 output):
    cdef plus[int32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(), stencil._vector.end()),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_int32_float32_stencil(
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewInt32 a,
        DeviceVectorViewFloat32 b,
        DeviceVectorViewInt32 output):
    cdef plus[int32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(), stencil._vector.end()),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    

    
cpdef sum_uint32_int32_stencil(
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewUint32 a,
        DeviceVectorViewInt32 b,
        DeviceVectorViewUint32 output):
    cdef plus[uint32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(), stencil._vector.end()),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_uint32_uint32_stencil(
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewUint32 a,
        DeviceVectorViewUint32 b,
        DeviceVectorViewUint32 output):
    cdef plus[uint32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(), stencil._vector.end()),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_uint32_float32_stencil(
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewUint32 a,
        DeviceVectorViewFloat32 b,
        DeviceVectorViewUint32 output):
    cdef plus[uint32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(), stencil._vector.end()),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    

    
cpdef sum_float32_int32_stencil(
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewFloat32 a,
        DeviceVectorViewInt32 b,
        DeviceVectorViewFloat32 output):
    cdef plus[float] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(), stencil._vector.end()),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_float32_uint32_stencil(
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewFloat32 a,
        DeviceVectorViewUint32 b,
        DeviceVectorViewFloat32 output):
    cdef plus[float] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(), stencil._vector.end()),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_float32_float32_stencil(
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewFloat32 a,
        DeviceVectorViewFloat32 b,
        DeviceVectorViewFloat32 output):
    cdef plus[float] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(), stencil._vector.end()),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    




    
cpdef sum_n_int32_int32_stencil(
        size_t N,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewInt32 a,
        DeviceVectorViewInt32 b,
        DeviceVectorViewInt32 output):
    cdef plus[int32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(),
                                  stencil._vector.begin() + N),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_n_int32_uint32_stencil(
        size_t N,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewInt32 a,
        DeviceVectorViewUint32 b,
        DeviceVectorViewInt32 output):
    cdef plus[int32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(),
                                  stencil._vector.begin() + N),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_n_int32_float32_stencil(
        size_t N,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewInt32 a,
        DeviceVectorViewFloat32 b,
        DeviceVectorViewInt32 output):
    cdef plus[int32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(),
                                  stencil._vector.begin() + N),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    

    
cpdef sum_n_uint32_int32_stencil(
        size_t N,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewUint32 a,
        DeviceVectorViewInt32 b,
        DeviceVectorViewUint32 output):
    cdef plus[uint32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(),
                                  stencil._vector.begin() + N),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_n_uint32_uint32_stencil(
        size_t N,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewUint32 a,
        DeviceVectorViewUint32 b,
        DeviceVectorViewUint32 output):
    cdef plus[uint32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(),
                                  stencil._vector.begin() + N),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_n_uint32_float32_stencil(
        size_t N,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewUint32 a,
        DeviceVectorViewFloat32 b,
        DeviceVectorViewUint32 output):
    cdef plus[uint32_t] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(),
                                  stencil._vector.begin() + N),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    

    
cpdef sum_n_float32_int32_stencil(
        size_t N,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewFloat32 a,
        DeviceVectorViewInt32 b,
        DeviceVectorViewFloat32 output):
    cdef plus[float] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(),
                                  stencil._vector.begin() + N),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_n_float32_uint32_stencil(
        size_t N,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewFloat32 a,
        DeviceVectorViewUint32 b,
        DeviceVectorViewFloat32 output):
    cdef plus[float] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(),
                                  stencil._vector.begin() + N),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
cpdef sum_n_float32_float32_stencil(
        size_t N,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewFloat32 a,
        DeviceVectorViewFloat32 b,
        DeviceVectorViewFloat32 output):
    cdef plus[float] plus_f

    transform2(
        make_permutation_iterator(a._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(a._vector.begin(),
                                  stencil._vector.begin() + N),
        make_permutation_iterator(b._vector.begin(), stencil._vector.begin()),
        make_permutation_iterator(output._vector.begin(),
                                  stencil._vector.begin()), plus_f)
    
