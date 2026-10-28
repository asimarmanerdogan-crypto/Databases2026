"""Rebuild only the isolated course labs and regenerate their checked reports."""
from pathlib import Path
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def run(script):
    subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,check=True)

if __name__ == '__main__':
    versions = subprocess.run([sys.executable,str(ROOT/'Module01/uv-check.py')],cwd=ROOT,
                              check=True,capture_output=True,text=True)
    print(versions.stdout,end='')
    (ROOT/'Module01/uv-check-output.txt').write_text(versions.stdout,encoding='utf-8')
    run('Module01/generate_telemetry.py')
    run('Module01/load_telemetry.py')
    run('Module01/verify_telemetry.py')
    run('Module02/verify_module02.py')
    warehouse = ROOT/'Module03/warehouse.db'
    if warehouse.exists() and warehouse.read_bytes()[:16] != b'SQLite format 3\x00':
        raise SystemExit('warehouse.db is not SQLite; preserve/inspect the file before rebuilding')
    with sqlite3.connect(warehouse) as conn:
        conn.executescript((ROOT/'Module03/setup.sql').read_text(encoding='utf-8-sig'))
        counts = {table:conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                  for table in ('customer','product','orders','order_line')}
        assert counts == dict(customer=2000,product=500,orders=60000,order_line=240000)
        assert conn.execute('PRAGMA integrity_check').fetchone() == ('ok',)
    (ROOT/'Module03/warehouse-check.txt').write_text(
        '\n'.join(f'{table}: {count}' for table,count in counts.items())+'\nIntegrity check: ok\n',encoding='utf-8')
    for script in ('bench.py','injection_demo.py','verify_task_b.py','plan_safari.py','query_rewrites.py'):
        run('Module03/'+script)
    # Reproduce the covering-index and SQL-clause examples as well.
    with sqlite3.connect(':memory:') as conn:
        conn.executescript('CREATE TABLE t(a INTEGER,b TEXT); CREATE INDEX i ON t(a);')
        lines=[]
        for query, covering in [('SELECT a FROM t WHERE a=1',True),('SELECT a,b FROM t WHERE a=1',False)]:
            plan=conn.execute('EXPLAIN QUERY PLAN '+query).fetchall()
            assert any('COVERING' in row[3] for row in plan) == covering
            lines.extend([query,str(plan)])
        try:
            conn.execute('SELECT a,COUNT(*) FROM t WHERE COUNT(*)>1 GROUP BY a')
        except sqlite3.OperationalError as exc:
            lines.append('Aggregate in WHERE: '+str(exc))
        else:
            raise AssertionError('Aggregate in WHERE unexpectedly accepted')
        assert conn.execute("SELECT date('2025-01-01','+'||(540%540)||' days')").fetchone()[0]=='2025-01-01'
        lines.append('PASS covering/non-covering plans, aggregate WHERE error and setup date boundary')
    (ROOT/'Module03/concept-checks.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('PASS all technical exercises and checks')
