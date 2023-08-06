import numpy as np

def kronn(b, c, *args) :
    """
    A version of :func:`numpy.kron` which takes an arbitrary 
    number of arguments.
    """
    a = np.kron(b, c)
    for d in args :
        a = np.kron(a, d)
    return a

def max_or_default(iterable, default) :
    """
    Like :func:`max`, but returns a default value if the
    iterable is empty.
    """
    try :
        return max(iterable)
    except ValueError :
        return default

def binom(n, r) :
    """
    Returns the binomial coefficient as a long integer.
    """
    assert n >= 0
    assert 0 <= r <= n
    c = 1
    denom = 1
    for (num, denom) in zip(range(n, n-r, -1), range(1, r+1, 1)):
        c = (c * num) // denom
    return c

def as_numpy_scalar(x) :
    """
    Returns a :class:`numpy` scalar.
    """
    return np.array(x).dtype.type(x)

