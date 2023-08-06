# -*- coding: utf-8 -*-
"""

.. class:: MVPolyDict
   :synopsis: Multivariate polynomial class whose 
   coefficient representation is a dictionary

.. moduleauthor:: J.J. Green <j.j.green@gmx.co.uk>

"""

import mvpoly.base
import mvpoly.util.dict
import mvpoly.util.dtype
import mvpoly.util.common

import numbers
import numpy as np
import scipy as sp
import warnings

class MVPolyDict(mvpoly.base.MVPoly) :
    """
    Return an object of class :class:`MVPolyDict` with
    the coefficient dictionary set to the optional *coef*
    argument.
    """
    def __init__(self, arg=None, **kwd) :
        if isinstance(arg, mvpoly.base.MVPoly) :
            coef = self.init_from_nonzero(arg, arg.dtype).coef
            kwd['dtype'] = arg.dtype
        else :
            coef = arg
        super(MVPolyDict, self).__init__(**kwd)
        if coef is None :
            coef = {}
        else :
            for k, v in coef.items() :
                coef[k] = self.dtype.type(v)
        self._coef = coef

    def __setitem__(self, index, value) :
        """
        The setter method, which sets coefficient of the
        given *index* to the given *value*.
        """
        if value == 0 :
            return
        key = MVPolyDictMonomial(index = index).key
        self.coef[key] = self.dtype.type(value)


    def __getitem__(self, index) :
        """
        The getter method, returning the coefficient of the
        specified *index*.
        """
        key = MVPolyDictMonomial(index = index).key
        return self.coef.get(key, self.dtype.type(0))


    def __add__(self, other) :
        """
        Add an :class:`MVPolyDict` to another, or to a number; 
        return an :class:`MVPolyDict`.
        """
        a = self.coef
        a_dtype = self.dtype
        if isinstance(other, MVPolyDict) :
            b = other.coef
            b_dtype = other.dtype
        else :
            if isinstance(other, numbers.Number) :
                other = mvpoly.util.common.as_numpy_scalar(other)
            if isinstance(other, np.generic) :
                m = MVPolyDict()
                m[0] = other
                b = m.coef
                b_dtype = other.dtype
            else :
                raise TypeError("cannot add MVPolyDict to %s" % type(other))
        dtype = mvpoly.util.dtype.dtype_add(a_dtype, b_dtype)
        return MVPolyDict(mvpoly.util.dict.sum(a, b), dtype = dtype)


    def __radd__(self, other) :
        """
        As add, but with the types in the opposite order -- this is
        routed to add.
        """
        return self.__add__(other)


    def __neg__(self) :
        """
        Negation of a polynomial, return the polynomial with negated 
        coefficients.
        """
        d = mvpoly.util.dict.negate(self.coef)
        return MVPolyDict(d, dtype = self.dtype)


    def __mul__(self, other) :
        """
        Product of polynomials, or of a polynomial and a number.
        """
        d = {}
        if isinstance(other, MVPolyDict) :
            dtype = mvpoly.util.dtype.dtype_mul(self.dtype, other.dtype)
            for k1, v1 in other.coef.items() :
                m1 = MVPolyDictMonomial(key = k1)
                for k2, v2 in self.coef.items() :
                    m2 = MVPolyDictMonomial(key = k2)
                    k = (m1 * m2).key
                    v = v1 * v2 + d.get(k, 0)
                    d[k] = v
            for k, v in list(d.items()) :                
                if v == 0 :
                    d.pop(k, None)
        else :
            if isinstance(other, numbers.Number) :
                other = mvpoly.util.common.as_numpy_scalar(other)
            if isinstance(other, np.generic) :
                dtype = mvpoly.util.dtype.dtype_mul(self.dtype, other.dtype)
                if other != 0 :
                    for k, v in self.coef.items() :
                        d[k] = other * v
            else :
                msg = "cannot multiply MVPolyDict by %s" % type(other)
                raise TypeError(msg)

        return MVPolyDict(d, dtype=dtype)


    def __rmul__(self, other) :
        """
        Reverse order multiply, as add
        """
        return self.__mul__(other)


    def __eq__(self, other) :
        """
        Equality of polynomials. 
        """
        return not any((self - other).coef)

    
    def astype(self, dtype) :
        """
        Return a polynomial using the specified *dtype* for the
        coefficients.
        """
        return MVPolyDict.init_from_nonzero(self, dtype=dtype)


    @property
    def coef(self) :
        """
        Return the dictionary of coefficients. 
        """
        return self._coef

    @coef.setter
    def coef(self, value) :
        self._coef = value


    def compose(self, *args) :
        """
        Compose polynomials. The arguments, which should be
        :class:`MVPolyDict` polynomials, are substituted 
        into the corresponding variables of the polynomial.
        """
        return self.rmf_eval(*args);


    @property
    def degrees(self) :
        """
        Return the maximal degrees of each of the variables of
        the polynomial as a tuple of integers
        """
        idxs = [ MVPolyDictMonomial(key = key).index for
                 key in self.coef.keys() ]
        n = mvpoly.util.common.max_or_default((len(idx) for idx in idxs), 0)
        idxs = [idx + (0,) * (n - len(idx)) for idx in idxs]
        if idxs == [] :
            degs = () 
        else :
            degs = tuple(max(idx[i] for idx in idxs) for i in range(n)) 
        return degs


    @property
    def degree(self) :
        """
        The (total, homogeneous) *degree*, the maximal sum of the
        monomial degrees of monomials with nonzero coefficients. 
        Returns :math:`-1` for the zero polynomial.
        """
        degs = [np.sum(list(MVPolyDictMonomial(key = k).dict.values()))
                for k in self.coef.keys()]
        if not degs :
            return -1
        return max(degs)


    def diff(self, *args) :
        """
        Differentiate polynomial. The integer arguments
        should indicate the number to times to differentiate
        with respect to the corresponding polynomial variable,
        hence ``p.diff(0,1,1)`` would correspond to 
        :math:`\partial^2 p / \partial y \partial z`.
        """
        def diff2(idx, m0, m0_coef) :
            m0_dict  = m0.dict
            m1_dict = {}
            for i, n in enumerate(idx) :
                m0i = m0_dict.get(i, 0)
                if m0i < n :
                    return (None, 0)
                if m0i == n :
                    continue
                m1_dict[i] = m0i - n
                for k in range(n) :
                    m0_coef *= (m0i - k)
            return (MVPolyDictMonomial(dict = m1_dict), m0_coef)

        d = {}
        for m0_key, m0_coef in self.coef.items() :
            m0 = MVPolyDictMonomial(key = m0_key)
            m1, m1_coef = diff2(args, m0, m0_coef)
            if m1 is not None :
                d[m1.key] = m1_coef

        return MVPolyDict(d, dtype = self.dtype)


    def eval(self, *args) :
        """
        Evaluate the polynomial at the points given by *args*.
        There should be as many arguments as the polynomial 
        has variables.  The argument can be numbers, or arrays
        (all of the same shape).
        """
        # if the arguments are lists then we need to convert
        # them to numpy arrays, since rmf_eval() requires that
        array_args = [np.array(arg) for arg in args]
        array_shps = set(arg.shape for arg in array_args)
        if len(array_shps) != 1 :
            raise ValueError("eval() with arguments of differing shapes")
        array_shp = array_shps.pop()
        if array_shp == (1,) :
            return self.rmf_eval(*args);
        else :
            return self.rmf_eval(*array_args);


    def rmf_eval(self, *args) :
        """
        Both :meth:`eval` and :meth:`compose` are routed to
        this method, which performs the evaluation of polynomials
        by a depth-first pre-order traversal of a tree derived from
        the polynomial: a simplified form of the algorithm described in 
        W. C. Rheinboldt, 
        C. K. Mesztenyi,
        J. M. Fitzgerald,
        *On the evaluation of multivariate polynomials and their
        derivatives*, 
        BIT 17 (1977), 
        437–450.
        """
        nodes = [EvalNode(k, v) for k, v in self.coef.items()]
        if self.__getitem__(0) == 0 :
            nodes += [EvalNode((), np.int_(0))]
        nodes.sort(key = lambda x : x.index)

        deltas = [node1.delta(node2) 
                  for node1, node2 in zip(nodes[1:], nodes)] + [-1]

        M = self.degree
        s = [ nodes[0].coef ] + [0] * M
        i = [0] * M
        m = 0
        k = 0

        nodes = nodes[1:]
        N = len(nodes)

        while m < N :
            while True :
                i[k] = nodes[m].index[k]
                if k < nodes[m].degree - 1 :
                    s[k+1] = 0
                else :
                    s[k+1] = nodes[m].coef
                    m += 1
                    if k >= deltas[m] :
                        break
                k += 1
            while True :
                # cannot use += here, baffled? see
                # http://stackoverflow.com/questions/20133767
                s[k] = s[k] + s[k+1] * args[i[k]]
                s[k+1] = 0
                if (k == 0) or (k == deltas[m]) :
                    break
                else :
                    k -= 1
        return s[0]

    def int(self, *args, **kwargs) :
        """
        Indefinite integral of polynomial. The arguments are
        as for :meth:`diff`.
        """
        dtype = np.dtype(kwargs.get('dtype', self.dtype))
        if dtype.kind in set(['i', 'u']) :
            msg = "integral output of type %s" % (dtype.name)
            warnings.warn(msg, RuntimeWarning)

        def int2(idx, m0, m0_coef) :
            m1_coef = m0_coef.copy()
            m1_dict = {}
            for i, n in enumerate(idx) :
                m0i = m0.dict.get(i, 0)
                if m0i + n == 0 :
                    continue
                m1_dict[i] = m0i + n
                for k in range(n) :
                    m1_coef /= (m0i + k + 1)
            return (MVPolyDictMonomial(dict = m1_dict), m1_coef)

        d = {}
        for m0_key, m0_coef in self.coef.items() :
            m0 = MVPolyDictMonomial(key = m0_key)
            m1, m1_coef = int2(args, m0, m0_coef)
            d[m1.key] = m1_coef

        return MVPolyDict(d, dtype = dtype)


    @property
    def nonzero(self) :
        """
        Returns a list of 2-element tuples, for each the first
        being a (monomial) index, the second the corresponding 
        coefficient. The indices do not have trailing zeros,
        so the return value for the polynomial
        :math:`p(x,y) = 2 + 3x + 4y` would be
        ``[((), 2), ((1,), 3), ((0,1), 4)]``.
        """
        return [(MVPolyDictMonomial(key = k).index, v) 
                for k, v in self.coef.items()]


    @classmethod
    def init_from_nonzero(cls, p, dtype) :
        """
        Create a polynomial from one of any subclass; this is used 
        internally by the 
        :py:meth:`~mvpoly.cube.MVPolyDict.__init__` constructor, but
        may be useful for direct application.
        """
        q = cls.zero(dtype = dtype)
        for idx, val in p.nonzero :
            q[idx] = val
        return q


    @classmethod
    def monomials(cls, n, **kwd) :
        """
        Return a *n*-tuple of each of the monomials (*x*, *y*, ..) 
        of an *n*-variate system.
        """
        return [cls.monomial(i, n, **kwd) for i in range(n)]


    @classmethod
    def _numpy_scalar(cls, v, **kwd) :
        """
        Return a :class:`numpy` scalar which, if the optional
        argument contains a ``dtype`` entry, will be of that 
        *dtype*.
        """
        dtype = kwd.get('dtype', False) 
        if dtype :
            return np.dtype(dtype).type(v)
        else :
            return np.int_(v)


    @classmethod
    def monomial(cls, i, n, **kwd) :
        """
        Return the *i*-th monomial of an *n*-variate system,
        (*i* = 0, ..., *n*-1).
        """
        m = MVPolyDictMonomial({i:1})
        d = { m.key : cls._numpy_scalar(1, **kwd) }
        return cls(d, **kwd)


    @classmethod
    def zero(cls, **kwd) :
        """
        Return the zero polynomial. 
        """
        return cls(**kwd)


    @classmethod
    def one(cls, **kwd) :
        """
        Return the unit (1) polynomial. 
        """
        m = MVPolyDictMonomial({})
        d = { m.key: cls._numpy_scalar(1, **kwd) }
        return cls(d, **kwd)


    @classmethod
    def bernstein(cls, i, n, **kwd) :
        """
        Return the degree *n*
        `Bernstein polynomial <http://www.encyclopediaofmath.org/index.php/Bernstein_polynomials>`_ 
        of the specified index *i*. Both *n* and *i* may
        be lists or tuples of non-negative numbers of the
        same size and with *i* dominated by *n*.
        """
        def coerce_list(m) :
            if isinstance(m, str) : m = [m]
            else:
                try: iter(m)
                except TypeError: m = [m]
                else: m = list(m)
            return m

        i = coerce_list(i)
        n = coerce_list(n)
        if len(i) != len(n) :
            raise ValueError("index and degree not of same length")
        inpairs = list(zip(i, n))
        nvar    = len(inpairs)
        if any(ik > nk for ik, nk in inpairs) :
            raise ValueError("bad index %s for degree %s" % (repr(i), repr(n)))

        q  = cls.one(**kwd)
        xs = cls.monomials(nvar, **kwd)

        for k in range(nvar) :
            ik, nk = inpairs[k]
            xk = xs[k]
            C = mvpoly.util.common.binom(nk, ik)
            q = q * C * xk**ik * (1 - xk)**(nk-ik) 

        return q


class EvalNode(object) :
    """
    Helper class for the :meth:`__call__` method.
    """
    def __init__(self, key, coef) :
        self._index = MVPolyDictMonomial(key = key).occurences
        self._coef = coef.copy()

    @property
    def index(self) :
        return self._index

    @property
    def coef(self) :
        return self._coef

    @property 
    def degree(self) :
        return len(self._index)

    def delta(self, other) :
        """
        The minimal index of :meth:`index` property such that the 
        `self` and `other` differ. 
        """
        n1 = len(self.index)
        n2 = len(other.index)
        for i in range(min(n1, n2)) :
            if self.index[i] != other.index[i] :
                return i
        if n1 > n2 :
            return n2
        return 0


class MVPolyDictMonomial(object) :
    """
    A class of sparse monomials, represented internally as a 
    dict of variable numbers mapped to variable degrees (so that
    ``{0:2, 2:3}`` represents :math:`x^2 z^3`).  These can be
    serialised to a hashable :meth:`key` or expressed in a dense
    index (the above monomial has length-4 index of ``(2, 0, 3, 0)``).
    """
    def __init__(self, dict = None, key = None, index = None) :
        if dict is None :
            self._dict = {}
            if key is not None :
                self.key = key
            elif index is not None :
                self.index = index
        else :
            self._dict = dict

    def __mul__(self, other) :
        """
        Return the product of monomials.
        """
        d = mvpoly.util.dict.merge_dicts(self.dict, 
                                         other.dict, 
                                         lambda x, y : x+y) 
        return MVPolyDictMonomial(dict = d)

    @property
    def degree(self) :
        """
        The degree of the monomial: the sum of exponents.
        """
        return sum(self.dict.values())

    @property
    def dict(self) :
        """
        The dictionary.
        """
        return self._dict

    @dict.setter
    def dict(self, d) :
        self._dict = d

    @property
    def index(self) :
        """
        The monomial as an tuple of variable exponents up to the
        last variable with nonzero exponent;
        thus ``m.index`` would return ``(3, 2)``
        if ``m`` represents the monomial :math:`x^3 y^2`.
        """
        n = mvpoly.util.common.max_or_default(self.dict.keys(), -1) + 1
        return self.index_of_length(n)

    @index.setter
    def index(self, idx) :
        if hasattr(idx, "__getitem__") :
            self._dict = {k: v for (k, v) in enumerate(idx) if v != 0}
        else :
            self._dict = {} if idx == 0 else {0: idx}

    def index_of_length(self, n) :
        """
        Return the monomial as an *n*-tuple of variable exponents;
        thus ``m.index_of_length(3)`` would return ``(3, 2, 0)``
        if ``m`` represents the monomial :math:`x^3y^2`.
        """
        return tuple(self.dict.get(k, 0) for k in range(n))

    @property
    def key(self) :
        """
        A hashable representation (as a tuple of pairs) of the
        dictionary.
        """
        return tuple((k, self.dict[k]) for k in sorted(self.dict.keys()))

    @key.setter
    def key(self, kvs) :
        self._dict = {k: v for (k, v) in kvs}

    @property
    def occurences(self) :
        """
        The monomial as a tuple of variable indices repeated
        as many times as the exponent of the variable;
        thus ``m.occurences`` would return ``(0, 0, 0, 1, 1)``
        if ``m`` represents the monomial :math:`x^3 y^2`. The 
        length of this vector is the :attr:`degree` of the 
        monomial.
        """
        return tuple(i for i, e in enumerate(self.index) for _ in range(e))
        
