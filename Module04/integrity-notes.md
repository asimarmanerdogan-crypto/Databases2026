# Integrity study — AI-assisted, verified locally

## Three layers

| Layer | Purpose | Executed example |
| --- | --- | --- |
| Entity | Identify rows and prevent duplicate identities | Duplicate sensor_id and duplicate (machine_id, metric) rejected |
| Referential | Child references an existing parent | Reading for sensor 99 rejected with foreign_keys=ON |
| Domain | Values obey the declared rules | 9000, unknown metric, zero interval and text 'hot' rejected |

NOT NULL prevents missing required values. STRICT is a typing guard; it is not a check of physical truth. PRIMARY KEY/UNIQUE alone do not establish that a value is meaningful.

## Acceptance experiment

The loose table accepted 9000, 'hot' in a REAL-declared column, the bogus metric with -500, and a fully NULL row. The constrained version rejected the corresponding bad rows one at a time. Exact SQL, parameter values and SQLite errors are in [verification.txt](verification.txt).

Surprises verified by execution:

- CHECK(v>0) allowed NULL. Add NOT NULL when missing data must be rejected.
- STRICT accepted '42.0' in REAL after lossless conversion.
- NULL in INTEGER PRIMARY KEY allocated a new ID instead of failing.
- Explicitly disabling foreign keys allowed an orphan, found by foreign_key_check; enabling enforcement rejected it.
- A valid-looking temperature from the wrong real sensor can still pass. Constraints enforce declared rules, not the truth of the source.

## LLM claims and checks

The assistant was asked to implement and verify the linked module while preserving existing files. Claims were checked with actual inserts, expected failures and assertions, not accepted from prose alone.

A CHECK cannot contain the parent-table lookup needed to enforce a relationship to an existing sensor; use a foreign key. A trigger can consult another table and insert an alarm, which a row-local CHECK cannot do. BEFORE and AFTER triggers can both reject a statement using RAISE(ABORT,...); neither makes side effects survive a failed statement. This lab directly tests failed-statement rollback for BEFORE and checks foreign-key enforcement on independent connections.

## Pod discussion — pending

No pod meeting or agreed conclusions are claimed. Use these questions in the real meeting:

1. Which surprising row did your unconstrained table accept?
2. Did CHECK reject NULL? Which additional rule was necessary?
3. Why did STRICT accept numeric text but reject 'hot'?
4. Why must (machine_id, metric) be unique together?
5. What happens when UPSERT updates a vibration from below 2.0 to above it?
6. Is the audit table actually immutable? What is missing?

After discussing, add the date, participating pod, agreed points and unresolved questions here. Questions for #sql-questions are prepared above; nothing was posted externally.
