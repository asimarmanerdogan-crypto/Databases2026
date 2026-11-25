"""Show both engines' plans for the same unfiltered aggregate."""

import sqlite3
from contextlib import closing

import duckdb

from prepare import HISTORY
from to_parquet import PARQUET, parquet_source

SQL = """
SELECT machine_id, site, technician, SUM(part_price) AS cost
FROM {}
GROUP BY machine_id, site, technician
"""


def main():
    with closing(sqlite3.connect(HISTORY)) as sqlite, duckdb.connect() as duck:
        for row in sqlite.execute("EXPLAIN QUERY PLAN " + SQL.format("report_history")):
            print(row[-1])
        for _, plan in duck.execute("EXPLAIN ANALYZE " + SQL.format(parquet_source(PARQUET))).fetchall():
            print(plan)


if __name__ == "__main__":
    main()
