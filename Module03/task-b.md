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
