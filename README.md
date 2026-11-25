# HSBI Databases Portfolio - Asim Arman Erdogan

This is my portfolio for the HSBI Databases course. It brings together my SQL exercises, Python scripts, query results and reflections.

| Module | Work | Reflection |
| --- | --- | --- |
| [01 - Introduction and Local-First](Module01-Restyle/README.md) | Tool setup, SQLite, telemetry and SQL Island | [Reflection 1](Reflections/ref01.md) |
| [02 - Data Contracts and Legacy Schemas](Module02-Restyle/README.md) | ER diagrams, data problems and a corrected schema | [Reflection 2](Reflections/ref02.md) |
| [03 - SQL and Query Profiling](Module03-Restyle/README.md) | Query plans, index benchmarks, injection and query rewrites | [Reflection 3](Reflections/ref03.md) |
| [04 - Data Integrity, Constraints and Triggers](Module04-Restyle/README.md) | Constraints, ingestion, triggers and access control | [Reflection 4](Reflections/ref04.md) |
| [05 - Normalization vs. Denormalization](Module05/README.md) | 3NF, anomalies, dashboard benchmarks and storage | [Reflection 5 draft](Reflections/ref05.md) |
| [06a - The Analytical Engine](Module06a/README.md) | SQLite and DuckDB benchmarks, Parquet, query plans and refresh memo | [Reflection 6a draft](Reflections/ref06a.md) |
| [06b - Polyglot Persistence](Module06b/README.md) | SQLite concurrency, JSON indexing, session benchmark and decision record | [Reflection 6b draft](Reflections/ref06b.md) |

[Checkpoint guide](CHECKPOINT.md) · [Pod work and AI assistance](COLLABORATION.md) · [Course workbook](https://github.com/iotempire/iotempire-teaching/tree/main/full-classes/hsbi-databases-10d) · [Syllabus](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/syllabus.md)

## Run the exercises

Install uv, then run these commands from the repository root:

```sh
uv sync --locked
uv run python reproduce.py
```

The Python version is set in .python-version and the packages are locked in uv.lock. The script rebuilds the course lab tables and updates their reports. Keep unrelated data outside these lab databases. Database files, generated CSV data and secrets stay out of Git.

## My pod

I work with [Habiba Darwish](https://github.com/Habiba-AladdinDarwish/Darwish_Databases_C2026). We also discussed Modules 2 and 3 with another pod in person. Habiba's portfolio is private, so its links require access.

## Still to finish

- A follow-up discussion with Habiba about the portfolio review.
- A short record of the main points from the Module 3 pod discussion. The [Module 2 discussion and shared diagram](Module02-Restyle/study-log.md#agreed-learning-pod-discussion) are documented.

SQL Island is completed, with [answers, certificate and a completion screenshot](Module01-Restyle/sql-island.md).
