// sieve.cpp
// Naive C++ implementation of Sieve of Eratosthenes (exposed via pybind11 - https://pybind11.readthedocs.io)

#include <cmath>
#include <vector>
#include <cstdlib>

// Used extern "C" to prevent name-mangling (not using pybind11 here)
extern "C" int sieve_cpp(int n, int *primes_out) {
    std::vector<char> is_prime(n + 1, true);

    for (int p = 2; p <= std::sqrt(n); p++) {
        if (is_prime[p]) {
            for (int k = p * p; k <= n; k += p)
                is_prime[k] = false;
        }
    }

    int count = 0;
    for (int i = 2; i <= n; i++) {
        if (is_prime[i]) {
            primes_out[count++] = i;
        }
    }
    return count;
}
