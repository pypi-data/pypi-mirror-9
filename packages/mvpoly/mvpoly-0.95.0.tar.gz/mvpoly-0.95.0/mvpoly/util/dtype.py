import numpy as np

def dtype_add(dt1, dt2) :
    return (np.dtype(dt1).type(0) + np.dtype(dt2).type(0)).dtype

def dtype_minus(dt1, dt2) :
    return (np.dtype(dt1).type(0) - np.dtype(dt2).type(0)).dtype

def dtype_mul(dt1, dt2) :
    return (np.dtype(dt1).type(0) * np.dtype(dt2).type(0)).dtype


