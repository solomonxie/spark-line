"""
Step 3: passing data between tasks via XCom.

A PythonOperator's return value is pushed to XCom automatically (under the
key `return_value`); a downstream task pulls it back out through its task
instance. This is how tasks — which may run on entirely different
machines — hand small values to each other.

Run:
    python3 hello_airflow_03_xcom_data_passing.py
"""
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def extract(**context):
    value = 42
    print(f"extracted: {value}")
    return value


def load(**context):
    value = context["ti"].xcom_pull(task_ids="extract")
    print(f"loaded value from XCom: {value}")


with DAG(
    dag_id="hello_airflow_03",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    t_extract = PythonOperator(task_id="extract", python_callable=extract)
    t_load = PythonOperator(task_id="load", python_callable=load)
    t_extract >> t_load


if __name__ == "__main__":
    dag.test()
