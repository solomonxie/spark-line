"""
Step 6: retries — a task that fails, then succeeds on a later attempt.

`default_args` applies to every task in the DAG; here it gives `flaky` two
extra attempts with a short delay between them, instead of failing the
whole run on the first error.

Run:
    python3 hello_airflow_06_retries.py
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# Module-level state so retries within one `dag.test()` run can observe
# progress across attempts — not something a real task should rely on
# (real tasks may retry on a different worker/process entirely).
_attempts = {"count": 0}


def flaky():
    _attempts["count"] += 1
    print(f"attempt {_attempts['count']}")
    if _attempts["count"] < 2:
        raise RuntimeError("simulated transient failure")
    print("succeeded")


with DAG(
    dag_id="hello_airflow_06",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(seconds=1)},
) as dag:
    PythonOperator(task_id="flaky", python_callable=flaky)


if __name__ == "__main__":
    dag.test()
