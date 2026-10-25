# HSBI Databases Portfolio — Asim Arman Erdogan

Personal portfolio for HSBI Databases (2026): reproducible local database experiments, SQL results, and verification of AI suggestions.

- [Module 01: Introduction and Local-First Foundations](Module01/README.md)
- [Module 02: Study log](Module02/study-log.md)
- [Module 03: SQL notes](Module03/sql-notes.md)
- [Course workbook](https://github.com/iotempire/iotempire-teaching/tree/main/full-classes/hsbi-databases-10d)
- [Syllabus](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/syllabus.md)

## Reproduce Module 01

Install uv and SQLite, then run from this repository root:

```sh
uv sync --locked
uv run python module-01/uv-check.py
uv run python module-01/generate_telemetry.py
uv run python module-01/load_telemetry.py
uv run python module-01/verify_telemetry.py
```

Python is pinned in `.python-version`; library versions are locked in `uv.lock`. Database files, generated telemetry and secrets stay local.

AI assistance was used to prepare code, documentation and verification evidence. Personal gameplay, pod participation and instructor access require separate evidence; see the module audit.
