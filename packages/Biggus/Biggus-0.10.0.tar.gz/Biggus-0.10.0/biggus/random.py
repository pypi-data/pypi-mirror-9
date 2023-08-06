from functools import wraps

import numpy as np

import biggus


def _wrap_shape(np_func):
    @wraps(np_func)
    def func(shape):
        return _RandomShape(np_func, shape)
    return func

def _wrap_sizes(np_func):
    @wraps(np_func)
    def func(*sizes):
        return _RandomSizes(np_func, sizes)
    return func


rand = _wrap_sizes(np.random.rand)
randn = _wrap_sizes(np.random.randn)

random = _wrap_shape(np.random.random)


class _RandomShape(biggus.Array):
    def __init__(self, func, shape):
        self.func = func
        self._shape = shape

    @property
    def shape(self):
        return self._shape

    @property
    def dtype(self):
        return np.dtype(float)

    def __getitem__(self, keys):
        shape = biggus._sliced_shape(self.shape, keys)
        return _RandomShape(self.func, shape)

    def ndarray(self):
        return self.func(self.shape)

    def masked_array(self):
        return np.ma.asarray(self.ndarray())


class _RandomSizes(biggus.Array):
    def __init__(self, np_func, shape):
        self.np_func = np_func
        self._shape = shape

    @property
    def shape(self):
        return self._shape

    @property
    def dtype(self):
        return np.dtype(float)

    def __getitem__(self, keys):
        shape = biggus._sliced_shape(self.shape, keys)
        return _RandomSizes(self.func, shape)

    def ndarray(self):
        return self.func(self.shape)

    def masked_array(self):
        return np.ma.asarray(self.ndarray())
