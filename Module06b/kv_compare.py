"""Measure 20,000 stored session values and indexed lookups in both stores."""

import shelve
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

ROWS = [(f"session-{i}", f"user-{i % 100}:filter=city:{i % 4}") for i in range(20_000)]


def measure_shelve(path):
    with shelve.open(str(path), flag="n") as sessions:
        start = perf_counter()
        for key, value in ROWS:
            sessions[key] = value
        sessions.sync()
        write_seconds = perf_counter() - start

        start = perf_counter()
        values = [sessions[key] for key, _ in ROWS]
        read_seconds = perf_counter() - start
    return write_seconds, read_seconds, values


def measure_sqlite(path):
    with closing(sqlite3.connect(path)) as db:
        db.execute("CREATE TABLE session(k TEXT PRIMARY KEY NOT NULL, v TEXT NOT NULL)")

        start = perf_counter()
        db.executemany("INSERT INTO session VALUES (?, ?)", ROWS)
        db.commit()
        write_seconds = perf_counter() - start

        start = perf_counter()
        cursor = db.cursor()
        values = [
            cursor.execute("SELECT v FROM session WHERE k = ?", (key,)).fetchone()[0]
            for key, _ in ROWS
        ]
        read_seconds = perf_counter() - start
    return write_seconds, read_seconds, values


def main():
    with TemporaryDirectory(prefix="module06b-kv-") as directory:
        folder = Path(directory)
        expected = [value for _, value in ROWS]
        for engine, measure, filename in (
            ("shelve", measure_shelve, "sessions"),
            ("SQLite", measure_sqlite, "sessions.db"),
        ):
            write, read, values = measure(folder / filename)
            if values != expected:
                raise RuntimeError(f"{engine} returned unexpected values")
            print(f"{engine}: set {write:.4f} s, get {read:.4f} s, {len(values):,} verified")


if __name__ == "__main__":
    main()
