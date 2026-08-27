# spark-line

Experimenting with Apache Spark and the data-engineering stack around it,
end to end. Each subdirectory ([`hello-spark/`](hello-spark/),
[`spark-1b-rows-challenge/`](spark-1b-rows-challenge/),
[`hello-databricks/`](hello-databricks/),
[`hello-airflow/`](hello-airflow/), [`hello-dbt/`](hello-dbt/),
[`hello-dagster/`](hello-dagster/)) is a self-contained, throwaway
environment: spin up, experiment, tear down.

## Conventions

Most projects own their Terraform state, Ansible inventory, and `Makefile`
(`deploy-infra`, `deploy-software`, `start-server`, `stop-server`,
`destroy-infra`) — see each README for specifics and deviations (e.g.
`hello-databricks` has no Ansible).

Nodes self-terminate a couple hours after creation as a cost safety net
(see each `terraform/`).
