# Task 7: LLM-assisted SQL verification

This record was generated and checked with AI assistance. It does not claim a personal student reflection.

## Exact prompt

Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL). Write a query that returns, for each machine, the average spindle load for readings taken overnight (after 18:00), ordered by average load descending.

## Generated SQL

```sql
SELECT machine, AVG(spindle_load) AS avg_spindle_load
FROM readings
WHERE time(ts) > '18:00:00'
GROUP BY machine
ORDER BY avg_spindle_load DESC;
```

Interpretation: “after 18:00” means strictly later than 18:00:00 on each date. Exactly 18:00 and early-morning readings are excluded. If “overnight” means an entire 18:00–06:00 shift, this query needs a different predicate, for example `time(ts) >= '18:00:00' OR time(ts) < '06:00:00'`. Confirm the business definition before using it.

## Execution results

| machine | avg_spindle_load |
| --- | --- |
| cnc-03 | 60.4340394499236 |
| cnc-01 | 60.36845395193777 |
| cnc-02 | 60.35721628003889 |

## EXPLAIN QUERY PLAN

| id | parent | notused | detail |
| --- | --- | --- | --- |
| 7 | 0 | 216 | SCAN readings |
| 12 | 0 | 0 | USE TEMP B-TREE FOR GROUP BY |
| 51 | 0 | 0 | USE TEMP B-TREE FOR ORDER BY |

`SCAN readings` confirms a full-table scan. The planner also uses temporary B-trees for grouping and ordering; no index was added for this exercise.

## Break it: verified checks

- Independent Python filtering and aggregation matched all three machine averages within 1e-9 and matched their ordering.
- Six-row boundary fixture: 17:59:59, 18:00:00, 18:00:01, next-day 00:00:00, 05:59:59, and 18:30:00. The generated query selected two rows, with average 45.0.
- Changing `>` to `>=` includes the boundary row and changes the fixture average to 36.666667.
- Replacing the daily-time predicate with `ts > '2026-01-05 18:00:00'` selects 4 fixture rows instead of 2, incorrectly including the next morning. Its average happens to match in this fixture, showing why checking row membership matters.
- Deliberate column typo produced SQLite error: `no such column: spindel_load`.

## AI-assisted verification paragraph

The model correctly grouped by machine, computed AVG and sorted descending, and the SQL executed successfully. Its interpretation of “overnight” is incomplete if the intended shift includes midnight through 06:00 or includes exactly 18:00. I verified execution and the full scan with EXPLAIN QUERY PLAN, independently recomputed the result in Python, and tested exact time boundaries and the next date in a small fixture. The deliberately broken date cutoff selected incorrect rows, and a misspelled column failed as expected. The business time boundary must be agreed before relying on the result.

## Reproduce

Run `uv run python module-01/verify_telemetry.py` after generating and loading the data. Failed checks raise assertions; successful checks recreate this evidence.
