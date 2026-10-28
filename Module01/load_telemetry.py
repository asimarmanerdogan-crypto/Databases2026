"""Load the generated CSV into a local, ignored SQLite database."""
import csv
import sqlite3
from pathlib import Path

here = Path(__file__).parent
with sqlite3.connect(here / "telemetry.db") as conn:
    conn.executescript("""
        DROP TABLE IF EXISTS readings;
        CREATE TABLE readings(
            ts TEXT NOT NULL,
            machine TEXT NOT NULL,
            temp_c REAL NOT NULL,
            vib_rms REAL NOT NULL,
            spindle_load REAL NOT NULL
        );
    """)
    with (here / "telemetry.csv").open(newline="", encoding="utf-8") as f:
        rows = csv.reader(f)
        next(rows)
        conn.executemany("INSERT INTO readings VALUES (?, ?, ?, ?, ?)", rows)
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
    print(f"loaded {n} rows into telemetry.db")
