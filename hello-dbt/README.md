# hello-dbt

Sandbox for experimenting with dbt — models, `ref()`, incremental builds,
tests, and macros — against local DuckDB. No infra: a local venv and
`dbt-duckdb` is all you need.

## How to use this

```
make install                          # creates venv/, installs dbt-duckdb
venv/bin/dbt run --select dbt_01_hello_model
```

All `dbt` commands assume you're in this directory — `profiles.yml` next
to `dbt_project.yml` is enough for dbt to find it.

## Progressive study path

Eight models (step 5 is two files), one dbt concept each. Each builds its
own data inline via `VALUES` rather than a shared seed, so — with one
exception — each stands alone: no `ref()` chain to build first.

| Step | File(s) | Concept |
| --- | --- | --- |
| 1 | `dbt_01_hello_model.sql` | The simplest model — a view over a literal row |
| 2 | `dbt_02_inline_data.sql` | An inline dataset via `VALUES` |
| 3 | `dbt_03_transformations.sql` | Derived columns, `CASE WHEN` |
| 4 | `dbt_04_aggregation.sql` | `GROUP BY` + `count`/`avg`/`max` |
| 5 | `dbt_05a_upstream_orders.sql` + `dbt_05b_downstream_summary.sql` | `ref()` — dbt's core idea (the one exception) |
| 6 | `dbt_06_incremental_model.sql` | Incremental materialization + `is_incremental()` |
| 7 | `dbt_07_macros.sql` | A custom Jinja macro |

Plus `models/schema.yml`, adding `not_null`/`unique` tests on steps 1 and
4 — run with `make test`.

Run any step directly:

```
venv/bin/dbt run --select dbt_01_hello_model
venv/bin/dbt run --select dbt_02_inline_data
venv/bin/dbt run --select dbt_03_transformations
venv/bin/dbt run --select dbt_04_aggregation
venv/bin/dbt run --select +dbt_05b_downstream_summary   # `+` builds 05a first
venv/bin/dbt run --select dbt_06_incremental_model      # run twice — 2nd run adds 0 rows
venv/bin/dbt run --select dbt_07_macros
make test
```

Or run everything: `make run` / `make test`.

## Notes

- `target/`, `logs/`, `venv/`, and `*.duckdb` are gitignored — nothing to
  commit there.
