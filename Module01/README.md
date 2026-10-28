# Module 01 - Introduction and Local-First Foundations

Owner: Asim Arman Erdogan.

Exploration plan: generate machine telemetry, measure local SQLite queries, and independently verify an AI-generated time-filtered aggregate.

## Learning goals

1. Explain how this class works - the CBL/PBL philosophy, the portfolio-based project work assessment, and the "moving bar" of a first-time course.
2. Set up your personal GitHub portfolio from the course template, with a clean first commit and a `.gitignore` that keeps databases and secrets out of Git.
3. Set up the entire toolchain reproducibly with `uv` - one fixed Python plus SQLite, DuckDB, Datasette, and more - on Windows, macOS, or Linux, and verify it.
4. Explain - with a measurement, not a slide - the difference between an embedded database and a client/server database, and why most local apps should not run a server.
5. Load real rows into SQLite and query them from Python using bound parameters.
6. Take a first LLM-generated query, run it, and begin the habit that defines this course: verify before you trust.

## Course and evidence links

- [Module instructions](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/01-introduction-and-local-first.md)
- [Syllabus](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/syllabus.md)
- [Reflection](../Reflections/ref01.md)
- [SQL Island - guided completion and certificate](sql-island.md)
- [Learning-goal evidence audit](audit.md)
- [Pod mate: Habiba Darwish](https://github.com/Habiba-AladdinDarwish/Darwish_Databases_C2026) (private portfolio).

Run commands from the repository root. Technical evidence is indexed below.

## Course model

Learning goals define the contract. Challenge- and project-based learning uses practical problems and portfolio evidence; assessment includes module points, a final project and reflections. The course is a first iteration, so task wording can evolve while learning goals remain the basis for assessment. A pod contains two or three students; two pods form the final project team.

## Embedded versus client/server

SQLite executes inside the Python process and stores data in a local file. This experiment holds 172,800 readings in 10,526,720 bytes; measured query times are recorded in the linked telemetry results. No database server was needed. This proves the local workload runs without a server; it does not benchmark a remote database.

An embedded database simplifies deployment and offline operation, but SQLite permits only one writer at a time. A client/server database supports shared network access and many concurrent writers, with server administration and network dependencies. A server becomes appropriate when those workload requirements justify it.

## Participation and attribution

I worked with Habiba and three other classmates over the weekend. My [reflection](../Reflections/ref01.md) describes that experience. See [collaboration notes](../COLLABORATION.md) for the portfolio review and how AI was used.

## Task 3: Reproducible toolchain

Run `uv run python Module01/uv-check.py` from the repository root.

- [Verification script](uv-check.py)
- [Recorded version output](uv-check-output.txt)
- [Project dependencies](../pyproject.toml)
- [Locked dependencies](../uv.lock)

## Task 4: SQLite shell tour

- [Replayable shell commands](tour-commands.sql)
- [Captured session, including query timing](shell-tour.txt)
- [Schema and data dump](tour.sql)

Replay from the repository root with `sqlite3 -echo Module01/tour.db ".read Module01/tour-commands.sql"`.
The local database is excluded from Git by `.gitignore`.

AI-assisted observation: `.schema` was useful because it displayed the exact table definition and column types before querying.

## Task 5: SQL Island

[Completed guided demonstration](sql-island.md), with the original certificate, completion screenshot and SQL examples. I watched the assistant enter and explain the queries, and added my answers below the game notes.

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
