from numba import jit
import pandas as pd
from pandas import DataFrame
import numpy as np
from magic import *

@jit(nopython=True)
def Test_calc(x, y, z):
    a = x + y
    b = y + z
    return (a, b)


@jit(nopython=True)
def Test_apply(a, b, x, y, z):  
                
    for i in range(len(a)):
        (a[i], b[i]) = Test_calc(x[i], y[i], z[i])

    return (a, b)

def Test(pm, pf):
    # Adjustments
    outputs = \
        pf.a, pf.b = \
            Test_apply(pm.a, pm.b, pf.x, pf.y, pf.z)

    header = ['a', 'b']
    return DataFrame(data=np.column_stack(outputs),
                     columns=header)

#@jit(nopython=True)
@apply_jit("a, b", "x, y, z", nopython=True)
def Magic_calc(x, y, z):
    a = x + y
    b = x + y + z
    return (a, b)


"""@jit(nopython=True)
def Test_apply(a, b, x, y, z):  
                
    for i in range(len(a)):
        (a[i], b[i]) = Test_calc(x[i], y[i], z[i])

    return (a, b)"""

def Magic(pm, pf):
    # Adjustments
    outputs = \
        pf.a, pf.b = \
            Magic_calc(pm, pf)
            #Magic_calc(pm.a, pm.b, pf.x, pf.y, pf.z)

    header = ['a', 'b']
    return DataFrame(data=np.column_stack(outputs),
                     columns=header)


class Foo(object):
    pass

def test_stuff():
    pm = Foo()
    pf = Foo()
    pm.a = np.zeros((5,))
    pm.b = np.zeros((5,))
    pf.x = np.zeros((5,))
    pf.y = np.zeros((5,))
    pf.z = np.zeros((5,))
    xx = Test(pm, pf)


def test_magic():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    xx = Magic(pm, pf)
    import pdb
    pdb.set_trace()
    assert xx is not None
