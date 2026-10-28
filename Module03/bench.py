"""Build an isolated warehouse fixture; profile before timing, verify every result."""
import hashlib
import json
import platform
import sqlite3
import statistics
import tempfile
from collections import defaultdict
from pathlib import Path
from time import perf_counter

here = Path(__file__).resolve().parent
dashboard = (here / "dashboard.sql").read_text(encoding="utf-8")
day = "SELECT o.order_id, o.ordered_on, c.name FROM orders o JOIN customer c ON c.customer_id=o.customer_id WHERE o.ordered_on='2026-02-14'"
wrapped = day.replace("o.ordered_on='", "date(o.ordered_on)='")
product = "SELECT order_id, product_id, qty FROM order_line WHERE product_id=42"
indexes = {
    "ix_orders_ordered_on": "CREATE INDEX ix_orders_ordered_on ON orders(ordered_on)",
    "ix_orderline_order": "CREATE INDEX ix_orderline_order ON order_line(order_id)",
    "ix_orderline_product": "CREATE INDEX ix_orderline_product ON order_line(product_id)",
}

# Save an explicit AI-assisted prediction before any plan execution in this run.
prediction = {
    "attribution": "AI-assisted predictions saved before checking the query plans",
    "baseline_dashboard": "SCAN ol; SEARCH o,c,p by primary key; temporary B-trees for grouping, distinct counting and ordering",
    "date_only": "May leave dashboard unchanged; single-day lookup should SEARCH the date index",
    "line_order": "May change join order and may be slower for this broad aggregate",
    "line_product": "Likely unused for dashboard but used for direct product filter",
    "wrapped_date": "Ordinary date index should not narrow date(ordered_on)",
}
(here / "plan-predictions.json").write_text(json.dumps(prediction, indent=2)+"\n", encoding="utf-8")


def independent(conn):
    customers = dict(conn.execute("SELECT customer_id, city FROM customer"))
    prices = dict(conn.execute("SELECT product_id, price FROM product"))
    orders = {i: (cid, dt) for i, cid, dt in conn.execute("SELECT order_id, customer_id, ordered_on FROM orders")}
    totals = defaultdict(float)
    people = defaultdict(set)
    for oid, pid, qty in conn.execute("SELECT order_id, product_id, qty FROM order_line"):
        cid, dt = orders[oid]
        if "2025-01-01" <= dt < "2026-01-01":
            city = customers[cid]
            totals[city] += qty * prices[pid]
            people[city].add(cid)
    return sorted([(city, len(people[city]), amount) for city, amount in totals.items()], key=lambda r: (-r[2], r[0]))


def canonical(rows):
    return sorted(rows)


source = here / "warehouse.db"
if not source.is_file():
    raise SystemExit("Run sqlite3 Module03/warehouse.db '.read Module03/setup.sql' first")
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
with sqlite3.connect(source.as_uri()+"?mode=ro", uri=True) as original:
    assert original.execute("PRAGMA integrity_check").fetchone() == ("ok",)
    counts = {t: original.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("customer","product","orders","order_line")}
    assert counts == dict(customer=2000, product=500, orders=60000, order_line=240000), counts
    reference = independent(original)
    assert canonical(original.execute(dashboard).fetchall()) == canonical(reference)

measurements = []
with tempfile.TemporaryDirectory(prefix="bench-", dir=here) as directory:
    conn = sqlite3.connect(str(Path(directory)/"warehouse.db"), cached_statements=0)
    conn.executescript((here/"setup.sql").read_text(encoding="utf-8-sig"))
    assert canonical(conn.execute(dashboard).fetchall()) == canonical(reference)
    baseline_results = {}

    def reset():
        for name in indexes:
            conn.execute(f"DROP INDEX IF EXISTS {name}")
        conn.commit()

    def measure(stage, query_name, query, batch=1):
        # Plan capture always precedes timing. Timings include execute + full fetch.
        plan = conn.execute("EXPLAIN QUERY PLAN " + query).fetchall()
        result = conn.execute(query).fetchall()  # untimed cache warmup
        baseline_results.setdefault(query_name, canonical(result))
        assert canonical(result) == baseline_results[query_name]
        samples = []
        for _ in range(3):
            start = perf_counter()
            for _ in range(batch):
                rows = conn.execute(query).fetchall()
            samples.append((perf_counter()-start)*1000/batch)
            assert canonical(rows) == baseline_results[query_name]
        entry = dict(stage=stage, query=query_name, sql=query, plan=plan,
                     samples_ms=samples, median_ms=statistics.median(samples),
                     batch=batch, rows=len(result))
        measurements.append(entry)
        return entry

    reset()
    base = measure("baseline", "dashboard", dashboard)
    # Isolated tests attribute each index to its own change from baseline.
    for name, ddl in indexes.items():
        reset()
        conn.execute(ddl)
        measure("only "+name, "dashboard", dashboard)
    # Also reproduce the course's cumulative sequence.
    reset()
    for name, ddl in indexes.items():
        conn.execute(ddl)
        measure("cumulative through "+name, "dashboard", dashboard)
    reset()
    measure("baseline", "single day", day, batch=50)
    conn.execute(indexes["ix_orders_ordered_on"])
    indexed_day = measure("date index", "single day", day, batch=50)
    assert any("SEARCH o USING INDEX ix_orders_ordered_on" in r[3] for r in indexed_day["plan"])
    negative = measure("date index", "wrapped date", wrapped, batch=10)
    assert baseline_results["wrapped date"] == baseline_results["single day"]
    assert not any("SEARCH o USING INDEX ix_orders_ordered_on" in r[3] for r in negative["plan"])
    reset()
    measure("baseline", "product lookup", product, batch=10)
    conn.execute(indexes["ix_orderline_product"])
    indexed_product = measure("product index", "product lookup", product, batch=10)
    assert any("SEARCH order_line USING INDEX ix_orderline_product" in r[3] for r in indexed_product["plan"])
    conn.close()

# Small fixture explicitly tests the year boundary, DISTINCT and missing orders.
fixture = sqlite3.connect(":memory:")
fixture.executescript("""
CREATE TABLE customer(customer_id INTEGER, name TEXT, city TEXT);
CREATE TABLE product(product_id INTEGER, price REAL);
CREATE TABLE orders(order_id INTEGER, customer_id INTEGER, ordered_on TEXT);
CREATE TABLE order_line(order_id INTEGER, product_id INTEGER, qty INTEGER);
INSERT INTO customer VALUES(1,'A','X'),(2,'No orders','X'),(3,'Only 2026','Y');
INSERT INTO product VALUES(1,10);
INSERT INTO orders VALUES(1,1,'2024-12-31'),(2,1,'2025-01-01'),(3,1,'2025-12-31'),(4,3,'2026-01-01');
INSERT INTO order_line VALUES(1,1,100),(2,1,2),(2,1,3),(3,1,4),(4,1,100);
""")
assert fixture.execute(dashboard).fetchall() == [("X",1,90.0)]
fixture.close()
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
output = dict(sqlite=sqlite3.sqlite_version, python=platform.python_version(),
              timer="perf_counter; same process/connection; one untimed warmup; 3 batches; execute+fetch; ms/query",
              counts=counts, dashboard_results=reference, measurements=measurements,
              checks=["Independent Python aggregate agrees", "Year boundaries, DISTINCT, no-order fixture passed",
                      "All benchmark results preserved", "Source warehouse file hash unchanged"])
(here/"benchmark-results.json").write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
report = ["# Task 1-2 - Measured warehouse query plans", "",
          f"SQLite {sqlite3.sqlite_version}; Python {platform.python_version()}.",
          output["timer"], "Index build cost is excluded; this measures warm query execution, not end-to-end deployment cost.",
          "Fresh fixture in a temporary disk database; the existing warehouse.db is opened read-only and unchanged.", "",
          "## Dashboard results", "", "| city | distinct customers | revenue |", "| --- | --- | --- |"]
report += [f"| {city} | {n} | {revenue:.2f} |" for city,n,revenue in reference]
report += ["", "## Benchmarks", "", "| stage | query | samples ms/query | median ms/query | batch size |", "| --- | --- | --- | --- | --- |"]
for m in measurements:
    report.append(f"| {m['stage']} | {m['query']} | {', '.join(f'{x:.4f}' for x in m['samples_ms'])} | {m['median_ms']:.4f} | {m['batch']} |")
report += ["", "## Exact plans captured before timing", ""]
for m in measurements:
    report += [f"### {m['stage']} - {m['query']}", "```text", *[repr(tuple(p)) for p in m["plan"]], "```", ""]
report += ["## Plan and time changes relative to dashboard baseline", ""]
for m in measurements:
    if m["query"] == "dashboard" and m is not base:
        changed = [r[3] for r in m["plan"]] != [r[3] for r in base["plan"]]
        ratio = m["median_ms"]/base["median_ms"]
        report.append(f"- {m['stage']}: plan changed={changed}; median/baseline={ratio:.3f} ({'slower' if ratio>1 else 'faster'} in this run).")
report += ["", "## Verification", "", *["- "+c for c in output["checks"]], "",
           "Timings depend on the machine, cache and SQLite build. A changed plan proves a different strategy, not a universal speedup. No forced-index hints or disabled automatic indexes were used."]
(here/"benchmark-results.md").write_text("\n".join(report)+"\n",encoding="utf-8")
print("PASS: independent results, boundary fixture, isolated/cumulative benchmarks and negative controls")
print(json.dumps(reference,ensure_ascii=False))
