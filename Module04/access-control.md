# Task 4 - Access control without a server

The access checks were prepared and run with AI assistance. [view.sql](view.sql) defines the machine-health summary; [verification.txt](verification.txt) records the actual results.

## View and read-only connection

The view groups readings by machine and metric, showing the peak value and reading count. It is created while the database is writable.

A separate connection opened with `mode=ro` could read all five readings. DELETE failed with `attempt to write a readonly database`. Another connection using `PRAGMA query_only=ON` rejected DELETE with the same error.

A view makes a report easier to read, but it does not stop someone with direct file access from querying the original tables. A connection owner can also turn query_only off.

## File permissions on Windows

The course uses Unix `chmod`. On this Windows machine, the verifier temporarily set the database's read-only attribute through `os.chmod(path, 0o444)`. The write was rejected, and the original mode was restored in a finally block.

This demonstrates the Windows read-only attribute, not a complete NTFS permissions policy. The following is the course's Unix sequence for comparison; it was not run as a Unix permissions test here:

```sh
chmod 444 Module04/edge.db
sqlite3 'file:Module04/edge.db?mode=ro' 'SELECT COUNT(*) FROM reading;'
sqlite3 'file:Module04/edge.db?mode=ro' 'DELETE FROM reading;'
chmod 644 Module04/edge.db
```

## Comparison with PostgreSQL

PostgreSQL authenticates users and grants permissions to roles through a server. SQLite relies on the application's connection and the operating system's control of the database file. Read-only access is useful for a trusted local reporting tool. A multi-tenant application needs authentication and tenant-specific authorization; handing out a database file does not provide that separation.
