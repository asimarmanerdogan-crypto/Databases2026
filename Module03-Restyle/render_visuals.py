"""Rebuild static module diagrams after checking the local SQL and recorded data."""
import html
import json
import sqlite3
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE/'assets';OUT.mkdir(exist_ok=True)
db=sqlite3.connect(':memory:')
db.executescript((HERE/'setup.sql').read_text(encoding='utf-8-sig'))
counts={t:db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('customer','product','orders','order_line')}
data=json.loads((HERE/'benchmark-results.json').read_text(encoding='utf-8'))
assert counts==data['counts']
assert db.execute((HERE/'dashboard.sql').read_text(encoding='utf-8')).fetchall()==[tuple(r) for r in data['dashboard_results']]
for table in counts:assert not db.execute(f'PRAGMA foreign_key_list({table})').fetchall()

def start(height,title,subtitle):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',
 f'<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(subtitle)}</desc>',
 f'<rect width="1200" height="{height}" rx="16" fill="#0b1420"/>',
 f'<text x="40" y="44" fill="#f1f5f9" font-family="Arial,sans-serif" font-size="27" font-weight="700">{html.escape(title)}</text>',
 f'<text x="40" y="75" fill="#94a3b8" font-family="Arial,sans-serif" font-size="16">{html.escape(subtitle)}</text>']
def text(p,x,y,s,size=18,color='#cbd5e1',bold=False):
 p.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,sans-serif" font-size="{size}"'+(' font-weight="700"' if bold else '')+'>'+html.escape(s)+'</text>')
def card(p,x,y,w,h):p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#101e2e" stroke="#31516a"/>')
def save(name,p):
 p.append('</svg>');(OUT/name).write_text('\n'.join(p)+'\n',encoding='utf-8')

p=start(300,'Query profiling workflow','The same result is checked before interpreting execution time.')
for i,(title,desc) in enumerate([('01 / SQL','Define the result'),('02 / PLAN','Read SCAN / SEARCH'),('03 / MEASURE','Warm up + 3 batches'),('04 / VERIFY','Check rows + edge cases')]):
 x=30+i*295;card(p,x,120,255,115)
 text(p,x+18,154,title,17,'#5eead4',True);text(p,x+18,198,desc,16)
 if i<3:p.append(f'<path d="M{x+265} 178h19m-7-7 7 7-7 7" fill="none" stroke="#38bdf8" stroke-width="2"/>')
save('query-workflow.svg',p)

p=start(770,'Warehouse tables used by the dashboard','Join columns from dashboard.sql. setup.sql does not declare foreign keys.')
for path in ['M510 225H690','M915 330V450','M510 555H690']:
 p.append(f'<path d="{path}" fill="none" stroke="#38bdf8" stroke-width="2"/>')
text(p,550,210,'customer_id',14,'#5eead4');text(p,930,400,'order_id',14,'#5eead4');text(p,550,540,'product_id',14,'#5eead4')
models=[('customer',60,120,['customer_id (PRIMARY KEY)','name','city']),
 ('orders',690,120,['order_id (PRIMARY KEY)','customer_id','ordered_on','status']),
 ('product',60,450,['product_id (PRIMARY KEY)','sku','price']),
 ('order_line',690,450,['order_id','product_id','qty'])]
for table,x,y,fields in models:
 card(p,x,y,450,220)
 text(p,x+22,y+34,table.upper(),20,'#5eead4',True)
 text(p,x+310,y+34,f'{counts[table]:,} rows',16,'#94a3b8')
 for j,f in enumerate(fields):text(p,x+22,y+74+31*j,f,18)
text(p,40,730,'Logical joins are verified against the SQL query; a join diagram alone does not enforce referential integrity.',16)
save('warehouse-model.svg',p)

notes=(HERE/'plan-safari-notes.md').read_text(encoding='utf-8')
assert 'SEARCH maint_job USING INDEX ix_job_tech' in notes
assert "LIKE '%ei%'" in notes
p=start(500,'Recorded plan safari: technician index','Plans are access strategies. This four-row fixture does not establish a meaningful speedup.')
labels=[('Technician equality','technician = Beier','SCAN','SEARCH'),
 ('Different table','machine_name filter','SCAN','SCAN'),
 ('Leading wildcard',"technician LIKE '%ei%'",'SCAN','SCAN')]
for i,(title,description,before,after) in enumerate(labels):
 y=115+i*105;card(p,40,y,1120,88)
 text(p,62,y+30,title,18,'#e2e8f0',True);text(p,62,y+61,description,16)
 text(p,635,y+48,before,20,'#94a3b8',True)
 p.append(f'<path d="M775 {y+40}h65m-10-9 10 9-10 9" fill="none" stroke="#38bdf8" stroke-width="2"/>')
 text(p,910,y+48,after,20,'#5eead4' if after=='SEARCH' else '#94a3b8',True)
text(p,40,465,'The ordinary technician index also does not narrow LOWER(technician) in the recorded negative test.',16)
save('plan-safari.svg',p)
db.close()
print('PASS: warehouse counts, city aggregates, join columns and recorded plan comparison; saved three SVGs.')
