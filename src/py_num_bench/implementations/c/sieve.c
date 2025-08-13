/* sieve.c
   Naive C implementation of the Sieve of Eratosthenes for benchmarking.
   Arguments:
     n       - upper bound for primes
     primes  - output array (preallocated)
     count   - pointer to store number of primes found
*/

#include <math.h>
#include <stdlib.h>

// Returns number of primes <= n, fills primes_out array (must be size >= n+1)
int sieve_c(int n, int *primes_out) {
    char *is_prime = calloc(n + 1, sizeof(char));
    if (!is_prime) return -1;

    for (int i = 2; i <= n; i++) is_prime[i] = 1;

    for (int p = 2; p <= sqrt(n); p++) {
        if (is_prime[p]) {
            for (int k = p * p; k <= n; k += p)
                is_prime[k] = 0;
        }
    }

    int count = 0;
    for (int i = 2; i <= n; i++) {
        if (is_prime[i]) {
            primes_out[count++] = i;
        }
    }

    free(is_prime);
    return count;
}
