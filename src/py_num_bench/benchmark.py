import csv
import io
import statistics
import time
from tabulate import tabulate


def simple_benchmark(func, warmups=1, repeats=5, min_time=None):
    """
    Run func() multiple times and return timing stats.
    Warm-up runs excluded from stats.
    """
    # Warm-up
    for _ in range(warmups):
        func()

    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        func()
        elapsed = time.perf_counter() - start
        samples.append(elapsed)
        if min_time and sum(samples) >= min_time:
            break

    return {
        "mean": statistics.mean(samples) if samples else float("nan"),
        "median": statistics.median(samples) if samples else float("nan"),
        "min": min(samples) if samples else float("nan"),
        "max": max(samples) if samples else float("nan"),
        "stdev": statistics.stdev(samples) if len(samples) > 1 else 0.0,
        "samples": samples,
    }


class Benchmark:
    """Manages timing and validating multiple implementations of an algorithm."""

    def __init__(self, name: str, tolerance: float = 1e-9):
        self.name = name
        self.implementations = {}
        self.results = []
        self.outputs = []
        self.tolerance = tolerance

    def register(self, lang: str, func):
        """Register a callable implementation under the language label."""
        self.implementations[lang] = func

    def run(self, inputs, args_func, warmups=1, repeats=5, min_time=None):
        """Run benchmark for all implementations over inputs."""
        # print(f"Implementations: {', '.join(self.implementations.keys())}")
        if "Python" not in self.implementations:
            raise RuntimeError("Python reference implementation required.")

        for inp in inputs:
            times, outs = {}, {}
            args = args_func(inp)

            # Baseline (Python)
            try:
                py_stats = simple_benchmark(
                    lambda: self.implementations["Python"](*args),
                    warmups,
                    repeats,
                    min_time,
                )
                py_time = py_stats["median"]
                py_output = self.implementations["Python"](*args)
            except Exception as e:
                print(f"[ERROR] Python impl failed on input {inp}: {e}")
                continue

            times["Python"] = py_time
            outs["Python"] = py_output

            # Other langs
            for lang, func in self.implementations.items():
                if lang == "Python":
                    continue
                try:
                    stats = simple_benchmark(
                        lambda: func(*args), warmups, repeats, min_time
                    )
                    elapsed = stats["median"]
                    output = func(*args)
                    times[lang] = elapsed
                    outs[lang] = output

                    # Validate against Python
                    if hasattr(py_output, "__iter__") and not isinstance(
                        py_output, (str, bytes)
                    ):
                        if list(output) != list(py_output):
                            print(f"[WARN] {lang} output differs for input {inp}")
                    else:
                        if abs(output - py_output) > self.tolerance:
                            print(
                                f"[WARN] {lang} output differs at input {inp}: {output} != {py_output}"
                            )
                except Exception as e:
                    print(f"[WARN] {lang} failed on input {inp}: {e}")

            self.results.append((inp, times))
            self.outputs.append((inp, outs))

    def report(self, fmt_cfg=None):
        """
        Build headers and a list-of-dicts for Reporter output.
        Returns: (headers, rows)
        """
        fmt_cfg = fmt_cfg or {}
        integral_decimals = fmt_cfg.get("integral_decimals", 4)
        show_sep = fmt_cfg.get("show_thousands_sep", True)

        langs = sorted(self.implementations.keys())

        # Pick headers
        if self.name.lower().startswith("prime sieve"):
            headers = ["N (max)", "Prime Count"]
        elif "trapezoidal" in self.name.lower():
            headers = ["N (subints)", "Integral"]
        else:
            headers = ["Input Size"]
        headers.extend([f"{lang} Time (s)" for lang in langs])

        table_dicts = []  # always list-of-dicts, possibly empty

        for inp, times in self.results:
            inp_fmt = f"{inp:,}" if show_sep else str(inp)
            py_out = next(o["Python"] for x, o in self.outputs if x == inp)
            row_dict = {}

            if self.name.lower().startswith("prime sieve"):
                prime_count = f"{len(py_out):,}" if show_sep else str(len(py_out))
                row_dict[headers[0]] = inp_fmt
                row_dict[headers[1]] = prime_count
            elif "trapezoidal" in self.name.lower():
                row_dict[headers[0]] = inp_fmt
                row_dict[headers[1]] = f"{py_out:.{integral_decimals}f}"
            else:
                row_dict[headers[0]] = inp_fmt

            # timings as raw floats for relative timing
            for lang in langs:
                row_dict[f"{lang} Time (s)"] = float(times.get(lang, float("nan")))

            table_dicts.append(row_dict)

        return headers, table_dicts


class BenchmarkSuite:
    """Holds and runs a group of Benchmark objects."""

    def __init__(self):
        self.benchmarks = {}

    def add_benchmark(self, bench: Benchmark):
        self.benchmarks[bench.name] = bench

    def run_all(self, inputs, arg_funcs, warmups=1, repeats=5, min_time=None):
        for name, bench in self.benchmarks.items():
            print(f"\n=== Running {name} ===")
            bench.run(inputs[name], arg_funcs[name], warmups, repeats, min_time)

    def final_report(self, fmt_cfg, reporter):
        for bench in self.benchmarks.values():
            headers, rows = bench.report(fmt_cfg)
            print(reporter.render(bench.name, (headers, rows)))


class AlgoBenchmark:
    """Wrapper for a single algorithm's benchmark using a loader to register backends."""

    def __init__(self, name, algo_key, inputs, arg_func, tolerance, loader):
        self.name = name
        self.algo_key = algo_key
        self.inputs = inputs
        self.arg_func = arg_func
        self.benchmark = Benchmark(name, tolerance=tolerance)
        self.loader = loader

    def register_languages(self, langs):
        for lang in langs:
            impl = self.loader.load(self.algo_key, lang)
            if impl:
                label = "Rust" if lang == "rust" else lang.capitalize()
                self.benchmark.register(label, impl)
