import numpy as np
import pandas as pd
import inspect
from numba import jit, vectorize, guvectorize
from functools import wraps
from io import StringIO

def create_apply_function_string(sigout, sigin):
    s = StringIO()
    total_len = len(sigout) + len(sigin)
    out_args = ["x_" + str(i) for i in range(0, len(sigout))]
    in_args = ["x_" + str(i) for i in range(len(sigout), total_len)]

    s.write("def ap_func({0}):\n".format(",".join(out_args + in_args)))
    s.write("  for i in range(len(x_0)):\n")

    out_index = [x + "[i]" for x in out_args]
    in_index = [x + "[i]" for x in in_args]
    s.write("    " + ",".join(out_index) + " = ")
    s.write("jitted_f(" + ",".join(in_index) + ")\n")
    s.write("  return " + ",".join(out_args) + "\n")

    return s.getvalue()


def apply_jit(dtype_sig_out, dtype_sig_in, **kwargs):
    """
    make a decorator that takes in a _calc-style function, handle the apply step
    """
    dtype_sig_out = [s.strip() for s in dtype_sig_out.split(",")]
    dtype_sig_in = [s.strip() for s in dtype_sig_in.split(",")]
    dtype_sigs = dtype_sig_out + dtype_sig_in
    def make_wrapper(func):
        theargs = inspect.getargspec(func).args
        jitted_f = jit(**kwargs)(func)

        """def ap_func(*final_array):
            for i in range(len(np_arrays[0])):
                ans = jitted_f(*[x[i] for x in final_array[2:])
            return final_array[:2]"""

        afunc = """def ap_func(r, s, t, u, v):
                    for i in range(len(r)):
                        r[i], s[i] = jitted_f(t[i], u[i], v[i])
                    return r, s
                """
        #exec(afunc)
        bfunc = create_apply_function_string(dtype_sig_out, dtype_sig_in)
        afunc_code = compile(bfunc, "<string>", "exec")
        fakeglobals = {}
        eval(afunc_code, {"jitted_f": jitted_f}, fakeglobals)

        #import pdb
        #pdb.set_trace()

        """def ap_func(r, s, t, u, v):
        #def ap_func(*dtype_sigs):
            for i in range(len(r)):
                #r[i], s[i] = jitted_f(*[x[i] for x in [t,u,v] ])
                r[i], s[i] = jitted_f(t[i], u[i], v[i])
                #dtype_sigs[0][i], dtype_sigs[1][i] = jitted_f(dtype_sigs[2][i], dtype_sigs[3][i], dtype_sigs[4][i])
            return r, s"""

        #jitted_apply = jit(**kwargs)(ap_func)
        #jitted_apply = jit(**kwargs)(locals()['ap_func'])
        jitted_apply = jit(**kwargs)(fakeglobals['ap_func'])

        def wrapper(*args, **kwargs):
            in_arrays = []
            out_arrays = []
            for farg in theargs:
                if hasattr(args[0], farg):
                    in_arrays.append(getattr(args[0], farg))
                else:
                    in_arrays.append(getattr(args[1], farg))

            for farg in dtype_sig_out:
                if hasattr(args[0], farg):
                    out_arrays.append(getattr(args[0], farg))
                else:
                    out_arrays.append(getattr(args[1], farg))

            final_array = in_arrays + out_arrays
            ans = jitted_apply(*final_array)
            return ans

        return wrapper
    return make_wrapper
