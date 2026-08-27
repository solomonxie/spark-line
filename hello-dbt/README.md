# hello-dbt

Sandbox for experimenting with dbt — models, `ref()`, incremental builds,
tests, and macros — against local DuckDB. No infra: a local venv and
`dbt-duckdb` is all you need (`make install`).

`dbt_01_hello_model.sql` → `dbt_07_macros.sql` (step 5 is two files) are a
progressive study path, one dbt concept per file, mostly standalone (step
5's `ref()` chain is the one exception) — run any directly, e.g.
`venv/bin/dbt run --select dbt_01_hello_model`, or everything with
`make run` / `make test`. `models/schema.yml` adds `not_null`/`unique`
tests on steps 1 and 4.

## Notes

- `target/`, `logs/`, `venv/`, and `*.duckdb` are gitignored — nothing to
  commit there.
