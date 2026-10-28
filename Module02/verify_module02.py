"""Rebuild the isolated lab fixture and generate measured audit evidence."""
from datetime import date
from pathlib import Path
import shutil
import sqlite3
from time import perf_counter

from pydantic import ValidationError
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import CreateTable
from contract import (Machine, Part, MaintenanceJob, machine_t, technician_t,
                      part_t, maint_job_t, job_part_t, metadata, make_engine)

here = Path(__file__).resolve().parent
db = here / "legacy.db"
if db.exists() and db.read_bytes()[:16] != b"SQLite format 3\x00":
    backup = here / "legacy-original-text.sql"
    if backup.exists():
        raise RuntimeError("Refusing to overwrite an existing original-file backup")
    shutil.move(db, backup)
    print("Preserved mislabeled SQL text as legacy-original-text.sql")

conn = sqlite3.connect(db)
conn.executescript((here / "legacy-setup.sql").read_text(encoding="utf-8-sig"))
assert conn.execute("PRAGMA integrity_check").fetchone() == ("ok",)
assert [conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in ("machine", "part", "maint_job")] == [4, 4, 4]


def render_query(query):
    started = perf_counter()
    cursor = conn.execute(query)
    rows = cursor.fetchall()
    elapsed = (perf_counter() - started) * 1000
    names = [c[0] for c in cursor.description]
    text = ["```sql", query, "```", "| " + " | ".join(names) + " |",
            "| " + " | ".join("---" for _ in names) + " |"]
    text += ["| " + " | ".join("NULL" if v is None else str(v) for v in row) + " |" for row in rows]
    text += [f"Measured execute + fetch: {elapsed:.3f} ms (one local run).", ""]
    return "\n".join(text)


queries = (here / "defect-queries.sql").read_text().split(";")
report = ["# Integrity defects - actual query results", "",
          "Each query below checks a problem in the sample data. The SQL comments explain what could go wrong in use.", ""]
for query in queries:
    if query.strip():
        report.append(render_query(query.strip() + ";"))
assert conn.execute("SELECT job_id FROM maint_job WHERE machine_name NOT IN (SELECT machine_name FROM machine)").fetchall() == [(3,)]
assert conn.execute("SELECT part_no, COUNT(*) FROM part GROUP BY part_no HAVING COUNT(*)>1").fetchall() == [("P-1003", 2)]
assert conn.execute("SELECT COUNT(*) FROM part WHERE unit_price < '15'").fetchone()[0] == 1
assert conn.execute("SELECT COUNT(*) FROM part WHERE CAST(unit_price AS NUMERIC) < 15").fetchone()[0] == 3
assert conn.execute("SELECT machine_name FROM machine WHERE installed='unknown'").fetchall() == [("RANDOM-NAME",)]
assert conn.execute("SELECT j.job_id FROM maint_job j JOIN part p ON p.part_no=j.parts_used ORDER BY j.job_id").fetchall() == [(2,), (2,), (3,)]
report += ["The naive list join returns job 2 twice because P-1003 is duplicated; job 1 is absent. CAST repairs this fixture's comparison but is not general validation of arbitrary text prices."]
(here / "defect-results.md").write_text("\n".join(report), encoding="utf-8")

counts = ["# Cardinality observations in the legacy fixture", "",
          "Observed counts support intended relationships; they do not enforce future cardinality.", ""]
for query in [
    "SELECT machine_name, COUNT(*) AS jobs FROM maint_job GROUP BY machine_name;",
    "SELECT technician, COUNT(*) AS jobs FROM maint_job GROUP BY technician;",
    "SELECT job_id, parts_used, CASE WHEN parts_used IS NULL OR trim(parts_used)='' THEN 0 ELSE length(parts_used)-length(replace(parts_used, ',', ''))+1 END AS n_parts FROM maint_job;",
    """WITH RECURSIVE split(job_id, part_no, rest) AS (
      SELECT job_id, '', coalesce(parts_used,'') || ',' FROM maint_job
      UNION ALL SELECT job_id, substr(rest,1,instr(rest,',')-1), substr(rest,instr(rest,',')+1)
      FROM split WHERE rest<>''
    ) SELECT trim(part_no) AS part_no, COUNT(DISTINCT job_id) AS jobs
      FROM split WHERE trim(part_no)<>'' GROUP BY trim(part_no);""",
]:
    counts.append(render_query(query))
(here / "cardinality-results.md").write_text("\n".join(counts), encoding="utf-8")
conn.close()

proof = sqlite3.connect(":memory:")
proof.executescript((here / "cardinality.sql").read_text())
assert proof.execute("SELECT machine_id, COUNT(*) FROM sensor GROUP BY machine_id").fetchall() == [(1, 2)]
try:
    proof.execute("INSERT INTO sensor VALUES(103,99)")
except sqlite3.IntegrityError:
    pass
else:
    raise AssertionError("Orphan sensor accepted")
proof.close()

valid = dict(machine_id=1, machine_name="cnc-01", serial_no="SN-1", site="Plant", installed="2026-01-01")
Machine(**valid)
checks = []
for field, value in [("installed", "2026-02-30"), ("serial_no", "BAD"), ("machine_id", 0), ("site", " ")]:
    try:
        Machine(**(valid | {field: value}))
    except ValidationError:
        checks.append(f"PASS model rejects {field}={value!r}")
    else:
        raise AssertionError(field)
for price in ("-1.00", "1.234", "10000000.00"):
    try:
        Part(part_no="P-1", description="Bearing", unit_price=price)
    except ValidationError:
        checks.append(f"PASS model rejects price {price}")
    else:
        raise AssertionError(price)
try:
    MaintenanceJob(job_id=1, machine_id=1, technician_id=1, done_on="2026-01-01", part_nos=["P-1", "P-1"])
except ValidationError:
    checks.append("PASS model rejects repeated part in a job")
else:
    raise AssertionError("Duplicate parts accepted")

engine = make_engine()
with engine.begin() as c:
    assert c.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
    c.execute(insert(machine_t), Machine(**valid).model_dump())
    c.execute(insert(technician_t), {"technician_id": 1, "name": "Tech"})
    c.execute(insert(part_t), {"part_no": "P-1", "description": "Bearing", "unit_price": 12.50})
    c.execute(insert(maint_job_t), {"job_id": 1, "machine_id": 1, "technician_id": 1, "done_on": date(2026,1,1)})
    c.execute(insert(job_part_t), {"job_id": 1, "part_no": "P-1"})

    def reject(label, statement, values):
        try:
            with c.begin_nested():
                c.execute(statement, values)
        except IntegrityError:
            checks.append("PASS database rejects " + label)
        else:
            raise AssertionError(label)

    reject("duplicate serial", insert(machine_t), Machine(**(valid | {"machine_id":2,"machine_name":"cnc-02"})).model_dump())
    reject("orphan machine", insert(maint_job_t), {"job_id":2,"machine_id":99,"technician_id":1,"done_on":date(2026,1,1)})
    reject("orphan technician", insert(maint_job_t), {"job_id":2,"machine_id":1,"technician_id":99,"done_on":date(2026,1,1)})
    reject("duplicate junction pair", insert(job_part_t), {"job_id":1,"part_no":"P-1"})
    reject("missing part", insert(job_part_t), {"job_id":1,"part_no":"MISSING"})
    reject("negative price", insert(part_t), {"part_no":"P-2","description":"Bad","unit_price":-1})
    reject("excess precision", insert(part_t), {"part_no":"P-2","description":"Bad","unit_price":1.234})
    reject("NULL site", insert(machine_t), Machine(**(valid | {"machine_id":2,"machine_name":"cnc-02","serial_no":"SN-2"})).model_dump() | {"site":None})
    assert c.exec_driver_sql("PRAGMA foreign_key_check").fetchall() == []

ddl = "\n\n".join(str(CreateTable(t).compile(engine)).strip()+";" for t in metadata.sorted_tables)
(here / "contract-ddl.sql").write_text("\n".join(line.rstrip() for line in ddl.splitlines())+"\n", encoding="utf-8")
(here / "verification.txt").write_text("\n".join([
    "PASS legacy SQLite integrity_check; table counts 4/4/4",
    "PASS all five defect cases and numeric comparison counterexample",
    "PASS 1:n proof: machine 1 has two sensors; missing parent rejected",
    *checks, "PASS corrected schema foreign_key_check; emitted DDL", ""]), encoding="utf-8")
print("PASS Module02 fixture, defects, cardinality and contract checks")
