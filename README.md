# spark-line

Experimenting with Apache Spark and the data-engineering stack around it,
end to end.

Each subdirectory is a self-contained, throwaway environment: spin up,
experiment, tear down.

## Projects

- [`hello-spark/`](hello-spark/) — single-node Spark master/worker on EC2
  (Terraform + Ansible), an 8-step PySpark study path, and JupyterLab.

- [`spark-1b-rows-challenge/`](spark-1b-rows-challenge/) — the [One Billion
  Row Challenge](https://github.com/gunnarmorling/1brc) in PySpark: read
  ~1 billion `station;temperature` rows and emit sorted per-station
  min/mean/max on a single t3.xlarge (1 driver + 2 workers), no OOM, no
  spill.

- [`hello-databricks/`](hello-databricks/) — single-node Databricks cluster
  + Unity Catalog, driven from your machine via Databricks Connect. Delta
  tables, MERGE, Volumes, Jobs.

- [`hello-airflow/`](hello-airflow/) — Airflow standalone on EC2 (Terraform
  + Ansible). DAGs, XComs, branching, TaskFlow, retries — runnable locally
  via `DAG.test()`.

- [`hello-dbt/`](hello-dbt/) — dbt against local DuckDB, no infra. Models,
  `ref()`, incremental builds, tests, macros, with an optional EC2 Postgres
  target.

- [`hello-dagster/`](hello-dagster/) — Dagster (`dagster dev`) on EC2
  (Terraform + Ansible). Assets, resources, IO managers, partitions,
  schedules/sensors — runnable locally via `materialize()`.

## Conventions

Most projects own their Terraform state, Ansible inventory, and `Makefile`
(`deploy-infra`, `deploy-software`, `start-server`, `stop-server`,
`destroy-infra`) — see each README for specifics and deviations (e.g.
`hello-databricks` has no Ansible).

Nodes self-terminate a couple hours after creation as a cost safety net
(see each `terraform/`).
