# Query rewrites - subqueries, windows and HAVING

These query rewrites were prepared and checked with AI assistance.
SQLite 3.53.1. Reproduce: `uv run python Module03/query_rewrites.py`.

## Query and plan comparison

The course report is the grouped baseline. The rewrites were prepared with AI assistance. For this report, GROUP BY is the clearest form. The correlated form repeats an indexed count per customer and uses EXISTS to retain exactly the customers present in the original inner join. The window form preserves each late-order row; DISTINCT reduces repeated customer/count pairs to one row per customer. No timing advantage is claimed.

A query-specific `(customer_id,status)` index is added only to an in-memory backup. It covers the count/EXISTS predicates; a different index/workload can produce different plans.

### Grouped report
```sql
SELECT c.customer_id, c.name, COUNT(*) AS late_orders
FROM orders o JOIN customer c ON c.customer_id=o.customer_id
WHERE o.status='late'
GROUP BY c.customer_id, c.name
ORDER BY late_orders DESC, c.customer_id;
```

```text
(8, 0, 213, 'SCAN o USING COVERING INDEX ix_rewrite_customer_status')
(12, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
(15, 0, 0, 'USE TEMP B-TREE FOR GROUP BY')
(54, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

Result rows: 400. First five (stable order):
| customer_id | name | late_orders |
| --- | --- | --- |
| 1 | Customer 1 | 30 |
| 6 | Customer 6 | 30 |
| 11 | Customer 11 | 30 |
| 16 | Customer 16 | 30 |
| 21 | Customer 21 | 30 |

### Correlated subquery
```sql
SELECT c.customer_id, c.name,
       (SELECT COUNT(*) FROM orders o
        WHERE o.customer_id=c.customer_id AND o.status='late') AS late_orders
FROM customer c
WHERE EXISTS (SELECT 1 FROM orders o
              WHERE o.customer_id=c.customer_id AND o.status='late')
ORDER BY late_orders DESC, c.customer_id;
```

```text
(5, 0, 216, 'SCAN c')
(7, 0, 54, 'SEARCH o EXISTS USING COVERING INDEX ix_rewrite_customer_status (customer_id=? AND status=?)')
(14, 0, 0, 'CORRELATED SCALAR SUBQUERY 1')
(19, 14, 54, 'SEARCH o USING COVERING INDEX ix_rewrite_customer_status (customer_id=? AND status=?)')
(37, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

Result rows: 400. First five (stable order):
| customer_id | name | late_orders |
| --- | --- | --- |
| 1 | Customer 1 | 30 |
| 6 | Customer 6 | 30 |
| 11 | Customer 11 | 30 |
| 16 | Customer 16 | 30 |
| 21 | Customer 21 | 30 |

### Window rewrite
```sql
WITH late_rows AS (
    SELECT c.customer_id, c.name,
           COUNT(*) OVER (PARTITION BY c.customer_id) AS late_orders
    FROM orders o JOIN customer c ON c.customer_id=o.customer_id
    WHERE o.status='late'
)
SELECT DISTINCT customer_id, name, late_orders
FROM late_rows
ORDER BY late_orders DESC, customer_id;
```

```text
(2, 0, 0, 'CO-ROUTINE late_rows')
(5, 2, 0, 'CO-ROUTINE (subquery-3)')
(9, 5, 213, 'SCAN o USING COVERING INDEX ix_rewrite_customer_status')
(13, 5, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
(22, 5, 0, 'USE TEMP B-TREE FOR ORDER BY')
(38, 2, 196, 'SCAN (subquery-3)')
(92, 0, 196, 'SCAN late_rows')
(106, 0, 0, 'USE TEMP B-TREE FOR DISTINCT')
(107, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

Result rows: 400. First five (stable order):
| customer_id | name | late_orders |
| --- | --- | --- |
| 1 | Customer 1 | 30 |
| 6 | Customer 6 | 30 |
| 11 | Customer 11 | 30 |
| 16 | Customer 16 | 30 |
| 21 | Customer 21 | 30 |

### HAVING threshold
```sql
SELECT c.customer_id, c.name, COUNT(*) AS late_orders
FROM orders o JOIN customer c ON c.customer_id=o.customer_id
WHERE o.status='late'
GROUP BY c.customer_id, c.name
HAVING COUNT(*) >= 2
ORDER BY late_orders DESC, c.customer_id;
```

```text
(8, 0, 213, 'SCAN o USING COVERING INDEX ix_rewrite_customer_status')
(12, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
(15, 0, 0, 'USE TEMP B-TREE FOR GROUP BY')
(55, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

Result rows: 400. First five (stable order):
| customer_id | name | late_orders |
| --- | --- | --- |
| 1 | Customer 1 | 30 |
| 6 | Customer 6 | 30 |
| 11 | Customer 11 | 30 |
| 16 | Customer 16 | 30 |
| 21 | Customer 21 | 30 |

## Edge-case proof

- Fixture: customer 1 has two late orders and one shipped order; customer 2 only shipped orders; customer 3 no orders; customer 4 one late order.
- All three aligned reports return `(1, Two late, 2)` and `(4, One late, 1)`.
- Removing EXISTS from the correlated version returns customers 2 and 3 with count 0. That is useful for a different report, but not equivalent to this inner-join baseline.
- Before DISTINCT, the window result contains `(1,2)` twice and `(4,1)` once. Windows annotate rows; GROUP BY collapses groups.
- HAVING COUNT(*) >= 2 retains only customer 1 in the fixture. WHERE filters individual orders before aggregation; HAVING filters groups afterwards.
- All warehouse report rows match exactly, including order and multiplicities. The source warehouse is not modified.

## Algebra connection

The baseline selects late orders (sigma), joins customers (join), groups by customer and counts (gamma), then sorts (tau). HAVING adds a selection over the grouped result. Window functions use extended SQL semantics rather than ordinary set projection.

PASS equivalent warehouse results, two/one/zero late-order fixtures, row-preserving window example and HAVING threshold.
