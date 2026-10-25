# Task 1–2 — Measured warehouse query plans

SQLite 3.53.1; Python 3.14.8.
perf_counter; same process/connection; one untimed warmup; 3 batches; execute+fetch; ms/query
Index build cost is excluded; this measures warm query execution, not end-to-end deployment cost.
Fresh fixture in a temporary disk database; the existing warehouse.db is opened read-only and unchanged.

## Dashboard results

| city | distinct customers | revenue |
| --- | --- | --- |
| Bielefeld | 500 | 11242176.00 |
| Gütersloh | 500 | 8422344.00 |
| Münster | 500 | 5493504.00 |
| Paderborn | 500 | 2815656.00 |

## Benchmarks

| stage | query | samples ms/query | median ms/query | batch size |
| --- | --- | --- | --- | --- |
| baseline | dashboard | 148.8350, 157.0080, 166.2666 | 157.0080 | 1 |
| only ix_orders_ordered_on | dashboard | 164.6979, 161.0909, 168.5761 | 164.6979 | 1 |
| only ix_orderline_order | dashboard | 144.7543, 145.1798, 146.6074 | 145.1798 | 1 |
| only ix_orderline_product | dashboard | 141.2010, 140.1556, 148.4327 | 141.2010 | 1 |
| cumulative through ix_orders_ordered_on | dashboard | 141.0921, 145.9739, 155.2281 | 145.9739 | 1 |
| cumulative through ix_orderline_order | dashboard | 1640.4235, 1654.6662, 1734.7740 | 1654.6662 | 1 |
| cumulative through ix_orderline_product | dashboard | 1648.9737, 1682.8363, 1625.2575 | 1648.9737 | 1 |
| baseline | single day | 3.7769, 3.7856, 3.6604 | 3.7769 | 50 |
| date index | single day | 0.2569, 0.2539, 0.2527 | 0.2539 | 50 |
| date index | wrapped date | 8.6895, 8.5644, 8.6017 | 8.6017 | 10 |
| baseline | product lookup | 14.5023, 14.9353, 14.9635 | 14.9353 | 10 |
| product index | product lookup | 3.7131, 3.6836, 3.6300 | 3.6836 | 10 |

## Exact plans captured before timing

### baseline — dashboard
```text
(12, 0, 216, 'SCAN ol')
(14, 0, 45, 'SEARCH o USING INTEGER PRIMARY KEY (rowid=?)')
(21, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
(24, 0, 45, 'SEARCH p USING INTEGER PRIMARY KEY (rowid=?)')
(27, 0, 0, 'USE TEMP B-TREE FOR GROUP BY')
(76, 0, 0, 'USE TEMP B-TREE FOR count(DISTINCT)')
(79, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

### only ix_orders_ordered_on — dashboard
```text
(12, 0, 216, 'SCAN ol')
(14, 0, 45, 'SEARCH o USING INTEGER PRIMARY KEY (rowid=?)')
(21, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
(24, 0, 45, 'SEARCH p USING INTEGER PRIMARY KEY (rowid=?)')
(27, 0, 0, 'USE TEMP B-TREE FOR GROUP BY')
(76, 0, 0, 'USE TEMP B-TREE FOR count(DISTINCT)')
(79, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

### only ix_orderline_order — dashboard
```text
(12, 0, 216, 'SCAN ol')
(14, 0, 45, 'SEARCH o USING INTEGER PRIMARY KEY (rowid=?)')
(21, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
(24, 0, 45, 'SEARCH p USING INTEGER PRIMARY KEY (rowid=?)')
(27, 0, 0, 'USE TEMP B-TREE FOR GROUP BY')
(76, 0, 0, 'USE TEMP B-TREE FOR count(DISTINCT)')
(79, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

### only ix_orderline_product — dashboard
```text
(12, 0, 216, 'SCAN ol')
(14, 0, 45, 'SEARCH o USING INTEGER PRIMARY KEY (rowid=?)')
(21, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
(24, 0, 45, 'SEARCH p USING INTEGER PRIMARY KEY (rowid=?)')
(27, 0, 0, 'USE TEMP B-TREE FOR GROUP BY')
(76, 0, 0, 'USE TEMP B-TREE FOR count(DISTINCT)')
(79, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

### cumulative through ix_orders_ordered_on — dashboard
```text
(12, 0, 216, 'SCAN ol')
(14, 0, 45, 'SEARCH o USING INTEGER PRIMARY KEY (rowid=?)')
(21, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
(24, 0, 45, 'SEARCH p USING INTEGER PRIMARY KEY (rowid=?)')
(27, 0, 0, 'USE TEMP B-TREE FOR GROUP BY')
(76, 0, 0, 'USE TEMP B-TREE FOR count(DISTINCT)')
(79, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

### cumulative through ix_orderline_order — dashboard
```text
(14, 0, 165, 'SEARCH o USING INDEX ix_orders_ordered_on (ordered_on>? AND ordered_on<?)')
(20, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
(23, 0, 62, 'SEARCH ol USING INDEX ix_orderline_order (order_id=?)')
(28, 0, 45, 'SEARCH p USING INTEGER PRIMARY KEY (rowid=?)')
(31, 0, 0, 'USE TEMP B-TREE FOR GROUP BY')
(81, 0, 0, 'USE TEMP B-TREE FOR count(DISTINCT)')
(84, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

### cumulative through ix_orderline_product — dashboard
```text
(14, 0, 165, 'SEARCH o USING INDEX ix_orders_ordered_on (ordered_on>? AND ordered_on<?)')
(20, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
(23, 0, 62, 'SEARCH ol USING INDEX ix_orderline_order (order_id=?)')
(28, 0, 45, 'SEARCH p USING INTEGER PRIMARY KEY (rowid=?)')
(31, 0, 0, 'USE TEMP B-TREE FOR GROUP BY')
(81, 0, 0, 'USE TEMP B-TREE FOR count(DISTINCT)')
(84, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

### baseline — single day
```text
(3, 0, 216, 'SCAN o')
(7, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
```

### date index — single day
```text
(4, 0, 62, 'SEARCH o USING INDEX ix_orders_ordered_on (ordered_on=?)')
(9, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
```

### date index — wrapped date
```text
(3, 0, 216, 'SCAN o')
(8, 0, 45, 'SEARCH c USING INTEGER PRIMARY KEY (rowid=?)')
```

### baseline — product lookup
```text
(2, 0, 216, 'SCAN order_line')
```

### product index — product lookup
```text
(3, 0, 62, 'SEARCH order_line USING INDEX ix_orderline_product (product_id=?)')
```

## Plan and time changes relative to dashboard baseline

- only ix_orders_ordered_on: plan changed=False; median/baseline=1.049 (slower in this run).
- only ix_orderline_order: plan changed=False; median/baseline=0.925 (faster in this run).
- only ix_orderline_product: plan changed=False; median/baseline=0.899 (faster in this run).
- cumulative through ix_orders_ordered_on: plan changed=False; median/baseline=0.930 (faster in this run).
- cumulative through ix_orderline_order: plan changed=True; median/baseline=10.539 (slower in this run).
- cumulative through ix_orderline_product: plan changed=True; median/baseline=10.502 (slower in this run).

## Verification

- Independent Python aggregate agrees
- Year boundaries, DISTINCT, no-order fixture passed
- All benchmark results preserved
- Source warehouse file hash unchanged

Timings depend on the machine, cache and SQLite build. A changed plan proves a different strategy, not a universal speedup. No forced-index hints or disabled automatic indexes were used.
