# Module 03 — Tasks A and B

## Objective

Compare actual SQLite query plans before and after adding an ordinary index, and find predicates that cannot use it to narrow the search. Prepared with AI assistance using Python's built-in sqlite3; no SQLite CLI installation is needed.

## Original predictions — recorded before this run

| Query | Before-index prediction |
| --- | --- |
| Q1: `SELECT * FROM maint_job WHERE technician = 'Beier';` | SCAN |
| Q2: `SELECT * FROM machine WHERE machine_name = 'cnc-02';` | SCAN |
| Q3: `SELECT * FROM maint_job WHERE technician LIKE '%ei%';` | SCAN |

Database: `C:\Users\aerdogan4\Documents\Codex\Databases2026\Module02\legacy.db`. Python SQLite version: `3.53.1`.

Initial indexes: `[]`. No index existed, so none was removed.

## Actual comparison

| Query | Prediction | Before | After |
| --- | --- | --- | --- |
| Q1 | SCAN | `SCAN maint_job` | `SEARCH maint_job USING INDEX ix_job_tech (technician=?)` |
| Q2 | SCAN | `SCAN machine` | `SCAN machine` |
| Q3 | SCAN | `SCAN maint_job` | `SCAN maint_job` |

## Exact EXPLAIN QUERY PLAN outputs

Each tuple is `(id, parent, notused, detail)`, exactly as returned by Python.

### Before indexing

```sql
EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician = 'Beier';
```

```text
(2, 0, 216, 'SCAN maint_job')
```

```sql
EXPLAIN QUERY PLAN SELECT * FROM machine WHERE machine_name = 'cnc-02';
```

```text
(2, 0, 216, 'SCAN machine')
```

```sql
EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician LIKE '%ei%';
```

```text
(2, 0, 216, 'SCAN maint_job')
```

### After indexing

```sql
EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician = 'Beier';
```

```text
(3, 0, 62, 'SEARCH maint_job USING INDEX ix_job_tech (technician=?)')
```

```sql
EXPLAIN QUERY PLAN SELECT * FROM machine WHERE machine_name = 'cnc-02';
```

```text
(2, 0, 216, 'SCAN machine')
```

```sql
EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician LIKE '%ei%';
```

```text
(2, 0, 216, 'SCAN maint_job')
```

## SCAN versus SEARCH

SCAN means scanning a table or index rather than restricting traversal to a lookup range. SEARCH means visiting a subset using a key/index lookup. A plan is a strategy, not a timing measurement or proof of a speedup.

## Why the plans behave this way

Q1 compares the indexed technician value directly with one constant. An ordinary index can locate matching keys without inspecting every table row, then retrieve the matching records. On four rows, the overhead can outweigh any benefit; no meaningful speedup is claimed. SQLite may prefer SCAN in other data or statistics conditions. The recorded plan above is the observed result.

Q2 filters machine.machine_name, while the added index belongs to maint_job. That index cannot help locate rows in a different table. Q3 has a leading wildcard: the matching substring may occur anywhere, so there is no fixed leading prefix to turn into a narrow range of ordinary index keys. A scan is still needed for this query.

## Negative experiments

```sql
EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE LOWER(technician) = 'beier';
```

```text
(2, 0, 216, 'SCAN maint_job')
```

```sql
EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician LIKE '%ei%';
```

```text
(2, 0, 216, 'SCAN maint_job')
```

LOWER(technician) asks SQLite to compare a computed expression. The normal index stores the original technician values, not the LOWER expression, so it cannot directly narrow this expression lookup. An appropriately matching expression index would be a different experiment; none was added. The repeated leading-wildcard LIKE is the second negative example.

## Prediction check

All three before-index SCAN predictions matched. No incorrect prediction is invented.

## Data-preservation check

All user-table row counts and SHA-256 fingerprints of sorted record representations were identical before and after. Query result sets also matched across the index change. Only the experiment index was added.

```json
{
  "machine": {
    "count": 4,
    "sha256": "504f995ecf8ba7b4cace289d514eecb06f0536be0b7a093864dc46aa65fc0a5b"
  },
  "maint_job": {
    "count": 4,
    "sha256": "11c927bb065949a26c38237f56a9cdfa317c2a94da2f750284c5373d1adaceea"
  },
  "part": {
    "count": 4,
    "sha256": "275c9b9306ff52a307857d83abd3b82610b6464b021913902576330b95f66033"
  }
}
```

## Conclusion

An index helps when the filter can use its stored keys to find a smaller set of rows. It does not automatically help every query. We ran the plans and saw which searches used it, while keeping every existing database record unchanged.

## Files and replay

- [SQL statements](plan-safari.sql): ordered record of this run, not a blindly repeatable reset script; the CREATE INDEX will fail if the experiment index already exists.
- [Python runner](plan_safari.py): checks the existing database and safely resets only a matching experiment index on later runs. Run with the project's Python interpreter.
- [Earlier CLI baseline](legacy-before-index.txt): retained as historical evidence; this run uses Python SQLite instead.

Task B, Task C and the warehouse exercise are outside this Task A run. No pod discussion or GitHub commit/push is claimed.

## Submission review — 2026-10-22

Verified by replaying the SQL statements on an in-memory SQLite backup. The original database was opened read-only; its complete file hash and schema were unchanged by this review. All eight raw plan outputs exactly matched the documented tuples on Python SQLite 3.53.1. These tuples can differ on another SQLite version.

The SQL transcript now includes each plain SELECT immediately after its EXPLAIN QUERY PLAN. EXPLAIN describes a plan; it does not fetch the query's data. The original Python runner already executed all three main queries before and after indexing. The review additionally executed both negative SELECTs, which previously had plan output only. The runner was updated to execute those too and to locate the repository relative to its own file.

| Execution | Returned records |
| --- | --- |
| Q1 before / after | 2 / 2: job_id 1 and 3 |
| Q2 before / after | 1 / 1: machine_name cnc-02 |
| Q3 before / after | 2 / 2: job_id 1 and 3 |
| LOWER negative experiment | 2: job_id 1 and 3 |
| Repeated LIKE negative experiment | 2: job_id 1 and 3 |

All three user tables still contain four records each, with the same fingerprints recorded during the original experiment. This confirms their current contents match that recorded snapshot; it is not a forensic claim that no temporary change ever occurred between runs. Duplicate parts and the orphan cnc-05 job remain intact.

[Machine-readable review evidence](plan-safari-review.json) includes full query results, exact plans, record fingerprints and database hashes.

To rerun with the project's existing Python environment, from the repository root on Windows:

```powershell
.\.venv\Scripts\python.exe Module03/plan_safari.py
```

The runner verifies and resets only the known experiment index; do not replay the SQL transcript against an already-indexed database without first checking that index. No records are reset. The predictions are the previously recorded AI-assisted predictions, clearly separated from observations, rather than a claim of unaided student work.

Technical references checked during review: [SCAN and SEARCH](https://www.sqlite.org/eqp.html), [LIKE optimization](https://www.sqlite.org/optoverview.html#the_like_optimization), and [expression indexes](https://www.sqlite.org/expridx.html).

Task A's individual technical experiment and portfolio evidence are complete. Task B's relational-algebra exercise and Task C's real pod comparison remain separate; no such discussion is claimed here. No changes were committed or pushed during this review.

## Task B — SQL and relational algebra

### Chosen query

```sql
SELECT * FROM maint_job WHERE technician = 'Beier';
```

Meaning: retain the complete maintenance-job records whose technician is Beier.

### Initial attempt and assistance

I initially did not know how to express this in relational algebra and asked the LLM for help. The expression below was taught by the LLM before the formal translation prompt was submitted. There is therefore no independent, unaided student translation to compare, and no pod discussion is claimed.

Assisted expression: `σ_{technician = 'Beier'}(maint_job)`.

### Exact LLM prompt

```text
Translate the following SQL query into relational algebra using σ (selection), π (projection), and ⋈ (join) where appropriate.

SELECT * FROM maint_job WHERE technician = 'Beier';

Explain each operator. Do not introduce unnecessary operators. Do not inspect or modify my existing answers or project files.
```

The file-inspection restriction applied to that earlier translation-only request. This portfolio section was added later at my explicit request to complete Task B.

### LLM response and operator explanation

The response was `σ_{technician = 'Beier'}(maint_job)`.

- `maint_job` is the input relation.
- `σ` (selection) keeps rows satisfying the technician condition, preserving their columns.
- `π` (projection) is unnecessary because `SELECT *` requests every column.
- `⋈` (join) is unnecessary because there is only one input table.

### Comparison and learning

| Item | Earlier assisted expression | Formal LLM response |
| --- | --- | --- |
| Input | maint_job | maint_job |
| Selection | technician = 'Beier' | technician = 'Beier' |
| Projection | None | None |
| Join | None | None |

There is no semantic difference between the two assisted expressions. This is a consistency check, not proof of independent understanding. The key learning is that SQL's SELECT keyword does not automatically require relational-algebra projection: WHERE maps to selection here, and all columns remain.

### Verification against legacy.db

The SQL returned job_id 1 and 3, with all five original columns. A separate Python selection filtered all four source records by technician and returned the same two complete records. The check compares multisets so record multiplicities cannot silently disappear. Both records have a non-null technician, so SQL's NULL comparison behaviour causes no difference here.

Classical relational algebra has set semantics, while SQL normally preserves duplicates. This fixture has distinct full result rows, so that distinction does not change this result. Neither expression promises a display order. The orphan machine reference cnc-05 in job 3 remains in the result because this query filters only the technician and performs no machine join.

- [Full verification output](task-b-verification.txt)
- [Read-only verification script](verify_task_b.py)

Reproduce from the repository root:

```powershell
.\.venv\Scripts\python.exe Module03/verify_task_b.py
```

The database was opened read-only and its SHA-256 was unchanged. No data or index was modified. This completes the AI-assisted technical record for Task B; it does not replace the exercise's intended independent first attempt. Task C's real pod comparison remains pending.
