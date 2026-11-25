"""Compare equivalent SQLite and DuckDB aggregates with five interleaved runs."""

import math
import sqlite3
from contextlib import closing
from statistics import median
from time import perf_counter

import duckdb

from prepare import HISTORY
from to_parquet import PARQUET, parquet_source

RUNS = 5
DASHBOARD = """
SELECT machine_id, site, technician, SUM(part_price) AS cost
FROM {source}
WHERE done_on >= '2026-01-01'
GROUP BY machine_id, site, technician
ORDER BY machine_id, site, technician
"""
MONTHLY = """
SELECT {month} AS month, machine_id, COUNT(*) AS jobs, SUM(part_price) AS cost
FROM {source}
GROUP BY month, machine_id
ORDER BY month, machine_id
"""


def elapsed_ms(query):
    start = perf_counter()
    query()
    return (perf_counter() - start) * 1000


def same_groups(left, right):
    return len(left) == len(right) and all(
        a[:-1] == b[:-1] and math.isclose(a[-1], b[-1], rel_tol=0, abs_tol=0.005)
        for a, b in zip(left, right)
    )


def main():
    source = parquet_source(PARQUET)
    with closing(sqlite3.connect(HISTORY)) as sqlite, duckdb.connect() as duck:
        print(f"SQLite {sqlite3.sqlite_version}, DuckDB {duckdb.__version__}")
        for label, template in (("dashboard", DASHBOARD), ("monthly", MONTHLY)):
            sqlite_sql = template.format(source="report_history", month="strftime('%Y-%m', done_on)")
            duck_sql = template.format(source=source, month="strftime(done_on, '%Y-%m')")

            def sqlite_query():
                return sqlite.execute(sqlite_sql).fetchall()

            def duck_query():
                return duck.execute(duck_sql).fetchall()

            first, second = sqlite_query(), duck_query()
            if not same_groups(first, second):
                raise RuntimeError(f"{label} result mismatch")

            samples = [[], []]
            queries = (sqlite_query, duck_query)
            for run in range(RUNS):
                for engine in (run % 2, 1 - run % 2):
                    samples[engine].append(elapsed_ms(queries[engine]))

            print(f"{label}: {len(first):,} matching groups, "
                  f"{median(samples[0]) / median(samples[1]):.2f}x")
            for engine, times in zip(("SQLite", "DuckDB"), samples):
                print(f"  {engine}: {median(times):.2f} ms "
                      f"[{min(times):.2f} to {max(times):.2f}] "
                      f"samples={[round(ms, 2) for ms in times]}")


if __name__ == "__main__":
    main()
