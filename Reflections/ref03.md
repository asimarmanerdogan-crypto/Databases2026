# Reflection 03 - SQL and query profiling

## Take-away

I learned that a query can return the right result but still be slow. An index does not automatically make every query faster. I need to look at the query plan and measurements together.

## What was good?

I understood query plans quite well. Indexes and SQL injection were especially interesting to me, and I enjoyed learning about them.

## What was difficult?

Relational algebra was the hardest part. Writing a SQL query as an algebra expression was difficult, and I needed AI explanations to work through it.

## Exploration and show stoppers

The index experiments were interesting because adding an index could also make a query slower. The injection example showed how user input could change the meaning of a query and why bound parameters matter.

## Interaction with peers and instructors

I worked with Habiba and discussed the module with another pod in person. We helped each other with the material. I still need to write down the specific points from that discussion.

## How did you verify AI suggestions?

The [benchmark](../Module03/benchmark-results.md) compares query plans and the median of three measurements. The checks were prepared and run with AI assistance and also compare the SQL results with a separate Python calculation. The [injection demo](../Module03/injection-output.txt) shows that the unsafe query returns all customers for the test payload, while the bound-parameter version treats it as data.

## Help and extra work

AI explanations helped me with relational algebra, and working with my pod helped me discuss the tasks. I want to practise translating a query into algebra without help and keep exploring indexes and SQL injection.
