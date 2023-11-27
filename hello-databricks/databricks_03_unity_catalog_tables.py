"""
Step 3: managed Delta tables in Unity Catalog.

Every Databricks table lives at a three-level `catalog.schema.table`
address and is Delta by default — this writes one into the schema
../terraform created, then reads it back by name (no path required,
unlike plain PySpark's file-based tables).

Requires the schema from ../terraform, in addition to step 1's env vars:
    export DATABRICKS_CATALOG=$(terraform -chdir=../terraform output -raw unity_catalog_schema | cut -d. -f1)
    export DATABRICKS_SCHEMA=$(terraform -chdir=../terraform output -raw unity_catalog_schema | cut -d. -f2)

Run:
    python3 databricks_03_unity_catalog_tables.py
"""
import os

from databricks.connect import DatabricksSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = (
    DatabricksSession.builder
    .remote(
        host=os.environ["DATABRICKS_HOST"],
        token=os.environ["DATABRICKS_TOKEN"],
        cluster_id=os.environ["DATABRICKS_CLUSTER_ID"],
    )
    .getOrCreate()
)

catalog = os.environ["DATABRICKS_CATALOG"]
schema = os.environ["DATABRICKS_SCHEMA"]
table = f"{catalog}.{schema}.hello_cities"

schema_def = StructType([
    StructField("city", StringType(), False),
    StructField("temperature_c", DoubleType(), False),
])
data = [("Toronto", 18.5), ("Miami", 29.1), ("Reykjavik", 7.2), ("Singapore", 31.0)]
df = spark.createDataFrame(data, schema=schema_def)

print(f"--- Writing managed Delta table {table} ---")
df.write.mode("overwrite").saveAsTable(table)

print("--- Reading it back by name ---")
spark.table(table).orderBy("city").show()

print("--- Same thing, via SQL ---")
spark.sql(f"SELECT city, temperature_c FROM {table} ORDER BY temperature_c DESC").show()

spark.stop()
