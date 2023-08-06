# distutils: language = c++
# cython: embedsignature = True

from libc.stdint cimport (uint8_t, uint16_t, uint32_t, uint64_t, int8_t,
                          int16_t, int32_t, int64_t)
from cythrust.thrust.device_vector cimport device_vector
from cythrust.thrust.sort cimport sort_by_key, sort

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




    
cpdef sort_int8_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewInt8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint8_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewUint8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int16_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewInt16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint16_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewUint16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int32_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewInt32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint32_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewUint32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int64_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewInt64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint64_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewUint64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float32_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewFloat32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float64_by_int8_key(DeviceVectorViewInt8 keys, DeviceVectorViewFloat64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    

    
cpdef sort_int8_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewInt8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint8_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewUint8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int16_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewInt16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint16_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewUint16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int32_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewInt32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint32_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewUint32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int64_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewInt64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint64_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewUint64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float32_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewFloat32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float64_by_uint8_key(DeviceVectorViewUint8 keys, DeviceVectorViewFloat64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    

    
cpdef sort_int8_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewInt8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint8_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewUint8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int16_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewInt16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint16_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewUint16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int32_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewInt32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint32_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewUint32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int64_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewInt64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint64_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewUint64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float32_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewFloat32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float64_by_int16_key(DeviceVectorViewInt16 keys, DeviceVectorViewFloat64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    

    
cpdef sort_int8_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewInt8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint8_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewUint8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int16_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewInt16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint16_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewUint16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int32_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewInt32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint32_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewUint32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int64_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewInt64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint64_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewUint64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float32_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewFloat32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float64_by_uint16_key(DeviceVectorViewUint16 keys, DeviceVectorViewFloat64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    

    
cpdef sort_int8_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewInt8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint8_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewUint8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int16_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewInt16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint16_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewUint16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int32_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewInt32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint32_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewUint32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int64_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewInt64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint64_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewUint64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float32_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewFloat32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float64_by_int32_key(DeviceVectorViewInt32 keys, DeviceVectorViewFloat64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    

    
cpdef sort_int8_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewInt8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint8_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewUint8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int16_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewInt16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint16_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewUint16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int32_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewInt32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint32_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewUint32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int64_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewInt64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint64_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewUint64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float32_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewFloat32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float64_by_uint32_key(DeviceVectorViewUint32 keys, DeviceVectorViewFloat64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    

    
cpdef sort_int8_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewInt8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint8_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewUint8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int16_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewInt16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint16_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewUint16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int32_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewInt32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint32_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewUint32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int64_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewInt64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint64_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewUint64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float32_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewFloat32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float64_by_int64_key(DeviceVectorViewInt64 keys, DeviceVectorViewFloat64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    

    
cpdef sort_int8_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewInt8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint8_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewUint8 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int16_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewInt16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint16_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewUint16 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int32_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewInt32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint32_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewUint32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_int64_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewInt64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_uint64_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewUint64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float32_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewFloat32 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    
cpdef sort_float64_by_uint64_key(DeviceVectorViewUint64 keys, DeviceVectorViewFloat64 values):
    sort_by_key(keys._vector.begin(), keys._vector.end(),
                values._vector.begin())
    




cpdef sort_int8(DeviceVectorViewInt8 values):
    sort(values._vector.begin(), values._vector.end())

cpdef sort_uint8(DeviceVectorViewUint8 values):
    sort(values._vector.begin(), values._vector.end())

cpdef sort_int16(DeviceVectorViewInt16 values):
    sort(values._vector.begin(), values._vector.end())

cpdef sort_uint16(DeviceVectorViewUint16 values):
    sort(values._vector.begin(), values._vector.end())

cpdef sort_int32(DeviceVectorViewInt32 values):
    sort(values._vector.begin(), values._vector.end())

cpdef sort_uint32(DeviceVectorViewUint32 values):
    sort(values._vector.begin(), values._vector.end())

cpdef sort_int64(DeviceVectorViewInt64 values):
    sort(values._vector.begin(), values._vector.end())

cpdef sort_uint64(DeviceVectorViewUint64 values):
    sort(values._vector.begin(), values._vector.end())

cpdef sort_float32(DeviceVectorViewFloat32 values):
    sort(values._vector.begin(), values._vector.end())

cpdef sort_float64(DeviceVectorViewFloat64 values):
    sort(values._vector.begin(), values._vector.end())
