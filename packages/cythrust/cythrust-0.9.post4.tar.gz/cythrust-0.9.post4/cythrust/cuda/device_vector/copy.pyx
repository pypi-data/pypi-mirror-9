# distutils: language = c++
# cython: embedsignature = True

from libc.stdint cimport (uint8_t, uint16_t, uint32_t, uint64_t, int8_t,
                          int16_t, int32_t, int64_t)
from cythrust.thrust.device_vector cimport device_vector
from cythrust.thrust.copy cimport copy_if, copy_if_w_stencil, copy_n
from cythrust.thrust.functional cimport (positive, negative, non_positive,
                                         non_negative)
from cythrust.thrust.iterator.permutation_iterator cimport \
    make_permutation_iterator

from cythrust.cuda.device_vector cimport DeviceVectorViewInt8
from cythrust.cuda.device_vector cimport DeviceVectorViewUint8
from cythrust.cuda.device_vector cimport DeviceVectorViewInt16
from cythrust.cuda.device_vector cimport DeviceVectorViewUint16
from cythrust.cuda.device_vector cimport DeviceVectorViewInt32
from cythrust.cuda.device_vector cimport DeviceVectorViewUint32
from cythrust.cuda.device_vector cimport DeviceVectorViewInt64
from cythrust.cuda.device_vector cimport DeviceVectorViewUint64
from cythrust.cuda.device_vector cimport DeviceVectorViewFloat32
from cythrust.cuda.device_vector cimport DeviceVectorViewFloat64




    
cpdef copy_int32_if_positive(DeviceVectorViewInt32 values,
                                DeviceVectorViewInt32 output):
    cdef positive[int32_t] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), positive) - output._vector.begin())
    return count
    
cpdef copy_uint32_if_positive(DeviceVectorViewUint32 values,
                                DeviceVectorViewUint32 output):
    cdef positive[uint32_t] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), positive) - output._vector.begin())
    return count
    
cpdef copy_float32_if_positive(DeviceVectorViewFloat32 values,
                                DeviceVectorViewFloat32 output):
    cdef positive[float] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), positive) - output._vector.begin())
    return count
    

    
cpdef copy_int32_if_negative(DeviceVectorViewInt32 values,
                                DeviceVectorViewInt32 output):
    cdef negative[int32_t] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), negative) - output._vector.begin())
    return count
    
cpdef copy_uint32_if_negative(DeviceVectorViewUint32 values,
                                DeviceVectorViewUint32 output):
    cdef negative[uint32_t] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), negative) - output._vector.begin())
    return count
    
cpdef copy_float32_if_negative(DeviceVectorViewFloat32 values,
                                DeviceVectorViewFloat32 output):
    cdef negative[float] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), negative) - output._vector.begin())
    return count
    

    
cpdef copy_int32_if_non_positive(DeviceVectorViewInt32 values,
                                DeviceVectorViewInt32 output):
    cdef non_positive[int32_t] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), non_positive) - output._vector.begin())
    return count
    
cpdef copy_uint32_if_non_positive(DeviceVectorViewUint32 values,
                                DeviceVectorViewUint32 output):
    cdef non_positive[uint32_t] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), non_positive) - output._vector.begin())
    return count
    
cpdef copy_float32_if_non_positive(DeviceVectorViewFloat32 values,
                                DeviceVectorViewFloat32 output):
    cdef non_positive[float] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), non_positive) - output._vector.begin())
    return count
    

    
cpdef copy_int32_if_non_negative(DeviceVectorViewInt32 values,
                                DeviceVectorViewInt32 output):
    cdef non_negative[int32_t] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), non_negative) - output._vector.begin())
    return count
    
cpdef copy_uint32_if_non_negative(DeviceVectorViewUint32 values,
                                DeviceVectorViewUint32 output):
    cdef non_negative[uint32_t] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), non_negative) - output._vector.begin())
    return count
    
cpdef copy_float32_if_non_negative(DeviceVectorViewFloat32 values,
                                DeviceVectorViewFloat32 output):
    cdef non_negative[float] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>copy_if(
        values._vector.begin(), values._vector.end(),
        output._vector.begin(), non_negative) - output._vector.begin())
    return count
    





    
        
cpdef copy_int32_if_int32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewInt32 output):
    cdef positive[int32_t] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        positive) - output._vector.begin())
    return count
        
cpdef copy_int32_if_uint32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewInt32 output):
    cdef positive[uint32_t] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        positive) - output._vector.begin())
    return count
        
cpdef copy_int32_if_float32_stencil_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewInt32 output):
    cdef positive[float] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        positive) - output._vector.begin())
    return count
        
    
        
cpdef copy_uint32_if_int32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewUint32 output):
    cdef positive[int32_t] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        positive) - output._vector.begin())
    return count
        
cpdef copy_uint32_if_uint32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewUint32 output):
    cdef positive[uint32_t] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        positive) - output._vector.begin())
    return count
        
cpdef copy_uint32_if_float32_stencil_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewUint32 output):
    cdef positive[float] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        positive) - output._vector.begin())
    return count
        
    
        
cpdef copy_float32_if_int32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewFloat32 output):
    cdef positive[int32_t] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        positive) - output._vector.begin())
    return count
        
cpdef copy_float32_if_uint32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewFloat32 output):
    cdef positive[uint32_t] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        positive) - output._vector.begin())
    return count
        
cpdef copy_float32_if_float32_stencil_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewFloat32 output):
    cdef positive[float] positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        positive) - output._vector.begin())
    return count
        
    

    
        
cpdef copy_int32_if_int32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewInt32 output):
    cdef negative[int32_t] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        negative) - output._vector.begin())
    return count
        
cpdef copy_int32_if_uint32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewInt32 output):
    cdef negative[uint32_t] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        negative) - output._vector.begin())
    return count
        
cpdef copy_int32_if_float32_stencil_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewInt32 output):
    cdef negative[float] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        negative) - output._vector.begin())
    return count
        
    
        
cpdef copy_uint32_if_int32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewUint32 output):
    cdef negative[int32_t] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        negative) - output._vector.begin())
    return count
        
cpdef copy_uint32_if_uint32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewUint32 output):
    cdef negative[uint32_t] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        negative) - output._vector.begin())
    return count
        
cpdef copy_uint32_if_float32_stencil_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewUint32 output):
    cdef negative[float] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        negative) - output._vector.begin())
    return count
        
    
        
cpdef copy_float32_if_int32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewFloat32 output):
    cdef negative[int32_t] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        negative) - output._vector.begin())
    return count
        
cpdef copy_float32_if_uint32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewFloat32 output):
    cdef negative[uint32_t] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        negative) - output._vector.begin())
    return count
        
cpdef copy_float32_if_float32_stencil_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewFloat32 output):
    cdef negative[float] negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        negative) - output._vector.begin())
    return count
        
    

    
        
cpdef copy_int32_if_int32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewInt32 output):
    cdef non_positive[int32_t] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_positive) - output._vector.begin())
    return count
        
cpdef copy_int32_if_uint32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewInt32 output):
    cdef non_positive[uint32_t] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_positive) - output._vector.begin())
    return count
        
cpdef copy_int32_if_float32_stencil_non_positive(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewInt32 output):
    cdef non_positive[float] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_positive) - output._vector.begin())
    return count
        
    
        
cpdef copy_uint32_if_int32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewUint32 output):
    cdef non_positive[int32_t] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_positive) - output._vector.begin())
    return count
        
cpdef copy_uint32_if_uint32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewUint32 output):
    cdef non_positive[uint32_t] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_positive) - output._vector.begin())
    return count
        
cpdef copy_uint32_if_float32_stencil_non_positive(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewUint32 output):
    cdef non_positive[float] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_positive) - output._vector.begin())
    return count
        
    
        
cpdef copy_float32_if_int32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewFloat32 output):
    cdef non_positive[int32_t] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_positive) - output._vector.begin())
    return count
        
cpdef copy_float32_if_uint32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewFloat32 output):
    cdef non_positive[uint32_t] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_positive) - output._vector.begin())
    return count
        
cpdef copy_float32_if_float32_stencil_non_positive(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewFloat32 output):
    cdef non_positive[float] non_positive

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_positive) - output._vector.begin())
    return count
        
    

    
        
cpdef copy_int32_if_int32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewInt32 output):
    cdef non_negative[int32_t] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_negative) - output._vector.begin())
    return count
        
cpdef copy_int32_if_uint32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewInt32 output):
    cdef non_negative[uint32_t] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_negative) - output._vector.begin())
    return count
        
cpdef copy_int32_if_float32_stencil_non_negative(
        DeviceVectorViewInt32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewInt32 output):
    cdef non_negative[float] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[int32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_negative) - output._vector.begin())
    return count
        
    
        
cpdef copy_uint32_if_int32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewUint32 output):
    cdef non_negative[int32_t] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_negative) - output._vector.begin())
    return count
        
cpdef copy_uint32_if_uint32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewUint32 output):
    cdef non_negative[uint32_t] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_negative) - output._vector.begin())
    return count
        
cpdef copy_uint32_if_float32_stencil_non_negative(
        DeviceVectorViewUint32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewUint32 output):
    cdef non_negative[float] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[uint32_t].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_negative) - output._vector.begin())
    return count
        
    
        
cpdef copy_float32_if_int32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewInt32 stencil,
        DeviceVectorViewFloat32 output):
    cdef non_negative[int32_t] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_negative) - output._vector.begin())
    return count
        
cpdef copy_float32_if_uint32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewUint32 stencil,
        DeviceVectorViewFloat32 output):
    cdef non_negative[uint32_t] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_negative) - output._vector.begin())
    return count
        
cpdef copy_float32_if_float32_stencil_non_negative(
        DeviceVectorViewFloat32 values,
        DeviceVectorViewFloat32 stencil,
        DeviceVectorViewFloat32 output):
    cdef non_negative[float] non_negative

    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    cdef int32_t count = (<device_vector[float].iterator>
        copy_if_w_stencil(values._vector.begin(), values._vector.end(),
                        stencil._vector.begin(), output._vector.begin(),
                        non_negative) - output._vector.begin())
    return count
        
    




cpdef permute_int32(DeviceVectorViewInt32 values,
                              DeviceVectorViewInt32 index,
                              DeviceVectorViewInt32 output):
    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    copy_n(make_permutation_iterator(values._vector.begin(),
                                     index._vector.begin()),
           <size_t>index.size, output._vector.begin())

cpdef permute_uint32(DeviceVectorViewUint32 values,
                              DeviceVectorViewInt32 index,
                              DeviceVectorViewUint32 output):
    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    copy_n(make_permutation_iterator(values._vector.begin(),
                                     index._vector.begin()),
           <size_t>index.size, output._vector.begin())

cpdef permute_float32(DeviceVectorViewFloat32 values,
                              DeviceVectorViewInt32 index,
                              DeviceVectorViewFloat32 output):
    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    copy_n(make_permutation_iterator(values._vector.begin(),
                                     index._vector.begin()),
           <size_t>index.size, output._vector.begin())




cpdef permute_n_int32(DeviceVectorViewInt32 values,
                                DeviceVectorViewInt32 index, size_t count,
                                DeviceVectorViewInt32 output):
    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    copy_n(make_permutation_iterator(values._vector.begin(),
                                     index._vector.begin()), count,
           output._vector.begin())

cpdef permute_n_uint32(DeviceVectorViewUint32 values,
                                DeviceVectorViewInt32 index, size_t count,
                                DeviceVectorViewUint32 output):
    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    copy_n(make_permutation_iterator(values._vector.begin(),
                                     index._vector.begin()), count,
           output._vector.begin())

cpdef permute_n_float32(DeviceVectorViewFloat32 values,
                                DeviceVectorViewInt32 index, size_t count,
                                DeviceVectorViewFloat32 output):
    # result_type operator() (T1 j_is_sync, T2 delay_ij, T3 t_a_j) {
    copy_n(make_permutation_iterator(values._vector.begin(),
                                     index._vector.begin()), count,
           output._vector.begin())
