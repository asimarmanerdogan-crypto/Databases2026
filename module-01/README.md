# Module 01

## Task 3: Reproducible toolchain

Run `uv run module-01/uv-check.py` from the repository root.

- [Verification script](uv-check.py)
- [Recorded version output](uv-check-output.txt)
- [Project dependencies](../pyproject.toml)
- [Locked dependencies](../uv.lock)

## Task 4: SQLite shell tour

- [Replayable shell commands](tour-commands.sql)
- [Captured session, including query timing](shell-tour.txt)
- [Schema and data dump](tour.sql)

Replay from the repository root with `sqlite3 -echo module-01/tour.db ".read module-01/tour-commands.sql"`.
The local database is excluded from Git by `.gitignore`.

AI-assisted observation: `.schema` was useful because it displayed the exact table definition and column types before querying.

## Task 5: SQL Island

[Skipped at the student's request](sql-island.md); no gameplay evidence is claimed.

## Task 6: Telemetry pipeline

- [Generator](generate_telemetry.py)
- [SQLite loader](load_telemetry.py)
- [Three SQL queries](queries.sql)
- [Results, timings, database size and row count](telemetry-results.md)

Generated CSV and database files stay local and can be reproduced from the scripts.

## Task 7: AI-assisted SQL verification

- [Generated query](overnight.sql)
- [Prompt, execution, query plan and verification report](ai-sql-verification.md)
- [Reproducible verification script](verify_telemetry.py)

Implementation and evidence were prepared with AI assistance. Review the time-boundary interpretation in the verification report.
