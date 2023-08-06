import numpy as np
import scipy as sp
import mvpoly.util.common
import unittest

class TestMPUtilCommonBinom(unittest.TestCase) :
    
    def test_binom_reference(self) :
        for n, i in [ (3,2), (5,0), (7, 6) ] :
            a = mvpoly.util.common.binom(n, i)
            b = int(round(sp.special.binom(n, i)))
            self.assertTrue(a == b, "binomial against reference")

class TestMPUtilCommonKronn(unittest.TestCase):

    def test_kronn_simple(self) :
        a = np.array([1, -1])
        b = np.array([1, 1])
        expected = np.array([1, 1, 1, 1, -1, -1, -1, -1])
        obtained = mvpoly.util.common.kronn(a, b, b)
        self.assertTrue((expected == obtained).all(),
                        "bad kronn:\n%s" % repr(obtained))

    def test_kronn_1_arg(self) :
        a = np.array([2,3])
        self.assertRaises(TypeError, mvpoly.util.common.kronn, a)

    def test_kronn_2_arg(self) :
        a = np.array([2,3])
        b = np.array([4,1])
        expected = np.kron(a, b)
        obtained = mvpoly.util.common.kronn(a, b)
        self.assertTrue((expected == obtained).all(),
                        "bad kronn:\n%s" % repr(obtained))

    def test_kronn_dtype(self) :
        for dt in (int, float) :
            a = np.array([[2, 3], [4, 5]], dtype=dt)
            expected = dt
            obtained = mvpoly.util.common.kronn(a, a, a).dtype
            self.assertTrue(expected == obtained,
                            "bad kronn dtype:\n%s" % repr(obtained))


if __name__ == '__main__':
    unittest.main()
