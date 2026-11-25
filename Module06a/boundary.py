"""Compare 1,000 per-row writes and lookups in memory, then try executemany."""

import sqlite3
from contextlib import closing
from time import perf_counter

import duckdb

N = 1000
ROWS = [(i, f"k{i}", i * 1.5) for i in range(N)]
INSERT = "INSERT INTO sample VALUES (?, ?, ?)"


def run(connection, engine, value_type, batch):
    connection.execute(f"CREATE TABLE sample(id INTEGER PRIMARY KEY, k TEXT, v {value_type})")

    start = perf_counter()
    connection.execute("BEGIN")
    if batch:
        connection.executemany(INSERT, ROWS)
    else:
        for row in ROWS:
            connection.execute(INSERT, row)
    connection.commit()
    insert_ms = (perf_counter() - start) * 1000

    start = perf_counter()
    for key, _, value in ROWS:
        result = connection.execute("SELECT v FROM sample WHERE id = ?", (key,)).fetchone()
        if result != (value,):
            raise RuntimeError(f"Unexpected result for {key}: {result}")
    lookup_ms = (perf_counter() - start) * 1000
    method = "executemany" if batch else "execute loop"
    print(f"{engine} {method}: inserts {insert_ms:.2f} ms, lookups {lookup_ms:.2f} ms")


def main():
    # Warm up Python parameter binding outside the measured workload.
    with duckdb.connect() as warmup:
        warmup.execute("SELECT ?", (0,)).fetchone()
    for batch in (False, True):
        with closing(sqlite3.connect(":memory:")) as sqlite, duckdb.connect() as duck:
            run(sqlite, "SQLite", "REAL", batch)
            run(duck, "DuckDB", "DOUBLE", batch)


if __name__ == "__main__":
    main()
