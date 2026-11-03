-- 1. Orphan job: cannot be assigned to a real machine/site.
SELECT j.job_id, j.machine_name FROM maint_job j
LEFT JOIN machine m ON m.machine_name=j.machine_name WHERE m.machine_name IS NULL;

-- 2. Duplicate part key: ambiguous identity and duplicated join results.
SELECT part_no, COUNT(*) AS copies FROM part GROUP BY part_no HAVING COUNT(*)>1;

-- 3. Text comparison omits the 9.90 parts: wrong purchasing/invoice decisions.
SELECT part_no, unit_price FROM part WHERE unit_price < '15';
SELECT part_no, unit_price FROM part WHERE CAST(unit_price AS NUMERIC) < 15;

-- 4. Unknown installation date: age-based maintenance cannot be scheduled.
-- This detects format defects only, not all impossible calendar dates.
SELECT machine_name, installed FROM machine
WHERE installed IS NULL OR installed NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]';

-- 5. List equality loses multipart job 1 and duplicates job 2.
SELECT j.job_id, p.description FROM maint_job j JOIN part p ON p.part_no=j.parts_used;
