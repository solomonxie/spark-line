# hello-dbt

Experiments on dbt — models, `ref()`, incremental builds, tests, and
macros — against local DuckDB. No infra: a local venv is all you need
(`make install`).

A progressive set of models walks through one dbt concept at a time, each
runnable on its own (`make run` for all of them, `make test` for the
tests).

## Notes

- Build artifacts and the local venv are gitignored — nothing to commit
  there.
