# Terraform

Provisions a single-node cluster and a Unity Catalog schema/volume inside
an existing Databricks workspace — no `ansible/` here, since Databricks
manages the cluster's runtime itself.

Run through the repo-root `Makefile` (`make deploy-infra`), not `terraform
apply` directly.

```
terraform apply
  ├─ providers.tf        → auth against the workspace (host + token)
  ├─ variables.tf        → resolve inputs
  ├─ cluster.tf           → look up a Spark version + node type → single-node cluster
  ├─ unity_catalog.tf     → schema + managed volume under var.catalog_name
  └─ outputs.tf           → cluster_id, schema, volume_path
        │
        ▼
  DATABRICKS_HOST / DATABRICKS_TOKEN / DATABRICKS_CLUSTER_ID
        │
        ▼
  python3 databricks_01_connect_session.py ... (Databricks Connect, from your machine)
```

## `terraform.tfvars`

Gitignored, not committed. Create it with:

```
databricks_host  = "https://<workspace-id>.cloud.databricks.com"
databricks_token = "<personal access token>"
```

(`catalog_name`, `schema_name`, `autotermination_minutes` all have
defaults — override here if needed.)

## Self-termination

No EventBridge rule to write here — `databricks_cluster.hello`'s
`autotermination_minutes` (default 30) is Databricks' own built-in
equivalent: the cluster stops itself after that many idle minutes. Its
*definition* still exists (in Terraform state) until you `terraform
destroy` or `make stop-cluster`; only the running compute goes away.
