"""
Step 1: the smallest possible DAG, run without a scheduler.

`DAG.test()` (Airflow 2.5+) executes every task in dependency order using
a throwaway local database — no webserver, no scheduler, no other infra
required. That's what makes every file in this study path runnable on its
own with a plain `python3`.

Run:
    python3 hello_airflow_01_hello_dag.py
"""
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def say_hello():
    print("hello from Airflow")


with DAG(
    dag_id="hello_airflow_01",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    PythonOperator(task_id="say_hello", python_callable=say_hello)


if __name__ == "__main__":
    dag.test()
