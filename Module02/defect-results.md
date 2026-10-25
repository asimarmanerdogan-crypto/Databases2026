# Integrity defects — actual query results

AI-assisted verification against the deliberately flawed fixture. Comments state production impact.

```sql
-- 1. Orphan job: cannot be assigned to a real machine/site.
SELECT j.job_id, j.machine_name FROM maint_job j
LEFT JOIN machine m ON m.machine_name=j.machine_name WHERE m.machine_name IS NULL;
```
| job_id | machine_name |
| --- | --- |
| 3 | cnc-05 |
Measured execute + fetch: 0.135 ms (one local run).

```sql
-- 2. Duplicate part key: ambiguous identity and duplicated join results.
SELECT part_no, COUNT(*) AS copies FROM part GROUP BY part_no HAVING COUNT(*)>1;
```
| part_no | copies |
| --- | --- |
| P-1003 | 2 |
Measured execute + fetch: 0.111 ms (one local run).

```sql
-- 3. Text comparison omits the 9.90 parts: wrong purchasing/invoice decisions.
SELECT part_no, unit_price FROM part WHERE unit_price < '15';
```
| part_no | unit_price |
| --- | --- |
| P-1001 | 12.50 |
Measured execute + fetch: 0.086 ms (one local run).

```sql
SELECT part_no, unit_price FROM part WHERE CAST(unit_price AS NUMERIC) < 15;
```
| part_no | unit_price |
| --- | --- |
| P-1001 | 12.50 |
| P-1003 | 9.90 |
| P-1003 | 9.90 |
Measured execute + fetch: 0.089 ms (one local run).

```sql
-- 4. Unknown installation date: age-based maintenance cannot be scheduled.
-- This detects format defects only, not all impossible calendar dates.
SELECT machine_name, installed FROM machine
WHERE installed IS NULL OR installed NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]';
```
| machine_name | installed |
| --- | --- |
| RANDOM-NAME | unknown |
Measured execute + fetch: 0.095 ms (one local run).

```sql
-- 5. List equality loses multipart job 1 and duplicates job 2.
SELECT j.job_id, p.description FROM maint_job j JOIN part p ON p.part_no=j.parts_used;
```
| job_id | description |
| --- | --- |
| 2 | Coolant filter |
| 2 | Coolant filter |
| 3 | Ball bearing 6203 |
Measured execute + fetch: 0.109 ms (one local run).

The naive list join returns job 2 twice because P-1003 is duplicated; job 1 is absent. CAST repairs this fixture's comparison but is not general validation of arbitrary text prices.