# SQL Island - completed guided demonstration

I completed the English version using the character name Asim. After the pilot was released, the character left the island and the game showed its completion screen.

## Completion evidence

- [Original completion certificate (PDF)](evidence/Certificate_SQL-Island.pdf) (original file).
- [Completion screenshot](evidence/sql-island-completed.jpg).

![SQL Island completion screen](evidence/sql-island-completed.jpg)

## How the session was completed

I completed the game as a guided session. The assistant entered the queries and explained them in Turkish while I watched. Some examples were run automatically by the game.

## Commands and patterns demonstrated

| Concept | Example from the session | What it does |
| --- | --- | --- |
| Read a table | `SELECT * FROM inhabitant;` | Shows all inhabitants and columns. |
| Select a column and filter rows | `SELECT personid FROM inhabitant WHERE name = 'Stranger';` | Returned character ID 20. SELECT chooses columns; WHERE chooses rows. |
| Combine conditions | `WHERE state = 'friendly' AND (job = 'dealer' OR job = 'merchant')` | Finds friendly people with either job. Parentheses preserve the intended grouping. |
| Match a pattern | `WHERE state = 'friendly' AND job LIKE '%smith'` | Finds friendly workers whose job ends in smith. |
| Find missing owners | `SELECT * FROM item WHERE owner IS NULL;` | Finds ownerless items. NULL is tested with IS NULL, not = NULL. |
| Change selected records | `UPDATE item SET owner = 20 WHERE owner IS NULL;` | Assigns only ownerless items to the character. |
| Sort | `SELECT * FROM inhabitant WHERE job = 'baker' ORDER BY gold DESC;` | Lists bakers from richest to poorest. |
| Combine related tables | `SELECT i.name FROM village AS v JOIN inhabitant AS i ON v.chief = i.personid WHERE v.name = 'Onionville';` | Matches the chief ID to a person ID; returned Fred Dix. |
| Count rows | `SELECT COUNT(*) FROM inhabitant WHERE villageid = 3;` | The equivalent game example joined by village name and counted 8 inhabitants. |
| Sum selected values | `SELECT SUM(gold) FROM inhabitant WHERE job IN ('baker', 'dealer', 'merchant');` | Returned 4130 gold for those jobs. |
| Group and average | `SELECT state, AVG(gold) FROM inhabitant GROUP BY state;` | Returns one average for each state rather than one row for each person. |
| Add a record | `INSERT INTO item (item, owner) VALUES ('sword', 20);` | The game automatically added the sword. |
| Delete a selected record | `DELETE FROM inhabitant WHERE name = 'Dirty Diane';` | Removes that fictional character's row. Omitting WHERE would affect the whole table. |
| Release the pilot | `UPDATE inhabitant SET state = 'friendly' WHERE personid = 8;` | Changes Arthur Tailor's state, allowing the story to finish. |

## Verification and a correction during play

At one point, the editor kept an earlier SELECT, and the result still included evil characters. Clearing the editor and running only the filtered query fixed this. It was a useful reminder to look at the result, not just the success message.

The inventory query confirmed six items with owner 20 after collecting ownerless items. Results identified the pilot as Arthur Tailor, personid 8, initially kidnapped. After the release UPDATE, the game advanced to the departure and completion screens.

## My answers

1. **What did you learn about databases and SQL from the game alone?**
   It was good practice for me and helped me understand SQL commands and how they work.

2. **Which SQL commands and patterns did you actually use?**
   I used SELECT, WHERE, JOIN, GROUP BY, INSERT, UPDATE and DELETE.

3. **In your own words, what are a table, a row, a column and a query?**
   A table organizes data. A row is one record, and a column holds one type of information. A query is an instruction to get or change data.

4. **What surprised you and what is still confusing?**
   I was surprised that SQL commands could control the story. JOIN and GROUP BY are still a little confusing, and I need more practice with them.

[Game](https://sql-island.informatik.uni-kl.de/) · [Module instructions](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/01-introduction-and-local-first.md)
