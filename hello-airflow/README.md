# hello-airflow

Sandbox for experimenting with Apache Airflow — DAGs, task dependencies,
XComs, and the TaskFlow API. Infra is throwaway: spin up, poke at it, tear
down.

`make deploy-infra && make deploy-software` provisions the node and starts
Airflow standalone with the study-path DAGs deployed (webserver:
`http://<public-ip>:8080`, login `admin`/`admin`); `make destroy-infra`
tears down. Node self-terminates ~2h after creation regardless — see
`terraform/auto_terminate.tf`.

`hello_airflow_01_hello_dag.py` → `hello_airflow_08_real_pipeline.py` are
a progressive, self-contained study path, one Airflow concept per file —
run any directly with `venv/bin/python hello_airflow_01_hello_dag.py`
(`python3 -m venv venv && venv/bin/pip install apache-airflow && export
AIRFLOW_HOME=$(pwd)/.airflow_home && venv/bin/airflow db migrate` first).

## Notes

- Airflow and Python versions must stay compatible with each other's
  constraints file — see `ansible/README.md`. Bump `airflow_version` in
  `ansible/roles/admin/vars/main.yml` to upgrade.
