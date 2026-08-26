# spark-line

Experimenting with Apache Spark and the data-engineering stack around it,
end to end.

Each subdirectory is a self-contained, throwaway environment: spin up,
experiment, tear down.

## Projects

- [`spark-helloworld/`](spark-helloworld/) — single-node Spark master/worker
  on one EC2 instance, provisioned with Terraform + Ansible. Starting point
  for standalone-mode basics, with an 8-step progressive PySpark study path.

- [`spark-1b-rows-challenge/`](spark-1b-rows-challenge/) — the [One Billion
  Row Challenge (1BRC)](https://github.com/gunnarmorling/1brc) done in
  PySpark: read a
  ~1 billion row `station;temperature` file and emit sorted per-station
  min/mean/max, on a single t3.xlarge node (1 driver + 2 workers) without
  OOM-killing an executor or spilling the aggregation to disk.

- [`hello-databricks/`](hello-databricks/) — a single-node Databricks
  cluster + Unity Catalog schema/volume, provisioned with Terraform, driven
  from your own machine via Databricks Connect. Progressive path through
  Delta tables, MERGE upserts, Volumes, and submitting a Databricks Job.


## Conventions

Most project directories own their own Terraform state, Ansible inventory,
and `Makefile` (`deploy-infra`, `deploy-software`, `start-server`,
`stop-server`, `destroy-infra`) — see each project's README for specifics
and for where it deviates (e.g. `hello-databricks` has no Ansible; managed
services don't need one).

Nodes self-terminate a couple hours after creation as a cost safety net
(see each project's `terraform/` for specifics).
