# hello-databricks

Sandbox for experimenting with Databricks — Unity Catalog, Delta Lake, and
the managed Jobs runtime — from your own machine via Databricks Connect.
Infra is throwaway: spin up a cluster, poke at it, tear down.

Unlike this repo's other `hello-*` projects, there's no local fallback:
every script here needs a real workspace and a running cluster — no
`local[*]` equivalent.

## How to use this

```
make deploy-infra     # terraform apply — creates the cluster + schema/volume
make start-cluster     # databricks clusters start — resume a stopped cluster
make stop-cluster      # databricks clusters delete — stop it, keep the definition
make destroy-infra     # terraform destroy — tear everything down
```

`start-cluster`/`stop-cluster` need the `databricks` CLI configured
separately from Terraform (`databricks auth login`, or reuse
`DATABRICKS_HOST`/`DATABRICKS_TOKEN`).

## Progressive study path

Six standalone scripts, one Databricks concept each beyond plain PySpark
(see `../hello-spark` for fundamentals). Self-contained, though none can
run without a real workspace and cluster.

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
Runtime major version.

## Self-termination

No EventBridge rule here — `terraform/cluster.tf`'s
`autotermination_minutes` (default 30) is Databricks' own idle-shutdown,
set on the cluster.

## Notes

- These scripts are checked against current `databricks-connect`/
  `databricks-sdk` APIs but not run end-to-end here — that needs a real
  workspace. If something's drifted, the SDK's own docstrings (`python3 -c
  "help(...)"`) are the fastest check.
