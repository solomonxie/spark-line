# spark-line

Experimenting with Apache Spark end to end.

Each subdirectory is a self-contained, throwaway environment: spin up,
experiment, tear down.

## Projects

- [`spark-helloworld/`](spark-helloworld/) — single-node Spark master/worker
  on one EC2 instance, provisioned with Terraform + Ansible. Starting point
  for standalone-mode basics.

- [`spark-1b-rows-challenge/`](spark-1b-rows-challenge/) — the [One Billion
  Row Challenge (1BRC)](https://github.com/gunnarmorling/1brc) done in
  PySpark: read a
  ~1 billion row `station;temperature` file and emit sorted per-station
  min/mean/max, on a single t3.xlarge node (1 driver + 2 workers) without
  OOM-killing an executor or spilling the aggregation to disk.


## Conventions

Each project directory owns its own Terraform state, Ansible inventory, and
`Makefile` (`deploy-infra`, `deploy-software`, `start-server`,
`stop-server`, `destroy-infra`) — see that project's README for specifics.

Nodes self-terminate a couple hours after creation as a cost safety net
(see each project's `terraform/` for specifics).
