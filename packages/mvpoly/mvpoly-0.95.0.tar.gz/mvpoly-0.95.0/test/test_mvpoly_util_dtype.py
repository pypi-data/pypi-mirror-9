import numpy as np
import mvpoly.util.dtype
import unittest

testdat = [ [int,        int,        int],
            [float,      int,        float],
            [int,        float,      float],
            [float,      float,      float],
            [np.int,     np.int,     np.int],
            [np.float,   np.int,     np.float],
            [np.int,     np.float,   np.float],
            [np.float,   np.float,   np.float],
            [np.float32, np.float32, np.float32],
            [np.float64, np.float32, np.float64],
            [np.float32, np.float64, np.float64],
            [np.float64, np.float64, np.float64],
            ]

class TestMPUtilDtype(unittest.TestCase) :

    def test_dtype_add(self) :
        for dat in  testdat :
            t1, t2, exp = dat
            obt = mvpoly.util.dtype.dtype_add(t1, t2)
            self.assertTrue(obt == exp, "dtype plus %s" % (repr(obt)))

    def test_dtype_minus(self) :
        for dat in  testdat :
            t1, t2, exp = dat
            obt = mvpoly.util.dtype.dtype_minus(t1, t2)
            self.assertTrue(obt == exp, "dtype minus %s" % (repr(obt)))

    def test_dtype_mul(self) :
        for dat in  testdat :
            t1, t2, exp = dat
            obt = mvpoly.util.dtype.dtype_mul(t1, t2)
            self.assertTrue(obt == exp, "dtype mul %s" % (repr(obt)))


