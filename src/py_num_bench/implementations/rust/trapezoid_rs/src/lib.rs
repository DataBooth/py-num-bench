// lib.rs - Rust PyO3 implementation of trapezoidal integration for f(x) = x^2

use pyo3::prelude::*;

#[pyfunction]
fn trapezoid_rs(a: f64, b: f64, n: usize) -> f64 {
    let h = (b - a) / (n as f64);
    let mut s = 0.5 * (a*a + b*b);
    for i in 1..n {
        let x = a + (i as f64) * h;
        s += x*x;
    }
    s * h
}

#[pymodule]
fn trapezoid_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(trapezoid_rs, m)?)?;
    Ok(())
}
