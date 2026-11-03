# Reflection 04 - Data integrity and triggers


## Take-away

A database rule needs a test that shows what it rejects. CHECK, STRICT and foreign keys protect different things. A value can follow all the rules and still be wrong in the real world.

## What was good?

The CSV example gives a clear result: loading the same file twice kept four readings. The alarm and audit examples also produced records that can be inspected directly. My own comments on the exercise are still to add.

## What was difficult?

The checks show some important details: CHECK allows NULL, STRICT can convert numeric text, and foreign keys need to be enabled for each connection. I still need to add which parts I personally found difficult.

## Exploration and show stoppers

The BEFORE-trigger experiment showed that an alarm does not remain when the reading is rejected. The sample energy calculation has a units problem, and the audit table can still be changed by a writer. These are useful points to discuss with the pod or instructor.

## Interaction with peers and instructors

The Module 4 discussion is still to record. The [study notes](../Module04/integrity-notes.md#pod-discussion) contain questions to compare with another pod.

## How did you verify AI suggestions?

The [verification script](../Module04/verify_module04.py), prepared and run with AI assistance, checks rejected values, reading counts, generated values, alarms, audit records and read-only access. It also measures five batches with and without the alarm trigger. The [recorded results](../Module04/verification.txt) show what happened; I still need to review and explain these checks myself.

## Help and extra work

AI assistance was used for the implementation, explanations and checks. The optional BEFORE-trigger experiment is included. My personal practice and any help exchanged with classmates are still to add.
