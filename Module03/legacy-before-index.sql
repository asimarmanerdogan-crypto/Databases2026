.bail on
.echo on
.headers on
.mode column
.timer on
SELECT sqlite_version() ASsqlite3 Module02/legacy.db sqlite_version;
SELECT 'machine' AS table_name, COUNT(*) AS n FROM machine
UNION ALL SELECT 'part', COUNT(*) FROM part
UNION ALL SELECT 'maint_job', COUNT(*) FROM maint_job;
SELECT name, tbl_name FROM sqlite_schema WHERE type = 'index';
EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician = 'Beier';
SELECT * FROM maint_job WHERE technician = 'Beier';
EXPLAIN QUERY PLAN SELECT * FROM machine WHERE machine_name = 'cnc-02';
SELECT * FROM machine WHERE machine_name = 'cnc-02';
EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician LIKE '%ei%';
SELECT * FROM maint_job WHERE technician LIKE '%ei%';
