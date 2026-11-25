"""Build the SQLite history and export the original Module 5 rows as UTF-8 CSV."""

import csv
import sqlite3
from contextlib import closing
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE05 = HERE.parent / "Module05"
OUTPUT = HERE / "output"
HISTORY = OUTPUT / "history.db"
CSV = OUTPUT / "report_jobpart.csv"
COLUMNS = "job_id, machine_id, site, technician, part_no, part_price, done_on"
QUARTERS = 10
BASE_ROWS = 200_000


def main():
    OUTPUT.mkdir(exist_ok=True)
    with closing(sqlite3.connect(":memory:")) as source:
        for name in ("setup.sql", "report.sql"):
            source.executescript((MODULE05 / name).read_text(encoding="utf-8"))
        count = source.execute("SELECT COUNT(*) FROM report_jobpart").fetchone()[0]
        if count != BASE_ROWS:
            raise RuntimeError(f"Expected {BASE_ROWS:,} Module 5 rows, got {count:,}")

        with CSV.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(COLUMNS.split(", "))
            writer.writerows(source.execute(f"SELECT {COLUMNS} FROM report_jobpart"))

        source.execute("ATTACH DATABASE ? AS output", (str(HISTORY),))
        with source:
            source.execute("BEGIN")
            source.execute("DROP TABLE IF EXISTS output.report_history")
            source.execute(
                """CREATE TABLE output.report_history AS
                   WITH RECURSIVE quarters(k) AS (
                       SELECT 0 UNION ALL SELECT k + 1 FROM quarters WHERE k + 1 < ?
                   )
                   SELECT job_id + k * 1000000 AS job_id,
                          machine_id, site, technician, part_no, part_price,
                          date(done_on, '+' || (k * 91) || ' days') AS done_on
                   FROM quarters CROSS JOIN report_jobpart""",
                (QUARTERS,),
            )
            rows, start, end = source.execute(
                "SELECT COUNT(*), MIN(done_on), MAX(done_on) FROM output.report_history"
            ).fetchone()
            if rows != count * QUARTERS:
                raise RuntimeError(f"Unexpected history row count: {rows:,}")

    print(f"SQLite: {rows:,} rows, {start} to {end}, {HISTORY.stat().st_size:,} bytes")
    print(f"CSV: {count:,} base rows, {CSV.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
