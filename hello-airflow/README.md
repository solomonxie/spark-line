# hello-airflow

Experiments on Apache Airflow — DAGs, task dependencies, XComs, and the
TaskFlow API. Infra is throwaway: spin up, poke at it, tear down.

`make deploy-infra && make deploy-software` provisions the node and starts
Airflow standalone with the study-path DAGs deployed (webserver:
`http://<public-ip>:8080`, login `admin`/`admin`); `make destroy-infra`
tears down. The node also self-terminates ~2h after creation regardless.

A progressive, self-contained set of DAGs walks through one Airflow
concept at a time, each runnable on its own locally, no scheduler
required.

## Notes

- Airflow and Python versions must stay compatible with each other's
  constraints file — pinned together in the Ansible role that installs
  Airflow.
