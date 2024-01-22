"""
Step 7: a schedule, plus a sensor that waits for a condition before
letting downstream tasks run.

`schedule` only matters to a live scheduler (it decides *when* a DAG run
gets created) — `dag.test()` always runs immediately regardless, so this
step is really about the sensor: `check_ready` is polled every
`poke_interval` seconds until it returns True or `timeout` is hit.

Run:
    python3 hello_airflow_07_schedule_and_sensors.py
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor


def check_ready():
    print("condition met immediately, for this demo")
    return True


def do_work():
    print("doing work now that the sensor is satisfied")


with DAG(
    dag_id="hello_airflow_07",
    start_date=datetime(2024, 1, 1),
    schedule=timedelta(hours=1),
    catchup=False,
) as dag:
    wait = PythonSensor(
        task_id="wait_for_ready",
        python_callable=check_ready,
        poke_interval=1,
        timeout=10,
    )
    work = PythonOperator(task_id="do_work", python_callable=do_work)
    wait >> work


if __name__ == "__main__":
    dag.test()
