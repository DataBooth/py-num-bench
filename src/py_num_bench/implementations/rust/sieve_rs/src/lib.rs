// lib.rs - Rust PyO3 implementation of Sieve of Eratosthenes

use pyo3::prelude::*;

#[pyfunction]
fn sieve_rs(n: usize) -> Vec<usize> {
    let mut is_prime = vec![true; n+1];
    if n >= 0 { is_prime[0] = false; }
    if n >= 1 { is_prime[1] = false; }
    let limit = (n as f64).sqrt() as usize;
    for i in 2..=limit {
        if is_prime[i] {
            for j in (i*i..=n).step_by(i) {
                is_prime[j] = false;
            }
        }
    }
    (2..=n).filter(|&x| is_prime[x]).collect()
}

#[pymodule]
fn sieve_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sieve_rs, m)?)?;
    Ok(())
}
