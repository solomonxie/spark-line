# hello-databricks

Experiments on Databricks — Unity Catalog, Delta Lake, and the managed
Jobs runtime — from your own machine via Databricks Connect. Infra is
throwaway: spin up a cluster, poke at it, tear down. Unlike this repo's
other projects, every script here needs a real workspace and a running
cluster — no local fallback.

`make deploy-infra` provisions the cluster and a Unity Catalog
schema/volume; `make start-cluster` / `make stop-cluster` resume/stop it
(needs the `databricks` CLI configured separately); `make destroy-infra`
tears down. No EventBridge rule here — the cluster's own idle-shutdown
setting stops it after inactivity.

A progressive, self-contained set of scripts walks through one Databricks
concept at a time beyond plain PySpark — run any directly once Databricks
Connect is installed and the workspace/cluster/catalog environment
variables (from Terraform's outputs) are exported.

## Notes

- These scripts are checked against current Databricks Connect/SDK APIs
  but not run end-to-end here — that needs a real workspace.
