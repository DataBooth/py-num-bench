# sieve_cython.pyx

"""
Cython implementation of the Sieve of Eratosthenes for benchmarking.
Uses typed memoryviews for efficiency.
"""

import array
from cpython cimport array

def sieve_cython(int n):
    cdef int i, j
    # Create Python array.array of signed chars with value 1 (True)
    cdef array.array arr = array.array('b', [1] * (n + 1))
    cdef signed char[:] is_prime = arr  # memoryview with matching signed char type

    is_prime[0] = 0
    is_prime[1] = 0

    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = 0

    # Collect and return list of primes
    return [i for i in range(n + 1) if is_prime[i]]



