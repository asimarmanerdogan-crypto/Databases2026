"""Rebuild the two overview visuals from the local legacy fixture and contract DDL.

Run from the repository root:
    uv run --no-project --script Module02-Restyle/render_visuals.py
"""
import html
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'assets'
OUT.mkdir(exist_ok=True)
legacy = sqlite3.connect(':memory:')
legacy.executescript((HERE/'legacy-setup.sql').read_text(encoding='utf-8-sig'))
target = sqlite3.connect(':memory:')
target.executescript((HERE/'contract-ddl.sql').read_text(encoding='utf-8-sig'))
names=lambda c:[r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
assert names(legacy)==['machine','maint_job','part']
assert names(target)==['job_part','machine','maint_job','part','technician']
assert legacy.execute('SELECT COUNT(*) FROM maint_job').fetchone()[0]==4
for table in names(legacy):
    assert not legacy.execute(f'PRAGMA foreign_key_list({table})').fetchall()
    assert not any(r[5] for r in legacy.execute(f'PRAGMA table_info({table})'))
target_fks=sum(len(target.execute(f'PRAGMA foreign_key_list({t})').fetchall()) for t in names(target))
assert target_fks==4
assert legacy.execute('SELECT job_id FROM maint_job WHERE machine_name NOT IN (SELECT machine_name FROM machine)').fetchall()==[(3,)]
assert legacy.execute('SELECT part_no,COUNT(*) FROM part GROUP BY part_no HAVING COUNT(*)>1').fetchall()==[('P-1003',2)]
assert legacy.execute("SELECT COUNT(*) FROM part WHERE unit_price < '15'").fetchone()[0]==1
assert legacy.execute('SELECT COUNT(*) FROM part WHERE CAST(unit_price AS NUMERIC) < 15').fetchone()[0]==3
assert legacy.execute("SELECT machine_name FROM machine WHERE installed='unknown'").fetchall()==[('RANDOM-NAME',)]
assert legacy.execute('SELECT j.job_id FROM maint_job j JOIN part p ON p.part_no=j.parts_used ORDER BY j.job_id').fetchall()==[(2,),(2,),(3,)]

def start(height,title,subtitle):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',
    f'<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(subtitle)}</desc>',
    f'<rect width="1200" height="{height}" rx="16" fill="#0b1420"/>',
    f'<text x="40" y="45" fill="#f1f5f9" font-family="Arial,sans-serif" font-size="28" font-weight="700">{html.escape(title)}</text>',
    f'<text x="40" y="76" fill="#94a3b8" font-family="Arial,sans-serif" font-size="16">{html.escape(subtitle)}</text>']
def text(parts,x,y,value,color='#cbd5e1',size=18,bold=False):
    parts.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,sans-serif" font-size="{size}"'+(' font-weight="700"' if bold else '')+'>'+html.escape(value)+'</text>')
def box(parts,x,y,w,h):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#101e2e" stroke="#31516a"/>')

p=start(480,'Legacy fixture and corrected target','Schema comparison derived from legacy-setup.sql and contract-ddl.sql.')
box(p,40,110,500,300);box(p,660,110,500,300)
text(p,65,150,'LEGACY FIXTURE','#fbbf24',19,True)
text(p,685,150,'CORRECTED TARGET','#5eead4',19,True)
for i,line in enumerate(['3 tables: machine, part, maint_job','No primary keys or foreign keys','Technician stored as a name','Part references stored as comma-separated text','Invalid legacy rows retained for the audit']):
    text(p,65,195+i*39,line,size=17)
for i,line in enumerate(['5 entities, including technician and job_part','Primary keys, unique keys and 4 foreign keys','Technician identity stored as technician_id','One row per job/part association','Application validation + database constraints']):
    text(p,685,195+i*39,line,size=17)
p.append('<path d="M555 255h90m-12-10 12 10-12 10" stroke="#38bdf8" stroke-width="3" fill="none"/>')
text(p,40,450,'Target design only. Orphans, duplicate identities and unknown dates require migration decisions.',size=17)
p.append('</svg>');(OUT/'schema-comparison.svg').write_text('\n'.join(p)+'\n',encoding='utf-8')

p=start(690,'Five integrity defect categories','Examples and query outcomes verified directly against the legacy fixture.')
cards=[
 ('01 / ORPHAN REFERENCE','Job 3 points to cnc-05','No matching machine row exists.'),
 ('02 / DUPLICATE IDENTITY','P-1003 appears twice','A part number does not identify one row.'),
 ('03 / TEXT PRICE COMPARISON',"Text < '15': 1 row",'Numeric < 15: 3 rows, including duplicates.'),
 ('04 / UNKNOWN DATE','RANDOM-NAME: installed = unknown','The format check flags this record.'),
 ('05 / LIST-BASED JOIN','Naive join returns job IDs: 2, 2, 3','Multipart job 1 is lost; job 2 is duplicated.'),
 ]
for i,(heading,line1,line2) in enumerate(cards):
    x=40+(i%2)*580;y=110+(i//2)*175
    box(p,x,y,540,145)
    text(p,x+22,y+35,heading,'#5eead4',17,True)
    text(p,x+22,y+76,line1,'#f1f5f9',19,True)
    text(p,x+22,y+110,line2,size=16)
text(p,40,665,'Counts describe this deliberately flawed fixture; the original SQL and full results remain below.',size=16)
p.append('</svg>');(OUT/'integrity-defects.svg').write_text('\n'.join(p)+'\n',encoding='utf-8')
legacy.close();target.close()
print('PASS: schema counts, four target foreign keys and all five defect categories; saved two SVG summaries.')
