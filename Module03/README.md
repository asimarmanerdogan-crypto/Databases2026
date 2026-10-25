# Module 03 — LLM-Assisted SQL and Query Profiling

[Course module](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/03-llm-assisted-sql-and-query-profiling.md) · [Portfolio](../README.md)

## Learning goals

Build complex queries; read SCAN, SEARCH and covering-index plans; measure index effects; verify AI SQL correctness and edge cases; prevent injection with bound parameters.

## Task status and evidence

| Task | Evidence | Status |
| --- | --- | --- |
| A — Plan safari | [Current plans](plan-safari-notes.md), [runner](plan_safari.py) | Rechecked; existing records preserved |
| B — Algebra check | [Assisted comparison](task-b.md), [verification](task-b-verification.txt) | Technical result verified; independent first attempt was not made |
| C — Pod comparison | sql-notes.md | Actual exchange and shared questions pending |
| Warehouse setup | [setup.sql](setup.sql), [checked counts](warehouse-check.txt) | 2,000 customers, 500 products, 60,000 orders, 240,000 lines |
| 1 — Dashboard | [SQL](dashboard.sql), [request and correctness](warehouse-notes.md), [predictions](plan-predictions.json), [plans/results](benchmark-results.md) | Reference-query alternative used and independently verified |
| 2 — Index benchmark | [bench.py](bench.py), [report](benchmark-results.md), [raw JSON](benchmark-results.json) | Three samples per variant; isolated/cumulative tests and negative controls passed |
| 3 — Injection | [demo](injection_demo.py), [output](injection-output.txt), [explanation](warehouse-notes.md) | Apostrophe crash, bypass and bound-parameter fix verified |
| 4 — Algebra to plan | [Dashboard algebra and verification](warehouse-notes.md) | Completed with AI assistance |
| Reflection | [Personal prompts](../Reflections/ref03.md) | Student answers pending |

The source labels the task content as a provisional draft. All starred technical tasks were checked as the current working list. Optional Task 5 is outside this pass. The broader window-function/subquery learning goal still benefits from the optional exercise or checkpoint practice.

## Reproduce from the repository root

```sh
uv run --locked python Module03/bench.py
uv run --locked python Module03/injection_demo.py
uv run --locked python Module03/verify_task_b.py
uv run --locked python Module03/plan_safari.py
```

If warehouse.db is missing, first run `sqlite3 Module03/warehouse.db ".read Module03/setup.sql"`. This resets only the warehouse lab tables. If legacy.db is missing, use the Module02 fixture first. Database files stay out of Git.

The benchmark uses a temporary disk database and preserves the existing warehouse. The safari changes only the verified experiment index in Module02/legacy.db and now writes plan-safari-notes.md, so replay no longer erases sql-notes.md or Task B notes. Earlier review JSON and CLI output are historical evidence with their original dates/hashes.
