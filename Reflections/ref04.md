# Reflection 04 — Integrity and triggers

> AI-assisted technical draft, prepared 2026-11-03. The student must review and add personal experience; no peer discussion or independent mastery is claimed.

## Take-away

Technical finding: rules must be tested by deliberately inserting bad data. CHECK, STRICT and foreign keys cover different failure modes; none proves that a plausible reading is true.

## What was good?

Executed evidence: replaying the CSV kept four reading rows; alarm/audit records appeared automatically; read-only connections rejected DELETE. Personal assessment: to be added by the student.

## What was difficult?

Technical subtleties include NULL passing CHECK, STRICT converting numeric text, per-connection foreign keys and INSERT-only alarms missing UPDATEs. Which of these was personally difficult: to be added by the student.

## Exploration and show stoppers

The optional BEFORE-trigger experiment showed that a rejected reading leaves no alarm behind. The sample energy_j expression has inappropriate units for the provided metrics, and the sample audit table is not immutable. These are useful discussion questions for the instructor.

## Interaction with peers and instructors

Pending actual discussion. Add the participating pod, date, feedback received and advice given. See the prepared questions in Module04/integrity-notes.md.

## How did you verify AI suggestions?

The assistant generated and ran [the verifier](../Module04/verify_module04.py), checking expected errors, row counts, generated values, alarm/audit effects, read-only failures and five benchmark samples per variant. [Recorded results](../Module04/verification.txt) show the executed outcomes. This is AI-assisted automated verification; the student should rerun and explain the checks before claiming independent understanding.

## Help and extra work

Implementation, documentation and experiments were prepared with AI assistance. The optional BEFORE-trigger task is included. Add personal practice and real peer help after completing them.
