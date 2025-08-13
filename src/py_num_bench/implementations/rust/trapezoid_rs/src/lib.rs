// use pyo3::prelude::*; (commented out as this is a C-compatible FFI implementation)

/// FFI-exported trapezoid integration of f(x) = x^2 on [a,b] with n intervals.
#[no_mangle]
pub extern "C" fn trapezoid_rs(a: f64, b: f64, n: i32) -> f64 {
    let n = n as usize;
    if n == 0 {
        return 0.0;
    }
    let h = (b - a) / n as f64;
    let mut sum = 0.5 * (a * a + b * b);
    for i in 1..n {
        let x = a + i as f64 * h;
        sum += x * x;
    }
    sum * h
}

// // Pure Rust-to-Python version for PyO3 usage.
// #[pyfunction]
// fn trapezoid_py(a: f64, b: f64, n: i32) -> PyResult<f64> {
//     let n = n as usize;
//     if n == 0 {
//         return Ok(0.0);
//     }
//     let h = (b - a) / n as f64;
//     let mut sum = 0.5 * (a * a + b * b);
//     for i in 1..n {
//         let x = a + i as f64 * h;
//         sum += x * x;
//     }
//     Ok(sum * h)
// }

// #[pymodule]
// fn trapezoid_rs_py(py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_function(wrap_pyfunction!(trapezoid_py, py)?)?;
//     Ok(())
// }
