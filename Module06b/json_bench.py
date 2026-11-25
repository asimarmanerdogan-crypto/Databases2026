"""Query and index 1,000 validated vendor documents in SQLite."""

import json
import sqlite3
from contextlib import closing

VENDOR = "json_extract(meta, '$.vendor')"
FILTER = "SELECT name FROM device WHERE {} = 'Fanuc'"


def main():
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("""CREATE TABLE device(
            device_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            meta TEXT NOT NULL CHECK (json_valid(meta))
        ) STRICT""")
        rows = [
            ("cnc-01", {"vendor": "Siemens", "firmware": "4.2", "calibrated": "2026-01-10"}),
            ("cnc-02", {"vendor": "Fanuc", "firmware": "3.9"}),
            ("molder-07", {"vendor": "Arburg", "firmware": "8.1",
                           "calibrated": "2025-11-02", "nozzle_mm": 2.5}),
        ]
        for number in range(4, 1001):
            rows.append((f"device-{number:04d}", {
                "vendor": ("Siemens", "Fanuc", "Arburg")[number % 3],
                "firmware": f"{number % 5}.{number % 10}",
            }))
        db.executemany("INSERT INTO device(name, meta) VALUES (?, ?)",
                       ((name, json.dumps(meta)) for name, meta in rows))
        print(f"SQLite {sqlite3.sqlite_version}, {len(rows):,} devices")
        try:
            db.execute("INSERT INTO device(name, meta) VALUES ('invalid', 'not JSON')")
        except sqlite3.IntegrityError as error:
            print(f"Validation: {error}")
        else:
            raise RuntimeError("The invalid JSON was accepted")

        for row in db.execute(f"""SELECT name, {VENDOR}, meta ->> '$.firmware'
                                  FROM device ORDER BY device_id LIMIT 5"""):
            print(row)
        for row in db.execute("""SELECT d.name, j.key, j.value
                                 FROM device AS d CROSS JOIN json_each(d.meta) AS j
                                 WHERE d.name = 'cnc-01' ORDER BY j.key"""):
            print(row)

        db.execute(f"CREATE INDEX ix_device_vendor ON device({VENDOR})")
        queries = (FILTER.format(VENDOR), FILTER.format("meta ->> 'vendor'"))
        for query in queries:
            print(db.execute("EXPLAIN QUERY PLAN " + query).fetchone()[-1])
        indexed, shorthand = (sorted(db.execute(query).fetchall()) for query in queries)
        if indexed != shorthand:
            raise RuntimeError("The two predicates returned different results")
        print(f"Both predicates returned {len(indexed)} matching devices")


if __name__ == "__main__":
    main()
