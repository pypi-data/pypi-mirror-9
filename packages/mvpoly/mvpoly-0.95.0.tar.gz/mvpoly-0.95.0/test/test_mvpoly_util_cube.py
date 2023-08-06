import numpy as np
import mvpoly.util.cube
import unittest

class TestMPUtil(unittest.TestCase):

    def test_array_enlarge(self) :
        A = np.array( [[1, 2],
                       [3, 4]], dtype = int)
        shape = (3, 4)
        B = mvpoly.util.cube.array_enlarge(A, shape)
        self.assertTrue((B == [[1,2,0,0],
                               [3,4,0,0],
                               [0,0,0,0]]).all(),
                        "bad enlarge:\n%s" % repr(B))
        self.assertTrue(B.dtype == B.dtype, "enlarge dtype")

    def test_padded_sum(self) :
        A = np.array([1, 2, 3])
        B = np.array([[1], [1]])
        C0 = mvpoly.util.cube.padded_sum(A, B)
        C1 = np.array([[2, 2, 3], [1, 0, 0]]) 
        self.assertTrue((C0 == C1).all(),
                        "bad sum:\n%s" % repr(C0))

    def test_meshgridn(self) :
        L = np.array(range(3), dtype=int)
        G = np.meshgrid(L, L, indexing='ij')
        for i in range(2) :
            Gi = mvpoly.util.cube.meshgridn((3,3),i,L)
            self.assertTrue((Gi == G[i]).all(),
                            "bad meshgridm\n%s" % (repr(Gi)))


if __name__ == '__main__':
    unittest.main()
