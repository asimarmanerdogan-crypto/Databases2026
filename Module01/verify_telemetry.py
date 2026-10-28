"""Run Task 6 queries and record Task 7 AI verification evidence."""
import sqlite3
from pathlib import Path
from time import perf_counter

here = Path(__file__).parent
conn = sqlite3.connect(here / "telemetry.db")


def table(cursor):
    names = [c[0] for c in cursor.description]
    rows = cursor.fetchall()
    return "\n".join([
        "| " + " | ".join(names) + " |",
        "| " + " | ".join("---" for _ in names) + " |",
        *("| " + " | ".join(str(v) for v in row) + " |" for row in rows),
    ])


count = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
assert count == 172800
report = ["# Task 6: Synthetic telemetry in SQLite", "",
          "AI-assisted execution using the course's fixed-seed generator; these are synthetic readings, not real factory data.", "",
          f"Database size: {(here / 'telemetry.db').stat().st_size:,} bytes.",
          f"Row count: {count:,}.", "",
          "The database is embedded in a local file; no database server was started.", ""]
for query in (here / "queries.sql").read_text(encoding="utf-8").split(";"):
    if not query.strip():
        continue
    query = query.strip() + ";"
    started = perf_counter()
    cursor = conn.execute(query)
    result = table(cursor)
    elapsed = perf_counter() - started
    report.extend([f"```sql\n{query}\n```", result,
                   f"Wall-clock execute + fetch time: {elapsed * 1000:.3f} ms (one run).", ""])
report.extend(["Times are machine-dependent observations, not a benchmark.", "",
               "Cloud cost: this local run has no cloud-service charge; a hosted version would depend on the provider, resources, storage and traffic, with charges paid by the cloud account owner.", "",
               "Reproduce from the repository root:", "```text",
               "uv run python Module01/generate_telemetry.py",
               "uv run python Module01/load_telemetry.py",
               "uv run python Module01/verify_telemetry.py", "```"])
(here / "telemetry-results.md").write_text("\n".join(report), encoding="utf-8")

prompt = ('Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, '
          'vib_rms REAL, spindle_load REAL). Write a query that returns, for each '
          'machine, the average spindle load for readings taken overnight '
          '(after 18:00), ordered by average load descending.')
query = (here / "overnight.sql").read_text(encoding="utf-8").strip()
generated = conn.execute(query).fetchall()
plan = table(conn.execute("EXPLAIN QUERY PLAN " + query))
result = table(conn.execute(query))
assert any("SCAN readings" in row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + query))

# Independent filter/aggregation in Python, without SQL time functions.
loads = {}
for ts, machine, load in conn.execute("SELECT ts, machine, spindle_load FROM readings"):
    if ts[11:] > "18:00:00":
        loads.setdefault(machine, []).append(load)
expected = sorted(((m, sum(v) / len(v)) for m, v in loads.items()), key=lambda x: x[1], reverse=True)
assert len(expected) == len(generated) == 3
for actual, reference in zip(generated, expected):
    assert actual[0] == reference[0] and abs(actual[1] - reference[1]) < 1e-9

boundary = sqlite3.connect(":memory:")
boundary.execute("CREATE TABLE readings(ts TEXT, machine TEXT, spindle_load REAL)")
boundary.executemany("INSERT INTO readings VALUES (?, ?, ?)", [
    ("2026-01-05 17:59:59", "test", 10),
    ("2026-01-05 18:00:00", "test", 20),
    ("2026-01-05 18:00:01", "test", 30),
    ("2026-01-06 00:00:00", "test", 40),
    ("2026-01-06 05:59:59", "test", 50),
    ("2026-01-06 18:30:00", "test", 60),
])
assert boundary.execute(query).fetchall() == [("test", 45.0)]
inclusive = boundary.execute(query.replace("> '18:00:00'", ">= '18:00:00'")).fetchone()[1]
assert abs(inclusive - 110 / 3) < 1e-9
wrong = query.replace("time(ts) > '18:00:00'", "ts > '2026-01-05 18:00:00'")
wrong_average = boundary.execute(wrong).fetchone()[1]
assert wrong_average == 45.0  # Same average by coincidence: compare row membership too.
wrong_count = boundary.execute("SELECT COUNT(*) FROM readings WHERE ts > '2026-01-05 18:00:00'").fetchone()[0]
right_count = boundary.execute("SELECT COUNT(*) FROM readings WHERE time(ts) > '18:00:00'").fetchone()[0]
assert (right_count, wrong_count) == (2, 4)
try:
    conn.execute(query.replace("spindle_load", "spindel_load"))
except sqlite3.OperationalError as exc:
    typo_error = str(exc)
else:
    raise AssertionError("Column typo should fail")

report7 = f'''# Task 7: LLM-assisted SQL verification

This record was generated and checked with AI assistance. It does not claim a personal student reflection.

## Exact prompt

{prompt}

## Generated SQL

```sql
{query}
```

Interpretation: “after 18:00” means strictly later than 18:00:00 on each date. Exactly 18:00 and early-morning readings are excluded. If “overnight” means an entire 18:00–06:00 shift, this query needs a different predicate, for example `time(ts) >= '18:00:00' OR time(ts) < '06:00:00'`. Confirm the business definition before using it.

## Execution results

{result}

## EXPLAIN QUERY PLAN

{plan}

`SCAN readings` confirms a full-table scan. The planner also uses temporary B-trees for grouping and ordering; no index was added for this exercise.

## Break it: verified checks

- Independent Python filtering and aggregation matched all three machine averages within 1e-9 and matched their ordering.
- Six-row boundary fixture: 17:59:59, 18:00:00, 18:00:01, next-day 00:00:00, 05:59:59, and 18:30:00. The generated query selected two rows, with average 45.0.
- Changing `>` to `>=` includes the boundary row and changes the fixture average to {inclusive:.6f}.
- Replacing the daily-time predicate with `ts > '2026-01-05 18:00:00'` selects {wrong_count} fixture rows instead of {right_count}, incorrectly including the next morning. Its average happens to match in this fixture, showing why checking row membership matters.
- Deliberate column typo produced SQLite error: `{typo_error}`.

## AI-assisted verification paragraph

The model correctly grouped by machine, computed AVG and sorted descending, and the SQL executed successfully. Its interpretation of “overnight” is incomplete if the intended shift includes midnight through 06:00 or includes exactly 18:00. I verified execution and the full scan with EXPLAIN QUERY PLAN, independently recomputed the result in Python, and tested exact time boundaries and the next date in a small fixture. The deliberately broken date cutoff selected incorrect rows, and a misspelled column failed as expected. The business time boundary must be agreed before relying on the result.

## Reproduce

Run `uv run python Module01/verify_telemetry.py` after generating and loading the data. Failed checks raise assertions; successful checks recreate this evidence.
'''
(here / "ai-sql-verification.md").write_text(report7, encoding="utf-8")
boundary.close()
conn.close()
print("PASS: 172800 rows, Task 6 results, query plan, independent aggregation, boundary and negative checks.")

