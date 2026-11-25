"""Reproduce the course's SQLite fallback with two connections to one file."""

import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

INC = "UPDATE machine SET parts_produced = parts_produced + 1 WHERE machine_id = 1"


def main():
    with TemporaryDirectory(prefix="module06b-lock-") as directory:
        path = Path(directory) / "machine.db"
        with (
            closing(sqlite3.connect(path, timeout=0)) as first,
            closing(sqlite3.connect(path, timeout=0)) as second,
        ):
            first.executescript("""
                CREATE TABLE machine(
                    machine_id INTEGER PRIMARY KEY,
                    site TEXT NOT NULL,
                    parts_produced INTEGER NOT NULL DEFAULT 0
                );
                INSERT INTO machine VALUES (1, 'guetersloh', 0);
            """)
            first.execute("BEGIN IMMEDIATE")
            first.execute(INC)
            print("A incremented machine 1 and held the write transaction open")
            try:
                second.execute(INC)
            except sqlite3.OperationalError as error:
                if error.sqlite_errorcode != sqlite3.SQLITE_BUSY:
                    raise
                print(f"B's write with timeout=0: {error}")
                second.rollback()
            else:
                raise RuntimeError("Expected SQLite to reject the competing writer")

            first.commit()
            with second:
                second.execute(INC)
            value = second.execute(
                "SELECT parts_produced FROM machine WHERE machine_id = 1"
            ).fetchone()[0]
            if value != 2:
                raise RuntimeError(f"Expected both increments after retry, got {value}")
            print(f"After A committed and B retried: parts_produced = {value}")


if __name__ == "__main__":
    main()
