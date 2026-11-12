"""Build the Module 05 report, memo and visuals from the recorded evidence."""

import json
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
ASSETS.mkdir(exist_ok=True)
data = json.loads((HERE / "benchmark-results.json").read_text(encoding="utf-8"))
counts = data["counts"]
reads = data["reads"]
index = data["index_test"]
writes = data["writes"]
wide = data["wide_comparison"]
duck = data.get("duckdb")
size = data["storage"]

labels = [
    ("Normalized (3NF)", reads["normalized"]),
    ("Report with index", reads["indexed_report"]),
    ("Report without index", index["unindexed_report"]),
]

for _, measurement in labels:
    assert len(measurement["samples_ms"]) == 3
    assert statistics.median(measurement["samples_ms"]) == measurement["median_ms"]

plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": "#e2e8f0",
                    "axes.labelcolor": "#94a3b8", "xtick.color": "#94a3b8",
                    "ytick.color": "#e2e8f0", "font.size": 11})
fig, ax = plt.subplots(figsize=(12, 5.5), facecolor="#0b1420")
fig.subplots_adjust(left=.28, right=.96, top=.72, bottom=.26)
ax.set_facecolor("#101e2e")
fig.text(.055, .93, "MODULE 05 / RECORDED SQLITE BENCHMARK", color="#5eead4",
         fontfamily="DejaVu Sans Mono", fontsize=10)
fig.text(.055, .84, "Dashboard latency by schema and index", fontsize=22, weight="bold")
fig.text(.055, .77, f'{counts["flat_jobpart"]:,} source rows / 3 warm samples per variant',
         color="#94a3b8")
ax.barh(range(3), [m["median_ms"] for _, m in labels],
        color=["#38bdf8", "#2dd4bf", "#fbbf24"], height=.56, zorder=2)
maximum = max(max(m["samples_ms"]) for _, m in labels)
for row, (_, measurement) in enumerate(labels):
    samples = measurement["samples_ms"]
    ax.scatter(samples, [row-.13, row, row+.13], s=25, color="#f1f5f9",
               edgecolor="#0b1420", zorder=3)
    ax.text(max(samples) + maximum*.025, row, f'{measurement["median_ms"]:.2f} ms',
            va="center", fontsize=10)
ax.set_yticks(range(3), [name for name, _ in labels])
ax.invert_yaxis()
ax.set_xlim(0, maximum*1.28)
ax.set_xlabel("Elapsed time including result fetch (ms per query)", labelpad=10)
ax.tick_params(length=0, pad=8)
ax.grid(axis="x", color="#334155", linewidth=.7)
for spine in ax.spines.values():
    spine.set_visible(False)
fig.text(.055, .11, "Bars show medians. Dots show individual runs. The unindexed report was measured in a separate pass.", fontsize=9)
fig.savefig(ASSETS / "dashboard-benchmark.png", dpi=180)
plt.close(fig)

banner = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="380" viewBox="0 0 1200 380" role="img" aria-labelledby="title">
<title id="title">Module 05: Normalization and denormalization</title>
<defs>
  <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#081321"/><stop offset="1" stop-color="#102a3c"/></linearGradient>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#7dd3fc" stroke-opacity=".08"/></pattern>
</defs>
<rect width="1200" height="380" rx="18" fill="url(#bg)"/>
<rect width="1200" height="380" rx="18" fill="url(#grid)"/>
<rect x="48" y="48" width="4" height="284" rx="2" fill="#38bdf8"/>
<g font-family="Arial, sans-serif">
<text x="80" y="77" font-family="monospace" font-size="15" letter-spacing="4" fill="#67e8f9">HSBI / DATABASES 2026</text>
<text x="80" y="155" font-size="53" font-weight="700" fill="#f1f5f9">NORMALIZATION</text>
<text x="80" y="218" font-size="47" font-weight="700" fill="#5eead4">VS. DENORMALIZATION</text>
<text x="82" y="269" font-family="monospace" font-size="16" fill="#cbd5e1">SQLITE / 3NF / BENCHMARKS</text>
<text x="82" y="318" font-size="15" fill="#94a3b8">Asim Arman Erdogan · Module 05</text>
</g>
<g fill="#11283b" stroke="#38bdf8" stroke-width="2.5">
<path d="M980 153V181H886V211M980 181H1074V211" fill="none"/>
<rect x="906" y="100" width="148" height="53" rx="9"/>
<rect x="823" y="211" width="126" height="53" rx="9"/>
<rect x="1011" y="211" width="126" height="53" rx="9"/>
</g>
<g font-family="monospace" font-size="16" text-anchor="middle" fill="#67e8f9">
<text x="980" y="72">[ 05 ]</text><text x="980" y="133">FLAT</text>
<text x="886" y="244">3NF</text><text x="1074" y="244">REPORT</text>
</g>
</svg>
'''
(ASSETS / "module05-banner.svg").write_text(banner, encoding="utf-8")

diagram = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="512" viewBox="0 0 1200 512" role="img" aria-labelledby="title desc">
<title id="title">Flat relation and 3NF decomposition</title>
<desc id="desc">The flat job-part table on the left stores repeated facts. On the right, foreign keys connect job to machine, and job_part to job and part.</desc>
<rect width="1200" height="512" rx="16" fill="#0b1420"/>
<g fill="#101e2e" stroke="#31516a">
<rect x="35" y="103" width="420" height="322" rx="9"/>
<rect x="510" y="103" width="296" height="123" rx="9"/>
<rect x="866" y="103" width="296" height="123" rx="9"/>
<rect x="510" y="292" width="296" height="133" rx="9"/>
<rect x="866" y="292" width="296" height="133" rx="9"/>
</g>
<g fill="#38bdf8" stroke="#38bdf8" stroke-width="2">
<path d="M806 164H864m-8-6 8 6-8 6M657 292V228m-6 8 6-8 6 8M806 354H864m-8-6 8 6-8 6" fill="none"/>
</g>
<g font-family="Arial, sans-serif" fill="#f1f5f9">
<text x="35" y="50" font-size="27" font-weight="700">Flat relation</text>
<text x="510" y="50" font-size="27" font-weight="700">3NF decomposition</text>
<text x="35" y="78" font-size="17" fill="#94a3b8">One row per job and part</text>
<text x="510" y="78" font-size="17" fill="#94a3b8">Arrows point from foreign key to referenced key</text>
<g font-family="monospace" font-size="18" fill="#5eead4" font-weight="700">
<text x="54" y="137">flat_jobpart</text><text x="529" y="137">job</text><text x="885" y="137">machine</text>
<text x="529" y="327">job_part</text><text x="885" y="327">part</text>
</g>
<g font-size="17" fill="#cbd5e1">
<text x="54" y="177">{counts["flat_jobpart"]:,} rows</text>
<text x="54" y="217">Candidate key: job_id + part_no</text>
<text x="54" y="257">job_id → machine_id, technician, done_on</text>
<text x="54" y="297">machine_id → site</text>
<text x="54" y="337">part_no → part_price</text>
<text x="54" y="388" fill="#94a3b8">Site and catalog price repeat across job lines.</text>
<text x="529" y="169">{counts["job"]:,} rows · PK job_id</text><text x="529" y="200" font-size="15">FK machine_id · technician · done_on</text>
<text x="885" y="169">{counts["machine"]:,} rows · PK machine_id</text><text x="885" y="200">site</text>
<text x="529" y="360">{counts["job_part"]:,} rows · composite PK</text><text x="529" y="393">FK job_id + FK part_no</text>
<text x="885" y="360">{counts["part"]:,} rows · PK part_no</text><text x="885" y="393">part_price</text>
<text x="35" y="474" fill="#94a3b8">The 3NF join reproduces all {counts["flat_jobpart"]:,} source rows after converting text prices to numbers.</text>
</g>
</g>
</svg>
'''
(ASSETS / "schema-comparison.svg").write_text(diagram, encoding="utf-8")


def page(title, label):
    return f'''![Module 05 banner](assets/module05-banner.svg)

<p align="center"><sub>DATABASES 2026 &nbsp; / &nbsp; MODULE 05 &nbsp; / &nbsp; {label}</sub></p>
<h1 align="center">{title}</h1>
<p align="center"><a href="README.md">Overview</a> &nbsp; · &nbsp; <a href="normalization-notes.md">Design notes</a> &nbsp; · &nbsp; <a href="benchmark-results.md">Measurements</a> &nbsp; · &nbsp; <a href="recommendation.md">Memo</a></p>

'''


def median(measurement):
    return f'{measurement["median_ms"]:.4f}'


def samples(measurement):
    return ", ".join(f"{value:.4f}" for value in measurement["samples_ms"])


report = page("Normalization <em>Benchmark</em>", "MEASUREMENTS")
report += f'''<h2 align="center">◈ <code>03</code> / Verified build</h2>

| Table | Rows |
| --- | ---: |
'''
for name, count in counts.items():
    report += f'| {name} | {count:,} |\n'
report += f'''
The reconstructed rows matched the flat source, including multiplicities. Both dashboard queries returned **{data["result_rows"]:,} groups** and total parts cost **{data["total"]:,.2f}** for dates on or after 2026-03-01.

<h2 align="center">◈ <code>04</code> / Warm dashboard reads</h2>

![Dashboard latency, medians and individual measurements](assets/dashboard-benchmark.png)

Python {data["python"]}, SQLite {data["sqlite"]}, {data["cache_kib"]:,} KiB SQLite page cache. Each variant had one untimed warm-up before three timed runs. A and B alternated their starting order. Timings include fetching all rows. The index test is a separate paired pass after dropping the report index.

| Variant | Samples (ms) | Median (ms) |
| --- | --- | ---: |
'''
for label, measurement in labels:
    report += f'| {label} | {samples(measurement)} | **{median(measurement)}** |\n'
report += f'| 3NF control in the index pass | {samples(index["normalized"])} | {median(index["normalized"])} |\n'
report += '\n<a id="query-plans"></a>\n\n### Query plans\n'
for label, measurement in labels:
    report += f'\n**{label}**\n\n~~~text\n' + "\n".join(measurement["plan"]) + "\n~~~\n"
report += '''
The indexed report plan walks the machine index across the full report. The date predicate has no index in this fixture. Removing the machine index permits a direct table scan. All plans shown were captured on the same SQLite version.

<a id="write-and-storage-cost"></a>

<h2 align="center">◈ <code>05</code> / Write and storage cost</h2>

| Site update for cnc-02 | Rows changed | Statement samples (ms) | Median (ms) |
| --- | ---: | --- | ---: |
'''
for name, measurement in writes.items():
    report += f'| {name} | **{measurement["rows"]:,}** | {samples(measurement)} | {median(measurement)} |\n'
report += '\nThe indexed report and 3NF tables were updated in separate transactions and rolled back after timing. Timing covers the statement and excludes transaction start, commit and rollback.\n'
if size is not None:
    report += '\n| Objects | Table KiB | Index KiB | Total KiB |\n| --- | ---: | ---: | ---: |\n'
    for label, table_key, index_key in (
        ("3NF", "normalized_table_bytes", "normalized_index_bytes"),
        ("Indexed report", "report_table_bytes", "report_index_bytes"),
        ("Unindexed report", "report_table_bytes", None),
    ):
        table_bytes = size[table_key]
        index_bytes = size[index_key] if index_key else 0
        report += f'| {label} | {table_bytes/1024:,.0f} | {index_bytes/1024:,.0f} | {(table_bytes+index_bytes)/1024:,.0f} |\n'
    report += '\nSQLite dbstat measured allocated object pages. The flat seed, database metadata and freelist are outside these totals. Retaining both 3NF and the report adds the full report footprint to the transactional schema.\n'
else:
    report += '\nThis SQLite build does not expose dbstat, so storage figures are unavailable.\n'
report += f'''
### Wider SQLite comparison

The optional vendor and site dimensions produced **{wide["result_rows"]:,} matching groups** and total **{wide["total"]:,.2f}**. The six-table query took **{median(wide["reads"]["six_tables"])} ms** at the median. The wider report with no index took **{median(wide["reads"]["wide_report"])} ms**. The extra joins and added dimensions change the workload.

<a id="duckdb"></a>

### DuckDB stretch

'''
if duck:
    report += f'''DuckDB {duck["version"]} imported the same SQLite rows into native disk tables and ran with one worker thread. Both queries returned all {data["result_rows"]:,} expected groups. Import time is outside the measurements.

| DuckDB variant | Samples (ms) | Median (ms) |
| --- | --- | ---: |
| Normalized | {samples(duck["reads"]["normalized"])} | {median(duck["reads"]["normalized"])} |
| Report table | {samples(duck["reads"]["report"])} | {median(duck["reads"]["report"])} |

The 3NF query already runs within a 30-second refresh interval in this fixture. Compare against the actual dashboard latency target and freshness requirements before keeping a separate report.
'''
else:
    report += 'Run the benchmark with the DuckDB option to include this comparison.\n'
report += '\n[Raw samples, query plans and verification results](benchmark-results.json)\n'
(HERE / "benchmark-results.md").write_text(report, encoding="utf-8")

memo = page("Memo to the <em>Operations Lead</em>", "RECOMMENDATION")
memo += f'''Yasmin, I recommend serving the dashboard from the normalized query for this workload and keeping the transactional tables in **3NF**.
The [recorded benchmark](benchmark-results.md) measured **{median(reads["normalized"])} ms** for the normalized query, **{median(reads["indexed_report"])} ms** for the indexed report and **{median(index["unindexed_report"])} ms** for the unindexed report, with the same {data["result_rows"]} result groups.
The normalized query fits the lab's 30-second refresh interval, and a site change updates **{writes["machine"]["rows"]} row** in the source compared with **{writes["report_jobpart"]["rows"]:,} rows** in the report copy.
'''
if size is not None:
    memo += f'The unindexed report would add **{size["report_table_bytes"]/1024:,.0f} KiB** of allocated table pages alongside the 3NF data.\n'
memo += '''If production profiling shows that the join misses the latency target, test the unindexed report with a scheduled rebuild from the source tables.
Build and validate the replacement, then swap it into service in one transaction so readers get a complete snapshot.
Show the last successful refresh time and fall back to the normalized query if the snapshot exceeds the agreed freshness limit.
'''
(HERE / "recommendation.md").write_text(memo, encoding="utf-8")
print("Saved report, memo, chart and two SVGs.")
