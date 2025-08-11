# sieve_cython.pyx

"""
Cython implementation of the Sieve of Eratosthenes for benchmarking.
Uses typed memoryviews for efficiency.
"""

def sieve_cython(int n):
    cdef int i, j
    cdef bint[:] is_prime = [True] * (n+1)
    is_prime[0] = False
    is_prime[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(n+1) if is_prime[i]]
