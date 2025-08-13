import ctypes
import importlib
import importlib.resources as pkg_resources
import sys
import tomllib
from pathlib import Path

from py_num_bench.core import Benchmark, BenchmarkSuite
import py_num_bench.implementations.python as py_impl_root

# ---------------------------
# Config
# ---------------------------
CONFIG_PATH = Path(__file__).parents[2] / "conf" / "config.toml"
with open(CONFIG_PATH, "rb") as f:
    CONFIG = tomllib.load(f)

FMT_CFG = CONFIG["format"]
SIEVE_CFG = CONFIG["sieve"]
TRAP_CFG = CONFIG["trapezoid"]

# ---------------------------
# Dynamic package root detection
# ---------------------------
PKG_ROOT = py_impl_root.__package__.rsplit(".implementations.python", 1)[0]
# e.g. "py_num_bench"
PKG_IMPL = f"{PKG_ROOT}.implementations"  # base for other languages

# Load language packages from config.toml
# Example in config.toml:
# [languages]
# python = "python"
# cython = "cython"
# c      = "c"
# cpp    = "cpp"
# rust   = "rust"
LANG_PKG = {
    lang: f"{PKG_IMPL}.{subpkg}" for lang, subpkg in CONFIG["languages"].items()
}

# ---------------------------
# Algorithm signatures
# ---------------------------
ALGO_SIGS = {
    "sieve": ([ctypes.c_int, ctypes.POINTER(ctypes.c_int)], ctypes.c_int),
    "trapezoid": ([ctypes.c_double, ctypes.c_double, ctypes.c_int], ctypes.c_double),
}


# ---------------------------
# Helpers
# ---------------------------
def lib_filename(base: str, lang: str) -> str:
    if lang in ("c", "cpp"):  # both built as .so in GCC/Clang for your project
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


def wrap_algorithm(algo: str, lang: str, func):
    """
    Normalise raw impl to a benchmark-friendly (n,) signature.
    """
    if not func:
        return None

    if algo == "sieve":
        if lang in ("c", "cpp", "rust"):

            def sieve_wrapper(n):
                arr = (ctypes.c_int * (n + 1))()
                count = func(n, arr)
                return [arr[i] for i in range(count)]

            return sieve_wrapper
        # python / cython already take (n,)
        return func

    if algo == "trapezoid":
        a, b_lim = TRAP_CFG.get("a", 0.0), TRAP_CFG.get("b", 1.0)
        return lambda n: func(a, b_lim, n)

    return func


def load_impl(algorithm: str, lang: str):
    argtypes, restype = ALGO_SIGS[algorithm]
    pkg_base = LANG_PKG[lang]

    # Python
    if lang == "python":
        mod = importlib.import_module(f"{pkg_base}.{algorithm}")
        func = getattr(mod, f"{algorithm}_py", getattr(mod, algorithm, None))
        return wrap_algorithm(algorithm, lang, func)

    # Cython
    if lang == "cython":
        try:
            mod = importlib.import_module(f"{pkg_base}.{algorithm}_cython")
            func = getattr(mod, f"{algorithm}_cython")
            return wrap_algorithm(algorithm, lang, func)
        except (ImportError, AttributeError):
            return None

    # C / C++
    if lang in ("c", "cpp"):
        base_name = f"lib{algorithm}" + (f"_{lang}" if lang != "c" else "")
        lib_file = lib_filename(base_name, lang)

        # C sieve usually has `sieve_c`, others match algorithm name
        func_name = (
            f"{algorithm}_{lang}"
            if lang != "c"
            else (f"{algorithm}_c" if algorithm == "sieve" else algorithm)
        )
        raw_func = load_lib_function(pkg_base, lib_file, func_name, argtypes, restype)
        return wrap_algorithm(algorithm, lang, raw_func)

    # Rust
    if lang == "rust":
        base_name = f"lib{algorithm}_rs"
        lib_file = lib_filename(base_name, lang)
        func_name = f"{algorithm}_rs"
        raw_func = load_lib_function(pkg_base, lib_file, func_name, argtypes, restype)
        return wrap_algorithm(algorithm, lang, raw_func)

    return None


# ---------------------------
# Algorithm Benchmark class
# ---------------------------
class AlgorithmBenchmark:
    def __init__(self, name, algo_key, inputs, arg_func, tolerance):
        self.name = name
        self.algo_key = algo_key
        self.inputs = inputs
        self.arg_func = arg_func
        self.benchmark = Benchmark(name, tolerance=tolerance)

    def register_all_langs(self, langs):
        for lang in langs:
            impl = load_impl(self.algo_key, lang)
            if impl:
                self.benchmark.register(lang.capitalize(), impl)


# ---------------------------
# Create Benchmarks from config langs
# ---------------------------
enabled_langs = list(LANG_PKG.keys())  # From config (and packages exist)

# Prime Sieve
sieve_bench = AlgorithmBenchmark(
    "Prime Sieve",
    algo_key="sieve",
    inputs=SIEVE_CFG["inputs"],
    arg_func=lambda n: (n,),
    tolerance=SIEVE_CFG.get("tolerance", 1e-9),
)
sieve_bench.register_all_langs(enabled_langs)

# Trapezoid
trap_bench = AlgorithmBenchmark(
    "Trapezoidal Integration",
    algo_key="trapezoid",
    inputs=TRAP_CFG["inputs"],
    arg_func=lambda n: (n,),
    tolerance=TRAP_CFG.get("tolerance", 1e-8),
)
trap_bench.register_all_langs(enabled_langs)

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
