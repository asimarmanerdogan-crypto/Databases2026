# Module 6b reflection draft

The JSON exercise showed a difference between two SQL expressions that return the same values. SQLite searched the expression index for `json_extract` and scanned the device table for `->>`. The session benchmark separated another pair of choices. The two stores read keys at similar speeds on this run, while one committed SQLite batch wrote the same 20,000 records much faster.

The two-connection fallback gave a concrete example of contention. One writer failed immediately while the other held a transaction open, and retrying after commit preserved both increments. A real network deployment would also require testing reachability, authentication and what clients do when they cannot confirm the outcome of a write.
