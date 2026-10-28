# HSBI Databases Portfolio — Asim Arman Erdogan

Personal portfolio for HSBI Databases (2026): reproducible local database experiments, SQL results and verification of AI suggestions.

| Module | Evidence | Reflection |
| --- | --- | --- |
| [01 — Introduction and Local-First](Module01/README.md) | Toolchain, shell, telemetry and AI SQL verification | [ref01](Reflections/ref01.md) |
| [02 — Data Contracts and Legacy Schemas](Module02/README.md) | ER diagrams, five proven defects and executable contract | [ref02 — answers pending](Reflections/ref02.md) |
| [03 — SQL and Query Profiling](Module03/README.md) | Plans, benchmarks, injection, algebra and query rewrites | [ref03 — answers pending](Reflections/ref03.md) |

[Checkpoint guide](CHECKPOINT.md) · [Collaboration and attribution](COLLABORATION.md) · [Course workbook](https://github.com/iotempire/iotempire-teaching/tree/main/full-classes/hsbi-databases-10d) · [Syllabus](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/syllabus.md)

## Reproduce

Install uv, then run from this repository root:

```sh
uv sync --locked
uv run python reproduce.py
```

Python is selected by .python-version and dependency versions by uv.lock. The runner rebuilds only the course lab tables and generated reports, then verifies results. Keep unrelated data outside these lab files. Local databases, generated telemetry and secrets are ignored by Git. SQLite shell transcripts are separate CLI evidence; the full Python replay does not require the SQLite executable.

## Remaining personal work

- Four personal SQL Island answers; the [guided session, certificate and completion screenshot](Module01/sql-island.md) are now documented.
- Reflection 02 and 03 personal answers.
- The student's peer audit of a pod mate's work.

Pod mate: [Habiba Darwish](https://github.com/Habiba-AladdinDarwish). Module 2–3 discussions with another pod were held face to face. Specific takeaways, her portfolio URL and any Discord evidence will be revisited later; see [collaboration notes](COLLABORATION.md). Technical artifacts were prepared and checked with AI assistance. Personal understanding must be demonstrated at the checkpoint.
