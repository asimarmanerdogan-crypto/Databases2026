"""Apply the Module03 presentation without changing SQL or recorded query plans."""
import html
import re

LABELS={'README.md':'OVERVIEW','benchmark-results.md':'BENCHMARK RESULTS',
        'plan-safari-notes.md':'PLAN SAFARI','warehouse-notes.md':'QUERY VERIFICATION',
        'task-b.md':'RELATIONAL ALGEBRA','sql-notes.md':'STUDY NOTES',
        'query-rewrites.md':'QUERY REWRITES'}

def style_report(raw,name):
    raw=raw.replace('\u2014','-').replace('\u2013','-')
    first,body=raw.split('\n',1)
    title=first.lstrip('# ').strip()
    title=re.sub(r'^(Module 03 - |Tasks 1-4 - |Task 1-2 - )','',title)
    if name=='README.md':title='LLM-Assisted SQL and <em>Query Profiling</em>'
    else:title=html.escape(title)
    head=f'<p align="center"><sub>DATABASES 2026 &nbsp; / &nbsp; MODULE 03 &nbsp; / &nbsp; {LABELS[name]}</sub></p>\n\n<h1 align="center">{title}</h1>\n\n'
    if name=='README.md':
        head='![Module 03 - SQL and query profiling](assets/module03-banner.svg)\n\n'+head+'''<table align="center">
<tr>
<td align="center"><strong>60,000</strong><br><sub>ORDERS</sub></td>
<td align="center"><strong>240,000</strong><br><sub>ORDER LINES</sub></td>
<td align="center"><strong>12</strong><br><sub>MEASURED VARIANTS</sub></td>
<td align="center"><strong>3</strong><br><sub>SAMPLES PER VARIANT</sub></td>
</tr>
</table>

<p align="center"><a href="#learning-goals">Learning goals</a> &nbsp; · &nbsp; <a href="benchmark-results.md">Benchmarks</a> &nbsp; · &nbsp; <a href="plan-safari-notes.md">Query plans</a> &nbsp; · &nbsp; <a href="warehouse-notes.md">Verification</a></p>

**Creator:** Asim Arman Erdogan.

---

'''
    pieces=re.split(r'(```.*?```)',body,flags=re.S)
    counter=0
    def section(m):
        nonlocal counter
        counter+=1
        text=m[1].strip()
        anchor=re.sub(r'[^\w -]','',text.lower()).replace(' ','-')
        return f'<a id="{anchor}"></a>\n\n<h2 align="center">◈ <code>{counter:02}</code> / {html.escape(text)}</h2>'
    mappings={
      'Build complex DQL queries':'Build **complex DQL queries**',
      'Benchmark index effects':'Benchmark **index effects**',
      'with bound parameters.':'with **bound parameters**.',
      'Database files stay out of Git.':'Database files **stay out of Git**.',
      'Index build cost is excluded;':'**Index build cost is excluded**;',
      'No timing advantage is claimed.':'*No timing advantage is claimed.*',
      'This is booked order revenue;':'This is **booked order revenue**;',
      'The benchmark runs on a temporary copy':'The benchmark runs on a **temporary copy**',
      'A plan is a strategy, not a timing measurement or proof of a speedup.':'A plan is a **strategy**, not a timing measurement or proof of a speedup.',
      'No meaningful speedup is claimed.':'*No meaningful speedup is claimed.*',
      'Windows annotate rows; GROUP BY collapses groups.':'**Windows annotate rows; GROUP BY collapses groups.**',
      'Source records are unchanged.':'*Source records are unchanged.*',
    }
    for i in range(0,len(pieces),2):
        text=pieces[i]
        for old,new in mappings.items():text=text.replace(old,new)
        text=re.sub(r'^## (.+)$',section,text,flags=re.M)
        text=text.replace('SQLite 3.53.1; Python 3.14.10.','*Recorded environment: SQLite 3.53.1; Python 3.14.10.*')
        pieces[i]=text
    body=''.join(pieces).strip()
    if name=='README.md':
        body=body.replace('The technical work includes', '''![Query profiling workflow: SQL, plan, benchmark and verification](assets/query-workflow.svg)

[Recorded dashboard benchmark chart](benchmark-results.md#benchmark-charts) · [Warehouse model](warehouse-notes.md#warehouse-model).

The technical work includes''')
        body=body.replace('use the Module02 fixture first.','use the [Module02-Restyle fixture](../Module02-Restyle/legacy-setup.sql) first.')
        body+='''

<details>
<summary>Recreate the module visuals</summary>

```sh
uv run --no-project --script Module03-Restyle/render_visuals.py
uv run --no-project --script Module03-Restyle/plot_benchmarks.py
```

Charts use the recorded `benchmark-results.json`, not newly invented measurements. After rerunning the benchmark, rerun the chart script to update the graphics. The copied runners retain the presentation of regenerated reports and use the Module02-Restyle lab fixture.

</details>
'''
    elif name=='benchmark-results.md':
        visual='''<a id="benchmark-charts"></a>

![Recorded dashboard execution times for seven index configurations](assets/dashboard-benchmark.png)

*Bars show the median; dots show the three recorded samples. All values are milliseconds per query. Index construction time is excluded.*

![Recorded single-day, wrapped-date and product-lookup execution times](assets/lookup-benchmark.png)

*Each panel has its own scale starting at zero. These are observations from one recorded environment, not universal speedup claims.* [Recorded data](benchmark-results.json) · [Chart script](plot_benchmarks.py).

'''
        body=visual+body
    elif name=='warehouse-notes.md':
        body='''<a id="warehouse-model"></a>

![Warehouse tables and dashboard join columns; foreign keys are not declared by setup.sql](assets/warehouse-model.svg)

*The lines represent the dashboard's join conditions. They do not imply foreign-key enforcement in the original setup.*

'''+body
    elif name=='plan-safari-notes.md':
        body='''![Recorded query plans before and after the technician index](assets/plan-safari.svg)

*The visual summarizes the recorded plan comparison. SCAN and SEARCH describe access strategies, not elapsed times.*

'''+body
    footer='\n\n---\n\n<p align="center"><sub>MODULE 03 &nbsp; / &nbsp; SQL AND QUERY PROFILING</sub><br><a href="README.md">Module overview</a> &nbsp; · &nbsp; <a href="benchmark-results.md">Benchmarks</a> &nbsp; · &nbsp; <a href="../README.md">Portfolio</a></p>\n'
    return head+body+footer
