# Module 03 - LLM-Assisted SQL and Query Profiling

[Course module](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/03-llm-assisted-sql-and-query-profiling.md) · [Portfolio](../README.md)

## Learning goals

1. Build complex DQL queries with joins, GROUP BY/HAVING, subqueries and window functions.
2. Read EXPLAIN QUERY PLAN: SCAN, SEARCH, table lookup and covering index.
3. Benchmark index effects and explain why an index is ignored.
4. Generate or critique AI SQL and verify correctness, performance and edge cases.
5. Prevent SQL injection with bound parameters.

## Task status and evidence

| Task | Evidence | Status |
| --- | --- | --- |
| A - Plan safari | [Current plans](plan-safari-notes.md), [runner](plan_safari.py) | Rechecked; existing records preserved |
| B - Algebra check | [Assisted comparison](task-b.md), [verification](task-b-verification.txt) | AI-assisted translation checked against SQL |
| C - Pod comparison | [Curiosity list](sql-notes.md), [collaboration record](../COLLABORATION.md) | Discussed in person; takeaways still to write down |
| Warehouse setup | [setup.sql](setup.sql), [checked counts](warehouse-check.txt) | 2,000 customers, 500 products, 60,000 orders, 240,000 lines |
| 1 - Dashboard | [SQL](dashboard.sql), [request and correctness](warehouse-notes.md), [predictions](plan-predictions.json), [plans/results](benchmark-results.md) | Reference-query alternative used and independently verified |
| 2 - Index benchmark | [bench.py](bench.py), [report](benchmark-results.md), [raw JSON](benchmark-results.json) | Three samples per variant; isolated/cumulative tests and negative controls passed |
| 3 - Injection | [demo](injection_demo.py), [output](injection-output.txt), [explanation](warehouse-notes.md) | Apostrophe crash, bypass and bound-parameter fix verified |
| 4 - Algebra to plan | [Dashboard algebra and verification](warehouse-notes.md) | Completed with AI assistance |
| 5 - Query rewrites | [SQL, results, plans and comparison](query-rewrites.md), [runner](query_rewrites.py) | Correlated subquery, window function and HAVING verified |
| Reflection | [Reflection 3](../Reflections/ref03.md) | Completed |

The technical work includes the core exercises and [extra comparisons of window functions, correlated subqueries and HAVING](query-rewrites.md).

## Reproduce from the repository root

```sh
uv run --locked python Module03/bench.py
uv run --locked python Module03/injection_demo.py
uv run --locked python Module03/verify_task_b.py
uv run --locked python Module03/plan_safari.py
uv run --locked python Module03/query_rewrites.py
```

If warehouse.db is missing, first run `sqlite3 Module03/warehouse.db ".read Module03/setup.sql"`. This resets only the warehouse lab tables. If legacy.db is missing, use the Module02 fixture first. Database files stay out of Git.

The benchmark runs on a temporary copy and leaves warehouse.db unchanged. The safari resets its experiment index in Module02/legacy.db and saves the results to plan-safari-notes.md. It leaves the study notes and algebra exercise alone.
