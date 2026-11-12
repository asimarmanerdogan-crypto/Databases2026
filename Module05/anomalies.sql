CREATE TABLE flat5 (
    job_id INTEGER, machine_id TEXT, site TEXT, technician TEXT,
    part_no TEXT, part_price REAL
);
INSERT INTO flat5 VALUES
    (1, 'cnc-01', 'Gütersloh', 'tech-0', 'P-0001', 6.00),
    (1, 'cnc-01', 'Gütersloh', 'tech-0', 'P-0002', 7.00),
    (2, 'cnc-02', 'Gütersloh', 'tech-1', 'P-0001', 6.00),
    (2, 'cnc-02', 'Gütersloh', 'tech-1', 'P-0003', 8.50),
    (3, 'cnc-01', 'Gütersloh', 'tech-0', 'P-0003', 8.50);
