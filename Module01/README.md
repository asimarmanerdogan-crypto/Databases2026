# Module 01 — Introduction and Local-First Foundations

Owner: Asim Arman Erdogan.

Exploration plan: generate machine telemetry, measure local SQLite queries, and independently verify an AI-generated time-filtered aggregate.

## Learning goals

1. Explain how this class works — the CBL/PBL philosophy, the portfolio-based project work assessment, and the "moving bar" of a first-time course.
2. Set up your personal GitHub portfolio from the course template, with a clean first commit and a `.gitignore` that keeps databases and secrets out of Git.
3. Set up the entire toolchain reproducibly with `uv` — one fixed Python plus SQLite, DuckDB, Datasette, and more — on Windows, macOS, or Linux, and verify it.
4. Explain — with a measurement, not a slide — the difference between an embedded database and a client/server database, and why most local apps should not run a server.
5. Load real rows into SQLite and query them from Python using bound parameters.
6. Take a first LLM-generated query, run it, and begin the habit that defines this course: verify before you trust.

## Course and evidence links

- [Module instructions](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/01-introduction-and-local-first.md)
- [Syllabus](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/syllabus.md)
- [Runnable scripts and evidence for Tasks 3–7](../module-01/README.md)
- [Required-task audit](audit.md)

Existing scripts remain in `module-01/`; run commands from the repository root as shown in their evidence index.

## Course model

Learning goals define the contract. Challenge- and project-based learning uses practical problems and portfolio evidence; assessment includes module points, a final project and reflections. The course is a first iteration, so task wording can evolve while learning goals remain the basis for assessment. A pod contains two or three students; two pods form the final project team.

## Embedded versus client/server

SQLite executes inside the Python process and stores data in a local file. This experiment holds 172,800 readings in 10,526,720 bytes; measured query times are recorded in the linked telemetry results. No database server was needed. This proves the local workload runs without a server; it does not benchmark a remote database.

An embedded database simplifies deployment and offline operation, but SQLite permits only one writer at a time. A client/server database supports shared network access and many concurrent writers, with server administration and network dependencies. A server becomes appropriate when those workload requirements justify it.

## Participation and attribution

Code and evidence were prepared and rechecked with AI assistance. Pod members, portfolio links, division of work, peer audit and introductory experience/expectations have not yet been supplied. No pod activity or personal reflection is claimed here.
