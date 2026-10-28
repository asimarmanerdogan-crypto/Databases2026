# Module 02 - Data Contracts and Legacy Schema Audit

[Course module](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/02-data-contracts-and-legacy-schemas.md) · [Portfolio](../README.md)

## Learning goals

1. Reconstruct an ER/EER model from an undocumented SQL schema.
2. Identify integrity defects with queries.
3. Distinguish entities, relationships, attributes, surrogate keys and natural keys.
4. Express a corrected schema as a code-first Pydantic / SQLAlchemy contract.
5. Write the business requirements the original schema omitted.

## Task status

| Task | Evidence | Status |
| --- | --- | --- |
| A - Study | [Study log](study-log.md), two attributed example redraws and verified Q&A | References, examples and query checks recorded |
| B - Four sketches | [ER examples and proof](er-examples.md), [SQL](cardinality.sql) | Completed with AI assistance and executed proof |
| C - Explain and share | [Collaboration record](../COLLABORATION.md), agreed-learning section in study log | Discussed in person; notes and any shared post still to add |
| Setup | [Fixture](legacy-setup.sql) | Fixed: legacy.db was SQL text, now rebuilt as a real SQLite database |
| 1 - ER reconstruction | [ER audit](er-audit.md), [counts](cardinality-results.md) | Completed and checked |
| 2 - Integrity defects | [Queries](defect-queries.sql), [results and impact](defect-results.md) | All five demonstrated |
| 3 - Code contract | [Python](contract.py), [DDL](contract-ddl.sql), [decisions](contract-notes.md), [checks](verification.txt) | Built and checked with negative tests |
| Reflection | [Reflection 2](../Reflections/ref02.md) | Draft |

These files cover the core technical tasks. The optional inheritance and extra Mermaid exercises are not included.

## Reproduce

From the portfolio root:

```sh
uv run --locked python Module02/verify_module02.py
uv run --locked python Module02/contract.py
```

The verifier rebuilds the three lab tables, updates the reports and checks the corrected schema in a separate in-memory database. If legacy.db contains SQL text instead of a database, it keeps a backup before rebuilding it. Database files stay local.

The repaired contract is a target schema. The original orphan job, duplicate part and unknown installation date need explicit decisions before migration; they are not silently discarded or invented.
