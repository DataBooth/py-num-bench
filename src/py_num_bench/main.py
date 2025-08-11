"""
main.py - Entrypoint for running py-num-bench benchmarks.
"""

import ctypes

# import importlib
from py_num_bench.core import Benchmark, BenchmarkSuite


def load_c_lib(path, func_name, argtypes, restype=None):
    """Load a C shared library function via ctypes."""
    lib = ctypes.CDLL(path)
    func = getattr(lib, func_name)
    func.argtypes = argtypes
    if restype:
        func.restype = restype
    return func


def setup_sieve_benchmark():
    from py_num_bench.implementations.python import sieve as py_sieve

    b = Benchmark("Prime Sieve")
    b.register("Python", py_sieve.sieve_py)

    try:
        from py_num_bench.implementations.cython.sieve_cython import sieve_cython

        b.register("Cython", sieve_cython)
    except ImportError:
        pass

    try:
        sieve_c = load_c_lib(
            "src/py_num_bench/implementations/c/libsieve.so",
            "sieve",
            [ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)],
        )

        def sieve_c_func(n):
            arr = (ctypes.c_int * (n + 1))()
            count = ctypes.c_int()
            sieve_c(n, arr, ctypes.byref(count))
            return list(arr)[: count.value]

        b.register("C", sieve_c_func)
    except OSError:
        pass

    try:
        from sieve_cpp import sieve_cpp

        b.register("C++", sieve_cpp)
    except ImportError:
        pass

    try:
        from py_num_bench.implementations.rust.sieve_rs import sieve_rs

        b.register("Rust", sieve_rs)
    except ImportError:
        pass

    return b


def setup_trapezoid_benchmark():
    from py_num_bench.implementations.python import trapezoid as py_trap

    b = Benchmark("Trapezoidal Integration", tolerance=1e-8)
    b.register("Python", py_trap.trapezoid_py)

    try:
        from py_num_bench.implementations.cython.trapezoid_cython import (
            trapezoid_cython,
        )

        b.register("Cython", trapezoid_cython)
    except ImportError:
        pass

    try:
        trap_c = load_c_lib(
            "src/py_num_bench/implementations/c/libtrapezoid.so",
            "trapezoid",
            [ctypes.c_double, ctypes.c_double, ctypes.c_int],
            ctypes.c_double,
        )
        b.register("C", trap_c)
    except OSError:
        pass

    try:
        from trapezoid_cpp import trapezoid_cpp

        b.register("C++", trapezoid_cpp)
    except ImportError:
        pass

    try:
        from py_num_bench.implementations.rust.trapezoid_rs import trapezoid_rs

        b.register("Rust", trapezoid_rs)
    except ImportError:
        pass

    return b


if __name__ == "__main__":
    suite = BenchmarkSuite()
    suite.add_benchmark(setup_sieve_benchmark())
    suite.add_benchmark(setup_trapezoid_benchmark())

    inputs = {
        "Prime Sieve": [10, 100_000, 200_000, 400_000, 800_000],
        "Trapezoidal Integration": [10, 1_000_000, 2_000_000, 4_000_000],
    }
    arg_funcs = {
        "Prime Sieve": lambda n: (n,),
        "Trapezoidal Integration": lambda n: (0.0, 1.0, n),
    }

    suite.run_all(inputs, arg_funcs)
    suite.report_all()
    suite.plot_all()
