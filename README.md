# spark-line

Experiments on Apache Spark and the data-engineering stack around it, end
to end. Each subdirectory is a self-contained, throwaway environment: spin
up, experiment, tear down.

## Conventions

Most projects own their Terraform state, Ansible inventory, and `Makefile`
(`deploy-infra`, `deploy-software`, `start-server`, `stop-server`,
`destroy-infra`) — see each project's README for specifics and deviations
(some have no Ansible).

Nodes self-terminate a couple hours after creation as a cost safety net.
