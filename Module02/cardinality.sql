PRAGMA foreign_keys=ON;
CREATE TABLE machine(machine_id INTEGER PRIMARY KEY);
CREATE TABLE sensor(sensor_id INTEGER PRIMARY KEY,
    machine_id INTEGER NOT NULL REFERENCES machine(machine_id));
INSERT INTO machine VALUES(1);
INSERT INTO sensor VALUES(101,1),(102,1);
SELECT machine_id, COUNT(*) AS sensors FROM sensor GROUP BY machine_id;
