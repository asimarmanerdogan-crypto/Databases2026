# Module 04 — Data Integrity, Constraints & Edge Triggers

Owner: Asim Arman Erdogan. Technical implementation and verification prepared and run with AI assistance on 2026-11-03. Peer discussion and personal reflection require the student's own input.

[Course instructions](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/04-integrity-constraints-and-triggers.md) · [Portfolio](../README.md) · [Reflection draft](../Reflections/ref04.md)

## Learning goals

1. Create tables with NOT NULL, UNIQUE, CHECK, PRIMARY KEY, FOREIGN KEY and STRICT typing.
2. Derive values with generated columns.
3. Write triggers for domain rules and audit/rollup maintenance.
4. Use DML and UPSERT for idempotent ingestion.
5. Explain access control in embedded and server databases.

## Work and evidence

| Task | Evidence | Status |
| --- | --- | --- |
| A: acceptance experiments | [Study notes](integrity-notes.md), [exact errors](verification.txt) | Executed, including NULL and numeric-text cases |
| B: another pod | [Discussion prompts](integrity-notes.md#pod-discussion--pending) | Pending actual conversation; no participation invented |
| 1: constrained schema | [Setup SQL](setup.sql), [verification](verification.txt) | Rejections and generated column checked |
| 2: replay-safe ingestion | [CSV](readings.csv), [Python and UPSERT SQL](ingest.py) | First load: 4 rows; second load: 4; corrected value 41.7 |
| 3: alarm and audit | [Triggers](triggers.sql), [verification](verification.txt), [benchmark](benchmark-results.json) | Alarm/audit rows and 10,000-row timings checked |
| 4: access control | [View](view.sql), [access notes](access-control.md), [verification](verification.txt) | Read-only DELETE rejected; Windows adaptation documented |
| 5: optional BEFORE experiment | [Verifier](verify_module04.py), [verification](verification.txt) | Successful insert alarms; rejected statement leaves no alarm |

## Reproduce

From the repository root, using the existing environment:

```powershell
.\.venv\Scripts\python.exe Module04\verify_module04.py
```

Alternatively use `uv run --locked python Module04/verify_module04.py` with a working uv environment. No new packages are required. The verifier creates `Module04/edge.db` only when absent; if present it preserves it and runs the lab in an isolated temporary database. It rewrites only Module04's generated reports. Earlier module files and databases are not opened. Generated databases and temporary files are ignored by Git.

To replay the CSV into the prepared Module04 database:

```powershell
.\.venv\Scripts\python.exe Module04\ingest.py Module04\readings.csv --db Module04\edge.db
```

This UPSERT intentionally matches the course: on conflict it updates value only. A corrected interval_s would therefore need an explicit policy/change. Replaying after triggers exist can add audit records even for unchanged values; reading-row idempotence does not imply side-effect idempotence.

## Interpreting the benchmark

Five fresh disk-backed databases per variant, alternating order; each batch has 10,000 readings and 5,000 above-threshold vibrations. The timer includes insertion and commit, but excludes setup. The audit trigger exists in both variants and does not fire on these inserts. Compare medians in the JSON report; these are local measurements, not a universal performance guarantee.

## Verified limits of the teaching schema

- `energy_j = value * interval_s` is retained to reproduce the example. Temperature, vibration and spindle-load values multiplied by seconds do **not** represent joules. Real energy requires power in watts multiplied by seconds.
- The generic CHECK range does not validate each metric's actual physical domain, timestamp format or unit consistency. Plausible but incorrect readings can pass.
- The alarm trigger handles INSERT only; UPDATE/UPSERT can cross the threshold without an alarm. It records every high inserted reading, not only a transition from low to high.
- The audit trigger records updates but does not stop an authorized writer from editing/deleting audit records. The course's word “immutable” is not enforced by this DDL.
- BEFORE and AFTER triggers both participate in the statement transaction. AFTER is suitable for recording a successfully inserted reading; BEFORE is not automatically an independent durable alarm.
- `CHECK` accepts NULL unless NOT NULL rejects it; STRICT permits lossless conversions such as numeric text to REAL. Foreign-key enforcement must be enabled on each connection.
