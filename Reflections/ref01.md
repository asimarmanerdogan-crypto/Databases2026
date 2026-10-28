# Module 01 — Reflection

## Take-away

The first module mainly focused on setting up the tools and environment. I learned how uv manages Python and project dependencies, how SQLite dot-commands work, and why a local-first database can be more suitable than a cloud-based system for some applications. My main takeaway is that AI can speed up coding, but its output still needs human verification. A person must take responsibility for the final result, because AI can make mistakes and cannot be held accountable.

## What was good?

It gets better as I advance in learning.

## What was difficult?

As someone learning databases and GitHub from scratch, I found the beginning quite challenging. I am enjoying it more as I understand what is happening.

## Exploration and show stoppers

At first, the whole module was an exploration because these topics were new to me.

## Interaction with peers and instructors

My pod mate is Habiba Darwish. We also worked with three other classmates over the weekend and helped each other understand the material. No completed peer audit is claimed here.

## How did you verify AI suggestions?

My original reflection mainly described installation and live tests without observed wrong results. That description was too broad: the portfolio also includes a [reproducible SQL verification report](../Module01/ai-sql-verification.md). The AI-assisted checks compare SQL aggregation with a separate Python calculation, inspect EXPLAIN QUERY PLAN and test time boundaries. They identify an ambiguity: “after 18:00” excludes early-morning readings, whereas an entire overnight shift would need a different predicate. A deliberately misspelled column also raises an error. These are documented automated checks, not a claim that I performed each check independently. My takeaway is to distinguish a query that runs from a query that matches the intended business meaning.

## Help and extra work

We worked together with my pod and three other classmates over the weekend. We helped each other with the parts we understood and the parts we did not understand.

---

Edited for clarity from the student's existing reflection. The technical verification paragraph was reconciled with the linked evidence using AI assistance; no additional personal participation is claimed.
