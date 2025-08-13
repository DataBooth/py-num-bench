// use pyo3::prelude::*; (commented out as this is a C-compatible FFI implementation)

/// FFI-exported C-compatible Sieve of Eratosthenes.
/// Fills `primes_out` with primes <= n and returns the number of primes found.
#[no_mangle]
pub extern "C" fn sieve_rs(n: i32, primes_out: *mut i32) -> i32 {
    if n < 2 {
        return 0;
    }
    let limit = n as usize;
    let mut is_prime = vec![true; limit + 1];

    for p in 2..=((limit as f64).sqrt() as usize) {
        if is_prime[p] {
            for multiple in (p * p..=limit).step_by(p) {
                is_prime[multiple] = false;
            }
        }
    }

    let mut count = 0;
    unsafe {
        for i in 2..=limit {
            if is_prime[i] {
                *primes_out.add(count) = i as i32;
                count += 1;
            }
        }
    }
    count as i32
}

// /// Pure Rust-to-Python function for PyO3 usage (not using PyO3 for this example)
// #[pyfunction]
// fn sieve_py(n: i32) -> PyResult<Vec<i32>> {
//     let mut primes = Vec::new();
//     let limit = n as usize;
//     let mut is_prime = vec![true; limit + 1];

//     for p in 2..=((limit as f64).sqrt() as usize) {
//         if is_prime[p] {
//             for multiple in (p * p..=limit).step_by(p) {
//                 is_prime[multiple] = false;
//             }
//         }
//     }
//     for i in 2..=limit {
//         if is_prime[i] {
//             primes.push(i as i32);
//         }
//     }
//     Ok(primes)
// }

// #[pymodule]
// fn sieve_rs_py(py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_function(wrap_pyfunction!(sieve_py, py)?)?;
//     Ok(())
// }
