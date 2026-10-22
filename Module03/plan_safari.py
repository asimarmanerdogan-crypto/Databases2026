"""Execute the index-only lab against an existing database; never create it."""
import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def folder(name):
    matches = [p for p in ROOT.iterdir() if p.is_dir() and p.name.casefold() == name.casefold()]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one existing {name} folder")
    return matches[0]

db = folder("Module02") / "legacy.db"
out = folder("Module03")
if not db.is_file():
    raise RuntimeError("Existing legacy.db is missing; refusing to create it")
conn = sqlite3.connect(db.as_uri() + "?mode=rw", uri=True, cached_statements=0)
queries = [
    "SELECT * FROM maint_job WHERE technician = 'Beier';",
    "SELECT * FROM machine WHERE machine_name = 'cnc-02';",
    "SELECT * FROM maint_job WHERE technician LIKE '%ei%';",
]
negative = "SELECT * FROM maint_job WHERE LOWER(technician) = 'beier';"
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
assert {"maint_job", "machine"} <= set(tables), "Required tables missing"

def records():
    result = {}
    for name in tables:
        quoted = '"' + name.replace('"', '""') + '"'
        rows = sorted(repr(row) for row in conn.execute(f"SELECT * FROM {quoted}"))
        result[name] = {"count": len(rows), "sha256": hashlib.sha256("\n".join(rows).encode()).hexdigest()}
    return result

before = records()
indexes = conn.execute("SELECT name,tbl_name,sql FROM sqlite_schema WHERE type='index' ORDER BY name").fetchall()
existing = [r for r in indexes if r[0].casefold() == "ix_job_tech"]
drop = ""
if existing:
    name, table, ddl = existing[0]
    # Only an ordinary, non-unique, single-column experiment index may be reset.
    normalized = re.sub(r'[\s"`\[\]]', '', ddl or '').lower()
    if table != "maint_job" or normalized != "createindexix_job_techonmaint_job(technician)":
        raise RuntimeError(f"Refusing to remove an unfamiliar index: {existing}")
    drop = 'DROP INDEX "ix_job_tech";'

notes = """# Module 03 — Task A: Plan Safari

## Objective

Compare actual SQLite query plans before and after adding an ordinary index, and find predicates that cannot use it to narrow the search. Prepared with AI assistance using Python's built-in sqlite3; no SQLite CLI installation is needed.

## Original predictions — recorded before this run

| Query | Before-index prediction |
| --- | --- |
""" + "\n".join(f"| Q{i}: `{q}` | SCAN |" for i, q in enumerate(queries, 1)) + "\n\nActual plans pending execution.\n"
(out / "sql-notes.md").write_text(notes, encoding="utf-8")

sql = ["-- Task A: run against the EXISTING Module02/legacy.db only.",
       "-- Predictions before indexing: Q1 SCAN; Q2 SCAN; Q3 SCAN.",
       "SELECT sqlite_version();",
       "SELECT name, sql FROM sqlite_schema WHERE type='table' AND name IN ('maint_job','machine');",
       "SELECT name, tbl_name, sql FROM sqlite_schema WHERE type='index';"]
if drop:
    sql.extend(["-- Existing index definition was checked by the runner before removal.", drop])
else:
    sql.append("-- No existing ix_job_tech was present; no index was dropped.")
sql += ["-- Baseline"] + [statement for q in queries for statement in ("EXPLAIN QUERY PLAN " + q, q)]
sql += ["CREATE INDEX ix_job_tech ON maint_job(technician);", "-- After indexing"]
sql += [statement for q in queries for statement in ("EXPLAIN QUERY PLAN " + q, q)]
sql += ["-- Negative experiments", "EXPLAIN QUERY PLAN " + negative, negative, "EXPLAIN QUERY PLAN " + queries[2], queries[2]]
(out / "plan-safari.sql").write_text("\n\n".join(sql) + "\n", encoding="utf-8")

def plan(q):
    return conn.execute("EXPLAIN QUERY PLAN " + q).fetchall()

try:
    conn.execute("BEGIN IMMEDIATE")
    if drop:
        conn.execute(drop)
    baseline = [plan(q) for q in queries]
    baseline_rows = [conn.execute(q).fetchall() for q in queries]
    conn.execute("CREATE INDEX ix_job_tech ON maint_job(technician)")
    indexed = [plan(q) for q in queries]
    negative_plans = [plan(negative), plan(queries[2])]
    negative_rows = [conn.execute(q).fetchall() for q in (negative, queries[2])]
    after = records()
    assert before == after, "Record contents changed; rolling back"
    for q, original in zip(queries, baseline_rows):
        assert sorted(map(repr, original)) == sorted(map(repr, conn.execute(q).fetchall()))
    conn.commit()
except BaseException:
    conn.rollback()
    raise

def details(p):
    return "; ".join(r[3] for r in p)

notes = notes.replace("Actual plans pending execution.", f"Database: `{db}`. Python SQLite version: `{sqlite3.sqlite_version}`.\n\nInitial indexes: `{indexes!r}`. " + ("Only the verified experiment index was reset." if drop else "No index existed, so none was removed."))
notes += "\n## Actual comparison\n\n| Query | Prediction | Before | After |\n| --- | --- | --- | --- |\n"
for i, (b, a) in enumerate(zip(baseline, indexed), 1):
    notes += f"| Q{i} | SCAN | `{details(b)}` | `{details(a)}` |\n"
notes += "\n## Exact EXPLAIN QUERY PLAN outputs\n\nEach tuple is `(id, parent, notused, detail)`, exactly as returned by Python.\n"
for label, plans in [("Before indexing", baseline), ("After indexing", indexed)]:
    notes += f"\n### {label}\n"
    for q, p in zip(queries, plans):
        notes += f"\n```sql\nEXPLAIN QUERY PLAN {q}\n```\n\n```text\n" + "\n".join(repr(r) for r in p) + "\n```\n"
notes += "\n## SCAN versus SEARCH\n\nSCAN means scanning a table or index rather than restricting traversal to a lookup range. SEARCH means visiting a subset using a key/index lookup. A plan is a strategy, not a timing measurement or proof of a speedup.\n"
notes += "\n## Why the plans behave this way\n\nQ1 compares the indexed technician value directly with one constant. An ordinary index can locate matching keys without inspecting every table row, then retrieve the matching records. On four rows, the overhead can outweigh any benefit; no meaningful speedup is claimed. SQLite may prefer SCAN in other data or statistics conditions. The recorded plan above is the observed result.\n\nQ2 filters machine.machine_name, while the added index belongs to maint_job. That index cannot help locate rows in a different table. Q3 has a leading wildcard: the matching substring may occur anywhere, so there is no fixed leading prefix to turn into a narrow range of ordinary index keys. A scan is still needed for this query.\n"
notes += "\n## Negative experiments\n"
for q, p in zip([negative, queries[2]], negative_plans):
    notes += f"\n```sql\nEXPLAIN QUERY PLAN {q}\n```\n\n```text\n" + "\n".join(repr(r) for r in p) + "\n```\n"
notes += "\nLOWER(technician) asks SQLite to compare a computed expression. The normal index stores the original technician values, not the LOWER expression, so it cannot directly narrow this expression lookup. An appropriately matching expression index would be a different experiment; none was added. The repeated leading-wildcard LIKE is the second negative example.\n"
wrong = [f"Q{i}" for i, p in enumerate(baseline, 1) if not all(r[3].startswith("SCAN") for r in p)]
notes += "\n## Prediction check\n\n" + ("Predictions that differed: " + ", ".join(wrong) if wrong else "All three before-index SCAN predictions matched. No incorrect prediction is invented.") + "\n"
notes += "\n## Data-preservation check\n\nAll user-table row counts and SHA-256 fingerprints of sorted record representations were identical before and after. Query result sets also matched across the index change. Only the experiment index was added.\n\n```json\n" + json.dumps(before, indent=2) + "\n```\n"
notes += "\n## Conclusion\n\nAn index helps when the filter can use its stored keys to find a smaller set of rows. It does not automatically help every query. We ran the plans and saw which searches used it, while keeping every existing database record unchanged.\n\n## Files and replay\n\n- [SQL statements](plan-safari.sql): ordered record of this run, not a blindly repeatable reset script; the CREATE INDEX will fail if the experiment index already exists.\n- [Python runner](plan_safari.py): checks the existing database and safely resets only a matching experiment index on later runs. Run with the project's Python interpreter.\n- [Earlier CLI baseline](legacy-before-index.txt): retained as historical evidence; this run uses Python SQLite instead.\n\nTask B, Task C and the warehouse exercise are outside this Task A run. No pod discussion or GitHub commit/push is claimed.\n"
(out / "sql-notes.md").write_text(notes, encoding="utf-8")
conn.close()
print(json.dumps({"database": str(db), "sqlite_version": sqlite3.sqlite_version,
                  "initial_indexes": indexes, "before": baseline, "after": indexed,
                  "negative": negative_plans, "records_unchanged": before == after,
                  "files": [str(out / n) for n in ["plan-safari.sql", "sql-notes.md", "plan_safari.py"]]}, indent=2))
