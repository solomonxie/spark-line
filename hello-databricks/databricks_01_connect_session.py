"""
Step 1: connect to a real Databricks cluster from your own machine.

Unlike plain PySpark's local[*] mode (see ../spark-helloworld), there's no
local fallback here — Databricks Connect always drives a real, already-
running cluster over the network. Also note Spark Connect (what Databricks
Connect is built on) is DataFrame/SQL-only — no sparkContext/RDD API.

Requires the cluster from ../terraform (or any cluster you already have)
and:
    export DATABRICKS_HOST=https://<workspace-id>.cloud.databricks.com
    export DATABRICKS_TOKEN=<personal-access-token>
    export DATABRICKS_CLUSTER_ID=$(terraform -chdir=../terraform output -raw cluster_id)

Run:
    python3 databricks_01_connect_session.py
"""
import os

from databricks.connect import DatabricksSession

spark = (
    DatabricksSession.builder
    .remote(
        host=os.environ["DATABRICKS_HOST"],
        token=os.environ["DATABRICKS_TOKEN"],
        cluster_id=os.environ["DATABRICKS_CLUSTER_ID"],
    )
    .getOrCreate()
)

print(f"Connected to cluster: {os.environ['DATABRICKS_CLUSTER_ID']}")

# spark.range(...) is a DataFrame, not an RDD — this count runs on the
# cluster, not on your machine.
total = spark.range(1, 1_000_001).count()
print(f"Total count (computed on the cluster): {total}")

spark.stop()
