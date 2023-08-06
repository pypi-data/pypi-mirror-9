# distutils: language = c++
# cython: embedsignature = True

from libc.stdint cimport (uint8_t, uint16_t, uint32_t, uint64_t, int8_t,
                          int16_t, int32_t, int64_t)
from cython.operator import dereference as deref
from cythrust.thrust.device_vector cimport device_vector
from cythrust.thrust.reduce cimport reduce_by_key, reduce
from cythrust.thrust.iterator.transform_iterator cimport \
    make_transform_iterator
from cythrust.thrust.iterator.zip_iterator cimport make_zip_iterator
from cythrust.thrust.tuple cimport make_tuple2
from cythrust.thrust.extrema cimport max_element
from cythrust.thrust.functional cimport (equal_to, duplicate, minmax_tuple,
                                         maximum, absolute)

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




cpdef minmax_int8_by_key(DeviceVectorViewInt32 keys,
                                DeviceVectorViewInt8 values,
                                DeviceVectorViewInt32 reduced_keys,
                                DeviceVectorViewInt8 min_values,
                                DeviceVectorViewInt8 max_values):
    cdef duplicate[int8_t] duplicate_f
    cdef minmax_tuple[int8_t] minmax_f
    cdef equal_to[int32_t] reduce_compare  # Functor to compare reduction keys.

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>(reduce_by_key(
        keys._vector.begin(), keys._vector.end(),
        make_transform_iterator(values._vector.begin(), duplicate_f),
        reduced_keys._vector.begin(),
        make_zip_iterator(
            make_tuple2(min_values._vector.begin(),
                        max_values._vector.begin())),
        reduce_compare, minmax_f).first) - reduced_keys._vector.begin())
    return count

cpdef minmax_uint8_by_key(DeviceVectorViewInt32 keys,
                                DeviceVectorViewUint8 values,
                                DeviceVectorViewInt32 reduced_keys,
                                DeviceVectorViewUint8 min_values,
                                DeviceVectorViewUint8 max_values):
    cdef duplicate[uint8_t] duplicate_f
    cdef minmax_tuple[uint8_t] minmax_f
    cdef equal_to[int32_t] reduce_compare  # Functor to compare reduction keys.

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>(reduce_by_key(
        keys._vector.begin(), keys._vector.end(),
        make_transform_iterator(values._vector.begin(), duplicate_f),
        reduced_keys._vector.begin(),
        make_zip_iterator(
            make_tuple2(min_values._vector.begin(),
                        max_values._vector.begin())),
        reduce_compare, minmax_f).first) - reduced_keys._vector.begin())
    return count

cpdef minmax_int16_by_key(DeviceVectorViewInt32 keys,
                                DeviceVectorViewInt16 values,
                                DeviceVectorViewInt32 reduced_keys,
                                DeviceVectorViewInt16 min_values,
                                DeviceVectorViewInt16 max_values):
    cdef duplicate[int16_t] duplicate_f
    cdef minmax_tuple[int16_t] minmax_f
    cdef equal_to[int32_t] reduce_compare  # Functor to compare reduction keys.

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>(reduce_by_key(
        keys._vector.begin(), keys._vector.end(),
        make_transform_iterator(values._vector.begin(), duplicate_f),
        reduced_keys._vector.begin(),
        make_zip_iterator(
            make_tuple2(min_values._vector.begin(),
                        max_values._vector.begin())),
        reduce_compare, minmax_f).first) - reduced_keys._vector.begin())
    return count

cpdef minmax_uint16_by_key(DeviceVectorViewInt32 keys,
                                DeviceVectorViewUint16 values,
                                DeviceVectorViewInt32 reduced_keys,
                                DeviceVectorViewUint16 min_values,
                                DeviceVectorViewUint16 max_values):
    cdef duplicate[uint16_t] duplicate_f
    cdef minmax_tuple[uint16_t] minmax_f
    cdef equal_to[int32_t] reduce_compare  # Functor to compare reduction keys.

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>(reduce_by_key(
        keys._vector.begin(), keys._vector.end(),
        make_transform_iterator(values._vector.begin(), duplicate_f),
        reduced_keys._vector.begin(),
        make_zip_iterator(
            make_tuple2(min_values._vector.begin(),
                        max_values._vector.begin())),
        reduce_compare, minmax_f).first) - reduced_keys._vector.begin())
    return count

cpdef minmax_int32_by_key(DeviceVectorViewInt32 keys,
                                DeviceVectorViewInt32 values,
                                DeviceVectorViewInt32 reduced_keys,
                                DeviceVectorViewInt32 min_values,
                                DeviceVectorViewInt32 max_values):
    cdef duplicate[int32_t] duplicate_f
    cdef minmax_tuple[int32_t] minmax_f
    cdef equal_to[int32_t] reduce_compare  # Functor to compare reduction keys.

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>(reduce_by_key(
        keys._vector.begin(), keys._vector.end(),
        make_transform_iterator(values._vector.begin(), duplicate_f),
        reduced_keys._vector.begin(),
        make_zip_iterator(
            make_tuple2(min_values._vector.begin(),
                        max_values._vector.begin())),
        reduce_compare, minmax_f).first) - reduced_keys._vector.begin())
    return count

cpdef minmax_uint32_by_key(DeviceVectorViewInt32 keys,
                                DeviceVectorViewUint32 values,
                                DeviceVectorViewInt32 reduced_keys,
                                DeviceVectorViewUint32 min_values,
                                DeviceVectorViewUint32 max_values):
    cdef duplicate[uint32_t] duplicate_f
    cdef minmax_tuple[uint32_t] minmax_f
    cdef equal_to[int32_t] reduce_compare  # Functor to compare reduction keys.

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>(reduce_by_key(
        keys._vector.begin(), keys._vector.end(),
        make_transform_iterator(values._vector.begin(), duplicate_f),
        reduced_keys._vector.begin(),
        make_zip_iterator(
            make_tuple2(min_values._vector.begin(),
                        max_values._vector.begin())),
        reduce_compare, minmax_f).first) - reduced_keys._vector.begin())
    return count

cpdef minmax_int64_by_key(DeviceVectorViewInt32 keys,
                                DeviceVectorViewInt64 values,
                                DeviceVectorViewInt32 reduced_keys,
                                DeviceVectorViewInt64 min_values,
                                DeviceVectorViewInt64 max_values):
    cdef duplicate[int64_t] duplicate_f
    cdef minmax_tuple[int64_t] minmax_f
    cdef equal_to[int32_t] reduce_compare  # Functor to compare reduction keys.

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>(reduce_by_key(
        keys._vector.begin(), keys._vector.end(),
        make_transform_iterator(values._vector.begin(), duplicate_f),
        reduced_keys._vector.begin(),
        make_zip_iterator(
            make_tuple2(min_values._vector.begin(),
                        max_values._vector.begin())),
        reduce_compare, minmax_f).first) - reduced_keys._vector.begin())
    return count

cpdef minmax_uint64_by_key(DeviceVectorViewInt32 keys,
                                DeviceVectorViewUint64 values,
                                DeviceVectorViewInt32 reduced_keys,
                                DeviceVectorViewUint64 min_values,
                                DeviceVectorViewUint64 max_values):
    cdef duplicate[uint64_t] duplicate_f
    cdef minmax_tuple[uint64_t] minmax_f
    cdef equal_to[int32_t] reduce_compare  # Functor to compare reduction keys.

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>(reduce_by_key(
        keys._vector.begin(), keys._vector.end(),
        make_transform_iterator(values._vector.begin(), duplicate_f),
        reduced_keys._vector.begin(),
        make_zip_iterator(
            make_tuple2(min_values._vector.begin(),
                        max_values._vector.begin())),
        reduce_compare, minmax_f).first) - reduced_keys._vector.begin())
    return count

cpdef minmax_float32_by_key(DeviceVectorViewInt32 keys,
                                DeviceVectorViewFloat32 values,
                                DeviceVectorViewInt32 reduced_keys,
                                DeviceVectorViewFloat32 min_values,
                                DeviceVectorViewFloat32 max_values):
    cdef duplicate[float] duplicate_f
    cdef minmax_tuple[float] minmax_f
    cdef equal_to[int32_t] reduce_compare  # Functor to compare reduction keys.

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>(reduce_by_key(
        keys._vector.begin(), keys._vector.end(),
        make_transform_iterator(values._vector.begin(), duplicate_f),
        reduced_keys._vector.begin(),
        make_zip_iterator(
            make_tuple2(min_values._vector.begin(),
                        max_values._vector.begin())),
        reduce_compare, minmax_f).first) - reduced_keys._vector.begin())
    return count

cpdef minmax_float64_by_key(DeviceVectorViewInt32 keys,
                                DeviceVectorViewFloat64 values,
                                DeviceVectorViewInt32 reduced_keys,
                                DeviceVectorViewFloat64 min_values,
                                DeviceVectorViewFloat64 max_values):
    cdef duplicate[double] duplicate_f
    cdef minmax_tuple[double] minmax_f
    cdef equal_to[int32_t] reduce_compare  # Functor to compare reduction keys.

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>(reduce_by_key(
        keys._vector.begin(), keys._vector.end(),
        make_transform_iterator(values._vector.begin(), duplicate_f),
        reduced_keys._vector.begin(),
        make_zip_iterator(
            make_tuple2(min_values._vector.begin(),
                        max_values._vector.begin())),
        reduce_compare, minmax_f).first) - reduced_keys._vector.begin())
    return count




cpdef max_abs_int8(DeviceVectorViewInt8 values):
    cdef int8_t result
    cdef absolute[int8_t] absolute_f
    cdef maximum[int8_t] maximum_f

    result = reduce(
        make_transform_iterator(values._vector.begin(), absolute_f),
        make_transform_iterator(values._vector.end(), absolute_f),
        0, maximum_f)
    return result

cpdef max_abs_uint8(DeviceVectorViewUint8 values):
    cdef uint8_t result
    cdef absolute[uint8_t] absolute_f
    cdef maximum[uint8_t] maximum_f

    result = reduce(
        make_transform_iterator(values._vector.begin(), absolute_f),
        make_transform_iterator(values._vector.end(), absolute_f),
        0, maximum_f)
    return result

cpdef max_abs_int16(DeviceVectorViewInt16 values):
    cdef int16_t result
    cdef absolute[int16_t] absolute_f
    cdef maximum[int16_t] maximum_f

    result = reduce(
        make_transform_iterator(values._vector.begin(), absolute_f),
        make_transform_iterator(values._vector.end(), absolute_f),
        0, maximum_f)
    return result

cpdef max_abs_uint16(DeviceVectorViewUint16 values):
    cdef uint16_t result
    cdef absolute[uint16_t] absolute_f
    cdef maximum[uint16_t] maximum_f

    result = reduce(
        make_transform_iterator(values._vector.begin(), absolute_f),
        make_transform_iterator(values._vector.end(), absolute_f),
        0, maximum_f)
    return result

cpdef max_abs_int32(DeviceVectorViewInt32 values):
    cdef int32_t result
    cdef absolute[int32_t] absolute_f
    cdef maximum[int32_t] maximum_f

    result = reduce(
        make_transform_iterator(values._vector.begin(), absolute_f),
        make_transform_iterator(values._vector.end(), absolute_f),
        0, maximum_f)
    return result

cpdef max_abs_uint32(DeviceVectorViewUint32 values):
    cdef uint32_t result
    cdef absolute[uint32_t] absolute_f
    cdef maximum[uint32_t] maximum_f

    result = reduce(
        make_transform_iterator(values._vector.begin(), absolute_f),
        make_transform_iterator(values._vector.end(), absolute_f),
        0, maximum_f)
    return result

cpdef max_abs_int64(DeviceVectorViewInt64 values):
    cdef int64_t result
    cdef absolute[int64_t] absolute_f
    cdef maximum[int64_t] maximum_f

    result = reduce(
        make_transform_iterator(values._vector.begin(), absolute_f),
        make_transform_iterator(values._vector.end(), absolute_f),
        0, maximum_f)
    return result

cpdef max_abs_uint64(DeviceVectorViewUint64 values):
    cdef uint64_t result
    cdef absolute[uint64_t] absolute_f
    cdef maximum[uint64_t] maximum_f

    result = reduce(
        make_transform_iterator(values._vector.begin(), absolute_f),
        make_transform_iterator(values._vector.end(), absolute_f),
        0, maximum_f)
    return result

cpdef max_abs_float32(DeviceVectorViewFloat32 values):
    cdef float result
    cdef absolute[float] absolute_f
    cdef maximum[float] maximum_f

    result = reduce(
        make_transform_iterator(values._vector.begin(), absolute_f),
        make_transform_iterator(values._vector.end(), absolute_f),
        0, maximum_f)
    return result

cpdef max_abs_float64(DeviceVectorViewFloat64 values):
    cdef double result
    cdef absolute[double] absolute_f
    cdef maximum[double] maximum_f

    result = reduce(
        make_transform_iterator(values._vector.begin(), absolute_f),
        make_transform_iterator(values._vector.end(), absolute_f),
        0, maximum_f)
    return result
