import argparse
import ctypes
import tomllib
from pathlib import Path

import logfire

import py_num_bench.implementations.python as py_impl_root
from py_num_bench.algo_implementation_loader import AlgoImplementationLoader
from py_num_bench.benchmark import AlgoBenchmark, BenchmarkSuite
from py_num_bench.reporter import BenchmarkReporter
from py_num_bench.track_store import (
    duckdb_connect,
    make_run_id,
    normalize_results_to_df,
    query_results_duckdb,
    save_results_duckdb,
)

CONFIG_PATH = Path(__file__).parents[2] / "conf" / "config.toml"
DB_PATH = str(Path(__file__).parents[2] / "data" / "benchmark_results.duckdb")

with open(CONFIG_PATH, "rb") as f:
    CONFIG = tomllib.load(f)

FMT_CFG = CONFIG["format"]
SIEVE_CFG = CONFIG["sieve"]
TRAP_CFG = CONFIG["trapezoid"]

# Set up implementation package naming
base_pkg = py_impl_root.__package__  # e.g. "py_num_bench.implementations.python"
PKG_IMPL = base_pkg.rpartition(".")[0]  # "py_num_bench.implementations"
LANG_PKG = {
    lang: f"{PKG_IMPL}.{subpkg}" for lang, subpkg in CONFIG["languages"].items()
}

ALGO_SIGS = {
    "sieve": ([ctypes.c_int, ctypes.POINTER(ctypes.c_int)], ctypes.c_int),
    "trapezoid": ([ctypes.c_double, ctypes.c_double, ctypes.c_int], ctypes.c_double),
}


def build_and_run(args):
    from py_num_bench.algo_implementation_loader import AlgoImplementationLoader

    loader = AlgoImplementationLoader(LANG_PKG, ALGO_SIGS, TRAP_CFG)
    enabled_langs = list(LANG_PKG.keys())

    # Explicitly track AlgoBenchmark objects so you can access their results and report method later
    algo_benchmarks = [
        AlgoBenchmark(
            "Prime Sieve",
            "sieve",
            SIEVE_CFG["inputs"],
            lambda n: (n,),
            SIEVE_CFG.get("tolerance", 1e-9),
            loader,
        ),
        AlgoBenchmark(
            "Trapezoidal Integration",
            "trapezoid",
            TRAP_CFG["inputs"],
            lambda n: (n,),
            TRAP_CFG.get("tolerance", 1e-8),
            loader,
        ),
    ]

    suite = BenchmarkSuite()
    for bench in algo_benchmarks:
        bench.register_languages(enabled_langs)
        suite.add_benchmark(bench.benchmark)
        print(
            f"Implementations for {bench.name}: {', '.join(getattr(bench, 'implementations', {}).keys())}"
        )

    suite.run_all(
        {b.name: b.inputs for b in algo_benchmarks},
        {b.name: b.arg_func for b in algo_benchmarks},
        warmups=4,
        repeats=50,
        min_time=2.0,
    )

    run_id = args.run_id or make_run_id("bench")
    con = duckdb_connect(DB_PATH)
    reporter = BenchmarkReporter(FMT_CFG)

    logfire.configure()
    with logfire.span("Benchmark run py-num-bench"):
        logfire.info(
            "Benchmark configuration",
            run_id=run_id,
            enabled_langs=enabled_langs,
            format=FMT_CFG,
            sieve=SIEVE_CFG,
            trapezoid=TRAP_CFG,
            languages=LANG_PKG,
        )
        for bench in algo_benchmarks:
            # Use bench.report (preferred for encapsulation) or reporter.df_to_report_struct(bench.results, bench.name)
            headers, rows = bench.report(FMT_CFG)
            df = normalize_results_to_df(
                bench.name,
                headers,
                rows,
                run_id,
                {
                    "format": FMT_CFG,
                    "sieve": SIEVE_CFG,
                    "trapezoid": TRAP_CFG,
                    "languages": LANG_PKG,
                },
            )
            if not df.empty:
                save_results_duckdb(con, df)
            logfire.info(f"Benchmark Table: {bench.name}", headers=headers, rows=rows)
        logfire.info("DuckDB file saved", path=DB_PATH)
    print(f"Saved results to: {DB_PATH}")
    return run_id


def report_from_duckdb(run_id=None, algorithms=None):
    con = duckdb_connect(DB_PATH)
    reporter = BenchmarkReporter(FMT_CFG)
    if not run_id:
        runs = con.execute(
            "SELECT DISTINCT run_id FROM bench ORDER BY run_id DESC"
        ).fetchall()
        if not runs:
            print("No saved results found.")
            return
        run_id = runs[0]

    if algorithms:
        algos = algorithms
    else:
        # Unpack tuple to string directly, so algos is always a list of str
        algos = [
            row
            for row in con.execute(
                "SELECT DISTINCT algorithm FROM bench WHERE run_id = $run_id",
                {"run_id": run_id},
            ).fetchall()
        ]

    for algo in algos:
        df = query_results_duckdb(con, run_id=run_id, algorithm=algo)
        headers, rows = reporter.df_to_report_struct(df, algo)
        print(reporter.render(algo, (headers, rows)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["run", "report"], default="run")
    parser.add_argument(
        "--run-id", default=None, help="Use specific run id for reporting"
    )
    parser.add_argument(
        "--algorithms", nargs="*", default=None, help="Algorithms to include"
    )
    args = parser.parse_args()
    if args.mode == "run":
        run_id = build_and_run(args)
        report_from_duckdb(run_id, args.algorithms)
    else:
        report_from_duckdb(args.run_id, args.algorithms)


if __name__ == "__main__":
    main()
