"""Reproduce Module04 evidence in isolated databases; never touch earlier modules.

Existing edge.db is preserved. Repeated verification uses a temporary database.
"""
import json
import os
import platform
import sqlite3
import statistics
import tempfile
import time
from pathlib import Path
from ingest import ingest

HERE = Path(__file__).resolve().parent
SCRATCH = HERE / '.scratch'
SCRATCH.mkdir(exist_ok=True)
log = [f'Python: {platform.python_version()}; SQLite: {sqlite3.sqlite_version}']

def sqlfile(name):
    return (HERE / name).read_text(encoding='utf-8')

def reject(conn, sql, layer, parameters=()):
    log.append(f'\n[{layer}] {sql} parameters={parameters!r}')
    try:
        conn.execute(sql, parameters)
    except sqlite3.DatabaseError as exc:
        log.append(f'{type(exc).__name__}: {exc}')
    else:
        raise AssertionError(f'Expected rejection: {sql}')

def fresh(path=':memory:'):
    c = sqlite3.connect(path)
    c.executescript(sqlfile('setup.sql'))
    c.execute("INSERT INTO sensor VALUES(1,'cnc-01','temp_c','degC'),(2,'cnc-01','vib_rms','mm/s')")
    c.commit()
    return c

def study():
    c = sqlite3.connect(':memory:')
    c.execute('CREATE TABLE t(sensor_id INTEGER,metric TEXT,value REAL)')
    examples = [(1,'temp_c',9000),(1,'temp_c','hot'),(2,'bogus',-500),(None,None,None)]
    c.executemany('INSERT INTO t VALUES(?,?,?)', examples)
    log.append('\nTask A: unconstrained rows: '+repr(c.execute('SELECT * FROM t').fetchall()))
    c.execute("CREATE TABLE guarded(sensor_id INTEGER PRIMARY KEY, metric TEXT NOT NULL CHECK(metric IN ('temp_c','vib_rms','spindle_load')),value REAL NOT NULL CHECK(value BETWEEN -273.15 AND 5000)) STRICT")
    for row, layer in zip(examples[:3], ['Domain CHECK','STRICT typing','Metric domain CHECK']):
        reject(c,'INSERT INTO guarded VALUES(?,?,?)',layer,row)
    c.execute("INSERT INTO guarded VALUES(1,'temp_c',41.5)")
    reject(c,"INSERT INTO guarded VALUES(1,'temp_c',42)",'Entity PRIMARY KEY')
    reject(c,"INSERT INTO guarded VALUES(2,'temp_c',NULL)",'NOT NULL')
    c.execute('CREATE TABLE nullable(v REAL CHECK(v>0)) STRICT')
    c.execute('INSERT INTO nullable VALUES(NULL)')
    assert c.execute('SELECT v IS NULL FROM nullable').fetchone()[0] == 1
    log.append('CHECK(v>0) accepted NULL; NOT NULL is a separate requirement.')
    c.execute("INSERT INTO guarded VALUES(NULL,'temp_c','42.0')")
    log.append('INTEGER PRIMARY KEY NULL auto-assigned an ID; STRICT converted numeric text to REAL: '+repr(c.execute('SELECT *,typeof(value) FROM guarded').fetchall()))
    # A foreign-key claim must be checked with two independent connections.
    for enabled in (False, True):
        x=sqlite3.connect(':memory:')
        x.executescript('CREATE TABLE p(id INTEGER PRIMARY KEY); CREATE TABLE ch(id INTEGER REFERENCES p(id));')
        x.execute(f'PRAGMA foreign_keys={int(enabled)}')
        if enabled:
            reject(x,'INSERT INTO ch VALUES(99)','Foreign keys ON')
        else:
            x.execute('INSERT INTO ch VALUES(99)')
            assert x.execute('PRAGMA foreign_key_check').fetchall()
            log.append('Explicit foreign_keys=OFF allowed an orphan; foreign_key_check found it.')
        x.close()
    c.close()

def benchmark():
    samples={False:[], True:[]}
    for repetition in range(5):
        for enabled in ((False,True) if repetition%2==0 else (True,False)):
            with tempfile.TemporaryDirectory(prefix='bench-', dir=SCRATCH) as folder:
                c=fresh(Path(folder)/'bench.db')
                c.executescript(sqlfile('triggers.sql'))
                if not enabled:
                    c.execute('DROP TRIGGER trg_vib_alarm')
                rows=[(2,f'benchmark-{i:05}',2.7 if i%2 else 1.4,1) for i in range(10000)]
                start=time.perf_counter()
                with c:
                    c.executemany('INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES(?,?,?,?)',rows)
                samples[enabled].append(time.perf_counter()-start)
                assert c.execute('SELECT COUNT(*) FROM reading').fetchone()[0]==10000
                assert c.execute('SELECT COUNT(*) FROM alarm').fetchone()[0]==(5000 if enabled else 0)
                c.close()
    result={('with_alarm_trigger' if k else 'without_alarm_trigger'):{'seconds':v,'median_seconds':statistics.median(v)} for k,v in samples.items()}
    result['method']='Five disk-backed fresh databases per variant; alternating order; 10,000 rows; 50% alarm-producing; timing includes INSERT and COMMIT, excludes setup.'
    (HERE/'benchmark-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    log.append('\nTask 3 benchmark: '+json.dumps(result))

def lab(path):
    c=fresh(path)
    c.execute("INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES(1,'2026-03-01 08:00:00',41.5,1)")
    assert c.execute('SELECT energy_j FROM reading').fetchone()[0]==41.5
    log.append('\nTask 1 generated energy_j = 41.5 (course expression; see physical-units caveat).')
    base='INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES(?,?,?,?)'
    for row, layer in [((1,'bad-9000',9000,1),'Domain CHECK'),((1,'bad-text','hot',1),'STRICT'),((99,'bad-fk',40,1),'Referential FOREIGN KEY'),((1,'bad-null',None,1),'NOT NULL'),((1,'bad-interval',40,0),'Interval CHECK')]:
        reject(c,base,layer,row)
    reject(c,"INSERT INTO sensor VALUES(3,'cnc-01','temp_c','degC')",'Composite UNIQUE')
    reject(c,"INSERT INTO sensor VALUES(1,'cnc-02','temp_c','degC')",'PRIMARY KEY')
    reject(c,"INSERT INTO sensor VALUES(3,'cnc-02','bogus','x')",'Metric CHECK')
    c.commit()
    before=c.execute('SELECT COUNT(*) FROM reading').fetchone()[0]
    c.close()
    first=ingest(path,HERE/'readings.csv')
    second=ingest(path,HERE/'readings.csv')
    assert (before,first,second)==(1,4,4)
    c=sqlite3.connect(path)
    c.execute('PRAGMA foreign_keys=ON')
    assert c.execute("SELECT value FROM reading WHERE sensor_id=1 AND ts='2026-03-01 08:00:00'").fetchone()[0]==41.7
    log.append(f'\nTask 2 CSV replay: before={before}, first={first}, second={second}; corrected value=41.7.')
    c.executescript(sqlfile('triggers.sql'))
    c.execute("INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES(2,'2026-03-01 09:00:00',2.7,1)")
    c.execute("UPDATE reading SET value=1.4 WHERE sensor_id=2 AND ts='2026-03-01 09:00:00'")
    assert c.execute('SELECT COUNT(*) FROM alarm').fetchone()[0]==1
    assert c.execute('SELECT old_value,new_value FROM audit').fetchall()==[(2.7,1.4)]
    log.append('\nTask 3 alarm: '+repr(c.execute('SELECT * FROM alarm').fetchall()))
    log.append('Task 3 audit: '+repr(c.execute('SELECT * FROM audit').fetchall()))
    # Demonstrate limitations of the unmodified course triggers, without hiding them.
    c.execute('SAVEPOINT limitations')
    c.execute("UPDATE reading SET value=2.9 WHERE sensor_id=2 AND ts='2026-03-01 09:00:00'")
    assert c.execute('SELECT COUNT(*) FROM alarm').fetchone()[0]==1
    c.execute('DELETE FROM audit')
    assert c.execute('SELECT COUNT(*) FROM audit').fetchone()[0]==0
    c.execute('ROLLBACK TO limitations')
    c.execute('RELEASE limitations')
    log.append('Verified limitations: UPDATE above threshold creates no alarm; audit rows are deletable by a writer. Rolled back both probes.')
    c.executescript(sqlfile('view.sql'))
    log.append('\nTask 4 machine_health: '+repr(c.execute('SELECT * FROM machine_health').fetchall()))
    c.commit()
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    c.close()
    ro=sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True)
    assert ro.execute('SELECT COUNT(*) FROM reading').fetchone()[0]==5
    reject(ro,'DELETE FROM reading','mode=ro')
    ro.close()
    rw=sqlite3.connect(path)
    rw.execute('PRAGMA query_only=ON')
    reject(rw,'DELETE FROM reading','query_only')
    rw.close()
    # Windows read-only attribute is not a Unix ACL. Record actual outcome and restore.
    original=Path(path).stat().st_mode
    try:
        os.chmod(path,0o444)
        x=sqlite3.connect(path)
        try:
            x.execute('UPDATE reading SET value=value WHERE reading_id=1')
            x.commit()
            log.append('File read-only probe: write succeeded; filesystem flag is not sufficient protection here.')
        except sqlite3.DatabaseError as exc:
            log.append(f'File read-only probe: {type(exc).__name__}: {exc}')
        finally:
            x.close()
    finally:
        os.chmod(path,original)
    log.append('Original file mode restored in finally; Windows attribute test is not proof of Unix chmod/ACL security.')

def optional():
    c=fresh()
    c.executescript(sqlfile('triggers.sql').replace('trg_vib_alarm AFTER INSERT','trg_vib_alarm BEFORE INSERT'))
    c.execute("INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES(2,'before-test',2.7,1)")
    assert c.execute('SELECT COUNT(*) FROM alarm').fetchone()[0]==1
    log.append('\nOptional Task 5: BEFORE INSERT also produced one alarm for a successful insert.')
    c.execute('SAVEPOINT rejected')
    reject(c,"INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES(2,'invalid',9000,1)",'BEFORE trigger + rejected parent statement')
    assert c.execute('SELECT COUNT(*) FROM alarm').fetchone()[0]==1
    c.execute('ROLLBACK TO rejected')
    log.append('The rejected reading left no additional alarm: trigger effects are part of the statement transaction.')
    c.close()

if __name__=='__main__':
    study()
    target=HERE/'edge.db'
    if target.exists():
        log.append('Existing edge.db preserved; lab verified in a temporary database.')
        with tempfile.TemporaryDirectory(prefix='verify-', dir=SCRATCH) as folder:
            lab(Path(folder)/'edge.db')
    else:
        lab(target)
    benchmark()
    optional()
    log.append('\nPASS: all assertions completed. No earlier module database was opened.')
    (HERE/'verification.txt').write_text('\n'.join(log)+'\n',encoding='utf-8')
    print('\n'.join(log))
