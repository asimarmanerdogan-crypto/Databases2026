"""Verify Task B's selection using a read-only SQLite connection."""
import hashlib
import sqlite3
from collections import Counter
from pathlib import Path

here = Path(__file__).resolve().parent
db = here.parent / "Module02" / "legacy.db"
before = hashlib.sha256(db.read_bytes()).hexdigest()
query = "SELECT * FROM maint_job WHERE technician = 'Beier';"
with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as conn:
    cursor = conn.execute("SELECT * FROM maint_job")
    columns = [column[0] for column in cursor.description]
    all_rows = cursor.fetchall()
    technician_pos = columns.index("technician")
    # Implement sigma independently: retain complete rows matching the predicate.
    selected_rows = [r for r in all_rows if r[technician_pos] == "Beier"]
    cursor = conn.execute(query)
    sql_columns = [column[0] for column in cursor.description]
    sql_rows = cursor.fetchall()
    assert sql_columns == columns, "SELECT * must retain all columns"
    assert Counter(sql_rows) == Counter(selected_rows), "Selection and SQL differ"
    version = conn.execute("SELECT sqlite_version()").fetchone()[0]
after = hashlib.sha256(db.read_bytes()).hexdigest()
assert before == after, "Database file changed"
lines = [
    "Task B: SQL versus independently implemented selection",
    f"SQLite version: {version}",
    f"SQL: {query}",
    f"Columns: {columns}",
    f"Input rows: {len(all_rows)}",
    f"SQL result rows: {len(sql_rows)}",
    f"Selection result rows: {len(selected_rows)}",
    "Rows (sorted for display only; SQL specifies no result order):",
    *(repr(row) for row in sorted(sql_rows)),
    "PASS: same complete rows and multiplicities; no projection or join needed.",
    "PASS: read-only database hash unchanged.",
    f"SHA-256: {after}",
]
output = "\n".join(lines) + "\n"
(here / "task-b-verification.txt").write_text(output, encoding="utf-8")
print(output)
