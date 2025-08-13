# `py-num-bench`

A multi-language Python numerical benchmarking framework comparing Python, Cython, C, C++, and Rust implementations of typical numerical algorithms.

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/databooth/py-num-bench/CI)

## Overview

**py-num-bench** is a modular benchmarking framework designed to compare numerical algorithms implemented in several programming languages and paradigms. It currently includes:

- Prime sieve (Sieve of Eratosthenes).
- Numerical integration (Trapezoidal rule for $$ f(x) = x^2 $$).

Implementations exist in:

- Pure Python
- Cython
- C (shared libraries)
- C++ (shared libraries)
- Rust (separate crates, FFI and Python bindings)

The benchmark suite uses a **uniform Python interface** to load and run all implementations safely, with automatic detection of available backends.

***

## Features

- Consistent benchmark interface with configurable warmups, repeats, and tolerance.
- Supports Python-native and multiple compiled backends loaded via `ctypes`.
- Builds isolated Rust crates per algorithm, exposing both FFI APIs and Python modules (optional).
- Portable `justfile` for building and cleaning all targets without hardcoded paths.
- Detailed logs and fallbacks when certain language backends are unavailable.

***

## Getting Started

### Prerequisites

- Python 3.11+ environment with `tomllib` support.
- Rust (1.70+) for building Rust crates.
- GCC/G++ for building C and C++ shared libraries.
- Cython for optional Cython benchmarks.
- `just` command runner (optional but recommended).

### Installation

Clone the repository:

```bash
git clone 
cd py-num-bench
```

Install Python requirements if available (e.g., for Cython or benchmarking utilities).

***

### Build All Backends

Using the provided `justfile`, you can build all language implementations with:

```bash
just build-all
```

This will:

- Compile all C, C++, Rust (separate crates), and Cython targets.
- Copy Rust `.dylib` artifacts to locations for Python loading.

***

### Clean Build Artifacts

Clean all compiled artifacts and Rust target directories with:

```bash
just clean
```

This runs appropriate clean commands per language and crate, including `cargo clean`.

***

### Run Benchmarks

Benchmarks are invoked by running the main Python script:

```bash
uv run src/py_num_bench/main.py
```

This script loads all available implementations and runs benchmarks for configured input sizes specified in the config TOML file.

***

## Project Structure

```
src/py_num_bench/
├── implementations/
│   ├── c/               # C source and shared libs
│   ├── cpp/             # C++ source and shared libs
│   ├── cython/          # Cython source and compiled extensions
│   ├── python/          # Pure Python implementations
│   └── rust/            # Rust crates per algorithm
│       ├── sieve_rs/    # Rust crate for sieve algorithm
│       └── trapezoid_rs/ # Rust crate for trapezoidal integration
├── core.py              # Benchmark framework
├── main.py              # Benchmark orchestration and loading logic
├── conf/config.toml     # Configuration of inputs, tolerances, and formats
└── justfile             # Build and clean recipes
```

***

## Python Integration

The benchmark pipeline uses Python's `ctypes` to load compiled shared libraries when available. Rust crates expose:

- A C-compatible `extern "C"` function for direct FFI calls (used by benchmarks).
- Optionally, Python extensions via PyO3 modules for direct import.

Python wrappers safely load these libraries, define argument and return types, and provide simple higher-level wrappers exposing algorithmic functions.

***

# Appendices

***

## Appendix A: C Implementation Details

- Algorithms compiled as shared libraries (`.so`, `.dylib`) with position-independent code.
- Functions use simple C interfaces (e.g., `int sieve(int n, int *out_array)`).
- Python `ctypes` wrappers handle allocation of output buffers and error checking.
- Shared libraries located in `src/py_num_bench/implementations/c/`.

**Python notes:**

- Use `ctypes.CDLL` to load the shared lib.
- Define `argtypes` and `restype` precisely.
- Allocate ctypes arrays before calling for output buffers.

***

## Appendix B: C++ Implementation Details

- Functions declared with `extern "C"` linkage to disable name mangling.
- Source is compiled into shared libraries similarly to C.
- Internally uses C++ STL features (e.g., `std::vector`).
- Compatible with Python's `ctypes`.

**Python notes:**

- Load `.so`/`.dylib` with `ctypes`.
- Match function signatures in Python.
- No pybind11 module is needed unless you want direct Python import.

***

## Appendix C: Rust Implementation Details

- Separate crates per algorithm under `src/py_num_bench/implementations/rust/`.
- Each crate has a `Cargo.toml` with:

```toml
[lib]
crate-type = ["cdylib"]
```

- Provides:
  - `#[no_mangle] pub extern "C"` functions for FFI use with `ctypes`.
  - Optional `#[pyfunction]` wrappers exposed via PyO3 module for direct Python import.
- Shared libraries (`.dylib`) built under `target/release` and copied to a common directory for Python loading.
- Clean builds with `cargo clean`.

**Python notes:**

- Use `ctypes` to load the FFI functions from shared libs.
- Ensure argument and return types are carefully specified.
- Optionally, import PyO3 extension modules if installed.

***

## Appendix D: Cython Implementation Details

- Source in `src/py_num_bench/implementations/cython/`.
- Compiled with Python's C API into `.so` extensions.
- Loaded naturally as Python imports.
- Used for intermediate performance between pure Python and compiled languages.

***

## Appendix E: Benchmarking Framework

- `Benchmark` and `BenchmarkSuite` classes manage registration, execution, and reporting.
- Runs multiple tests with warmups and repeats.
- Configurable input sizes and tolerance levels via `conf/config.toml`.
- Results can be formatted flexibly.

***

## License

MIT license - see [LICENSE](LICENSE) file for details.

***

## Contributing

Add Instructions for contribution, reporting issues, submitting pull requests, etc.

***

## Contact

Add contact information or project homepage.

***

[1] https://milabench.readthedocs.io/en/stable/new_benchmarks.html
[2] https://github.com/benchopt/template_benchmark
[3] https://tomforb.es/blog/benchmarking-rustpython-with-criterion/
[4] https://www.makeareadme.com
[5] https://realpython.com/readme-python-project/
[6] https://www.reddit.com/r/programming/comments/cfeu99/readme_template_i_use_for_most_of_my_projects/
[7] https://thousandbrainsproject.readme.io/docs/running-benchmarks
[8] https://www.youtube.com/watch?v=12trn2NKw5I
[9] https://dbader.org/blog/write-a-great-readme-for-your-github-project