import ctypes
import tomllib
from pathlib import Path
from py_num_bench.core import Benchmark, BenchmarkSuite


# Load config
CONFIG_PATH = Path.cwd() / "conf" / "config.toml"
with open(CONFIG_PATH, "rb") as f:
    CONFIG = tomllib.load(f)

FMT_CFG = CONFIG["format"]
SIEVE_CFG = CONFIG["sieve"]
TRAP_CFG = CONFIG["trapezoid"]


def load_c_lib(path, func_name, argtypes, restype=None):
    """Helper to load compiled C shared library functions."""
    lib = ctypes.CDLL(path)
    func = getattr(lib, func_name)
    func.argtypes = argtypes
    if restype:
        func.restype = restype
    return func


def setup_sieve_benchmark():
    from py_num_bench.implementations.python import sieve as py_sieve

    b = Benchmark("Prime Sieve", tolerance=SIEVE_CFG.get("tolerance", 1e-9))
    b.register("Python", py_sieve.sieve_py)

    # Cython
    try:
        from py_num_bench.implementations.cython.sieve_cython import sieve_cython

        b.register("Cython", sieve_cython)
    except ImportError:
        print("[INFO] Cython sieve implementation not found, skipping.")

    # C
    try:
        cpath = (
            Path.cwd()
            / "src"
            / "py_num_bench"
            / "implementations"
            / "c"
            / "libsieve.so"
        )
        sieve_c = load_c_lib(
            str(cpath),
            "sieve",
            [ctypes.c_int, ctypes.POINTER(ctypes.c_int)],
            ctypes.c_int,
        )

        def sieve_c_wrapper(n):
            MAX_SIZE = n + 1
            arr = (ctypes.c_int * MAX_SIZE)()
            count = sieve_c(n, arr)
            return [arr[i] for i in range(count)]

        b.register("C", sieve_c_wrapper)
    except Exception as e:
        print(f"[INFO] C sieve implementation not available: {e}")

    # Rust
    try:
        rust_sieve = load_rust_sieve()
        if rust_sieve:
            b.register("Rust", rust_sieve)
    except Exception as e:
        print(f"[INFO] Rust sieve implementation not available: {e}")

    return b


def setup_trapezoid_benchmark():
    from py_num_bench.implementations.python import trapezoid as py_trap

    b = Benchmark("Trapezoidal Integration", tolerance=TRAP_CFG.get("tolerance", 1e-8))
    a, b_lim = TRAP_CFG.get("a", 0.0), TRAP_CFG.get("b", 1.0)
    b.register("Python", lambda n: py_trap.trapezoid_py(a, b_lim, n))

    # Cython
    try:
        from py_num_bench.implementations.cython.trapezoid_cython import (
            trapezoid_cython,
        )

        b.register("Cython", lambda n: trapezoid_cython(a, b_lim, n))
    except ImportError:
        print("[INFO] Cython trapezoid implementation not found, skipping.")

    # C
    try:
        cpath = (
            Path.cwd()
            / "src"
            / "py_num_bench"
            / "implementations"
            / "c"
            / "libtrapezoid.so"
        )
        trapezoid_c = load_c_lib(
            str(cpath),
            "trapezoid",
            [ctypes.c_double, ctypes.c_double, ctypes.c_int],
            ctypes.c_double,
        )

        def trapezoid_c_wrapper(n):
            return trapezoid_c(a, b_lim, n)

        b.register("C", trapezoid_c_wrapper)
    except Exception as e:
        print(f"[INFO] C trapezoid implementation not available: {e}")

    # Rust
    try:
        rust_trap = load_rust_trapezoid()
        if rust_trap:
            b.register("Rust", lambda n: rust_trap(a, b_lim, n))
    except Exception as e:
        print(f"[INFO] Rust trapezoid implementation not available: {e}")

    return b


def load_rust_sieve():
    path = Path(__file__).parent / "implementations" / "rust" / "libsieve_rs.dylib"
    lib = ctypes.CDLL(str(path))
    func = lib.sieve_rs
    func.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
    func.restype = ctypes.c_int

    def wrapper(n):
        arr = (ctypes.c_int * (n + 1))()
        count = func(n, arr)
        if count < 0 or count > n + 1:
            raise RuntimeError(f"Rust sieve returned invalid count {count}")
        return [arr[i] for i in range(count)]

    return wrapper


def load_rust_trapezoid():
    path = Path(__file__).parent / "implementations" / "rust" / "libtrapezoid_rs.dylib"
    lib = ctypes.CDLL(str(path))
    func = lib.trapezoid_rs
    func.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_int]
    func.restype = ctypes.c_double

    return func


if __name__ == "__main__":
    suite = BenchmarkSuite()
    suite.add_benchmark(setup_sieve_benchmark())
    suite.add_benchmark(setup_trapezoid_benchmark())

    inputs = {
        "Prime Sieve": SIEVE_CFG["inputs"],
        "Trapezoidal Integration": TRAP_CFG["inputs"],
    }
    arg_funcs = {
        "Prime Sieve": lambda n: (n,),
        "Trapezoidal Integration": lambda n: (n,),
    }

    suite.run_all(inputs, arg_funcs, warmups=4, repeats=50, min_time=2.0)
    suite.final_report(FMT_CFG)
