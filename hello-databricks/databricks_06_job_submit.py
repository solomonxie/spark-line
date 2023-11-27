"""
Step 6 (capstone): submit a one-time Databricks Job run via the SDK.

Everything so far ran your local Python process against the cluster over
Databricks Connect. A Job is the other model: the code itself runs *on*
the cluster, submitted and monitored from here. This uploads a tiny
notebook to the workspace, submits it as a one-off run against the
../terraform cluster, and blocks until it finishes.

Run:
    python3 databricks_06_job_submit.py
"""
import base64
import os

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import NotebookTask, SubmitTask
from databricks.sdk.service.workspace import ImportFormat, Language

w = WorkspaceClient(
    host=os.environ["DATABRICKS_HOST"],
    token=os.environ["DATABRICKS_TOKEN"],
)

cluster_id = os.environ["DATABRICKS_CLUSTER_ID"]
notebook_path = f"/Workspace/Users/{w.current_user.me().user_name}/hello_databricks_job"

notebook_source = """# Databricks notebook source
print("hello from a Databricks Job, running on the cluster itself")
spark.range(1_000_000).selectExpr("sum(id) as total").show()
"""

print(f"--- Uploading notebook to {notebook_path} ---")
w.workspace.import_(
    notebook_path,
    content=base64.b64encode(notebook_source.encode()).decode(),
    format=ImportFormat.SOURCE,
    language=Language.PYTHON,
    overwrite=True,
)

print(f"--- Submitting a one-time run against cluster {cluster_id} ---")
run = w.jobs.submit(
    run_name="hello-databricks-step-06",
    tasks=[
        SubmitTask(
            task_key="hello",
            existing_cluster_id=cluster_id,
            notebook_task=NotebookTask(notebook_path=notebook_path),
        )
    ],
).result()

print(f"--- Run finished: {run.state.result_state} ---")
print(f"View it at: {os.environ['DATABRICKS_HOST']}/#job/{run.job_id}/run/{run.number_in_job}")
