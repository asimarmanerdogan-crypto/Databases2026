"""Compare equivalent late-order reports; expose zero-count and window semantics."""
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUERIES = {
    'Grouped report': '''SELECT c.customer_id, c.name, COUNT(*) AS late_orders
FROM orders o JOIN customer c ON c.customer_id=o.customer_id
WHERE o.status='late'
GROUP BY c.customer_id, c.name
ORDER BY late_orders DESC, c.customer_id''',
    'Correlated subquery': '''SELECT c.customer_id, c.name,
       (SELECT COUNT(*) FROM orders o
        WHERE o.customer_id=c.customer_id AND o.status='late') AS late_orders
FROM customer c
WHERE EXISTS (SELECT 1 FROM orders o
              WHERE o.customer_id=c.customer_id AND o.status='late')
ORDER BY late_orders DESC, c.customer_id''',
    'Window rewrite': '''WITH late_rows AS (
    SELECT c.customer_id, c.name,
           COUNT(*) OVER (PARTITION BY c.customer_id) AS late_orders
    FROM orders o JOIN customer c ON c.customer_id=o.customer_id
    WHERE o.status='late'
)
SELECT DISTINCT customer_id, name, late_orders
FROM late_rows
ORDER BY late_orders DESC, customer_id''',
    'HAVING threshold': '''SELECT c.customer_id, c.name, COUNT(*) AS late_orders
FROM orders o JOIN customer c ON c.customer_id=o.customer_id
WHERE o.status='late'
GROUP BY c.customer_id, c.name
HAVING COUNT(*) >= 2
ORDER BY late_orders DESC, c.customer_id''',
}

def results(conn):
    rows = {name: conn.execute(sql).fetchall() for name, sql in QUERIES.items()}
    assert rows['Grouped report'] == rows['Correlated subquery'] == rows['Window rewrite']
    assert rows['HAVING threshold'] == [row for row in rows['Grouped report'] if row[2] >= 2]
    return rows

if __name__ == '__main__':
    path = HERE/'warehouse.db'
    if not path.exists():
        raise SystemExit('Run uv run python reproduce.py from the repository root first')
    conn = sqlite3.connect(path.as_uri()+'?mode=ro', uri=True)
    # Query-specific index prevents a correlated full-table scan for each customer.
    # A memory backup leaves the source warehouse unchanged.
    lab = sqlite3.connect(':memory:')
    conn.backup(lab); conn.close()
    lab.execute('CREATE INDEX IF NOT EXISTS ix_rewrite_customer_status ON orders(customer_id,status)')
    observed = results(lab)
    fixture = sqlite3.connect(':memory:')
    fixture.executescript('''CREATE TABLE customer(customer_id INTEGER PRIMARY KEY,name TEXT);
CREATE TABLE orders(order_id INTEGER PRIMARY KEY,customer_id INTEGER,status TEXT);
INSERT INTO customer VALUES(1,'Two late'),(2,'Only shipped'),(3,'No orders'),(4,'One late');
INSERT INTO orders VALUES(1,1,'late'),(2,1,'late'),(3,1,'shipped'),(4,2,'shipped'),(5,4,'late');''')
    edge = results(fixture)
    assert edge['Grouped report'] == [(1,'Two late',2),(4,'One late',1)]
    assert edge['HAVING threshold'] == [(1,'Two late',2)]
    all_customers = fixture.execute('''SELECT c.customer_id,
      (SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.customer_id AND o.status='late')
      FROM customer c ORDER BY c.customer_id''').fetchall()
    assert all_customers == [(1,2),(2,0),(3,0),(4,1)]
    raw_window = fixture.execute('''SELECT customer_id,COUNT(*) OVER(PARTITION BY customer_id)
      FROM orders WHERE status='late' ORDER BY customer_id''').fetchall()
    assert raw_window == [(1,2),(1,2),(4,1)]
    out = ['# Query rewrites - subqueries, windows and HAVING', '',
           'These query rewrites were prepared and checked with AI assistance.',
           f'SQLite {sqlite3.sqlite_version}. Reproduce: `uv run python Module03/query_rewrites.py`.', '',
           '## Query and plan comparison', '',
           'The course report is the grouped baseline. The rewrites were prepared with AI assistance. '
           'For this report, GROUP BY is the clearest form. The correlated form repeats an indexed count '
           'per customer and uses EXISTS to retain exactly the customers present in the original inner join. '
           'The window form preserves each late-order row; DISTINCT reduces repeated customer/count pairs '
           'to one row per customer. No timing advantage is claimed.', '',
           'A query-specific `(customer_id,status)` index is added only to an in-memory backup. '
           'It covers the count/EXISTS predicates; a different index/workload can produce different plans.', '']
    for name, sql in QUERIES.items():
        rows = observed[name]
        out += [f'### {name}', '```sql', sql+';', '```', '',
                '```text', *[str(row) for row in lab.execute('EXPLAIN QUERY PLAN '+sql)], '```', '',
                f'Result rows: {len(rows)}. First five (stable order):',
                '| customer_id | name | late_orders |','| --- | --- | --- |',
                *[f'| {cid} | {name} | {count} |' for cid,name,count in rows[:5]], '']
    out += ['## Edge-case proof', '',
            '- Fixture: customer 1 has two late orders and one shipped order; customer 2 only shipped orders; customer 3 no orders; customer 4 one late order.',
            '- All three aligned reports return `(1, Two late, 2)` and `(4, One late, 1)`.',
            '- Removing EXISTS from the correlated version returns customers 2 and 3 with count 0. That is useful for a different report, but not equivalent to this inner-join baseline.',
            '- Before DISTINCT, the window result contains `(1,2)` twice and `(4,1)` once. Windows annotate rows; GROUP BY collapses groups.',
            '- HAVING COUNT(*) >= 2 retains only customer 1 in the fixture. WHERE filters individual orders before aggregation; HAVING filters groups afterwards.',
            '- All warehouse report rows match exactly, including order and multiplicities. The source warehouse is not modified.', '',
            '## Algebra connection', '',
            'The baseline selects late orders (sigma), joins customers (join), groups by customer and counts (gamma), then sorts (tau). '
            'HAVING adds a selection over the grouped result. Window functions use extended SQL semantics rather than ordinary set projection.', '',
            'PASS equivalent warehouse results, two/one/zero late-order fixtures, row-preserving window example and HAVING threshold.']
    (HERE/'query-rewrites.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
    fixture.close(); lab.close()
    print('PASS query rewrites, zero-count domain, window multiplicity and HAVING')
