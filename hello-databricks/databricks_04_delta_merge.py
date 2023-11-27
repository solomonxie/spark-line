"""
Step 4: Delta MERGE — atomic upserts, no read-modify-write race.

Builds on step 3's hello_cities table: merges in a batch of "updates" that
both correct an existing row and add a new one, in one atomic statement.
Uses plain SQL (`MERGE INTO`) rather than the DeltaTable Python API, since
that API's Spark Connect support lags behind SQL's.

Run:
    python3 databricks_04_delta_merge.py
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

print(f"--- Ensuring {table} exists (from step 3) ---")
schema_def = StructType([
    StructField("city", StringType(), False),
    StructField("temperature_c", DoubleType(), False),
])
base_data = [("Toronto", 18.5), ("Miami", 29.1), ("Reykjavik", 7.2), ("Singapore", 31.0)]
spark.createDataFrame(base_data, schema=schema_def).write.mode("overwrite").saveAsTable(table)

print("--- Staging updates: correct Reykjavik, add Nairobi ---")
updates = [("Reykjavik", 9.0), ("Nairobi", 22.4)]
spark.createDataFrame(updates, schema=schema_def).createOrReplaceTempView("hello_cities_updates")

spark.sql(f"""
    MERGE INTO {table} AS target
    USING hello_cities_updates AS source
    ON target.city = source.city
    WHEN MATCHED THEN UPDATE SET target.temperature_c = source.temperature_c
    WHEN NOT MATCHED THEN INSERT (city, temperature_c) VALUES (source.city, source.temperature_c)
""")

print("--- Result ---")
spark.table(table).orderBy("city").show()

print("--- Delta transaction history (one row per MERGE/write) ---")
spark.sql(f"DESCRIBE HISTORY {table}").select("version", "timestamp", "operation").show()

spark.stop()
