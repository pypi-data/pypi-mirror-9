import numpy as np

from .int8.device_vector import (DeviceVector as DeviceVectorInt8,
                              DeviceVectorView as DeviceVectorViewInt8)
from .uint8.device_vector import (DeviceVector as DeviceVectorUint8,
                              DeviceVectorView as DeviceVectorViewUint8)
from .int16.device_vector import (DeviceVector as DeviceVectorInt16,
                              DeviceVectorView as DeviceVectorViewInt16)
from .uint16.device_vector import (DeviceVector as DeviceVectorUint16,
                              DeviceVectorView as DeviceVectorViewUint16)
from .int32.device_vector import (DeviceVector as DeviceVectorInt32,
                              DeviceVectorView as DeviceVectorViewInt32)
from .uint32.device_vector import (DeviceVector as DeviceVectorUint32,
                              DeviceVectorView as DeviceVectorViewUint32)
from .int64.device_vector import (DeviceVector as DeviceVectorInt64,
                              DeviceVectorView as DeviceVectorViewInt64)
from .uint64.device_vector import (DeviceVector as DeviceVectorUint64,
                              DeviceVectorView as DeviceVectorViewUint64)
from .float32.device_vector import (DeviceVector as DeviceVectorFloat32,
                              DeviceVectorView as DeviceVectorViewFloat32)
from .float64.device_vector import (DeviceVector as DeviceVectorFloat64,
                              DeviceVectorView as DeviceVectorViewFloat64)



def from_array(data):
    if data.dtype == np.bool:
        return DeviceVectorUint8.from_array(data)
    if data.dtype == np.int8:
        return DeviceVectorInt8.from_array(data)

    if data.dtype == np.bool:
        return DeviceVectorUint8.from_array(data)
    elif data.dtype == np.uint8:
        return DeviceVectorUint8.from_array(data)

    if data.dtype == np.bool:
        return DeviceVectorUint8.from_array(data)
    elif data.dtype == np.int16:
        return DeviceVectorInt16.from_array(data)

    if data.dtype == np.bool:
        return DeviceVectorUint8.from_array(data)
    elif data.dtype == np.uint16:
        return DeviceVectorUint16.from_array(data)

    if data.dtype == np.bool:
        return DeviceVectorUint8.from_array(data)
    elif data.dtype == np.int32:
        return DeviceVectorInt32.from_array(data)

    if data.dtype == np.bool:
        return DeviceVectorUint8.from_array(data)
    elif data.dtype == np.uint32:
        return DeviceVectorUint32.from_array(data)

    if data.dtype == np.bool:
        return DeviceVectorUint8.from_array(data)
    elif data.dtype == np.int64:
        return DeviceVectorInt64.from_array(data)

    if data.dtype == np.bool:
        return DeviceVectorUint8.from_array(data)
    elif data.dtype == np.uint64:
        return DeviceVectorUint64.from_array(data)

    if data.dtype == np.bool:
        return DeviceVectorUint8.from_array(data)
    elif data.dtype == np.float32:
        return DeviceVectorFloat32.from_array(data)

    if data.dtype == np.bool:
        return DeviceVectorUint8.from_array(data)
    elif data.dtype == np.float64:
        return DeviceVectorFloat64.from_array(data)

    raise ValueError('Unsupported type: %r' % data)


def view_from_vector(vector, first_i=0, last_i=-1):
    if vector.dtype == np.int8:
        return DeviceVectorViewInt8(vector, first_i, last_i)

    elif vector.dtype == np.uint8:
        return DeviceVectorViewUint8(vector, first_i, last_i)

    elif vector.dtype == np.int16:
        return DeviceVectorViewInt16(vector, first_i, last_i)

    elif vector.dtype == np.uint16:
        return DeviceVectorViewUint16(vector, first_i, last_i)

    elif vector.dtype == np.int32:
        return DeviceVectorViewInt32(vector, first_i, last_i)

    elif vector.dtype == np.uint32:
        return DeviceVectorViewUint32(vector, first_i, last_i)

    elif vector.dtype == np.int64:
        return DeviceVectorViewInt64(vector, first_i, last_i)

    elif vector.dtype == np.uint64:
        return DeviceVectorViewUint64(vector, first_i, last_i)

    elif vector.dtype == np.float32:
        return DeviceVectorViewFloat32(vector, first_i, last_i)

    elif vector.dtype == np.float64:
        return DeviceVectorViewFloat64(vector, first_i, last_i)

    raise ValueError('Unsupported type: %r' % vector)