# spark-line

Experimenting with Apache Spark end to end — standalone mode,
clustering, and data processing.

Each subdirectory is a self-contained, throwaway environment: spin up,
experiment, tear down.

## Projects

- [`spark-helloworld/`](spark-helloworld/) — single-node Spark master/worker
  on one EC2 instance, provisioned with Terraform + Ansible. Starting point
  for standalone-mode basics.
- [`spark-cluster/`](spark-cluster/) — multi-node Spark cluster.


## Conventions

Each project directory owns its own Terraform state, Ansible inventory, and
`Makefile` (`deploy-infra`, `deploy-software`, `start-server`,
`stop-server`, `destroy-infra`) — see that project's README for specifics.
