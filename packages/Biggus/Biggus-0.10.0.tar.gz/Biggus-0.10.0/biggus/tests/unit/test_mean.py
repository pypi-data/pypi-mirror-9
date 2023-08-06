# (C) British Crown Copyright 2014, Met Office
#
# This file is part of Biggus.
#
# Biggus is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Biggus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Biggus. If not, see <http://www.gnu.org/licenses/>.
"""Unit tests for `biggus.mean`."""

import numpy as np
import numpy.ma as ma
import unittest

import biggus
from biggus import mean


class TestInvalidAxis(unittest.TestCase):
    def setUp(self):
        self.array = biggus.NumpyArrayAdapter(np.arange(12))

    def test_none(self):
        with self.assertRaises(biggus.AxisSupportError):
            mean(self.array)

    def test_too_large(self):
        with self.assertRaises(ValueError):
            mean(self.array, axis=1)

    def test_too_small(self):
        with self.assertRaises(ValueError):
            mean(self.array, axis=-2)

    def test_multiple(self):
        array = biggus.NumpyArrayAdapter(np.arange(12).reshape(3, 4))
        with self.assertRaises(biggus.AxisSupportError):
            mean(array, axis=(0, 1))


class TestAggregationDtype(unittest.TestCase):
    def _check(self, source, target):
        array = biggus.NumpyArrayAdapter(np.arange(2, dtype=source))
        agg = mean(array, axis=0)
        self.assertEqual(agg.dtype, target)

    def test_int_to_float(self):
        dtypes = [np.int8, np.int16, np.int32, np.int]
        for dtype in dtypes:
            self._check(dtype, np.float)

    def test_bool_to_float(self):
        self._check(np.bool, np.float)

    def test_floats(self):
        dtypes = [np.float16, np.float32, np.float]
        for dtype in dtypes:
            self._check(dtype, dtype)

    def test_complex(self):
        self._check(np.complex, np.complex)


class TestNumpyArrayAdapter(unittest.TestCase):
    def setUp(self):
        self.data = np.arange(12)

    def _check(self, data, dtype=None, shape=None):
        data = np.asarray(data, dtype=dtype)
        if shape is not None:
            data = data.reshape(shape)
        array = biggus.NumpyArrayAdapter(data)
        result = mean(array, axis=0).ndarray()
        expected = np.mean(data, axis=0)
        if expected.ndim == 0:
            expected = np.asarray(expected)
        np.testing.assert_array_equal(result, expected)

    def test_flat_int(self):
        self._check(self.data)

    def test_multi_int(self):
        self._check(self.data, shape=(3, 4))

    def test_flat_float(self):
        self._check(self.data, dtype=np.float)

    def test_multi_float(self):
        self._check(self.data, dtype=np.float, shape=(3, 4))


class TestNumpyArrayAdapterMasked(unittest.TestCase):
    def _check(self, data):
        array = biggus.NumpyArrayAdapter(data)
        result = mean(array, axis=0).masked_array()
        expected = ma.mean(data, axis=0)
        if expected.ndim == 0:
            expected = ma.asarray(expected)
        np.testing.assert_array_equal(result.filled(), expected.filled())
        np.testing.assert_array_equal(result.mask, expected.mask)

    def test_no_mask_flat(self):
        for dtype in [np.int, np.float]:
            data = ma.arange(12, dtype=dtype)
            self._check(data)

    def test_no_mask_multi(self):
        for dtype in [np.int, np.float]:
            data = ma.arange(12, dtype=dtype).reshape(3, 4)
            self._check(data)

    def test_flat(self):
        for dtype in [np.int, np.float]:
            data = ma.arange(12, dtype=dtype)
            data[::2] = ma.masked
            self._check(data)

            data.mask = ma.nomask
            data[1::2] = ma.masked
            self._check(data)

    def test_multi(self):
        for dtype in [np.int, np.float]:
            data = ma.arange(12, dtype=dtype)
            data[::2] = ma.masked
            self._check(data.reshape(3, 4))

            data = ma.arange(12, dtype=dtype)
            data[1::2] = ma.masked
            self._check(data.reshape(3, 4))

            data = ma.arange(12, dtype=dtype).reshape(3, 4)
            data[::2] = ma.masked
            self._check(data)

            data = ma.arange(12, dtype=dtype).reshape(3, 4)
            data[1::2] = ma.masked
            self._check(data)


if __name__ == '__main__':
    unittest.main()
