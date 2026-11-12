SELECT machine_id, site, technician, SUM(part_price) AS cost
FROM report_jobpart
WHERE done_on >= '2026-03-01'
GROUP BY machine_id, site, technician
