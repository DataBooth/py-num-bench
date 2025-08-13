import ctypes
import importlib.resources as pkg_resources
import sys
import tomllib
from pathlib import Path

from py_num_bench.core import Benchmark, BenchmarkSuite
from py_num_bench.implementations.python import sieve as sieve_py
from py_num_bench.implementations.python import trapezoid as trapezoid_py

try:
    from py_num_bench.implementations.cython.sieve_cython import sieve_cython
except ImportError:
    sieve_cython = None

try:
    from py_num_bench.implementations.cython.trapezoid_cython import trapezoid_cython
except ImportError:
    trapezoid_cython = None


# ---------------------------
# Config
# ---------------------------
CONFIG_PATH = Path(__file__).parents[2] / "conf" / "config.toml"
with open(CONFIG_PATH, "rb") as f:
    CONFIG = tomllib.load(f)

FMT_CFG = CONFIG["format"]
SIEVE_CFG = CONFIG["sieve"]
TRAP_CFG = CONFIG["trapezoid"]

PKG_C = "py_num_bench.implementations.c"
PKG_RUST = "py_num_bench.implementations.rust"


# ---------------------------
# Helpers
# ---------------------------
def lib_filename(base: str, lang: str) -> str:
    """Return correct shared library filename for a given language."""
    if lang == "c":
        # C builds produce .so even on macOS
        return f"{base}.so"
    if lang == "rust":
        if sys.platform.startswith("darwin"):
            return f"{base}.dylib"
        elif sys.platform.startswith("win32"):
            return f"{base}.dll"
        else:
            return f"{base}.so"
    return f"{base}.so"


def load_lib_function(pkg: str, lib_file: str, func_name: str, argtypes, restype=None):
    """Generic shared library loader for ctypes functions."""
    try:
        with pkg_resources.as_file(pkg_resources.files(pkg) / lib_file) as lib_path:
            if not lib_path.exists():
                raise FileNotFoundError(f"Library not found: {lib_path}")
            lib = ctypes.CDLL(str(lib_path))
            func = getattr(lib, func_name)
            func.argtypes = argtypes
            if restype is not None:
                func.restype = restype
            return func
    except (FileNotFoundError, AttributeError, OSError) as e:
        print(f"[INFO] Could not load {func_name} from {lib_file}: {e}")
        return None


# ---------------------------
# Algorithm Benchmark class
# ---------------------------
class AlgorithmBenchmark:
    def __init__(self, name, inputs, arg_func, tolerance):
        self.name = name
        self.inputs = inputs
        self.arg_func = arg_func
        self.benchmark = Benchmark(name, tolerance=tolerance)

    def register_python(self, func):
        self.benchmark.register("Python", func)

    def register_cython(self, func):
        if func:
            self.benchmark.register("Cython", func)

    def register_c(self, func):
        if func:
            self.benchmark.register("C", func)

    def register_rust(self, func):
        if func:
            self.benchmark.register("Rust", func)


# ---------------------------
# Create Benchmarks
# ---------------------------

# Prime Sieve
sieve_bench = AlgorithmBenchmark(
    "Prime Sieve",
    inputs=SIEVE_CFG["inputs"],
    arg_func=lambda n: (n,),
    tolerance=SIEVE_CFG.get("tolerance", 1e-9),
)
sieve_bench.register_python(sieve_py.sieve_py)
sieve_bench.register_cython(sieve_cython)

# C implementation
_c_sieve = load_lib_function(
    PKG_C,
    lib_filename("libsieve", "c"),
    "sieve_c",  # function name in the C code
    [ctypes.c_int, ctypes.POINTER(ctypes.c_int)],
    ctypes.c_int,
)
if _c_sieve:

    def sieve_c(n):
        arr = (ctypes.c_int * (n + 1))()
        count = _c_sieve(n, arr)
        return [arr[i] for i in range(count)]

    sieve_bench.register_c(sieve_c)

# Rust implementation
_rust_sieve = load_lib_function(
    PKG_RUST,
    lib_filename("libsieve_rs", "rust"),
    "sieve_rs",
    [ctypes.c_int, ctypes.POINTER(ctypes.c_int)],
    ctypes.c_int,
)
if _rust_sieve:

    def sieve_rust(n):
        arr = (ctypes.c_int * (n + 1))()
        count = _rust_sieve(n, arr)
        return [arr[i] for i in range(count)]

    sieve_bench.register_rust(sieve_rust)

# ---------------------------
# Trapezoid Integration
# ---------------------------
trap_bench = AlgorithmBenchmark(
    "Trapezoidal Integration",
    inputs=TRAP_CFG["inputs"],
    arg_func=lambda n: (n,),
    tolerance=TRAP_CFG.get("tolerance", 1e-8),
)

a, b_lim = TRAP_CFG.get("a", 0.0), TRAP_CFG.get("b", 1.0)
trap_bench.register_python(lambda n: trapezoid_py.trapezoid_py(a, b_lim, n))
trap_bench.register_cython(
    lambda n: trapezoid_cython(a, b_lim, n) if trapezoid_cython else None
)

# C trapezoid
_c_trap = load_lib_function(
    PKG_C,
    lib_filename("libtrapezoid", "c"),
    "trapezoid",
    [ctypes.c_double, ctypes.c_double, ctypes.c_int],
    ctypes.c_double,
)
if _c_trap:
    trap_bench.register_c(lambda n: _c_trap(a, b_lim, n))

# Rust trapezoid
_rust_trap = load_lib_function(
    PKG_RUST,
    lib_filename("libtrapezoid_rs", "rust"),
    "trapezoid_rs",
    [ctypes.c_double, ctypes.c_double, ctypes.c_int],
    ctypes.c_double,
)
if _rust_trap:
    trap_bench.register_rust(lambda n: _rust_trap(a, b_lim, n))

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    suite = BenchmarkSuite()
    benchmarks = [sieve_bench, trap_bench]

    for bench in benchmarks:
        suite.add_benchmark(bench.benchmark)

    suite.run_all(
        {bench.name: bench.inputs for bench in benchmarks},
        {bench.name: bench.arg_func for bench in benchmarks},
        warmups=4,
        repeats=50,
        min_time=2.0,
    )
    suite.final_report(FMT_CFG)
