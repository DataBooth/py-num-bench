"""
core.py

Benchmarking framework for cross-language numerical algorithms.
Includes:
- Benchmark: runs all implementations of an algorithm, records timings, checks results.
- BenchmarkSuite: manages and runs multiple Benchmark instances.
"""

import time
import plotly.graph_objects as go


class Benchmark:
    """
    Represents a single algorithm benchmark across multiple implementations.
    """

    def __init__(self, name: str, tolerance: float = 1e-9):
        self.name = name
        self.implementations = {}  # {lang_name: callable}
        self.results = []  # [(input_size, {lang: time})]
        self.outputs = []  # [(input_size, {lang: output})]
        self.tolerance = tolerance

    def register(self, lang: str, func):
        """Register a callable implementation for a given language."""
        self.implementations[lang] = func

    def run(self, inputs, args_func):
        """
        Run all registered implementations for each input, compare to Python output.
        """
        if "Python" not in self.implementations:
            raise RuntimeError("Python reference implementation required.")

        for inp in inputs:
            times, outs = {}, {}
            # Reference Python implementation
            args = args_func(inp)
            start = time.perf_counter()
            ref_out = self.implementations["Python"](*args)
            times["Python"] = time.perf_counter() - start
            outs["Python"] = ref_out

            # Other implementations
            for lang, func in self.implementations.items():
                if lang == "Python":
                    continue
                args = args_func(inp)
                start = time.perf_counter()
                out = func(*args)
                times[lang] = time.perf_counter() - start
                outs[lang] = out
                # Correctness check
                if hasattr(ref_out, "__iter__"):
                    if list(out) != list(ref_out):
                        print(f"[WARN] {lang} output differs for input {inp}")
                else:
                    if abs(out - ref_out) > self.tolerance:
                        print(
                            f"[WARN] {lang} output differs at input {inp}: {out} != {ref_out}"
                        )

            self.results.append((inp, times))
            self.outputs.append((inp, outs))

    def report(self):
        """Pretty print benchmark results and sample outputs."""
        from tabulate import tabulate

        langs = sorted(self.implementations.keys())
        print(f"\nBenchmark: {self.name}")
        headers = ["Input Size"] + langs
        table = []
        for inp, times in self.results:
            table.append(
                [inp] + [f"{times.get(lang, float('nan')):.6f}" for lang in langs]
            )
        print(tabulate(table, headers=headers, tablefmt="github"))

        print("\nSample Outputs:")
        for inp, outs in self.outputs:
            if inp <= 20:
                print(f"n={inp}:")
                for lang, out in outs.items():
                    print(f"  {lang}: {str(out)[:80]}")

    def plot(self):
        """Interactive Plotly plot of runtimes."""
        fig = go.Figure()
        langs = sorted(self.implementations.keys())
        for lang in langs:
            xs = [inp for inp, _ in self.results]
            ys = [times.get(lang) for _, times in self.results]
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", name=lang))
        fig.update_layout(
            title=f"Benchmark: {self.name}",
            xaxis_title="Input Size",
            yaxis_title="Execution Time (seconds)",
            template="plotly_white",
        )
        fig.show()


class BenchmarkSuite:
    """Manages multiple Benchmark instances."""

    def __init__(self):
        self.benchmarks = {}

    def add_benchmark(self, benchmark: Benchmark):
        self.benchmarks[benchmark.name] = benchmark

    def run_all(self, inputs, args_funcs):
        for name, bench in self.benchmarks.items():
            bench.run(inputs[name], args_funcs[name])

    def report_all(self):
        for bench in self.benchmarks.values():
            bench.report()

    def plot_all(self):
        for bench in self.benchmarks.values():
            bench.plot()
