# hello-dbt

Sandbox for experimenting with dbt — models, `ref()`, incremental builds,
tests, and macros — against local DuckDB. No infra: a local venv and
`dbt-duckdb` is all you need.

## Layout

- `dbt_project.yml` / `profiles.yml` — a single project-local profile,
  `duckdb` target, zero infra.
- `models/dbt_01_hello_model.sql` ... `models/dbt_07_macros.sql` —
  a progressive study path, one dbt concept per file. See below.
- `macros/celsius_to_fahrenheit.sql` — the custom macro step 7 calls.
- `Makefile` — creates a local venv and installs `dbt-duckdb`.

## How to use this

```
make install                          # creates venv/, installs dbt-duckdb
venv/bin/dbt run --select dbt_01_hello_model
```

(all `dbt` commands below assume you're in this directory, with
`DBT_PROFILES_DIR` unset — `profiles.yml` living right next to
`dbt_project.yml` is enough for dbt to find it.)

## Progressive study path

Eight models (step 5 is two files — see below), each covering one dbt
concept. Every model builds its own data inline via `VALUES` rather than
reading a shared seed, so — with one deliberate exception — each stands
alone: no `ref()` chain to build first, no fixtures to set up.

| Step | File(s) | Concept |
| --- | --- | --- |
| 1 | `dbt_01_hello_model.sql` | The simplest model — a view over a literal row |
| 2 | `dbt_02_inline_data.sql` | An inline dataset via `VALUES` |
| 3 | `dbt_03_transformations.sql` | Derived columns, `CASE WHEN` |
| 4 | `dbt_04_aggregation.sql` | `GROUP BY` + `count`/`avg`/`max` |
| 5 | `dbt_05a_upstream_orders.sql` + `dbt_05b_downstream_summary.sql` | `ref()` — dbt's core idea (the one exception to "stands alone") |
| 6 | `dbt_06_incremental_model.sql` | Incremental materialization + `is_incremental()` |
| 7 | `dbt_07_macros.sql` | A custom Jinja macro |

Plus `models/schema.yml`, which adds `not_null`/`unique` tests on steps 1
and 4 — run with `make test`.

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

All seven models plus `dbt test` were run end to end against `dbt-duckdb`
1.11.0 / dbt-core 1.12.3 while writing this, including step 6's two-run
incremental behavior.

## Notes

- `target/`, `logs/`, `venv/`, and `*.duckdb` are gitignored — dbt and
  the venv regenerate all of them; there's nothing to commit there.
