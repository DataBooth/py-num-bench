import ctypes
import importlib
import importlib.resources as pkg_resources
import sys


class AlgoImplementationLoader:
    """
    Loads algorithm implementations from Python, Cython, C, C++, and Rust backends.
    Applies normalisation wrappers so all callables are (n,) for the benchmark runner.
    """

    def __init__(self, lang_pkg_map, algo_sigs, trap_cfg):
        self.lang_pkg_map = lang_pkg_map
        self.algo_sigs = algo_sigs
        self.trap_cfg = trap_cfg

    @staticmethod
    def lib_filename(base: str, lang: str) -> str:
        if lang in ("c", "cpp"):
            return f"{base}.so"
        if lang == "rust":
            if sys.platform.startswith("darwin"):
                return f"{base}.dylib"
            elif sys.platform.startswith("win32"):
                return f"{base}.dll"
            return f"{base}.so"
        return f"{base}.so"

    @staticmethod
    def load_lib_function(
        pkg: str, lib_file: str, func_name: str, argtypes, restype=None
    ):
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

    def wrap_algorithm(self, algo: str, lang: str, func):
        if not func:
            return None

        if algo == "sieve":
            if lang in ("c", "cpp", "rust"):

                def sieve_wrapper(n):
                    arr = (ctypes.c_int * (n + 1))()
                    count = func(n, arr)
                    return [arr[i] for i in range(count)]

                return sieve_wrapper
            return func

        if algo == "trapezoid":
            a, b = self.trap_cfg.get("a", 0.0), self.trap_cfg.get("b", 1.0)
            return lambda n: func(a, b, n)

        return func

    def load(self, algorithm: str, lang: str):
        argtypes, restype = self.algo_sigs[algorithm]
        pkg_base = self.lang_pkg_map[lang]

        if lang == "python":
            mod = importlib.import_module(f"{pkg_base}.{algorithm}")
            func = getattr(mod, f"{algorithm}_py", getattr(mod, algorithm, None))
            return self.wrap_algorithm(algorithm, lang, func)

        if lang == "cython":
            try:
                mod = importlib.import_module(f"{pkg_base}.{algorithm}_cython")
                func = getattr(mod, f"{algorithm}_cython")
                return self.wrap_algorithm(algorithm, lang, func)
            except (ImportError, AttributeError):
                return None

        if lang in ("c", "cpp"):
            base_name = f"lib{algorithm}" + (f"_{lang}" if lang != "c" else "")
            lib_file = self.lib_filename(base_name, lang)
            func_name = (
                f"{algorithm}_{lang}"
                if lang != "c"
                else (f"{algorithm}_c" if algorithm == "sieve" else algorithm)
            )
            raw_func = self.load_lib_function(
                pkg_base, lib_file, func_name, argtypes, restype
            )
            return self.wrap_algorithm(algorithm, lang, raw_func)

        if lang == "rust":
            base_name = f"lib{algorithm}_rs"
            lib_file = self.lib_filename(base_name, lang)
            func_name = f"{algorithm}_rs"
            raw_func = self.load_lib_function(
                pkg_base, lib_file, func_name, argtypes, restype
            )
            return self.wrap_algorithm(algorithm, lang, raw_func)

        return None
