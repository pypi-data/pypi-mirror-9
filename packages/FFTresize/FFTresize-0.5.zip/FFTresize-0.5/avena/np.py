#!/usr/bin/env python

from numpy import around, empty as _empty, mean, std
from numpy import int8, int16, int32, int64
from numpy import uint8, uint16, uint32, uint64
from numpy import float32, float64
from sys import float_info as _float_info


_eps = 10.0 * _float_info.epsilon

# Map of NumPy array type strings to types
_np_dtypes = {
    'int8':     int8,
    'int16':    int16,
    'int32':    int32,
    'int64':    int64,
    'uint8':    uint8,
    'uint16':   uint16,
    'uint32':   uint32,
    'uint64':   uint64,
    'float32':  float32,
    'float64':  float64,
}


_dtype_bounds = {
    'float32':  (0.0, 1.0),
    'float64':  (0.0, 1.0),
    'uint8':    (0, 255),
}


def from_uint8(array, dtype):
    new_array = array.astype(dtype)
    return new_array


def to_uint8(array):
    uint8_array = _empty(array.shape, dtype=uint8)
    around(array * 255, out=uint8_array)
    return uint8_array


def clip(array, bounds):
    '''Clip the values of an array to the given interval.'''
    (min, max) = bounds
    x = array < min + _eps
    y = array > max - _eps
    array[x] = min
    array[y] = max
    return


def normalize(array):
    '''Normalize an array to the interval [0,1].'''
    mu = mean(array)
    rho2 = std(array)
    min = mu - 3.0 * rho2
    max = mu + 3.0 * rho2
    array -= min
    if max - min > _eps:
        array /= max - min
    return


if __name__ == '__main__':
    pass
