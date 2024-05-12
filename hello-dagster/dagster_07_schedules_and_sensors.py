"""
Step 7: schedules and sensors — deciding *when* a job should run.

Neither one runs anything by itself; on a real deployment, `dagster-daemon`
polls them continuously. Locally, Dagster's testing utilities
(`build_schedule_context`/`build_sensor_context`) let you invoke the
decorated function directly and inspect what it decided, the same spirit
as ../hello-airflow's `DAG.test()`.

Run:
    python3 dagster_07_schedules_and_sensors.py
"""
from dagster import (
    Definitions,
    RunRequest,
    ScheduleEvaluationContext,
    SensorEvaluationContext,
    build_schedule_context,
    build_sensor_context,
    job,
    op,
    schedule,
    sensor,
)


@op
def do_work():
    print("doing work")


@job
def hello_job():
    do_work()


@schedule(cron_schedule="0 0 * * *", job=hello_job)
def daily_schedule(context: ScheduleEvaluationContext) -> RunRequest:
    return RunRequest(run_key=None)


@sensor(job=hello_job)
def demo_sensor(context: SensorEvaluationContext) -> RunRequest:
    # A real sensor would check for a new file, a queue message, etc. —
    # always-true here so this demo actually produces a run.
    return RunRequest(run_key="demo-run")


defs = Definitions(jobs=[hello_job], schedules=[daily_schedule], sensors=[demo_sensor])


if __name__ == "__main__":
    schedule_request = daily_schedule(build_schedule_context())
    print(f"schedule produced: {schedule_request}")

    sensor_request = demo_sensor(build_sensor_context())
    print(f"sensor produced: {sensor_request}")

    result = hello_job.execute_in_process()
    assert result.success
