CREATE TABLE machine (
	machine_id INTEGER NOT NULL,
	machine_name VARCHAR NOT NULL,
	serial_no VARCHAR NOT NULL,
	site VARCHAR NOT NULL,
	installed DATE NOT NULL,
	PRIMARY KEY (machine_id),
	CHECK (machine_id >= 1),
	CHECK (length(trim(machine_name)) > 0 AND length(trim(site)) > 0),
	CHECK (serial_no GLOB 'SN-?*'),
	UNIQUE (machine_name),
	UNIQUE (serial_no)
);

CREATE TABLE part (
	part_no VARCHAR NOT NULL,
	description VARCHAR NOT NULL,
	unit_price NUMERIC(9, 2) NOT NULL,
	PRIMARY KEY (part_no),
	CHECK (length(trim(part_no)) > 0 AND length(trim(description)) > 0),
	CHECK (typeof(unit_price) IN ('integer','real') AND unit_price >= 0 AND unit_price <= 9999999.99 AND round(unit_price, 2) = unit_price)
);

CREATE TABLE technician (
	technician_id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	PRIMARY KEY (technician_id),
	CHECK (technician_id >= 1 AND length(trim(name)) > 0)
);

CREATE TABLE maint_job (
	job_id INTEGER NOT NULL,
	machine_id INTEGER NOT NULL,
	technician_id INTEGER NOT NULL,
	done_on DATE NOT NULL,
	PRIMARY KEY (job_id),
	CHECK (job_id >= 1),
	FOREIGN KEY(machine_id) REFERENCES machine (machine_id),
	FOREIGN KEY(technician_id) REFERENCES technician (technician_id)
);

CREATE TABLE job_part (
	job_id INTEGER NOT NULL,
	part_no VARCHAR NOT NULL,
	PRIMARY KEY (job_id, part_no),
	FOREIGN KEY(job_id) REFERENCES maint_job (job_id),
	FOREIGN KEY(part_no) REFERENCES part (part_no)
);
