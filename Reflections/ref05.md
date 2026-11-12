# Reflection 05 - Normalization and denormalization

Technical draft prepared with AI assistance. Add personal observations after reviewing the experiments.

## Take-away

The schema can keep transactional facts in 3NF while serving a separate reporting table. The site-change experiment makes the maintenance cost visible.

## What was good?

The [benchmark](../Module05/benchmark-results.md) compares equal dashboard results and records the access plans alongside the timing samples.

## What was difficult?

Personal notes to add. The technical distinction to review is how a full index walk differs from an indexed lookup.

## Exploration and show stoppers

The [notes](../Module05/normalization-notes.md#harvest) collect questions about the generator, current versus historical pricing and the role of the index.

## Interaction with peers and instructors

Pending. Record the gate feedback, the memo question and the curiosity exchange here after discussing them.

## How did you verify AI suggestions?

The [runner](../Module05/benchmark.py) verifies the full reconstructed row set and compares dashboard outputs before timing them. The five-row suggestion that a machine determines a technician fails on the larger fixture.

## Help and extra work

AI assistance supported the implementation and checks. The optional wider SQLite query and DuckDB comparison are recorded with the benchmark. Add any help exchanged with classmates after the session.
