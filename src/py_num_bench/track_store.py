import json
import os
import platform
import sys
from datetime import datetime
from typing import Dict, List

import duckdb
import pandas as pd


def make_run_id(prefix: str = "bench") -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}"


def normalize_results_to_df(
    bench_name: str,
    headers: List[str],
    rows: List[Dict],
    run_id: str,
    config: Dict,
) -> pd.DataFrame:
    """
    Convert a benchmark's (headers, rows) into a normalized long-form DataFrame.
    Expects rows as list-of-dicts with timing columns named like '{Lang} Time (s)'.
    """
    records = []
    langs = [h.replace(" Time (s)", "") for h in headers if h.endswith(" Time (s)")]
    # Identify input/metric columns (first 1-2 columns depending on algorithm)
    id_cols = [h for h in headers if not h.endswith(" Time (s)")]
    for row in rows:
        base = {k: row.get(k) for k in id_cols}
        for lang in langs:
            t = row.get(f"{lang} Time (s)")
            rec = {
                "run_id": run_id,
                "algorithm": bench_name,
                "lang": lang,
                "time_s": float(t) if t is not None else float("nan"),
                "config_json": json.dumps(config, default=str),
                "platform": platform.platform(),
                "python_version": sys.version.split()[0],
            }
            # Attach identification columns, rename to stable names
            if "N (max)" in base:
                rec["input_n"] = base["N (max)"]
                rec["prime_count"] = row.get("Prime Count")
            elif "N (subints)" in base:
                rec["input_n"] = base["N (subints)"]
                rec["integral"] = row.get("Integral")
            elif "Input Size" in base:
                rec["input_n"] = base["Input Size"]
            else:
                rec["input_n"] = None
            records.append(rec)
    return pd.DataFrame.from_records(records)


def duckdb_connect(db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return duckdb.connect(db_path)


def save_results_duckdb(
    con,
    df: pd.DataFrame,
    table: str = "bench",
):
    # Create-or-append pattern
    con.execute(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM df WHERE 0=1")
    con.register("df", df)
    con.execute(f"INSERT INTO {table} SELECT * FROM df")
    con.unregister("df")


def query_results_duckdb(
    con,
    run_id: str = None,
    algorithm: str = None,
    table: str = "bench",
) -> pd.DataFrame:
    clauses = []
    if run_id:
        clauses.append("run_id = $run_id")
    if algorithm:
        clauses.append("algorithm = $algorithm")
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    q = f"SELECT * FROM {table} {where}"
    return con.execute(q, {"run_id": run_id, "algorithm": algorithm}).fetchdf()


class DummyRun:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def log_parameters(self, params):
        pass

    def log_metadata(self, payload):
        pass

    def log_metrics(self, metrics):
        pass

    def log_table(self, name, table):
        pass

    def log_artifact(self, name, path):
        pass
