## Task B - SQL and relational algebra

### Chosen query

```sql
SELECT * FROM maint_job WHERE technician = 'Beier';
```

Meaning: retain the complete maintenance-job records whose technician is Beier.

### Initial attempt and assistance

I needed help with relational algebra, so the first expression was explained by the LLM. I then compared it with a second AI translation. Both versions were assisted.

Assisted expression: `σ_{technician = 'Beier'}(maint_job)`.

### Exact LLM prompt

```text
Translate the following SQL query into relational algebra using σ (selection), π (projection), and ⋈ (join) where appropriate.

SELECT * FROM maint_job WHERE technician = 'Beier';

Explain each operator. Do not introduce unnecessary operators. Do not inspect or modify my existing answers or project files.
```

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

Both assisted expressions mean the same thing. The useful distinction is that SQL SELECT and algebra selection are different: WHERE maps to selection here, while SELECT * keeps every column.

### Verification against legacy.db

The SQL returned job_id 1 and 3, with all five original columns. A separate Python selection filtered all four source records by technician and returned the same two complete records. The check compares multisets so record multiplicities cannot silently disappear. Both records have a non-null technician, so SQL's NULL comparison behaviour causes no difference here.

Classical relational algebra has set semantics, while SQL normally preserves duplicates. This fixture has distinct full result rows, so that distinction does not change this result. Neither expression promises a display order. The orphan machine reference cnc-05 in job 3 remains in the result because this query filters only the technician and performs no machine join.

- [Full verification output](task-b-verification.txt)
- [Read-only verification script](verify_task_b.py)

Reproduce from the repository root:

```powershell
.\.venv\Scripts\python.exe Module03/verify_task_b.py
```

The check opens the database read-only and confirms that its file hash stays unchanged. It verifies the assisted translation; I still need to practise writing the expression without help.
