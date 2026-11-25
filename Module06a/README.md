# Module 6a | The analytical engine

The lab extends the existing Module 5 job-part history to 2,000,000 rows, builds matching Snappy and Zstandard Parquet copies, and compares SQLite with DuckDB.

| Task | Script or evidence |
| --- | --- |
| Build history | [prepare.py](prepare.py) |
| Convert and verify | [to_parquet.py](to_parquet.py) |
| Race both aggregates | [race.py](race.py) |
| Read the plans | [plan.py](plan.py) |
| Test small transactions | [boundary.py](boundary.py) |
| Report measurements and decide | [DuckDB notes and memo](duckdb-notes.md) |
| Reflection | [Reflection draft](../Reflections/ref06a.md) |

Run these commands from the repository root. The first script reuses the tracked Module 5 setup and report scripts because the Module 5 runner keeps its database in a temporary directory. Generated databases, CSV and Parquet stay under `Module06a/output/`.

```sh
uv run --no-project python Module06a/prepare.py
uv run --no-project --with duckdb==2.0.1 python Module06a/to_parquet.py
uv run --no-project --with duckdb==2.0.1 python Module06a/race.py
uv run --no-project --with duckdb==2.0.1 python Module06a/plan.py
uv run --no-project --with duckdb==2.0.1 python Module06a/boundary.py
```

[Course module](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/06a-duckdb-analytical-engine.md) · [Module 5 evidence](../Module05/benchmark-results.md) · [Module 6b](../Module06b/README.md)

Implementation and verification were prepared with AI assistance.
