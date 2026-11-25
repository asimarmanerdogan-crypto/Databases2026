"""Expand the Module 5 CSV into Parquet and verify both compression variants."""

import sqlite3
from contextlib import closing
from pathlib import Path

import duckdb

from prepare import CSV, HISTORY, OUTPUT, QUARTERS

PARQUET = OUTPUT / "report_history.parquet"
ZSTD = OUTPUT / "report_zstd.parquet"
CHECK = "SELECT COUNT(*), ROUND(SUM(part_price), 2) FROM {}"


def literal(path: Path):
    return "'" + path.as_posix().replace("'", "''") + "'"


def parquet_source(path: Path):
    return f"read_parquet({literal(path)})"


def main():
    with closing(sqlite3.connect(HISTORY)) as sqlite, duckdb.connect() as duck:
        expected = sqlite.execute(CHECK.format("report_history")).fetchone()
        source = literal(CSV)
        duck.execute(
            f"""COPY (
                SELECT job_id + k * 1000000 AS job_id, machine_id, site, technician,
                       part_no, part_price,
                       done_on + CAST(k * 91 AS INTEGER) AS done_on
                FROM read_csv({source}, header = true, columns = {{
                    'job_id': 'BIGINT', 'machine_id': 'VARCHAR', 'site': 'VARCHAR',
                    'technician': 'VARCHAR', 'part_no': 'VARCHAR',
                    'part_price': 'DOUBLE', 'done_on': 'DATE'
                }})
                CROSS JOIN range({QUARTERS}) AS quarters(k)
            ) TO {literal(PARQUET)} (FORMAT PARQUET, COMPRESSION SNAPPY)"""
        )
        duck.execute(
            f"COPY (SELECT * FROM {parquet_source(PARQUET)}) "
            f"TO {literal(ZSTD)} (FORMAT PARQUET, COMPRESSION ZSTD)"
        )

        print(f"SQLite check: {expected[0]:,} rows, part-price total {expected[1]:,.2f}")
        for path in (PARQUET, ZSTD):
            actual = duck.execute(CHECK.format(parquet_source(path))).fetchone()
            if actual != expected:
                raise RuntimeError(f"{path.name}: expected {expected}, got {actual}")
            print(f"{path.name}: {actual[0]:,} rows, total {actual[1]:,.2f}, "
                  f"{path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
