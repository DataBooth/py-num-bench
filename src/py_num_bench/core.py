import time
import statistics
from tabulate import tabulate


def simple_benchmark(func, warmups=1, repeats=5, min_time=None):
    """Run func() multiple times and return timing stats as dict."""
    # Warmup
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
    def __init__(self, name: str, tolerance: float = 1e-9):
        self.name = name
        self.implementations = {}
        self.results = []
        self.outputs = []
        self.tolerance = tolerance

    def register(self, lang: str, func):
        self.implementations[lang] = func

    def run(self, inputs, args_func, warmups=1, repeats=5, min_time=None):
        if "Python" not in self.implementations:
            raise RuntimeError("Python reference implementation required.")

        for inp in inputs:
            times, outs = {}, {}
            args = args_func(inp)

            # Python baseline
            try:
                stats = simple_benchmark(
                    lambda: self.implementations["Python"](*args),
                    warmups=warmups,
                    repeats=repeats,
                    min_time=min_time,
                )
                py_time = stats["median"]
                py_output = self.implementations["Python"](*args)
            except Exception as e:
                print(f"[ERROR] Python impl failed on input {inp}: {e}")
                continue

            times["Python"] = py_time
            outs["Python"] = py_output

            # Other implementations
            for lang, func in self.implementations.items():
                if lang == "Python":
                    continue
                try:
                    stats = simple_benchmark(
                        lambda: func(*args),
                        warmups=warmups,
                        repeats=repeats,
                        min_time=min_time,
                    )
                    elapsed = stats["median"]
                    output = func(*args)
                    times[lang] = elapsed
                    outs[lang] = output

                    # Correctness check
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
        fmt_cfg = fmt_cfg or {}
        time_sigfigs = fmt_cfg.get("time_sigfigs", 3)
        integral_decimals = fmt_cfg.get("integral_decimals", 4)
        show_thousands_sep = fmt_cfg.get("show_thousands_sep", True)

        langs = sorted(self.implementations.keys())
        if self.name.lower().startswith("prime sieve"):
            headers = ["N (max)", "Prime Count"]
        elif "trapezoidal" in self.name.lower():
            headers = ["N (subints)", "Integral"]
        else:
            headers = ["Input Size"]
        headers.extend([f"{lang} Time (s)" for lang in langs])

        table = []
        for inp, times in self.results:
            inp_fmt = f"{inp:,}" if show_thousands_sep else str(inp)
            py_out = next(o["Python"] for x, o in self.outputs if x == inp)

            if self.name.lower().startswith("prime sieve"):
                prime_count = (
                    f"{len(py_out):,}" if show_thousands_sep else str(len(py_out))
                )
                row = [inp_fmt, prime_count]
            elif "trapezoidal" in self.name.lower():
                row = [inp_fmt, f"{py_out:.{integral_decimals}f}"]
            else:
                row = [inp_fmt]

            row.extend(
                [f"{times.get(lang, float('nan')):.{time_sigfigs}g}" for lang in langs]
            )
            table.append(row)

        print(f"\nBenchmark: {self.name}")
        print(tabulate(table, headers=headers, tablefmt="github"))

        print("\nSample Outputs:")
        for inp, outs in self.outputs:
            if inp <= 20:
                print(f"n={inp}:")
                for lang, out in outs.items():
                    print(f"  {lang}: {str(out)[:80]}")


class BenchmarkSuite:
    def __init__(self):
        self.benchmarks = {}

    def add_benchmark(self, bench: Benchmark):
        self.benchmarks[bench.name] = bench

    def run_all(self, inputs, arg_funcs, warmups=1, repeats=5, min_time=None):
        for name, bench in self.benchmarks.items():
            print(f"\n=== Running {name} ===")
            bench.run(
                inputs[name],
                arg_funcs[name],
                warmups=warmups,
                repeats=repeats,
                min_time=min_time,
            )

    def final_report(self, fmt_cfg):
        for bench in self.benchmarks.values():
            bench.report(fmt_cfg)
