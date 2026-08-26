"""
Step 3: ops and jobs — the lower-level API assets are built on.

Assets (steps 1-2) are Dagster's preferred shape for anything that
produces a persistent piece of data. Ops/jobs are the more general,
imperative building block underneath — closer to Airflow's operators/DAGs
— useful when a step doesn't really represent a durable "asset" at all
(sending a notification, kicking off an external system, ...).

Run:
    python3 dagster_03_ops_and_jobs.py
"""
from dagster import Definitions, job, op


@op
def extract() -> list[int]:
    return [1, 2, 3, 4, 5]


@op
def transform(numbers: list[int]) -> list[int]:
    return [n * 2 for n in numbers]


@op
def load(numbers: list[int]) -> None:
    print(f"loaded: {numbers}")


@job
def hello_job():
    load(transform(extract()))


defs = Definitions(jobs=[hello_job])


if __name__ == "__main__":
    result = hello_job.execute_in_process()
    assert result.success
