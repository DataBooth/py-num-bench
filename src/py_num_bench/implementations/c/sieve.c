/* sieve.c
   Naive C implementation of the Sieve of Eratosthenes for benchmarking.
   Arguments:
     n       - upper bound for primes
     primes  - output array (preallocated)
     count   - pointer to store number of primes found
*/

#include <stdlib.h>
#include <stdbool.h>

void sieve(int n, int* primes, int* count) {
    bool* is_prime = malloc((n+1) * sizeof(bool));
    if (!is_prime) return;
    for (int i = 0; i <= n; ++i) is_prime[i] = true;
    is_prime[0] = false;
    is_prime[1] = false;

    for (int i = 2; i*i <= n; ++i) {
        if (is_prime[i]) {
            for (int j = i*i; j <= n; j += i)
                is_prime[j] = false;
        }
    }

    int k = 0;
    for (int i = 2; i <= n; ++i) {
        if (is_prime[i]) primes[k++] = i;
    }
    *count = k;
    free(is_prime);
}
