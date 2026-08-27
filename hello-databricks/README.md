# hello-databricks

Sandbox for experimenting with Databricks — Unity Catalog, Delta Lake, and
the managed Jobs runtime — from your own machine via Databricks Connect.
Infra is throwaway: spin up a cluster, poke at it, tear down. Unlike this
repo's other `hello-*` projects, every script here needs a real workspace
and a running cluster — no `local[*]` equivalent.

`make deploy-infra` provisions the cluster + Unity Catalog schema/volume;
`make start-cluster` / `make stop-cluster` resume/stop it (needs
`databricks auth login` configured separately); `make destroy-infra` tears
down. No EventBridge rule here — the cluster's own
`autotermination_minutes` (default 30) stops it after idle time.

`databricks_01_connect_session.py` → `databricks_06_job_submit.py` are a
progressive, self-contained study path, one Databricks concept each beyond
plain PySpark (see `../hello-spark` for fundamentals) — run any directly
once `databricks-connect`/`databricks-sdk` are installed and
`DATABRICKS_HOST`/`DATABRICKS_TOKEN`/`DATABRICKS_CLUSTER_ID` exported
(`terraform -chdir=terraform output ...` for values; add
`DATABRICKS_CATALOG`/`DATABRICKS_SCHEMA`/`DATABRICKS_VOLUME_PATH` from
step 3 on).

## Notes

- These scripts are checked against current `databricks-connect`/
  `databricks-sdk` APIs but not run end-to-end here — that needs a real
  workspace. If something's drifted, the SDK's own docstrings (`python3 -c
  "help(...)"`) are the fastest check.
