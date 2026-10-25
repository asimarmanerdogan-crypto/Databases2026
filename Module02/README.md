# Module 02 — Data Contracts and Legacy Schema Audit

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
| A — Study | [Study log](study-log.md), two attributed example redraws and verified Q&A | Technical notes present; actual pod study unconfirmed |
| B — Four sketches | [ER examples and proof](er-examples.md), [SQL](cardinality.sql) | Completed with AI assistance and executed proof |
| C — Explain and share | Agreed-learning section in study log | Actual neighbouring-pod discussion, shared image and Discord post pending |
| Setup | [Fixture](legacy-setup.sql) | Fixed: legacy.db was SQL text, now rebuilt as a real SQLite database |
| 1 — ER reconstruction | [ER audit](er-audit.md), [counts](cardinality-results.md) | Completed and checked |
| 2 — Integrity defects | [Queries](defect-queries.sql), [results and impact](defect-results.md) | All five demonstrated |
| 3 — Code contract | [Python](contract.py), [DDL](contract-ddl.sql), [decisions](contract-notes.md), [checks](verification.txt) | Built and checked with negative tests |
| Reflection | [Student reflection prompts](../Reflections/ref02.md) | Personal answers pending |

The source places a draft boundary before these tasks; this audit covers all starred tasks as the working checklist. Stretchers 4–5 were not required for this pass. Technical completion does not replace student participation or checkpoint explanation.

## Reproduce

From the portfolio root:

```sh
uv run --locked python Module02/verify_module02.py
uv run --locked python Module02/contract.py
```

The verifier resets only the three intentionally flawed Module02 lab tables using the committed fixture, rebuilds reports, emits the corrected target DDL, and checks constraints on a separate in-memory database. It preserves a mislabelled non-SQLite file before rebuilding. The local backup legacy-original-text.sql is kept for recovery. No .db file is committed.

The repaired contract is a target schema. The original orphan job, duplicate part and unknown installation date need explicit decisions before migration; they are not silently discarded or invented.
