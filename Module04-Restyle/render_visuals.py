"""Rebuild diagrams after checking the copied SQL in an isolated database."""
import html
import sqlite3
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE/'assets'; OUT.mkdir(exist_ok=True)
db=sqlite3.connect(':memory:')
db.executescript((HERE/'setup.sql').read_text(encoding='utf-8'))
db.executescript((HERE/'triggers.sql').read_text(encoding='utf-8'))
assert db.execute('PRAGMA foreign_keys').fetchone()[0]==1
assert len(db.execute("SELECT name FROM sqlite_master WHERE type='trigger'").fetchall())==2
db.execute("INSERT INTO sensor VALUES(1,'cnc-01','vib_rms','mm/s')")
db.execute("INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES(1,'test',2.7,1)")
assert db.execute('SELECT value FROM alarm').fetchall()==[(2.7,)]
db.execute('UPDATE reading SET value=1.4')
assert db.execute('SELECT old_value,new_value FROM audit').fetchall()==[(2.7,1.4)]
db.execute('UPDATE reading SET value=2.9')
assert db.execute('SELECT COUNT(*) FROM alarm').fetchone()[0]==1
assert db.execute('SELECT energy_j FROM reading').fetchone()[0]==2.9
db.close()

def start(height,title,subtitle):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',
      f'<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(subtitle)}</desc>',
      f'<rect width="1200" height="{height}" rx="16" fill="#0b1420"/>',
      f'<text x="40" y="45" fill="#f1f5f9" font-family="Arial,sans-serif" font-size="27" font-weight="700">{html.escape(title)}</text>',
      f'<text x="40" y="78" fill="#94a3b8" font-family="Arial,sans-serif" font-size="16">{html.escape(subtitle)}</text>']

def text(p,x,y,s,size=18,color='#cbd5e1',bold=False):
    p.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,sans-serif" font-size="{size}"'+(' font-weight="700"' if bold else '')+'>'+html.escape(s)+'</text>')
def card(p,x,y,w,h):p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#101e2e" stroke="#31516a"/>')
def save(name,p):
    p.append('</svg>'); (OUT/name).write_text('\n'.join(p)+'\n',encoding='utf-8')

p=start(405,'Three layers of data integrity','Rules from setup.sql and rejected examples from verification.txt.')
for i,(name,rule,example,extra) in enumerate([
 ('ENTITY','PRIMARY KEY + UNIQUE','Duplicate identity rejected','machine_id + metric is unique'),
 ('REFERENTIAL','FOREIGN KEY','Missing sensor 99 rejected','PRAGMA foreign_keys = ON'),
 ('DOMAIN','NOT NULL + CHECK + STRICT','9000 and hot rejected','Allowed range, required fields, types')]):
    x=35+i*390; card(p,x,115,365,210)
    text(p,x+20,150,f'0{i+1} / {name}',19,'#5eead4',True)
    text(p,x+20,192,rule,17,'#f1f5f9',True)
    text(p,x+20,238,example,17)
    text(p,x+20,285,extra,15,'#94a3b8')
text(p,40,370,'CHECK alone can accept NULL. STRICT can convert lossless numeric text such as 42.0.',17)
save('integrity-layers.svg',p)

p=start(635,'Alarm and audit: two different events','Verified against triggers.sql in a fresh in-memory database.')
rows=[(120,'INSERT reading','metric = vib_rms AND value > 2.0','ALARM','Example: insert 2.7 -> alarm 2.7'),
      (290,'UPDATE OF value','Runs even if the value stays equal','AUDIT','Example: 2.7 -> 1.4 records both')]
for y,event,condition,result,example in rows:
    card(p,40,y,330,125);card(p,430,y,365,125);card(p,855,y,305,125)
    text(p,60,y+40,event,21,'#5eead4',True)
    text(p,60,y+83,'AFTER / FOR EACH ROW',16)
    text(p,450,y+39,'Trigger condition',18,'#f1f5f9',True)
    text(p,450,y+83,condition,16)
    text(p,875,y+40,result,21,'#38bdf8',True)
    # The example is placed below the cards to keep its text readable.
    text(p,40,y+153,example,17)
    for x in (380,805):p.append(f'<path d="M{x} {y+62}h40m-8-7 8 7-8 7" fill="none" stroke="#38bdf8" stroke-width="2"/>')
text(p,40,505,'UPDATE above 2.0 does not create an alarm: the alarm trigger handles INSERT only.',18,'#fbbf24')
text(p,40,547,'The statement and its trigger effects roll back together if the statement fails.',18)
text(p,40,589,'Audit rows remain editable by a writer. Recording a change does not make history immutable.',17,'#94a3b8')
save('trigger-flow.svg',p)
print('PASS: two triggers, foreign-key setting, alarm condition, audit values and INSERT-only limitation.')
