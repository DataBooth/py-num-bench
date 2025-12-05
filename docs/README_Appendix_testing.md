# Appendix: Testing

## Rigorous Testing Strategies

1. **Unit Tests in Python**:  
   - Compare output of each implementation against a reference Python version for a known set of inputs.
   - Set up assertions for value equality and edge case handling (zero, negatives, large N, etc).
2. **Property-Based Testing**:  
   - For numerical algorithms, utilise libraries (e.g. `hypothesis` in Python) to generate random valid input sets.
   - Check properties like monotonicity, bounds, and invariants.
3. **Round-trip Consistency**:  
   - For algorithms with invertible operations, ensure computed outputs are reversible or reconstruct initial inputs.
4. **Profiling and Benchmarking**:  
   - Measure speed, but also memory footprint, for realistic scenarios.
   - Use `pytest-benchmark` or similar tools.
5. **Error and Exception Handling**:  
   - Ensure proper signals for invalid input; verify failures do not cause crashes in Python.
   - In C/C++/Rust, handle NULL pointers and malformed arrays.
   - 
## `pytest`-based Testing for All Implementations

Below are ready-to-use examples for testing the sieve and trapezoid implementations. You can save these as `test_sieve.py` and `test_trapezoid.py` and run with `pytest`.

### 1. Pure Python Implementation

Assuming your Python implementations are available as:

```python
from py_num_bench.implementations.python.sieve import sieve_py
from py_num_bench.implementations.python.trapezoid import trapezoid_py
```

**test_sieve.py**:

```python
import pytest
from py_num_bench.implementations.python.sieve import sieve_py

@pytest.mark.parametrize("n,expected", [
    (10, [2,3,5,7]),
    (2, [2]),
    (1, []),
])
def test_python_sieve_basic(n, expected):
    assert sieve_py(n) == expected
```

**test_trapezoid.py**:

```python
import pytest
from py_num_bench.implementations.python.trapezoid import trapezoid_py

def test_python_trapezoid_exact():
    # Analytical integral of x^2 from 0 to 1 is 1/3 ≈ 0.3333...
    approx = trapezoid_py(0.0, 1.0, 100000)
    assert abs(approx - 1.0/3.0) < 1e-6
```

***

### 2. C/C++ Implementations via ctypes

Assume you have:

- `libsieve.so`/`libsieve.dylib` with `int sieve(int n, int* arr)`
- `libtrapezoid.so`/`libtrapezoid.dylib` with `double trapezoid(double a, double b, int n)`

**test_sieve_c.py**:

```python
import pytest
import ctypes
from pathlib import Path
import sys

def get_ext():
    if sys.platform == "darwin":
        return ".dylib"
    elif sys.platform == "win32":
        return ".dll"
    else:
        return ".so"

@pytest.fixture(scope="module")
def sieve_c():
    path = Path(__file__).parent.parent / "src" / "py_num_bench" / "implementations" / "c" / f"libsieve{get_ext()}"
    lib = ctypes.CDLL(str(path))
    func = lib.sieve
    func.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
    func.restype = ctypes.c_int
    def wrapper(n):
        arr = (ctypes.c_int * (n+1))()
        count = func(n, arr)
        return [arr[i] for i in range(count)]
    return wrapper

def test_c_sieve(sieve_c):
    assert sieve_c(10) == [2,3,5,7]
    assert sieve_c(2) == [2]
    assert sieve_c(1) == []
```

**test_trapezoid_c.py**:

```python
import pytest
import ctypes
from pathlib import Path
import sys

def get_ext():
    if sys.platform == "darwin":
        return ".dylib"
    elif sys.platform == "win32":
        return ".dll"
    else:
        return ".so"

@pytest.fixture(scope="module")
def trapezoid_c():
    path = Path(__file__).parent.parent / "src" / "py_num_bench" / "implementations" / "c" / f"libtrapezoid{get_ext()}"
    lib = ctypes.CDLL(str(path))
    func = lib.trapezoid
    func.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_int]
    func.restype = ctypes.c_double
    return func

def test_c_trapezoid(trapezoid_c):
    approx = trapezoid_c(0.0, 1.0, 100000)
    assert abs(approx - 1.0/3.0) < 1e-6
```

***

### 3. Rust Implementations via ctypes

Assume you’ve copied the built `.dylib` from Rust crates as described.

**test_sieve_rust.py**:

```python
import pytest
import ctypes
from pathlib import Path
import sys

def get_ext():
    if sys.platform == "darwin":
        return ".dylib"
    elif sys.platform == "win32":
        return ".dll"
    else:
        return ".so"

@pytest.fixture(scope="module")
def sieve_rs():
    path = Path(__file__).parent.parent / "src" / "py_num_bench" / "implementations" / "rust" / f"libsieve_rs{get_ext()}"
    lib = ctypes.CDLL(str(path))
    func = lib.sieve_rs
    func.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
    func.restype = ctypes.c_int
    def wrapper(n):
        arr = (ctypes.c_int * (n+1))()
        count = func(n, arr)
        return [arr[i] for i in range(count)]
    return wrapper

def test_rust_sieve(sieve_rs):
    assert sieve_rs(10) == [2,3,5,7]
```

**test_trapezoid_rust.py**:

```python
import pytest
import ctypes
from pathlib import Path
import sys

def get_ext():
    if sys.platform == "darwin":
        return ".dylib"
    elif sys.platform == "win32":
        return ".dll"
    else:
        return ".so"

@pytest.fixture(scope="module")
def trapezoid_rs():
    path = Path(__file__).parent.parent / "src" / "py_num_bench" / "implementations" / "rust" / f"libtrapezoid_rs{get_ext()}"
    lib = ctypes.CDLL(str(path))
    func = lib.trapezoid_rs
    func.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_int]
    func.restype = ctypes.c_double
    return func

def test_rust_trapezoid(trapezoid_rs):
    approx = trapezoid_rs(0.0, 1.0, 100000)
    assert abs(approx - 1.0/3.0) < 1e-6
```

***

### 4. Cython Implementation

If your Cython modules are importable as regular Python modules:

```python
import pytest
from py_num_bench.implementations.cython.sieve_cython import sieve_cython

def test_cython_sieve():
    assert sieve_cython(10) == [2,3,5,7]
```

(similar test for trapezoid).

***

### 5. Native-Language Test Harnesses

- **C/C++**:  
  You can write a `test.c` with hardcoded inputs, print results, `assert` correctness, or integrate with testing frameworks like Catch2 (C++) or CUnit.
- **Rust**:  
  Cargo natively supports tests. In `lib.rs`:

  ```rust
  #[cfg(test)]
  mod tests {
      use super::*;
      #[test]
      fn test_sieve_rs() {
          // Setup output, call sieve_rs, check values
      }
      #[test]
      fn test_trapezoid_rs() {
          let result = trapezoid_rs(0.0, 1.0, 100000);
          assert!((result - 1.0/3.0).abs() < 1e-6);
      }
  }
  ```
  Run with `cargo test`.

- **PyO3**:  
  PyO3 functions can be tested in Rust as normal, or using Python-side pytest (if also compiled as a Python extension).

***

## How to Add/Generalise Testing for More Involved Algorithms

- **Strategy:**  
  Always create a pure Python “ground truth” implementation that is easy to read, debug, and assert on.  
  For each external (C/C++/Rust/etc) implementation, use pytest to compare output for a wide range of inputs, including edge cases, error handling, and exceptions.
- **Advanced Property Testing:**  
  Use `hypothesis` or random input testing for functions with complex input space.
- **Native/Language Test Frameworks:**  
  Use native language-specific test runners (see above) to catch bugs before linking to Python.
- **Automated Regression:**  
  Add legacy result files and check outputs match exactly or within some error tolerance for numerical algorithms.

***

**If you want complete test templates or CI integration advice for each language, just let me know!**

***

#### References
: https://en.wikipedia.org/wiki/Foreign_function_interface[1]
: https://handwiki.org/wiki/Foreign_function_interface[2]

[1] https://en.wikipedia.org/wiki/Foreign_function_interface
[2] https://handwiki.org/wiki/Foreign_function_interface
[3] https://www.haskell.org/onlinereport/haskell2010/haskellch8.html
[4] https://pen-lang.org/advanced-features/ffi/
[5] https://www.youtube.com/watch?v=fcx02vw9GNs
[6] https://stackoverflow.com/questions/5440968/understand-foreign-function-interface-ffi-and-language-binding
[7] https://docs.jax.dev/en/latest/ffi.html
[8] https://mlochbaum.github.io/BQN/doc/ffi.html