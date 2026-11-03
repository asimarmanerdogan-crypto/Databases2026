# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.10,<4"]
# ///
"""Plot the recorded benchmark JSON without running or replacing measurements."""
import json
import math
import statistics
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
DATA=json.loads((HERE/'benchmark-results.json').read_text(encoding='utf-8'))
ROWS=DATA['measurements']
assert len(ROWS)==12
for row in ROWS:
    assert len(row['samples_ms'])==3
    assert math.isclose(statistics.median(row['samples_ms']),row['median_ms'],abs_tol=1e-9)
    assert all(v>=0 for v in row['samples_ms'])
OUT=HERE/'assets'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
    'text.color':'#e2e8f0','axes.labelcolor':'#94a3b8',
    'xtick.color':'#94a3b8','ytick.color':'#cbd5e1',
    'svg.fonttype':'none','svg.hashsalt':'Module03-Restyle'})

def bars(ax,rows,labels,colors):
    ax.set_facecolor('#101e2e')
    values=[r['median_ms'] for r in rows]
    ax.barh(range(len(rows)),values,color=colors,height=.58,zorder=2)
    for i,row in enumerate(rows):
        # Small vertical offsets keep the three observed samples distinguishable.
        ax.scatter(row['samples_ms'],[i-.13,i,i+.13],s=19,facecolor='#f1f5f9',
                   edgecolor='#0b1420',linewidth=.65,zorder=3)
        ax.text(max(row['samples_ms'])+max(values)*.018,i,f"{values[i]:.4f} ms",va='center',fontsize=9)
    ax.set_yticks(range(len(rows)),labels)
    ax.invert_yaxis()
    ax.set_xlim(0,max(max(r['samples_ms']) for r in rows)*1.22)
    ax.set_xlabel('Execution time (ms per query)',labelpad=12)
    ax.grid(axis='x',color='#334155',alpha=.5,linewidth=.6,zorder=0)
    ax.tick_params(axis='both',length=0,pad=8)
    for s in ax.spines.values():s.set_visible(False)

def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=180,facecolor=fig.get_facecolor())
    path=OUT/(name+'.svg')
    fig.savefig(path,facecolor=fig.get_facecolor(),metadata={'Date':None})
    path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    plt.close(fig)

dashboard=[r for r in ROWS if r['query']=='dashboard']
assert [r['stage'] for r in dashboard]==['baseline','only ix_orders_ordered_on',
 'only ix_orderline_order','only ix_orderline_product',
 'cumulative through ix_orders_ordered_on','cumulative through ix_orderline_order',
 'cumulative through ix_orderline_product']
fig,ax=plt.subplots(figsize=(12,7.5))
fig.set_facecolor('#0b1420')
fig.subplots_adjust(left=.35,right=.95,top=.75,bottom=.20)
fig.text(.06,.94,'MODULE 03 / RECORDED BENCHMARK',color='#5eead4',fontsize=10,fontfamily='DejaVu Sans Mono')
fig.text(.06,.88,'Dashboard query: index configurations',fontsize=23,weight='bold')
fig.text(.06,.825,'60,000 orders / 240,000 order lines / 3 samples per variant',color='#94a3b8',fontsize=11)
bars(ax,dashboard,['Baseline','Date index only','Line-order index only','Line-product index only',
 'Cumulative: date','Cumulative: date + line order','Cumulative: date + line order + product'],
 ['#38bdf8']+['#2dd4bf']*4+['#fbbf24']*2)
fig.text(.06,.09,'Bars: median. Dots: recorded samples. Lower execution time is faster.',fontsize=10)
fig.text(.06,.045,f"Recorded SQLite {DATA['sqlite']} / Python {DATA['python']}. Warm query execution; index build cost excluded.",color='#94a3b8',fontsize=9)
save(fig,'dashboard-benchmark')

day=[r for r in ROWS if r['query'] in ('single day','wrapped date')]
product=[r for r in ROWS if r['query']=='product lookup']
assert [r['stage'] for r in day]==['baseline','date index','date index']
assert [r['stage'] for r in product]==['baseline','product index']
fig,axes=plt.subplots(2,1,figsize=(12,8.2))
fig.set_facecolor('#0b1420')
fig.subplots_adjust(left=.28,right=.95,top=.76,bottom=.18,hspace=.75)
fig.text(.06,.945,'MODULE 03 / RECORDED LOOKUP TESTS',color='#5eead4',fontsize=10,fontfamily='DejaVu Sans Mono')
fig.text(.06,.89,'Lookup queries and a negative control',fontsize=23,weight='bold')
fig.text(.06,.835,'Each panel uses its own linear scale starting at zero.',color='#94a3b8',fontsize=11)
bars(axes[0],day,['No added date index','Date index: direct equality','Date index: wrapped date()'],['#38bdf8','#2dd4bf','#fbbf24'])
axes[0].set_title('Single-day customer lookup',loc='left',fontsize=12,pad=12,weight='bold')
bars(axes[1],product,['No product index','With product index'],['#38bdf8','#2dd4bf'])
axes[1].set_title('Order lines for product 42',loc='left',fontsize=12,pad=12,weight='bold')
fig.text(.06,.075,'Bars: median. Dots: all 3 recorded samples. No new benchmark run was used.',fontsize=10)
fig.text(.06,.035,'Batch sizes: 50 direct-day, 10 wrapped-date, 10 product queries. Timings are per query.',color='#94a3b8',fontsize=9)
save(fig,'lookup-benchmark')
print('PASS: 12 recorded medians recalculated; all 36 sample values retained in the two chart figures.')
