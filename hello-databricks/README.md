# hello-databricks

Sandbox for experimenting with Databricks — Unity Catalog, Delta Lake, and
the managed Jobs runtime — from your own machine via Databricks Connect.
Infra is throwaway by design: spin up a cluster, poke at it, tear down.

Unlike this repo's other `hello-*` projects, there's no local fallback:
Databricks is a managed service, so every script here needs a real
workspace (a free trial or Community Edition works) and a running cluster
to talk to — there's no `local[*]` equivalent.

## Layout

- `terraform/` — provisions a single-node cluster and a Unity Catalog
  schema/volume inside your workspace. See `terraform/README.md`.
- No `ansible/` here — Databricks manages the cluster's OS/runtime itself;
  there's nothing to SSH into or configure.
- `databricks_01_connect_session.py` ... `databricks_06_job_submit.py` — a
  progressive study path, one Databricks concept per file. See below.
- `Makefile` — wraps Terraform + `databricks` CLI calls (see below).

## How to use this

```
make deploy-infra     # terraform apply — creates the cluster + schema/volume
make start-cluster     # databricks clusters start — resume a stopped cluster
make stop-cluster      # databricks clusters delete — stop it, keep the definition
make destroy-infra     # terraform destroy — tear everything down
```

`start-cluster`/`stop-cluster` need the `databricks` CLI configured
separately from Terraform (`databricks auth login`, or reuse the same
`DATABRICKS_HOST`/`DATABRICKS_TOKEN` the scripts below use).

## Progressive study path

Six standalone scripts, each covering one Databricks concept beyond plain
PySpark (see `../hello-spark` for the PySpark fundamentals — this
project doesn't re-teach those). Every file is self-contained — no imports
between them — though unlike the fully offline `hello-spark` scripts,
none of them can run without a real workspace and cluster.

| Step | File | Concept |
| --- | --- | --- |
| 1 | `databricks_01_connect_session.py` | Databricks Connect: a remote `SparkSession`, DataFrame-only (no RDDs) |
| 2 | `databricks_02_dataframe_basics.py` | DataFrame ops executed on the cluster, not locally |
| 3 | `databricks_03_unity_catalog_tables.py` | Managed Delta tables addressed as `catalog.schema.table` |
| 4 | `databricks_04_delta_merge.py` | Atomic `MERGE INTO` upserts + `DESCRIBE HISTORY` |
| 5 | `databricks_05_volumes_file_io.py` | Unity Catalog Volumes via the Files API (databricks-sdk) |
| 6 | `databricks_06_job_submit.py` | Capstone: submit + monitor a one-time Databricks Job run |

Requires, for every step:

```
pip install databricks-connect databricks-sdk

export DATABRICKS_HOST=https://<workspace-id>.cloud.databricks.com
export DATABRICKS_TOKEN=<personal-access-token>
export DATABRICKS_CLUSTER_ID=$(terraform -chdir=terraform output -raw cluster_id)
```

and, from step 3 onward:

```
export DATABRICKS_CATALOG=$(terraform -chdir=terraform output -raw unity_catalog_schema | cut -d. -f1)
export DATABRICKS_SCHEMA=$(terraform -chdir=terraform output -raw unity_catalog_schema | cut -d. -f2)
export DATABRICKS_VOLUME_PATH=$(terraform -chdir=terraform output -raw volume_path)
```

Then run any step directly:

```
python3 databricks_01_connect_session.py
```

`databricks-connect`'s version should match your cluster's Databricks
Runtime major version — if you change `spark_version` in `terraform/`,
reinstall `databricks-connect` to match.

## Self-termination

No EventBridge rule here — `terraform/cluster.tf`'s
`autotermination_minutes` (default 30) is Databricks' own idle-shutdown,
set directly on the cluster. See `terraform/README.md`.

## Notes

- These scripts are checked against the current `databricks-connect` /
  `databricks-sdk` APIs but not run end-to-end here — that needs a real
  workspace. If something's drifted by the time you run this, the SDK's
  own docstrings (`python3 -c "help(...)"`) are the fastest way to check
  a call's current shape.
