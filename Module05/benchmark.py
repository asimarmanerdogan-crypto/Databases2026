"""Run the Module 05 experiments and save the measured evidence."""

import argparse
from collections import Counter
from contextlib import closing
import csv
import json
from pathlib import Path
import platform
import sqlite3
import statistics
import tempfile
import time

HERE = Path(__file__).resolve().parent
TABLES = ("machine", "part", "job", "job_part")
EXPECTED = {"flat_jobpart": 200000, "machine": 50, "part": 10,
            "job": 20000, "job_part": 200000, "report_jobpart": 200000}
UPDATE_SITE = "UPDATE {} SET site = 'Bielefeld' WHERE machine_id = 'cnc-02'"


def sql(name):
    return (HERE / name).read_text(encoding="utf-8")


def anomalies(path):
    with closing(sqlite3.connect(path)) as first, closing(sqlite3.connect(path, timeout=0)) as second:
        first.executescript(sql("anomalies.sql"))
        first.execute("BEGIN IMMEDIATE")
        count = first.execute(UPDATE_SITE.format("flat5").replace("cnc-02", "cnc-01")).rowcount
        assert count == 3
        try:
            second.execute("UPDATE flat5 SET site = 'Paderborn' WHERE job_id = 3")
        except sqlite3.OperationalError as exc:
            assert exc.sqlite_errorcode == sqlite3.SQLITE_BUSY
            lock = exc.sqlite_errorname
            second.rollback()
        else:
            raise AssertionError("Second writer unexpectedly acquired the lock")
        first.commit()
        second.execute("UPDATE flat5 SET site = 'Paderborn' WHERE job_id = 3")
        second.commit()
        sites = first.execute("SELECT DISTINCT site FROM flat5 WHERE machine_id = 'cnc-01' ORDER BY site").fetchall()
        assert sites == [("Bielefeld",), ("Paderborn",)]
        with first:
            first.execute("INSERT INTO flat5(part_no, part_price) VALUES ('P-9999', 12.50)")
            orphan = first.execute("SELECT * FROM flat5 WHERE part_no = 'P-9999'").fetchone()
            assert orphan == (None, None, None, None, "P-9999", 12.5)
            count_deleted = first.execute("DELETE FROM flat5 WHERE job_id = 1").rowcount
            assert count_deleted == 2
            assert first.execute("SELECT COUNT(*) FROM flat5 WHERE part_no = 'P-0002'").fetchone()[0] == 0
        return {"update_rows": count, "concurrent_write": lock, "sites_after_retry": [r[0] for r in sites],
                "part_only_row": orphan, "deleted_rows": count_deleted, "lost_part": "P-0002"}


def timed_reads(db, queries, expected, explain="EXPLAIN QUERY PLAN ", plan_column=3):
    samples = {name: [] for name in queries}
    plans = {}
    for name, query in queries.items():
        assert sorted(db.execute(query).fetchall()) == expected
        # Distinct statement text forces a fresh plan after an index change.
        statement = f"{explain}/* {name} */ {query}"
        plans[name] = [r[plan_column] for r in db.execute(statement).fetchall()]
    entries = list(queries.items())
    for run in range(3):
        for name, query in entries if run % 2 == 0 else reversed(entries):
            start = time.perf_counter_ns()
            actual = db.execute(query).fetchall()
            samples[name].append((time.perf_counter_ns() - start) / 1_000_000)
            assert sorted(actual) == expected
    return {name: {"samples_ms": values, "median_ms": statistics.median(values), "plan": plans[name]}
            for name, values in samples.items()}


def storage(db):
    try:
        objects = dict(db.execute("SELECT name, SUM(pgsize) FROM dbstat GROUP BY name"))
    except sqlite3.OperationalError as exc:
        if "no such table: dbstat" not in str(exc):
            raise
        return None
    normalized_indexes = [row[0] for row in db.execute(
        "SELECT name FROM sqlite_schema WHERE type = 'index' AND tbl_name IN ('machine','part','job','job_part')"
    )]
    return {
        "normalized_table_bytes": sum(objects[name] for name in TABLES),
        "normalized_index_bytes": sum(objects[name] for name in normalized_indexes),
        "report_table_bytes": objects["report_jobpart"],
        "report_index_bytes": objects["ix_report_machine"],
    }


def timed_updates(db):
    measurements = {}
    for table, expected in (("machine", 1), ("report_jobpart", 4000)):
        samples = []
        for _ in range(3):
            db.execute("BEGIN IMMEDIATE")
            try:
                start = time.perf_counter_ns()
                changed = db.execute(UPDATE_SITE.format(table)).rowcount
                samples.append((time.perf_counter_ns() - start) / 1_000_000)
                assert changed == expected
            finally:
                db.rollback()
        measurements[table] = {"rows": expected, "samples_ms": samples, "median_ms": statistics.median(samples)}
    return measurements


def wide_comparison(db):
    db.executescript(sql("dimensions.sql"))
    join = """
        SELECT j.machine_id, m.site, sd.region, j.technician, v.vendor, SUM(p.part_price)
        FROM job AS j
        JOIN machine AS m ON m.machine_id = j.machine_id
        JOIN site_dim AS sd ON sd.site = m.site
        JOIN job_part AS jp ON jp.job_id = j.job_id
        JOIN part AS p ON p.part_no = jp.part_no
        JOIN vendor AS v ON v.part_no = p.part_no
        WHERE j.done_on >= '2026-03-01'
        GROUP BY j.machine_id, m.site, sd.region, j.technician, v.vendor
    """
    report = """
        SELECT machine_id, site, region, technician, vendor, SUM(part_price)
        FROM report_wide WHERE done_on >= '2026-03-01'
        GROUP BY machine_id, site, region, technician, vendor
    """
    expected = sorted(db.execute(join).fetchall())
    total = sum(r[-1] for r in expected)
    assert (len(expected), total) == (3500, 722610.0)
    return {"result_rows": len(expected), "total": total,
            "reads": timed_reads(db, {"six_tables": join, "wide_report": report}, expected)}


def duckdb_comparison(db, folder, expected):
    import duckdb

    with closing(duckdb.connect(str(folder / "comparison.duckdb"))) as duck:
        duck.execute("SET threads = 1")
        for name in (*TABLES, "report_jobpart"):
            csv_path = folder / f"{name}.csv"
            cursor = db.execute(f"SELECT * FROM {name}")
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow([column[0] for column in cursor.description])
                writer.writerows(cursor)
            duck.execute(f"CREATE TABLE {name} AS SELECT * FROM read_csv_auto(?)", [str(csv_path)])
            assert duck.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] == EXPECTED[name]
        queries = {"normalized": sql("normalized.sql"), "report": sql("denormalized.sql")}
        return {"version": duckdb.__version__, "threads": 1,
                "reads": timed_reads(duck, queries, expected, explain="EXPLAIN ", plan_column=1)}


def run(folder, with_duckdb):
    with closing(sqlite3.connect(folder / "normalize.db")) as db:
        db.execute("PRAGMA cache_size = -65536")
        db.executescript(sql("setup.sql"))
        db.executescript(sql("report.sql"))
        counts = {name: db.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] for name in EXPECTED}
        assert counts == EXPECTED
        assert db.execute("PRAGMA foreign_keys").fetchone() == (1,)
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        canonical = """SELECT job_id, machine_id, site, technician, part_no,
                              CAST(part_price AS REAL), done_on FROM flat_jobpart"""
        reconstructed = "SELECT * FROM report_jobpart"
        assert Counter(db.execute(canonical)) == Counter(db.execute(reconstructed))
        assert db.execute("SELECT COUNT(DISTINCT technician) FROM job WHERE machine_id = 'cnc-02'").fetchone() == (7,)

        normalized, report = sql("normalized.sql"), sql("denormalized.sql")
        expected = sorted(db.execute(normalized).fetchall())
        total = sum(r[-1] for r in expected)
        assert (len(expected), total) == (350, 722610.0)
        reads = timed_reads(db, {"normalized": normalized, "indexed_report": report}, expected)
        sizes = storage(db)
        writes = timed_updates(db)
        db.execute("DROP INDEX ix_report_machine")
        index_test = timed_reads(db, {"normalized": normalized, "unindexed_report": report}, expected)
        assert all("ix_report_machine" not in line for line in index_test["unindexed_report"]["plan"])
        result = {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
                  "cache_kib": 65536, "counts": counts, "lossless_join": True,
                  "result_rows": len(expected), "total": total, "reads": reads,
                  "index_test": index_test, "writes": writes, "storage": sizes,
                  "anomalies": anomalies(folder / "anomalies.db"),
                  "wide_comparison": wide_comparison(db)}
        if with_duckdb:
            result["duckdb"] = duckdb_comparison(db, folder, expected)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duckdb", action="store_true", help="Include the optional DuckDB comparison")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="module05-") as folder:
        result = run(Path(folder), args.duckdb)
    (HERE / "benchmark-results.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("PASS: lossless join, integrity, anomalies, result equality, and site update counts.")
    print("Saved benchmark-results.json.")


if __name__ == "__main__":
    main()
