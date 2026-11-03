<p align="center"><sub>DATABASES 2026 &nbsp; / &nbsp; MODULE 02 &nbsp; / &nbsp; CARDINALITY RESULTS</sub></p>

<h1 align="center">Cardinality observations in the legacy fixture</h1>

Observed counts support **intended relationships**; they *do not enforce future cardinality*.

### 01 / Jobs per machine

```sql
SELECT machine_name, COUNT(*) AS jobs FROM maint_job GROUP BY machine_name;
```
| machine_name | jobs |
| --- | --- |
| cnc-01 | 2 |
| cnc-02 | 1 |
| cnc-05 | 1 |

Measured execute + fetch: **0.108 ms** *(one local run)*.

### 02 / Jobs per technician

```sql
SELECT technician, COUNT(*) AS jobs FROM maint_job GROUP BY technician;
```
| technician | jobs |
| --- | --- |
| Beier | 2 |
| Klaas | 1 |
| Werther | 1 |

Measured execute + fetch: **0.085 ms** *(one local run)*.

### 03 / Part tokens per job

```sql
SELECT job_id, parts_used, CASE WHEN parts_used IS NULL OR trim(parts_used)='' THEN 0 ELSE length(parts_used)-length(replace(parts_used, ',', ''))+1 END AS n_parts FROM maint_job;
```
| job_id | parts_used | n_parts |
| --- | --- | --- |
| 1 | P-1001,P-1002 | 2 |
| 2 | P-1003 | 1 |
| 3 | P-1001 | 1 |
| 4 | NULL | 0 |

Measured execute + fetch: **0.097 ms** *(one local run)*.

### 04 / Jobs per part

```sql
WITH RECURSIVE split(job_id, part_no, rest) AS (
      SELECT job_id, '', coalesce(parts_used,'') || ',' FROM maint_job
      UNION ALL SELECT job_id, substr(rest,1,instr(rest,',')-1), substr(rest,instr(rest,',')+1)
      FROM split WHERE rest<>''
    ) SELECT trim(part_no) AS part_no, COUNT(DISTINCT job_id) AS jobs
      FROM split WHERE trim(part_no)<>'' GROUP BY trim(part_no);
```
| part_no | jobs |
| --- | --- |
| P-1001 | 2 |
| P-1002 | 1 |
| P-1003 | 1 |

Measured execute + fetch: **0.155 ms** *(one local run)*.

---

<p align="center"><sub>MODULE 02 &nbsp; / &nbsp; DATA CONTRACTS AND LEGACY SCHEMAS</sub><br><a href="README.md">Module overview</a> &nbsp; · &nbsp; <a href="er-audit.md">ER audit</a> &nbsp; · &nbsp; <a href="../README.md">Portfolio</a></p>
