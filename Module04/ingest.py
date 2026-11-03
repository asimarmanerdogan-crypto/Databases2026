"""Load a readings CSV without duplicating (sensor_id, ts).

Usage: python Module04/ingest.py Module04/readings.csv --db Module04/edge.db
The target database must already contain the Module04 schema and sensors.
"""
import argparse
import csv
import sqlite3
from pathlib import Path

UPSERT = """INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES(?,?,?,?)
ON CONFLICT(sensor_id,ts) DO UPDATE SET value=excluded.value"""

def ingest(db_path, csv_path):
    # mode=rw prevents accidentally creating a database at a mistyped path.
    conn = sqlite3.connect(Path(db_path).resolve().as_uri() + '?mode=rw', uri=True)
    try:
        conn.execute('PRAGMA foreign_keys=ON')
        with Path(csv_path).open(newline='', encoding='utf-8') as f:
            rows = [(int(r['sensor_id']), r['ts'], float(r['value']), int(r['interval_s']))
                    for r in csv.DictReader(f)]
        with conn:
            conn.executemany(UPSERT, rows)
        return conn.execute('SELECT COUNT(*) FROM reading').fetchone()[0]
    finally:
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    parser.add_argument('--db', type=Path, default=Path(__file__).with_name('edge.db'))
    args = parser.parse_args()
    print(f'Rows after ingest: {ingest(args.db, args.csv)}')
