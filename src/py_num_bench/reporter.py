class BenchmarkReporter:
    def __init__(self, config):
        self.config = config

    def df_to_report_struct(self, df, bench_name):
        """Format a benchmark results DataFrame into (headers, rows) for this reporter."""
        if df.empty:
            if bench_name.lower().startswith("prime sieve"):
                headers = ["N (max)", "Prime Count"]
            elif "trapezoidal" in bench_name.lower():
                headers = ["N (subints)", "Integral"]
            else:
                headers = ["Input Size"]
            return headers, []
        if bench_name.lower().startswith("prime sieve"):
            df["N (max)"] = df["input_n"]
            id_col = "N (max)"
            base_cols = ["N (max)"]
            pm = (
                df[["input_n", "prime_count"]]
                .dropna()
                .drop_duplicates()
                .set_index("input_n")["prime_count"]
            )
        elif "trapezoidal" in bench_name.lower():
            df["N (subints)"] = df["input_n"]
            id_col = "N (subints)"
            base_cols = ["N (subints)"]
            im = (
                df[["input_n", "integral"]]
                .dropna()
                .drop_duplicates()
                .set_index("input_n")["integral"]
            )
        else:
            df["Input Size"] = df["input_n"]
            id_col = "Input Size"
            base_cols = ["Input Size"]
        piv = df.pivot_table(
            index=base_cols, columns="lang", values="time_s", aggfunc="min"
        ).reset_index()
        if bench_name.lower().startswith("prime sieve"):
            piv["Prime Count"] = piv[id_col].map(pm.to_dict())
            col_order = [id_col, "Prime Count"]
        elif "trapezoidal" in bench_name.lower():
            piv["Integral"] = piv[id_col].map(im.to_dict())
            col_order = [id_col, "Integral"]
        else:
            col_order = [id_col]
        time_cols = [c for c in piv.columns if c not in col_order]
        rename = {c: f"{c} Time (s)" for c in time_cols}
        piv = piv[col_order + time_cols].rename(columns=rename)
        headers = piv.columns.tolist()
        rows = piv.to_dict(orient="records")
        return headers, rows

    def render(self, algo_name, report_struct):
        """Render a single algorithm's results as a human-readable table."""
        headers, rows = report_struct
        output = [f"\n==== {algo_name} ===="]
        output.append("\t".join(headers))
        for r in rows:
            output.append("\t".join(str(r[h]) for h in headers))
        return "\n".join(output)
