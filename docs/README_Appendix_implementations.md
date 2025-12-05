# Appendix 2: Comparing Implementations Across Languages and Algorithms

## Language Frameworks

| Language      | Integration Method         | Python Interop                        |
|---------------|---------------------------|---------------------------------------|
| Python        | Native                    | Direct, simple, slow                  |
| C             | Shared library + `ctypes` | Fast, manual buffer management        |
| C++           | `extern "C"` + `ctypes`   | Fast, C ABI required, STL-internal OK |
| Rust          | `#[no_mangle] extern "C"` + `ctypes` | Very fast, modern safety, needs careful FFI |
| Cython        | Python module (.so)       | Direct import, fast, seamless         |

## Algorithms: Sieve and Trapezoidal Rule

### Implementation Notes

- **Python**: Clean, readable, but slow for large loops or memory-bound algorithms.
- **C/C++/Rust via FFI**:
  - Use fixed-size types/indexing, manual memory buffer passing.
  - Return counts instead of actual output arrays for FFI.
  - For sieve, fill output arrays with primes and return count.
  - For trapezoid integration, just return the computed float.

### Pros & Cons

| Language    | Pros                                              | Cons                                           | Learning Curve                 | Python Interop                       |
|-------------|---------------------------------------------------|------------------------------------------------|-------------------------------|--------------------------------------|
| Python      | Easiest, portable, highly readable                | Slowest, not suited for heavy compute          | Very low                      | Direct                               |
| C           | Ultra fast, portable, mature ecosystem            | Manual memory, error-prone, harder debugging   | Medium (needs care)           | Simple via `ctypes`                  |
| C++         | Fast, modern STL, easier memory management        | Must use `extern "C"`, name mangling, need g++ | Medium/high for migration     | Simple if C ABI                      |
| Rust        | Safe, very fast, integrated memory safety         | Steep learning curve (ownership, borrowing)    | High, especially for FFI      | Excellent with proper FFI annotations|
| Cython      | Hybrid, easy to prototype, fast                   | Extra build step, sometimes cryptic errors     | Low for simple wrapping        | Seamless as Python module            |

### Migrating Algorithms

- **C/C++:** Modern C++11+ features can greatly ease pain points (RAII, vectors); using `extern "C"` is essential for Python interoperability.
- **Rust:** Can be a challenge for non-experts due to strict ownership system, but once mastered it prevents many bugs common in C/C++. PyO3 and the FFI ecosystem make Python integration straightforward if you follow conventions.
- **Cython:** Makes prototyping almost as easy as pure Python, with substantial performance boosts.

#### Practical notes:
- For most numerical tasks (array-oriented, simple math algorithms) **translation is repetitive but conceptually straightforward**—types, loops, and function returns mirror directly.  
- More complex algorithms (advanced data structures, external IO, OS-specific code) require deeper adaptation for each language, especially if you need to return complex objects or manage external resources.

***

## Generalising for More Involved Algorithms

As you target **more complex and computationally demanding algorithms**:
- **Data types and structures become more important:**  
  You'll need to decide on interoperable representations (structs, arrays, pointers) and provide Python wrappers or conversion logic.
- **Memory management and error handling**:  
  These are more subtle and critical—especially when using manual allocation in C, pointers, or FFI in Rust.
- **Interface consistency**:  
  Favor simple, C-style function signatures for FFI. Return counts, flags, error codes, and let Python handle more complex marshalling.
- **Testing and validation**:  
  Is even more critical: always build a high-quality reference implementation (often in Python) to compare against.
- **Performance tuning**:  
  Use benchmarking to guide optimisation effort. For some problems, algorithmic improvements in Python may yield larger speedups than migrating to C/C++/Rust.

### Key Takeaway

Migrating well-defined numeric algorithms to C/C++/Rust for Python performance is often straightforward for mature programmers—once boilerplate and FFI patterns are set. For intricate problems, invest effort into interface design and testing, as bugs in native code can manifest in unpredictable ways.

### Acronyms

- **FFI (Foreign Function Interface):**  
  A programming mechanism allowing code written in one language (e.g., Python) to call functions written in another language (e.g., C, Rust). FFIs are vital for “gluing” native libraries into higher-level code, especially for performance or system-level interoperability.[1][2]

- **ABI (Application Binary Interface):**  
  A low-level “contract” that defines how functions, data, and system calls are represented at the binary level between programs and the OS or between foreign code modules.

- **ctypes:**  
  A standard Python library for calling C functions in shared libraries, defining precise type mappings so Python can interact safely and efficiently with native code.

- **PyO3:**  
  A Rust crate (library) allowing you to write Python extension modules or interact with Python from Rust in a high-level, ergonomic way.

- **Cython:**  
  A language that mixes Python and C. Cython code is compiled to C, producing fast Python modules that can directly integrate C code.

- **RAII (Resource Acquisition Is Initialisation):**  
  A C++/Rust technique where resource management (memory, file handles) is tied to object construction/destruction, reducing manual cleanup errors.

- **STL (Standard Template Library):**  
  A powerful collection of standard data structures and algorithms in C++.

[1] https://book.pythontips.com/en/latest/python_c_extension.html
[2] https://saidvandeklundert.net/2022-06-02-extending-python-with-c/
[3] https://docs.python.org/3/library/ctypes.html
[4] https://realpython.com/build-python-c-extension-module/
[5] https://coderslegacy.com/python/ctypes-tutorial/
[6] https://nesi.github.io/perf-training/python-scatter/ctypes
[7] https://docs.python.org/3/extending/extending.html
[8] https://www.youtube.com/watch?v=neexS0HK9TY
[9] https://www.swiftorial.com/tutorials/programming_languages/python/c_extensions_ffi/ctypes
[10] https://stackoverflow.com/questions/8067171/ctypes-vs-c-extension
