# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.10,<4"]
# ///
"""Plot recorded trigger timings and refresh their report without benchmarking."""
import json
import math
import statistics
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'benchmark-results.json').read_text(encoding='utf-8'))
keys=['without_alarm_trigger','with_alarm_trigger']
rows=[data[k] for k in keys]
for row in rows:
    assert len(row['seconds'])==5 and all(v>=0 for v in row['seconds'])
    assert math.isclose(statistics.median(row['seconds']),row['median_seconds'],abs_tol=1e-12)
values=[r['median_seconds']*1000 for r in rows]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':'#e2e8f0',
    'axes.labelcolor':'#94a3b8','xtick.color':'#94a3b8','ytick.color':'#cbd5e1',
    'svg.fonttype':'none','svg.hashsalt':'Module04-Restyle'})
fig,ax=plt.subplots(figsize=(12,6.3)); fig.set_facecolor('#0b1420'); ax.set_facecolor('#101e2e')
fig.subplots_adjust(left=.27,right=.95,top=.70,bottom=.31)
fig.text(.055,.93,'MODULE 04 / RECORDED BENCHMARK',color='#5eead4',fontfamily='DejaVu Sans Mono',fontsize=10)
fig.text(.055,.85,'Alarm trigger: recorded insertion cost',fontsize=23,weight='bold')
fig.text(.055,.78,'10,000 readings per sample / 5 fresh disk databases per variant',color='#94a3b8',fontsize=11)
ax.barh([0,1],values,color=['#38bdf8','#2dd4bf'],height=.56,zorder=2)
for i,row in enumerate(rows):
    samples=[v*1000 for v in row['seconds']]
    ax.scatter(samples,[i-.16+j*.08 for j in range(5)],s=27,facecolor='#f1f5f9',edgecolor='#0b1420',linewidth=.7,zorder=3)
    ax.text(max(samples)+2,i,f'{values[i]:.4f} ms',va='center',fontsize=10)
ax.set_yticks([0,1],['Without alarm trigger','With alarm trigger'])
ax.invert_yaxis(); ax.set_xlim(0,max(max(r['seconds']) for r in rows)*1000*1.28)
ax.set_xlabel('INSERT + COMMIT time (ms per 10,000 readings)',labelpad=13)
ax.grid(axis='x',color='#334155',alpha=.5,linewidth=.6,zorder=0); ax.tick_params(length=0,pad=8)
for spine in ax.spines.values():spine.set_visible(False)
fig.text(.055,.195,'Bars: median. Dots: all five recorded samples. Linear scale starts at zero.',fontsize=10)
fig.text(.055,.13,'50% of inputs produce alarms when enabled. Audit trigger exists in both variants.',fontsize=10,color='#94a3b8')
fig.text(.055,.075,'Setup excluded; alternating run order. These local timings do not establish a universal trigger cost.',fontsize=10,color='#94a3b8')
out=HERE/'assets';out.mkdir(exist_ok=True)
fig.savefig(out/'trigger-benchmark.png',dpi=180,facecolor=fig.get_facecolor())
fig.savefig(out/'trigger-benchmark.svg',facecolor=fig.get_facecolor(),metadata={'Date':None})
svg=out/'trigger-benchmark.svg'
svg.write_text('\n'.join(s.rstrip() for s in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
plt.close(fig)
report='''![Module 04 - Data integrity and triggers](assets/module04-banner.svg)

<p align="center"><sub>DATABASES 2026 &nbsp; / &nbsp; MODULE 04 &nbsp; / &nbsp; MEASUREMENTS</sub></p>

<h1 align="center">Alarm Trigger: <em>Recorded Cost</em></h1>

<p align="center"><a href="README.md">Overview</a> &nbsp; · &nbsp; <a href="integrity-notes.md">Integrity notes</a> &nbsp; · &nbsp; <a href="benchmark-results.json">Raw measurements</a></p>

<a id="trigger-benchmark"></a>

<h2 align="center">◈ <code>01</code> / Measured insertion time</h2>

![Recorded insertion timing with and without the alarm trigger](assets/trigger-benchmark.png)

| Variant | Median (ms per 10,000 readings) | Five recorded samples (ms) |
| --- | ---: | --- |
'''
for label,row in zip(['Without alarm trigger','With alarm trigger'],rows):
    report+=f"| {label} | **{row['median_seconds']*1000:.4f}** | "+', '.join(f'{v*1000:.4f}' for v in row['seconds'])+' |\n'
report+='''
<h2 align="center">◈ <code>02</code> / Method and interpretation</h2>

'''+data['method']+'''

The **audit trigger exists in both variants** and does not fire on these INSERTs. With the alarm trigger enabled, each sample produces **5,000 alarm rows**. The measured difference therefore includes both trigger work and the extra alarm writes.

Bars show medians; dots show all five samples. Seconds from the JSON are multiplied by 1,000 to display milliseconds. The axis is linear and starts at zero.

*These are recorded local results for this workload, not a universal trigger overhead or a prediction for other machines.* No new measurements are created by this plotting script.

<details>
<summary>Recreate the chart</summary>

```sh
uv run --no-project --script Module04-Restyle/plot_benchmarks.py
```

After running `verify_module04.py`, rerun this script to refresh the chart and this report from the updated JSON.

</details>

---

<p align="center"><sub>MODULE 04 &nbsp; / &nbsp; DATA INTEGRITY</sub><br><a href="README.md">Module overview</a> &nbsp; · &nbsp; <a href="integrity-notes.md">Integrity notes</a></p>
'''
(HERE/'benchmark-results.md').write_text(report,encoding='utf-8')
print('PASS: two medians recomputed from all ten recorded samples; chart and report saved.')
