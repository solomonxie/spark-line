"""
Step 4: conditional paths with BranchPythonOperator.

`choose_branch` returns the task_id to run next; Airflow skips every
sibling not on that path. `join`'s trigger_rule matters here — the default
("all_success") would mark it skipped too, since exactly one of its two
upstream tasks is always skipped by design.

Run:
    python3 hello_airflow_04_branching.py
"""
import random
from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator


def choose_branch():
    # Seeded for a reproducible demo run, not real randomness.
    return "high_path" if random.Random(7).random() > 0.5 else "low_path"


def high():
    print("took the high path")


def low():
    print("took the low path")


with DAG(
    dag_id="hello_airflow_04",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    branch = BranchPythonOperator(task_id="branch", python_callable=choose_branch)
    high_path = PythonOperator(task_id="high_path", python_callable=high)
    low_path = PythonOperator(task_id="low_path", python_callable=low)
    join = EmptyOperator(task_id="join", trigger_rule="none_failed_min_one_success")

    branch >> [high_path, low_path] >> join


if __name__ == "__main__":
    dag.test()
