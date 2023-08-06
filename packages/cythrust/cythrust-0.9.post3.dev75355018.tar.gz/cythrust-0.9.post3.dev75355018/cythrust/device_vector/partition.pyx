# distutils: language = c++
# cython: embedsignature = True

from libc.stdint cimport (uint8_t, uint16_t, uint32_t, uint64_t, int8_t,
                          int16_t, int32_t, int64_t)
from cythrust.thrust.device_vector cimport device_vector
from cythrust.thrust.partition cimport partition, partition_w_stencil
from cythrust.thrust.functional cimport (positive, negative, non_positive,
                                         non_negative)

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




    
cpdef partition_int32_positive(DeviceVectorViewInt32
                                         values):
    cdef positive[int32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>partition(
        values._vector.begin(), values._vector.end(), _positive) -
        values._vector.begin())
    return count
    
cpdef partition_uint32_positive(DeviceVectorViewUint32
                                         values):
    cdef positive[uint32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>partition(
        values._vector.begin(), values._vector.end(), _positive) -
        values._vector.begin())
    return count
    
cpdef partition_float32_positive(DeviceVectorViewFloat32
                                         values):
    cdef positive[float] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>partition(
        values._vector.begin(), values._vector.end(), _positive) -
        values._vector.begin())
    return count
    

    
cpdef partition_int32_negative(DeviceVectorViewInt32
                                         values):
    cdef negative[int32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>partition(
        values._vector.begin(), values._vector.end(), _negative) -
        values._vector.begin())
    return count
    
cpdef partition_uint32_negative(DeviceVectorViewUint32
                                         values):
    cdef negative[uint32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>partition(
        values._vector.begin(), values._vector.end(), _negative) -
        values._vector.begin())
    return count
    
cpdef partition_float32_negative(DeviceVectorViewFloat32
                                         values):
    cdef negative[float] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>partition(
        values._vector.begin(), values._vector.end(), _negative) -
        values._vector.begin())
    return count
    

    
cpdef partition_int32_non_positive(DeviceVectorViewInt32
                                         values):
    cdef non_positive[int32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>partition(
        values._vector.begin(), values._vector.end(), _non_positive) -
        values._vector.begin())
    return count
    
cpdef partition_uint32_non_positive(DeviceVectorViewUint32
                                         values):
    cdef non_positive[uint32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>partition(
        values._vector.begin(), values._vector.end(), _non_positive) -
        values._vector.begin())
    return count
    
cpdef partition_float32_non_positive(DeviceVectorViewFloat32
                                         values):
    cdef non_positive[float] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>partition(
        values._vector.begin(), values._vector.end(), _non_positive) -
        values._vector.begin())
    return count
    

    
cpdef partition_int32_non_negative(DeviceVectorViewInt32
                                         values):
    cdef non_negative[int32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>partition(
        values._vector.begin(), values._vector.end(), _non_negative) -
        values._vector.begin())
    return count
    
cpdef partition_uint32_non_negative(DeviceVectorViewUint32
                                         values):
    cdef non_negative[uint32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>partition(
        values._vector.begin(), values._vector.end(), _non_negative) -
        values._vector.begin())
    return count
    
cpdef partition_float32_non_negative(DeviceVectorViewFloat32
                                         values):
    cdef non_negative[float] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>partition(
        values._vector.begin(), values._vector.end(), _non_negative) -
        values._vector.begin())
    return count
    




    
        
cpdef partition_int32_int32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil):
    cdef positive[int32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_int32_uint32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil):
    cdef positive[uint32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_int32_float32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil):
    cdef positive[float] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_uint32_int32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil):
    cdef positive[int32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_uint32_uint32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil):
    cdef positive[uint32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_uint32_float32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil):
    cdef positive[float] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_float32_int32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil):
    cdef positive[int32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_float32_uint32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil):
    cdef positive[uint32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_float32_float32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil):
    cdef positive[float] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
    

    
        
cpdef partition_int32_int32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil):
    cdef negative[int32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_int32_uint32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil):
    cdef negative[uint32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_int32_float32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil):
    cdef negative[float] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_uint32_int32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil):
    cdef negative[int32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_uint32_uint32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil):
    cdef negative[uint32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_uint32_float32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil):
    cdef negative[float] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_float32_int32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil):
    cdef negative[int32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_float32_uint32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil):
    cdef negative[uint32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_float32_float32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil):
    cdef negative[float] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
    

    
        
cpdef partition_int32_int32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil):
    cdef non_positive[int32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_int32_uint32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil):
    cdef non_positive[uint32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_int32_float32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil):
    cdef non_positive[float] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_uint32_int32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil):
    cdef non_positive[int32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_uint32_uint32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil):
    cdef non_positive[uint32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_uint32_float32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil):
    cdef non_positive[float] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_float32_int32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil):
    cdef non_positive[int32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_float32_uint32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil):
    cdef non_positive[uint32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_float32_float32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil):
    cdef non_positive[float] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
    

    
        
cpdef partition_int32_int32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil):
    cdef non_negative[int32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_int32_uint32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil):
    cdef non_negative[uint32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_int32_float32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil):
    cdef non_negative[float] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_uint32_int32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil):
    cdef non_negative[int32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_uint32_uint32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil):
    cdef non_negative[uint32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_uint32_float32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil):
    cdef non_negative[float] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_float32_int32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil):
    cdef non_negative[int32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_float32_uint32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil):
    cdef non_negative[uint32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_float32_float32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil):
    cdef non_negative[float] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.end(),
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
    




    
        
cpdef partition_n_int32_int32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef positive[int32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_int32_uint32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef positive[uint32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_int32_float32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef positive[float] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_uint32_int32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef positive[int32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_uint32_uint32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef positive[uint32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_uint32_float32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef positive[float] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_float32_int32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef positive[int32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_float32_uint32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef positive[uint32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_float32_float32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef positive[float] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
    

    
        
cpdef partition_n_int32_int32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef negative[int32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_int32_uint32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef negative[uint32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_int32_float32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef negative[float] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_uint32_int32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef negative[int32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_uint32_uint32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef negative[uint32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_uint32_float32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef negative[float] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_float32_int32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef negative[int32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_float32_uint32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef negative[uint32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_float32_float32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef negative[float] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
    

    
        
cpdef partition_n_int32_int32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef non_positive[int32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_int32_uint32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef non_positive[uint32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_int32_float32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef non_positive[float] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_uint32_int32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef non_positive[int32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_uint32_uint32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef non_positive[uint32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_uint32_float32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef non_positive[float] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_float32_int32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef non_positive[int32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_float32_uint32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef non_positive[uint32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_float32_float32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef non_positive[float] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
    

    
        
cpdef partition_n_int32_int32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef non_negative[int32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_int32_uint32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef non_negative[uint32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_int32_float32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef non_negative[float] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_uint32_int32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef non_negative[int32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_uint32_uint32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef non_negative[uint32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_uint32_float32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef non_negative[float] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_float32_int32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil, size_t N):
    cdef non_negative[int32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_float32_uint32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil, size_t N):
    cdef non_negative[uint32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_float32_float32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil, size_t N):
    cdef non_negative[float] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin(), values._vector.begin() + N,
                            stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
    




    
        
cpdef partition_n_offset_int32_int32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef positive[int32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_int32_uint32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef positive[uint32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_int32_float32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef positive[float] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_offset_uint32_int32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef positive[int32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_uint32_uint32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef positive[uint32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_uint32_float32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef positive[float] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_offset_float32_int32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef positive[int32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_float32_uint32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef positive[uint32_t] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_float32_float32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef positive[float] _positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _positive) -
        values._vector.begin())
    return count
        
    

    
        
cpdef partition_n_offset_int32_int32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef negative[int32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_int32_uint32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef negative[uint32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_int32_float32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef negative[float] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_offset_uint32_int32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef negative[int32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_uint32_uint32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef negative[uint32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_uint32_float32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef negative[float] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_offset_float32_int32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef negative[int32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_float32_uint32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef negative[uint32_t] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_float32_float32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef negative[float] _negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _negative) -
        values._vector.begin())
    return count
        
    

    
        
cpdef partition_n_offset_int32_int32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef non_positive[int32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_int32_uint32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef non_positive[uint32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_int32_float32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef non_positive[float] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_offset_uint32_int32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef non_positive[int32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_uint32_uint32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef non_positive[uint32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_uint32_float32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef non_positive[float] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_offset_float32_int32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef non_positive[int32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_float32_uint32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef non_positive[uint32_t] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_float32_float32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef non_positive[float] _non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_positive) -
        values._vector.begin())
    return count
        
    

    
        
cpdef partition_n_offset_int32_int32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef non_negative[int32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_int32_uint32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef non_negative[uint32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_int32_float32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef non_negative[float] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[int32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_offset_uint32_int32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef non_negative[int32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_uint32_uint32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef non_negative[uint32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_uint32_float32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef non_negative[float] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[uint32_t].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
    
        
cpdef partition_n_offset_float32_int32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil, size_t N,
        size_t offset):
    cdef non_negative[int32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_float32_uint32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil, size_t N,
        size_t offset):
    cdef non_negative[uint32_t] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
cpdef partition_n_offset_float32_float32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil, size_t N,
        size_t offset):
    cdef non_negative[float] _non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (
        <device_vector[float].iterator>
        partition_w_stencil(values._vector.begin() + N, values._vector.begin()
                            + N + offset, stencil._vector.begin(), _non_negative) -
        values._vector.begin())
    return count
        
    
