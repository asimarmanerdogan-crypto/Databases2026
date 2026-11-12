PRAGMA foreign_keys = ON;

CREATE TABLE flat_jobpart (
    job_id INTEGER, machine_id TEXT, site TEXT, technician TEXT,
    part_no TEXT, part_price TEXT, done_on TEXT
);

WITH RECURSIVE jobs(n) AS (
    SELECT 1 UNION ALL SELECT n + 1 FROM jobs WHERE n < 20000
), parts(k) AS (
    SELECT 1 UNION ALL SELECT k + 1 FROM parts WHERE k < 10
)
INSERT INTO flat_jobpart
SELECT n,
       'cnc-' || printf('%02d', (n % 50) + 1),
       CASE n % 50 WHEN 0 THEN 'Bielefeld' ELSE 'Gütersloh' END,
       'tech-' || (n % 7),
       'P-' || printf('%04d', (k % 40) + 1),
       printf('%.2f', 5 + (k % 40)),
       date('2026-01-01', '+' || (n % 90) || ' days')
FROM jobs CROSS JOIN parts;

CREATE INDEX ix_flat_machine ON flat_jobpart(machine_id);

CREATE TABLE machine (machine_id TEXT PRIMARY KEY NOT NULL, site TEXT NOT NULL);
CREATE TABLE part (part_no TEXT PRIMARY KEY NOT NULL, part_price REAL NOT NULL);
CREATE TABLE job (
    job_id INTEGER PRIMARY KEY,
    machine_id TEXT NOT NULL REFERENCES machine(machine_id),
    technician TEXT NOT NULL,
    done_on TEXT NOT NULL
);
CREATE TABLE job_part (
    job_id INTEGER NOT NULL REFERENCES job(job_id),
    part_no TEXT NOT NULL REFERENCES part(part_no),
    PRIMARY KEY (job_id, part_no)
);

INSERT INTO machine SELECT DISTINCT machine_id, site FROM flat_jobpart;
INSERT INTO part SELECT DISTINCT part_no, CAST(part_price AS REAL) FROM flat_jobpart;
INSERT INTO job SELECT DISTINCT job_id, machine_id, technician, done_on FROM flat_jobpart;
INSERT INTO job_part SELECT DISTINCT job_id, part_no FROM flat_jobpart;
