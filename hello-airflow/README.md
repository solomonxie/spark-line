# hello-airflow

Sandbox for experimenting with Apache Airflow — DAGs, task dependencies,
XComs, and the TaskFlow API. Infra is throwaway by design: spin up, poke
at it, tear down.

## Layout

- `terraform/` — provisions the EC2 node this project runs on and writes
  its address into the Ansible inventory. See `terraform/README.md` for
  the resource graph and the self-termination safety net.
- `ansible/` — installs a Python venv, Apache Airflow, and runs it
  standalone as a systemd service. See `ansible/README.md`.
- `hello_airflow_01_hello_dag.py` ... `hello_airflow_08_real_pipeline.py`
  — a progressive study path, one Airflow concept per file. See below.
- `Makefile` — day-to-day commands, wraps Terraform/Ansible/AWS CLI calls
  (see below).

## How to use this

```
make deploy-infra       # terraform apply — creates the EC2 node
make deploy-software    # ansible-playbook — installs & starts Airflow

make start-server       # aws ec2 start-instances (resume a stopped node)
make stop-server        # aws ec2 stop-instances (save cost when idle)
make destroy-infra      # terraform destroy — tear everything down
```

`AWS_PROFILE` defaults to `prod` in the Makefile; override with
`make deploy-infra AWS_PROFILE=<profile>`.

`deploy-software` also deploys the progressive study-path DAGs into the
node's `dags/` folder, so they show up in the webserver UI too. Webserver:
`http://<public-ip>:8080` (`terraform -chdir=terraform output
airflow_webserver_url`), login `admin` / `admin`.

## Progressive study path

Eight standalone scripts, `hello_airflow_01_...py` through
`hello_airflow_08_...py`, each covering one Airflow concept. Every file is
fully self-contained — its own DAG, no imports between them — and runs on
its own via `DAG.test()` (Airflow 2.5+), which executes the whole DAG
locally against a throwaway SQLite database. No webserver, no scheduler,
no EC2 node required to work through the path.

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

One-time setup (any machine with `apache-airflow` installed — a local
venv, or SSH'd into the node):

```
python3 -m venv venv && venv/bin/pip install apache-airflow
export AIRFLOW_HOME=$(pwd)/.airflow_home
venv/bin/airflow db migrate
```

Then run any step directly:

```
venv/bin/python hello_airflow_01_hello_dag.py
```

All eight were run end to end against Airflow 2.10.5 while writing this
(including step 6 genuinely retrying and succeeding on its second
attempt) — pin that version if you want the exact behavior described
above.

## Self-termination

The node auto-terminates ~2h after creation via a one-time EventBridge
Scheduler rule (cost safety net, no action needed) — see
`terraform/auto_terminate.tf`. If you're still using the node past that
window, re-running `make deploy-infra` does **not** push the deadline out;
you'd need to destroy/recreate it, or extend `auto_terminate.tf` yourself.

## Notes

- Airflow version and Python version must stay compatible with each
  other's constraints file — see the note in `ansible/README.md`. Bump
  `airflow_version` in `ansible/roles/admin/vars/main.yml` to upgrade.
