"""
Step 5: the TaskFlow API — `@dag`/`@task` instead of explicit operators.

Same extract/transform/load shape as step 2, but dependencies and XCom
passing (step 3) are both inferred from plain Python function calls and
arguments instead of `>>` and `xcom_pull`.

Run:
    python3 hello_airflow_05_taskflow_api.py
"""
from datetime import datetime

from airflow.decorators import dag, task


@dag(dag_id="hello_airflow_05", start_date=datetime(2024, 1, 1), schedule=None, catchup=False)
def hello_taskflow():
    @task
    def extract():
        return {"count": 42}

    @task
    def transform(data: dict):
        return data["count"] * 2

    @task
    def load(value: int):
        print(f"loaded: {value}")

    load(transform(extract()))


dag_instance = hello_taskflow()

if __name__ == "__main__":
    dag_instance.test()
