# Module 03 - Curiosity collection

These notes collect questions and examples from the exercises, with AI assistance.

| Curiosity | Source | Observation or question |
| --- | --- | --- |
| An index makes the dashboard slower | [Benchmark](benchmark-results.md) | Compare the cumulative date/order-line indexes with the baseline. A different plan can perform more random table lookups. |
| Leading wildcard and LOWER defeat a lookup | [Plan safari](plan-safari-notes.md) | The ordinary index cannot narrow these predicates; an expression index would be a separate design. |
| Covering scan versus covering search | [Concept checks](concept-checks.txt) | Covering says where values come from; SCAN/SEARCH says how many entries are traversed. |
| COUNT(*) OVER does not collapse rows | [Query rewrites](query-rewrites.md) | Why is a final DISTINCT needed for the chosen window rewrite? |
| Customers with no late orders | [Query rewrites](query-rewrites.md) | A correlated COUNT yields zero; the original inner join omits those customers. Align the result domain before comparing. |
| Setup rows come from a recursive query | [Setup](setup.sql) | WITH RECURSIVE generates rows; x modulo 540 wraps the date back to the start. |
| SQL SELECT versus algebra selection | [Algebra exercise](task-b.md) | WHERE maps to sigma; SELECT * does not need an additional projection. |

## Collaboration

We discussed Modules 2 and 3 with another pod face to face. I still need to add the main points, the other pod's SQLite version and any questions shared in Discord. See [pod notes](../COLLABORATION.md) for the review with Habiba.
