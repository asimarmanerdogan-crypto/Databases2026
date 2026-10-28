# Tasks 1–4 — Query verification notes

Prepared with AI assistance on 2026-10-25. No independent student prediction, pod conversation or Discord post is claimed.

## Task 1: Request, SQL and correctness

Exact exercise prompt used as the specification:

> SQLite schema: customer(customer_id, name, city), product(product_id, sku, price), orders(order_id, customer_id, ordered_on, status), order_line(order_id, product_id, qty). Write a query that returns, for each city, the number of distinct customers and the total revenue (sum of qty*price) of orders placed in 2025, ordered by revenue descending.

[dashboard.sql](dashboard.sql) uses the module's reference query, the explicitly permitted alternative to a separate model response. There is no invented external model conversation. [Predictions](plan-predictions.json) were saved by the AI-assisted runner before requesting plans; they are not a student's unaided first attempt. [Actual results and plans](benchmark-results.md) record what happened.

Correctness interpretation: count distinct customers with at least one qualifying order line, and sum all qualifying lines regardless of order status. This is booked order revenue; excluding open/late orders would be a different business rule. Customers without qualifying lines are excluded by the inner joins; cities with no qualifying lines have no row. If the manager means every registered customer, calculate that count separately and left join the revenue aggregate.

An independent Python aggregation over the actual warehouse agrees with all four city totals. A small fixture includes 2024-12-31, 2025-01-01, 2025-12-31 and 2026-01-01, multiple lines for one customer, a customer without orders and one with only 2026 orders. It returns one city, one distinct customer and revenue 90.0, proving the year boundary and distinct-count interpretation.

Baseline: SCAN order_line (ol); primary-key SEARCH lookups for orders, customer and product; temporary B-trees for GROUP BY, COUNT(DISTINCT), and ORDER BY. The exact tuples are in the measured report.

## Task 2: Optimization suggestions and actual findings

AI optimization question for this exercise: Which indexes on ordered_on, order_line.order_id and order_line.product_id might help this city revenue query, and how can we establish whether they actually help?

AI answer: try ix_orders_ordered_on, ix_orderline_order and ix_orderline_product; test isolated effects and the cumulative course sequence, without assuming a speedup. This is advice from the assistant preparing these files, not an independent external transcript.

[bench.py](bench.py) captures a plan before each timed variant, performs an untimed warmup, and reports three samples and their median. All measurements run in the same process and connection. Short lookups use repeated batches to amortize timer overhead. Isolated tests reset to the baseline; cumulative tests also reproduce the course sequence. Source warehouse.db is read-only; index changes occur on a temporary disk fixture built from setup.sql.

The [current benchmark report](benchmark-results.md) contains the authoritative samples, medians and plans for the latest replay. It confirms:

- The date index leaves this broad dashboard plan unchanged; small clock differences alone do not establish an improvement.
- Combining date and order-line-order indexes changes the dashboard plan and is slower than the baseline in the recorded run.
- A single-day lookup uses SEARCH through the date index and is substantially faster in this run.
- Wrapping ordered_on in date(...) prevents the ordinary narrow index lookup while preserving the result.
- The product index does not help this dashboard, but is used by a direct product filter.

Exact timings depend on the machine and cache. Consult the generated table rather than copying historical milliseconds into prose. Index build/storage cost is outside this query-only benchmark.

## Task 3: Injection and the apostrophe crash

[Demonstration](injection_demo.py) and [actual output](injection-output.txt): O'Brien crashes string-built SQL; the payload `' OR '1'='1` returns all 2,000 customers instead of an exact-name match. The bound-parameter query treats both strings as values. A separate fixture proves a real O'Brien record can be retrieved safely. Source records are unchanged.

Handwritten quote filtering changes legitimate names and is fragile across contexts and encodings. Correct literal escaping is possible when implemented for the exact dialect, but hand-built filters are a poor application boundary. Bound parameters delegate separation of values from SQL syntax to the driver. They do not parameterize table/column names: dynamic identifiers need a fixed allowlist or a trusted query builder. Parameterization does not itself enforce authorization.

## Task 4: Algebra for the dashboard

Let C, O, L and P denote renamed customer, orders, order_line and product relations:

```text
J = C join[C.customer_id = O.customer_id] O
      join[O.order_id = L.order_id] L
      join[L.product_id = P.product_id] P
F = sigma[O.ordered_on >= '2025-01-01' AND O.ordered_on < '2026-01-01'](J)
R = gamma[C.city; COUNT_DISTINCT(C.customer_id) -> customers,
          SUM(L.qty * P.price) -> revenue](F)
Answer = tau[revenue descending](R)
```

sigma is σ (selection); gamma is γ (grouping); join is ⋈; tau is τ (extended ordering). Grouping already emits the requested city and aggregates, so no extra projection π is necessary. This is extended algebra with bag-aware aggregation: classical set algebra alone would silently lose duplicate order lines that SQL preserves. The independent Python implementation performs the same joins through identity maps, year selection, distinct-customer sets, sums and sorting, and agrees with SQL. Task B's simpler selection exercise is retained in task-b.md.

## Setup constructs and curiosities to discuss

Source: [Module 3 setup and pod-study section](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/03-llm-assisted-sql-and-query-profiling.md).

- WITH RECURSIVE generates consecutive values from the seed until the termination condition; INSERT ... SELECT inserts those output rows. An empty result inserts zero rows.
- `(x % 2000)+1` produces existing customer IDs because this fixture inserted 1 through 2000; there is no FK enforcing it yet.
- The date modifier is concatenated text understood by SQLite's date function. At x=540 the remainder is zero and the date is 2025-01-01.
- printf('%05d', x) gives fixed-width SKU suffixes so lexicographic ordering matches numeric ordering for this range.
- Dropping children first matters when foreign keys are introduced.
- SQL logical order is FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY. SQLite permits some alias references as an extension, so “a SELECT alias always fails in WHERE” is an overgeneralization. An aggregate such as COUNT(*) in WHERE is a clearer invalid stage example.
- A covering index contains every requested value; asking for an unindexed payload column requires visiting the table. A full index scan can still be covering.

Pod mate Habiba Darwish and face-to-face discussions for Modules 2–3 are confirmed by the student. Specific exchanged curiosities, the other pod's SQLite version and any questions posted to #sql-questions will be revisited later; see [collaboration record](../COLLABORATION.md).

References: [SQLite plan vocabulary](https://www.sqlite.org/eqp.html), [optimizer behavior](https://www.sqlite.org/optoverview.html), [Python sqlite3 parameter binding](https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders). No personal web-search history is claimed.

[Executed covering-index and clause-order checks](concept-checks.txt).
