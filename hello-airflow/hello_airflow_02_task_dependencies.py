"""
Step 2: wiring tasks together with `>>`.

Three tasks — extract, transform, load — chained in order. Airflow infers
the DAG's shape from these dependency operators, not from the order the
tasks are defined in the file.

Run:
    python3 hello_airflow_02_task_dependencies.py
"""
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def extract():
    print("extracting data")


def transform():
    print("transforming data")


def load():
    print("loading data")


with DAG(
    dag_id="hello_airflow_02",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    t_extract = PythonOperator(task_id="extract", python_callable=extract)
    t_transform = PythonOperator(task_id="transform", python_callable=transform)
    t_load = PythonOperator(task_id="load", python_callable=load)

    t_extract >> t_transform >> t_load


if __name__ == "__main__":
    dag.test()
