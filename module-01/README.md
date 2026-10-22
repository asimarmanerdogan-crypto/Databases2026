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
