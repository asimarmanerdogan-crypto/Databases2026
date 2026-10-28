# Checkpoint — Modules 1–3

Assessment targets the learning goals and the ability to explain/run the evidence. Task completion alone does not establish understanding. [Assessment rules](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/syllabus.md).

## Suggested presentation route

1. **Module 1:** Show [telemetry results](Module01/telemetry-results.md), [bound-parameter loader](Module01/load_telemetry.py) and [AI verification](Module01/ai-sql-verification.md). Explain 172,800 readings, why a server is unnecessary for this workload, and the daily 18:00 boundary versus a full overnight shift.
2. **Module 2:** Show [ER model](Module02/er-audit.md), [five defects](Module02/defect-results.md) and [contract decisions](Module02/contract-notes.md). Explain the orphan job, duplicate part, incorrect text comparison, junction key and per-connection foreign-key switch. Counts illustrate sample cardinality; constraints enforce future records.
3. **Module 3:** Show [safari](Module03/plan-safari-notes.md), [benchmark](Module03/benchmark-results.md), [injection](Module03/injection-output.txt), [algebra](Module03/warehouse-notes.md) and [rewrites](Module03/query-rewrites.md). Explain SCAN/SEARCH/covering, why an index can hurt, DISTINCT and year boundaries, and row-preserving window functions.

## Before presenting

Run `uv sync --locked` and `uv run python reproduce.py` on the presentation machine. This generates the ignored lab databases. Open one evidence page per module and be ready to run/explain a query yourself. Timings vary by machine; explain the plan and median methodology rather than promising identical milliseconds.

[Reflection 1](Reflections/ref01.md) · [Reflection 2 (pending)](Reflections/ref02.md) · [Reflection 3 (pending)](Reflections/ref03.md) · [Collaboration record](COLLABORATION.md) · [SQL Island — guided completion; personal answers pending](Module01/sql-island.md)
