# Default list recipe
default:
    @just --list

# Run the benchmark (main)
bench:
    uv run src/py_num_bench/main.py


# Setup the py-num-bench project
create-structure:
    mkdir -p src/py_num_bench/implementations/python
    mkdir -p src/py_num_bench/implementations/cython
    mkdir -p src/py_num_bench/implementations/c
    mkdir -p src/py_num_bench/implementations/cpp
    mkdir -p src/py_num_bench/implementations/rust/sieve_rs/src
    mkdir -p src/py_num_bench/implementations/rust/trapezoid_rs/src
    touch src/py_num_bench/__init__.py
    touch src/py_num_bench/core.py
    touch src/py_num_bench/main.py
    touch src/py_num_bench/implementations/__init__.py
    touch src/py_num_bench/implementations/python/__init__.py
    touch src/py_num_bench/implementations/cython/__init__.py
    touch src/py_num_bench/implementations/python/sieve.py
    touch src/py_num_bench/implementations/python/trapezoid.py
    touch src/py_num_bench/implementations/cython/sieve_cython.pyx
    touch src/py_num_bench/implementations/cython/trapezoid_cython.pyx
    touch src/py_num_bench/implementations/cython/setup.py
    touch src/py_num_bench/implementations/c/sieve.c
    touch src/py_num_bench/implementations/c/trapezoid.c
    touch src/py_num_bench/implementations/cpp/sieve.cpp
    touch src/py_num_bench/implementations/cpp/trapezoid.cpp
    touch src/py_num_bench/implementations/rust/sieve_rs/Cargo.toml
    touch src/py_num_bench/implementations/rust/sieve_rs/src/lib.rs
    touch src/py_num_bench/implementations/rust/trapezoid_rs/Cargo.toml
    touch src/py_num_bench/implementations/rust/trapezoid_rs/src/lib.rs

all: build-cython build-c build-cpp build-rust

build-cython:
    cd src/py_num_bench/implementations/cython && python setup.py build_ext --inplace

build-c:
    gcc -O3 -shared -fPIC src/py_num_bench/implementations/c/sieve.c -o src/py_num_bench/implementations/c/libsieve.so
    gcc -O3 -shared -fPIC src/py_num_bench/implementations/c/trapezoid.c -o src/py_num_bench/implementations/c/libtrapezoid.so

build-cpp:
    c++ -O3 -Wall -shared -std=c++17 -fPIC \
        `python3 -m pybind11 --includes` \
        src/py_num_bench/implementations/cpp/sieve.cpp \
        -o sieve_cpp`python3-config --extension-suffix`
    c++ -O3 -Wall -shared -std=c++17 -fPIC \
        `python3 -m pybind11 --includes` \
        src/py_num_bench/implementations/cpp/trapezoid.cpp \
        -o trapezoid_cpp`python3-config --extension-suffix`

build-rust:
    cd src/py_num_bench/implementations/rust/sieve_rs && maturin develop --release
    cd src/py_num_bench/implementations/rust/trapezoid_rs && maturin develop --release

clean:
    find . -type f \( -name "*.so" -o -name "*.pyd" -o -name "*.egg-info" \) -delete
    rm -rf build dist .pytest_cache **/target
