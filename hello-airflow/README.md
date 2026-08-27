# hello-airflow

Sandbox for experimenting with Apache Airflow — DAGs, task dependencies,
XComs, and the TaskFlow API. Infra is throwaway: spin up, poke at it, tear
down.

## How to use this

```
make deploy-infra       # terraform apply — creates the EC2 node
make deploy-software    # ansible-playbook — installs & starts Airflow

make start-server       # aws ec2 start-instances (resume a stopped node)
make stop-server        # aws ec2 stop-instances (save cost when idle)
make destroy-infra      # terraform destroy — tear everything down
```

`AWS_PROFILE` defaults to `prod`; override with
`make deploy-infra AWS_PROFILE=<profile>`.

`deploy-software` also deploys the progressive study-path DAGs into the
node's `dags/` folder, so they show up in the webserver UI too. Webserver:
`http://<public-ip>:8080` (`terraform -chdir=terraform output
airflow_webserver_url`), login `admin` / `admin`.

## Progressive study path

Eight standalone scripts, `hello_airflow_01_...py` through
`hello_airflow_08_...py`, one Airflow concept each. Fully self-contained —
own DAG, no imports between them — and runnable via `DAG.test()` (Airflow
2.5+) against a throwaway SQLite database, no webserver/scheduler/EC2 node
required.

| Step | File | Concept |
| --- | --- | --- |
| 1 | `hello_airflow_01_hello_dag.py` | The smallest DAG; `DAG.test()` |
| 2 | `hello_airflow_02_task_dependencies.py` | Wiring tasks with `>>` |
| 3 | `hello_airflow_03_xcom_data_passing.py` | Passing values between tasks via XCom |
| 4 | `hello_airflow_04_branching.py` | `BranchPythonOperator` + trigger rules |
| 5 | `hello_airflow_05_taskflow_api.py` | The `@dag`/`@task` decorator API |
| 6 | `hello_airflow_06_retries.py` | `retries`/`retry_delay` on a failing task |
| 7 | `hello_airflow_07_schedule_and_sensors.py` | `schedule` + a polling `PythonSensor` |
| 8 | `hello_airflow_08_real_pipeline.py` | Capstone: a real extract/transform/load pipeline |

One-time setup (local venv or SSH'd into the node):

```
python3 -m venv venv && venv/bin/pip install apache-airflow
export AIRFLOW_HOME=$(pwd)/.airflow_home
venv/bin/airflow db migrate
```

Then run any step directly:

```
venv/bin/python hello_airflow_01_hello_dag.py
```

## Self-termination

The node auto-terminates ~2h after creation via a one-time EventBridge
rule (see `terraform/auto_terminate.tf`). Re-running `make deploy-infra`
doesn't push the deadline out — destroy/recreate, or extend
`auto_terminate.tf` yourself.

## Notes

- Airflow and Python versions must stay compatible with each other's
  constraints file — see `ansible/README.md`. Bump `airflow_version` in
  `ansible/roles/admin/vars/main.yml` to upgrade.
