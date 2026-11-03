# Access control — Windows and SQLite

The [view](view.sql) is created while the database is writable. The verifier reads its aggregated results, opens an independent URI connection with `mode=ro`, confirms SELECT works and records the exact DELETE error. A second connection tests `PRAGMA query_only=ON`. All outcomes are in [verification.txt](verification.txt).

## File protection on this machine

This computer runs Windows, so Unix `chmod 444/644` is not an equivalent Windows ACL demonstration. The verifier temporarily applies Python `os.chmod(path, 0o444)` to its Module04 database, tests a write and restores the original file mode in a finally block. On this run the write was rejected as read-only. Windows' read-only attribute is weaker than a complete NTFS access-control policy; this test must not be represented as proof of Unix permissions.

The course's Unix sequence, for reference (not claimed to have run on Windows):

```sh
chmod 444 Module04/edge.db
sqlite3 'file:Module04/edge.db?mode=ro' 'SELECT COUNT(*) FROM reading;'
sqlite3 'file:Module04/edge.db?mode=ro' 'DELETE FROM reading;'
chmod 644 Module04/edge.db
```

## Server comparison

PostgreSQL authenticates users and can grant distinct table/view privileges to roles through a server. SQLite trusts the application's connection and the operating system's access to its database file. A trusted local reporting application can use read-only access, but a multi-tenant service needs an authenticated application boundary and tenant authorization rather than distributing the database file. A view shapes results but does not by itself prevent a file reader from querying underlying tables, and query_only can be disabled by the connection owner.
