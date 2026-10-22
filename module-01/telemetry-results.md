# Task 6: Synthetic telemetry in SQLite

AI-assisted execution using the course's fixed-seed generator; these are synthetic readings, not real factory data.

Database size: 10,526,720 bytes.
Row count: 172,800.

The database is embedded in a local file; no database server was started.

```sql
SELECT machine, COUNT(*) AS n FROM readings GROUP BY machine;
```
| machine | n |
| --- | --- |
| cnc-01 | 57600 |
| cnc-02 | 57600 |
| cnc-03 | 57600 |
Wall-clock execute + fetch time: 97.359 ms (one run).

```sql
SELECT machine, MAX(vib_rms) AS peak_vib FROM readings GROUP BY machine;
```
| machine | peak_vib |
| --- | --- |
| cnc-01 | 2.398 |
| cnc-02 | 3.168 |
| cnc-03 | 2.55 |
Wall-clock execute + fetch time: 113.032 ms (one run).

```sql
SELECT COUNT(*) AS alarm_readings FROM readings WHERE vib_rms > 2.0;
```
| alarm_readings |
| --- |
| 11714 |
Wall-clock execute + fetch time: 30.307 ms (one run).

Times are machine-dependent observations, not a benchmark.

Cloud cost: this local run has no cloud-service charge; a hosted version would depend on the provider, resources, storage and traffic, with charges paid by the cloud account owner.

Reproduce from the repository root:
```text
uv run python module-01/generate_telemetry.py
uv run python module-01/load_telemetry.py
uv run python module-01/verify_telemetry.py
```