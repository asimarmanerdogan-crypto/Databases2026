# Task 3 — Contract enforcement decisions

[contract.py](contract.py) contains Pydantic models for Machine, Technician, Part and MaintenanceJob, plus SQLAlchemy tables for those entities and JobPart. [Emitted SQLite DDL](contract-ddl.sql) and [executed negative checks](verification.txt) accompany it.

- **Application:** calendar-date parsing, serial prefix, trimmed nonempty input, positive IDs, decimal precision/range, duplicate part-list rejection and unknown-field rejection give useful errors before writing.
- **Database:** primary keys, NOT NULL, unique machine serial/name, foreign keys and composite junction key protect shared identity and references. CHECK constraints also enforce positive IDs, basic nonempty fields, serial prefix and numeric price range/precision. Technician names deliberately are not unique.
- **Connection:** `make_engine()` enables SQLite foreign keys on every connection before table creation. Emitted DDL alone does not enable connection pragmas; external SQLite clients must issue `PRAGMA foreign_keys=ON` themselves.

Pydantic cannot establish database-wide uniqueness or reference existence. The application must insert a validated job and its JobPart rows in one transaction; the database checks actual references.

SQLite's Date declaration does not by itself reject impossible dates inserted with raw SQL. Calendar validity is an application rule here; bypassing the contract bypasses that protection. SQLite NUMERIC is not fixed-point storage: this lab adds checks, but exact monetary accounting should use integer minor units with an explicit currency/rounding policy.

This is a corrected target model, not an automatic migration of the invalid legacy fixture. The legacy defects intentionally remain available for the audit.

References: [Pydantic validators](https://docs.pydantic.dev/latest/concepts/validators/), [SQLAlchemy SQLite foreign-key support](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support), [SQLite type affinity](https://www.sqlite.org/datatype3.html).
