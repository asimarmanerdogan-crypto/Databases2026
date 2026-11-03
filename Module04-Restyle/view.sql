CREATE VIEW machine_health AS
SELECT s.machine_id,s.metric,MAX(r.value) AS peak,COUNT(*) AS n
FROM sensor s JOIN reading r USING(sensor_id)
GROUP BY s.machine_id,s.metric;
