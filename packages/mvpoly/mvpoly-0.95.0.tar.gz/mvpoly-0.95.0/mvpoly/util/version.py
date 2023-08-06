# some tools for versions of libraries

import scipy.version
import numpy.version

def at_least(libstr, req) :
    if libstr == 'scipy' :
        verstr = scipy.version.version
    elif libstr == 'numpy' :
        verstr = numpy.version.version
    else :
        raise ValueError("library %s not known" % (libstr))
    ver = tuple([int(c) for c in verstr.split('.')])
    return compare_versions(req, ver) <= 0

def compare_versions(v1, v2) :
    for p1, p2 in zip(v1, v2) :
        if p1 < p2 :
            return -1
        if p1 > p2 :
            return 1
    return 0
