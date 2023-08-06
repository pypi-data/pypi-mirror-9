from mvpoly.cube import *
import numpy as np
import warnings
import unittest

class TestMVPolyCube(unittest.TestCase) :

    def test_construct_from_empty(self) :
        obtained = MVPolyCube().coef
        expected = []
        self.assertTrue((expected == obtained).all(),
                        "bad constructor:\n%s" % repr(obtained))


class TestMVPolyCubeDtype(unittest.TestCase) :

    def setUp(self) :
        a = [1, 2, 3, 4]
        self.f = MVPolyCube(a, dtype=float) 
        self.i = MVPolyCube(a, dtype=int) 

    def test_construct_get_dtype(self) :
        self.assertTrue(self.f.dtype == float,
                        "bad dtype: %s" % repr(self.f.dtype))
        self.assertTrue(self.i.dtype == int,
                        "bad dtype: %s" % repr(self.i.dtype))

    def test_construct_set_dtype(self) :
        self.f.dtype = bool
        self.assertTrue(self.f.dtype == bool,
                        "bad dtype: %s" % repr(self.f.dtype))

    def test_construct_dtype_persist(self) :
        p = MVPolyCube([1, 2], dtype = int) 
        qs = [p+p, p+1, 1+p, p*p, 2*p, p*2, p**3, 2*p]
        for q in qs :
            self.assertTrue(q.dtype == int,
                            "bad dtype: %s" % repr(q.dtype))

class TestMVPolyCubeSetitem(unittest.TestCase) :

    def test_regression_broadcast(self) :
        # regression in __setitem__() : when passed an empty
        # tuple the value was broadcast to the whole array,
        # we don't want that
        coef = np.zeros((3,3), dtype=int)
        p = MVPolyCube(coef, dtype=int)
        p[()] = 1
        q = MVPolyCube.one(dtype=int)
        self.assertTrue(p == q, "setitem broadcast regression")


class TestMVPolyCubeEqual(unittest.TestCase) :

    def test_equal_self(self) :
        p = MVPolyCube([[1, 2, 3], [4, 5, 6]])
        self.assertTrue(p == p, "bad equality")

    def test_equal_diffsize(self) :
        p = MVPolyCube([[1, 2, 0], [4, 5, 0]])
        q = MVPolyCube([[1, 2], [4, 5]])
        self.assertTrue(p == q, "bad equality")

    def test_equal_diffdim(self) :
        p = MVPolyCube([[1, 2, 3], [0, 0, 0]])
        q = MVPolyCube([1, 2, 3])
        self.assertTrue(p == q, "bad equality")

    def test_unequal(self) :
        p = MVPolyCube([1, 2, 3])
        q = MVPolyCube([1, 2, 3, 4])
        self.assertFalse(p == q, "bad equality")
        self.assertTrue(p != q, "bad non-equality")


class TestMVPolyCubeNonzero(unittest.TestCase) :

    def test_nonzero_enumerate(self) :
        x, y = MVPolyCube.monomials(2)
        p = 3*x + y**2 + 7
        obt = p.nonzero
        exp = [((0, 0), 7.0), ((1, 0), 3.0), ((0, 2), 1.0)]
        self.assertTrue(sorted(obt) == sorted(exp),
                        "nonzero")


class TestMVPolyCubeAdd(unittest.TestCase) :

    def setUp(self) :
        self.A = MVPolyCube([1, 2, 3])
        self.B = MVPolyCube([[1], [1]])

    def test_add1(self) :
        obtained = (self.A + self.B).coef
        expected = [[2, 2, 3], [1, 0, 0]]
        self.assertTrue((expected == obtained).all(),
                        "bad sum:\n%s" % repr(obtained))

    def test_add2(self) :
        obtained = (self.A + 1).coef
        expected = [2, 2, 3]
        self.assertTrue((expected == obtained).all(),
                        "bad sum:\n%s" % repr(obtained))

    def test_add3(self) :
        obtained = (1 + self.A).coef
        expected = [2, 2, 3]
        self.assertTrue((expected == obtained).all(),
                        "bad sum:\n%s" % repr(obtained))


class TestMVPolyCubeMultiply(unittest.TestCase) :
    
    def setUp(self) :
        self.A = MVPolyCube([1, 1], dtype = int)
        self.B = MVPolyCube([[1, 1], [1, 1]], dtype = int)

    def test_multiply_scalar(self) :
        obtained = (2 * self.A).coef
        expected = [2, 2]
        self.assertTrue((expected == obtained).all(),
                        "bad multiply:\n%s" % repr(obtained))

    def test_multiply_1d(self) :
        obtained = (self.A * self.A).coef
        expected = [1, 2, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad multiply:\n%s" % repr(obtained))

    def test_multiply_dtype(self) :
        self.A.dtype = int
        C = self.A * self.A
        self.assertTrue((C.dtype == int),
                        "bad product type:\n%s" % repr(C.dtype))
        
    def test_multiply_dimension(self) :
        expected = [[1, 1], [2, 2], [1, 1]] 
        obtained = (self.A * self.B).coef
        self.assertTrue((expected == obtained).all(),
                        "bad AB multiply:\n%s" % repr(obtained))
        obtained = (self.B * self.A).coef
        self.assertTrue((expected == obtained).all(),
                        "bad BA multiply:\n%s" % repr(obtained))

    def test_multiply_arithmetic(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p1 = (x + y)*(2*x - y)
        p2 = 2*x**2 + x*y - y**2
        self.assertTrue((p1.coef == p2.coef).all(),
                        "bad multiply:\n%s\n%s" % (repr(p1.coef), 
                                                   repr(p2.coef)))

    def test_multiply_complex(self) :
        x, y = MVPolyCube.monomials(2, dtype=complex)
        p1 = (x + y)*(x + 1j*y)
        p2 = x**2 + (1 + 1j)*x*y + 1j*y**2
        self.assertTrue((p1.coef == p2.coef).all(),
                        "bad multiply:\n%s\n%s" % (repr(p1.coef), 
                                                   repr(p2.coef)))


class TestMVPolyCubePower(unittest.TestCase) :

    def test_power_small(self) :
        A = MVPolyCube([1, 1])
        obtained = (A**2).coef
        expected = [1, 2, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad power:\n%s" % repr(obtained))
        obtained = (A**3).coef
        expected = [1, 3, 3, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad power:\n%s" % repr(obtained))

    def test_power_types(self) :
        A = MVPolyCube([1, 1], dtype=int)
        obtained = (A**5).coef
        expected = [1, 5, 10, 10, 5, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad power:\n%s" % repr(obtained))
        self.assertTrue(obtained.dtype == int,
                        "wrong data type for power: %s" % repr(obtained.dtype))

    def test_power_badargs(self) :
        A = MVPolyCube([1, 1])
        self.assertRaises(TypeError, A.__pow__, 1.5)
        self.assertRaises(ArithmeticError, A.__pow__, -2)


class TestMVPolyCubeMonomials(unittest.TestCase) :

    def test_monomials_count(self) :
        for n in [2,3,4] :
            M = MVPolyCube.monomials(n)
            self.assertTrue(len(M) == n)

    def test_monomials_create(self) :
        x, y, z = MVPolyCube.monomials(3)
        self.assertTrue((x.coef == [[[0]],[[1]]]).all(), 
                        "bad x monomial: \n%s" % repr(x.coef))
        self.assertTrue((y.coef == [[[0],[1]]]).all(), 
                        "bad y monomial: \n%s" % repr(y.coef))
        self.assertTrue((z.coef == [[[0, 1]]]).all(), 
                        "bad z monomial: \n%s" % repr(z.coef))

    def test_monomials_build(self) :
        x, y = MVPolyCube.monomials(2)
        p = 2*x**2 + 3*x*y + 1
        self.assertTrue((p.coef == [[1, 0], [0, 3], [2, 0]]).all(),
                        "bad build: \n%s" % repr(p.coef))

    def test_monomials_dtype(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p = 2*x**2 + 3*x*y + 1
        for m in (x, y, p) :
            self.assertTrue(m.dtype == int,
                            "bad type: \n%s" % repr(m.dtype))
            self.assertTrue(m.coef.dtype == int,
                            "bad type: \n%s" % repr(m.coef.dtype))


class TestMVPolyCubeNeg(unittest.TestCase) :

    def test_negation(self) :
        x, y = MVPolyCube.monomials(2)
        p = 2*x**2 - 3*x*y + 1
        obtained = (-p).coef
        expected = [[-1, 0], [0, 3], [-2, 0]]
        self.assertTrue((obtained == expected).all(),
                        "bad negation:\n%s" % repr(obtained))


class TestMVPolyCubeSubtract(unittest.TestCase) :

    def test_subtract(self) :
        x, y = MVPolyCube.monomials(2)
        p = 1 - x
        q = -(x - 1)
        self.assertTrue((p.coef == q.coef).all(),
                        "bad subtract:\n%s\n%s" \
                            % (repr(p.coef), repr(q.coef)))


class TestMVPolyCubeEval(unittest.TestCase) :

    def makep(self, x, y) :
        return (1 - x**2) * (1 + y) - 8

    def setUp(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        self.p = self.makep(x, y)
        self.x = [0, 1, -1, 0,  7, 3,  -3, 1]
        self.y = [0, 0,  0, 3, -1, 2, -10, 2]
        self.n = len(self.x)

    def test_eval_point(self) :
        for i in range(self.n) :
            obtained = self.p(self.x[i], self.y[i])
            expected = self.makep(self.x[i], self.y[i])
            self.assertTrue(expected == obtained,
                            "bad eval: %s" % (repr(obtained)))

    def test_eval_array_1d(self) :
        obtained = self.p(self.x, self.y)
        expected = [self.makep(self.x[i], self.y[i]) for i in range(self.n)]
        self.assertTrue((expected == obtained).all(),
                        "bad eval: %s" % (repr(obtained)))

    def test_eval_array_2d(self) :
        n = self.n
        x = np.reshape(self.x, (2, n/2))
        y = np.reshape(self.y, (2, n/2))
        obtained = self.p(x, y)
        self.assertTrue(obtained.shape == (2, n/2))
        obtained.shape = (n,)
        expected = [self.makep(self.x[i], self.y[i]) for i in range(self.n)]
        self.assertTrue((expected == obtained).all(),
                        "bad eval: %s" % (repr(obtained)))

    def test_eval_badargs(self) :
        self.assertRaises(AssertionError, self.p, self.x[1:], self.y)


class TestMVPolyCubeDiff(unittest.TestCase) :

    def test_diff_invariant(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p  = x + 2*y
        expected = p.coef.copy()
        q = p.diff(1,0)
        obtained = p.coef
        self.assertTrue((expected == obtained).all(), 
                        "polynomial modified by diff %s" % \
                            (repr(obtained)))

class TestMVPolyCubeIntDiff(unittest.TestCase) :

    def test_intdif_random(self) :
        for dt in [float, complex] :
            shp = (9, 10, 11)
            c = np.random.randint(low=-10, high=10, size=shp)
            p = MVPolyCube(c, dtype=dt)
            expected = p.coef
            obtained = p.int(1, 1, 2).diff(1, 1, 2).coef
            self.assertTrue((np.abs(expected - obtained) < 1e-10).all(),
                            "bad integrate-differentiate \n%s\n%s" % \
                                (repr(obtained), repr(expected)))


# this will not be added for a while, it is here just to
# check that mvpoly integration works for the author

def have_maxmodnb() :
    try:
        import maxmodnb
    except ImportError:
        return False
    return True

@unittest.skipUnless(have_maxmodnb(), "maxmodnb not installed")
class TestMVPolyCubeMaxmodnb(unittest.TestCase) :

    def test_maxmodnb_simple(self) :
        eps = 1e-10
        x, y = MVPolyCube.monomials(2, dtype=complex)
        p = x**2 + 1
        expected = 2.0
        obtained = p.maxmodnb(eps = eps)[0]
        self.assertTrue(abs(expected - obtained) < eps*expected, 
                        "bad maxmodnb %s" % repr(obtained))

    def test_maxmodnb_fifomax(self) :
        x, y = MVPolyCube.monomials(2, dtype=complex)
        p = x**2 + 1
        self.assertRaises(RuntimeError, p.maxmodnb, fifomax = 3)

    def test_maxmodnb_unknown_keyword(self) :
        x, y = MVPolyCube.monomials(2, dtype=complex)
        p = x**2 + 1
        self.assertRaises(ValueError, p.maxmodnb, nosuchvar = 3)

    def test_maxmodnb_no_positional_args(self) :
        x, y = MVPolyCube.monomials(2, dtype=complex)
        p = x**2 + 1
        self.assertRaises(TypeError, p.maxmodnb, 3)


if __name__ == '__main__':
    unittest.main()
