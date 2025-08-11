// sieve.cpp
// Naive C++ implementation of Sieve of Eratosthenes (exposed via pybind11 - https://pybind11.readthedocs.io)

#include <pybind11/pybind11.h>
#include <vector>
#include <cmath>

namespace py = pybind11;

std::vector<int> sieve_cpp(int n) {
    std::vector<bool> is_prime(n+1, true);
    is_prime[0] = false;
    is_prime[1] = false;
    int limit = static_cast<int>(std::sqrt(n));
    for (int i = 2; i <= limit; ++i) {
        if (is_prime[i]) {
            for (int j = i*i; j <= n; j += i)
                is_prime[j] = false;
        }
    }
    std::vector<int> primes;
    for (int i = 2; i <= n; ++i) {
        if (is_prime[i]) primes.push_back(i);
    }
    return primes;
}

PYBIND11_MODULE(sieve_cpp, m) {
    m.def("sieve_cpp", &sieve_cpp);
}
