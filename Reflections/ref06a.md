# Module 6a reflection draft

The comparison uses the Module 5 report table as its starting point. Extending the same 200,000 rows over ten 91-day offsets lets both engines answer the same question over 2,000,000 rows. Comparing grouped results before timing is important because a query can get faster simply by answering a different question.

The useful boundary is the workload. Parquet can project a few columns for a historical aggregate. The operational path is built around short, keyed transactions, and the right benchmark for it is a series of small inserts and lookups. A snapshot adds a freshness obligation, so the reporting page should display when the last verified copy was produced.
