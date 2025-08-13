from py_num_bench.implementations.cython import sieve_cython

print(sieve_cython.sieve_cython(100))

import py_num_bench.implementations.cython.sieve_cython as sc_mod

print(type(sc_mod))  # should print <class 'module'>
print(hasattr(sc_mod, "sieve_cython"))  # should be True
print(callable(sc_mod.sieve_cython))  # should be True
