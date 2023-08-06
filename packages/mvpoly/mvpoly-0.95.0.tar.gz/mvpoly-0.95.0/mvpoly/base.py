# -*- coding: utf-8 -*-

import numpy as np
import mvpoly.util.common
import mvpoly.util.version
import scipy.integrate

class MVPoly(object) :
    """
    Base (new-style) class for MVPoly. 
    """
    def __init__(self, dtype = np.double) :
        self._dtype = np.dtype(dtype) 

    def asclass(self, C) :
        """
        Return a polynomial of the specified class *C*, which
        must be one of the :class:`MVPoly` subclasses.
        """
        return C(self, dtype=self.dtype)

    @property
    def dtype(self) :
        return self._dtype

    @dtype.setter
    def dtype(self, value) :
        self._dtype = np.dtype(value)

    def intd(self, *intervals) :
        """
        Evaluate the definite integral over the cube determined 
        by the *intervals*.
        """
        pv = self.degrees
        pn = len(pv)
        assert len(intervals) == pn, \
            "%i variables but %i intervals" % (pn, len(intervals))

        ip = self.int(*(tuple([1]*pn)))
        lims = np.array(intervals)

        v = lims[0, :]
        for i in range(1, pn) :
            v = np.vstack((np.tile(v, (1, 2)), 
                           np.kron(lims[i, :], np.ones((1, 2**i)))))

        if pn == 1 :
            sgn = [-1, 1]
        else :
            c = tuple([-1, 1] for i in range(pn))
            sgn = mvpoly.util.common.kronn(*c)

        if pn > 1 :
            v = [v[i, :] for i in range(pn)]
            w = ip.eval(*v)
        else :
            w = ip.eval(v)

        return np.dot(sgn, w)

    def norm(self, order) :
        """
        Returns the *norm* of the coefficients.  The *order*
        can be a float (for the p-norm) or any other value
        accepted by the :meth:`numpy.linalg.norm` method. 
        """
        v = np.array([val for idx, val in self.nonzero])
        if v.size > 0 :
            return np.linalg.norm(v, order);
        else :
            return 0

    def norm_L(self, p, n=None) :
        """
        Returns the *Lp norm* of the polynomial, the *Lp* integral over 
        the *n*-polycircle. If the optional argument *n* is not
        supplied, it will be taken to be the number of variables in 
        the polynomial or 1, whichever is the larger.

        This method is only implemented up to *n=3* due to the 
        (obvious) exponential complexity of the quadrature.
        """
        if np.isinf(p) :
            return self.maxmodnd()[0]

        nvar = len(self.degrees)
        if n is None :
            n = max(nvar, 1)
        elif nvar > n :
            msg = "n must be at least as large as number of variables"
            raise ValueError(msg)

        twopi = 2 * np.pi

        def f(ts, p, poly) :
            """
            The integrand
            """
            zs = np.array([np.exp(1j * t) for t in ts])
            pz = poly.eval(*zs)
            return pow(abs(pz), p)

        def limits(k) :
            return [0, twopi] + [lambda *_ : 0, lambda *_ : twopi] * (k-1)

        if nvar == 0 :
            Ip = pow(abs(self[0]), p) * (twopi**n)
        else :
            if  n == 1 :
                Ip = scipy.integrate.quad(lambda t : f([t], p, self), 
                                          *limits(1))[0]
            elif n == 2 :
                Ip = scipy.integrate.dblquad(lambda *ts : f(ts, p, self), 
                                             *limits(2))[0]
            elif n == 3 :
                Ip = scipy.integrate.tplquad(lambda *ts : f(ts, p, self), 
                                             *limits(3))[0]
            elif n > 3 :
                raise NotImplementedError()
                if not mvpoly.util.version.at_least('scipy', (0, 13, 0)) :
                    raise NotImplementedError("need scipy version 0.13.0")
                Ip = scipy.integrate.nquad(lambda *ts : f(ts, p, self), 
                                           *limits(n+1), args=None, opts=None)
            else :
                raise ValueError("bad dimension %i" % (n))

        return pow(Ip/(twopi**n), 1/float(p))

    @property
    def height(self) :
        """
        Returns the *height* of the polynomial: the largest
        of the absolute values of the coefficients.
        """
        return self.norm(np.inf)

    @property
    def length(self) :
        """
        Returns the *length* of the polynomial: the sum of
        absolute values of the coefficients.
        """
        return self.norm(1)

    def maxmodnd(self, epsilon = 1e-12, i0 = None) :
        """
        The maximum modulus of a complex *n*-variate polynomial on 
        the unit *n*-polydisc is estimated using a method of repeated 
        subdivision of :math:`[0,2\pi]^n` and rejection of non-maximizing 
        *n*-cubes. 

        The rejection criterion is based on a lemma of S.B. Stečkin,
        extended to *n*-variate polynomials by G. De La Chevrotière [#DLC]_.

        :param epsilon: relative precision required
        :type epsilon: float
        :param i0: initial number of intervals in each dimension
        :type i0: an *n*-vector of integers
        :rtype: a tuple (*M*, *t*, *h*, *evals*) 

        Here  *M* is the estimate of the maximum modulus;
        *t* is an *n*-row matrix whose columns are the midpoints of 
        non-rejected *n*-cubes; *h* is the half-width 
        of non-rejected *n*-cubes; *evals* is the total number of 
        evaluations of the polynomial used.

        .. [#DLC]
            G. De La Chevrotière. *Finding the maximum modulus of a
            polynomial on the polydisk using a generalization of 
            Stečkin's lemma*, SIAM Undergrad. Res. Online, 2, 2009.
        """

        def initial_workspace(i0, n, h) :
            t0 = np.arange(i0, dtype=float).reshape((1, i0))
            t  = t0.copy()
            for k in range(1, n) :
                a = np.tile(t, (1, i0))
                b = np.kron(t0, np.ones((1, i0**k), dtype=float))
                t = np.vstack((a, b))
            return 2*h*t + h

        def subdivide_workspace(t, n, h) :
            m = t.shape[1]
            t = np.tile(t, (1, 2**n))
            for k in range(n) :
                a = np.kron([h, -h], np.ones((1, m*2**k)))
                b = np.tile(a, (1, 2**(n-k-1)))
                t[np.r_[k, :]] += b
            return t

        # parameters
        n = len(self.degrees)
        deg = self.degree
        if i0 is None :
            i0 = 3*deg
        assert i0 > 2*deg, "i0 must be at least twice the polynomial degree"

        # starting values
        h = np.pi / i0
        evals = 0
        M2min = 0.0
        M2max = np.inf

        t = initial_workspace(i0, n, h)

        while True :

            # evaluate polynomial
            z = np.exp(t * 1j)            
            pz = self.eval(*(z[i, :] for i in range(n)))
            qz = np.real(pz)**2 + np.imag(pz)**2

            # statistics
            eval0 = qz.size
            evals += eval0

            # evaluate bounds
            M2min = max(M2min, np.max(qz))
            SC    = np.cos(deg*h)
            M2max = M2min/SC

            # check for termination
            if M2max - M2min < 4*epsilon*M2min :
                break

            # rejection
            rT  = M2min * SC
            ind = np.nonzero(qz > rT)[0]
            t   = t[:, ind]

            # subdivision
            h /= 2
            t = subdivide_workspace(t, n, h)

        M = np.sqrt((M2min + M2max)/2)

        return (M, t, h, evals)

    def _binary_pow(self, n) :
        """
        Integer power implemented by binary division.
        """
        p = self
        if n == 1 :
            return p
        if n % 2 == 0 :
            p = p._binary_pow(n/2)
            return p * p
        else :
            return p * p._binary_pow(n-1)

    def __pow__(self, n) :
        """
        Default integer power, subclasses may choose to implement a 
        more efficient method (FFT and so on) for their particular 
        data-representation.
        """
        if not isinstance(n, int) :
            raise TypeError("bad power exponent type")
        if n < 0 :
            raise ArithmeticError("cannot handle negative integer powers")
        if n == 0 :
            return self.one(dtype = self.dtype)
        return self._binary_pow(n)

    def __truediv__(self, other) :
        """
        Division by a scalar. 
        """
        # Note that routing this to (1/other)*self would give 
        # surprising results for integer dtypes, so we iterate
        # over the non-zero coefficients
        p = self.zero(dtype = self.dtype)
        for idx, val in self.nonzero :
            p[idx] = val/other
        return p

    def __div__(self, other) :
        """
        Division by a scalar (Python 2 compatibility)
        """
        return self.__truediv__(other)

    def __sub__(self, other) :
        """
        Subtraction implemented with add and negate.
        """
        return self + (-other)

    def __rsub__(self, other) :
        """
        Subtraction with reversed arguments.
        """
        return other + (-self)

    def __call__(self, *args) :
        """
        Evaluate or compose polynomials, depending on whether
        any of the arguments are of :class:`MVPoly` class.
        """
        if any(isinstance(arg, self.__class__) for arg in args) :
            return self.compose(*args)
        else :
            return self.eval(*args)


    @classmethod
    def bernstein(cls, i, n, **kwargs) :
        """
        Return the output of :meth:`mvpoly.dict.MVPolyDict.bernstein` 
        converted to other polynomial subclasess.
        """
        from mvpoly.dict import MVPolyDict
        return cls(MVPolyDict.bernstein(i, n, **kwargs), **kwargs)

    @classmethod
    def lehmer(cls, **kwargs) :
        """
        Return the output of :meth:`mvpoly.cube.MVPolyCube.lehmer` 
        converted to other polynomial subclasess.
        """
        from mvpoly.cube import MVPolyCube
        return cls(MVPolyCube.lehmer(**kwargs), **kwargs)

    @classmethod
    def rudin_shapiro(cls, n, **kwargs) :
        """
        Return the output of :meth:`mvpoly.cube.MVPolyCube.rudin_shapiro` 
        converted to other polynomial subclasess.
        """
        from mvpoly.cube import MVPolyCube
        return cls(MVPolyCube.rudin_shapiro(n, **kwargs), **kwargs)


# this code imports all of the 1d orthogonal polynomials from
# the scipy.special collection with a bit of metaprogramming

import scipy.special

def add_scipy_special(cls, meth) :
    def special(cls, *args) :
        from mvpoly.cube import MVPolyCube
        coef = meth(*args).coeffs
        p = MVPolyCube(coef[::-1])
        if cls == MVPolyCube :
            return p
        else :
            return cls(p)
    name = meth.__name__
    special.__name__ = name
    special.__doc__ = "Wrapper for :meth:`scipi.special.%s`" % (name)
    setattr(MVPoly, name, classmethod(special))

for meth in [ scipy.special.legendre, 
              scipy.special.chebyt,
              scipy.special.chebyu,
              scipy.special.chebyc,
              scipy.special.chebys,
              scipy.special.jacobi,
              scipy.special.laguerre,
              scipy.special.genlaguerre,
              scipy.special.hermite,
              scipy.special.hermitenorm,
              scipy.special.gegenbauer,
              scipy.special.sh_legendre,
              scipy.special.sh_chebyt,
              scipy.special.sh_chebyu,
              scipy.special.sh_jacobi ] :
    add_scipy_special(MVPoly, meth)
