"""
Step 2: DataFrame basics over a remote connection.

Same DataFrame API as plain PySpark (see ../spark-helloworld/hello_03_*)
— the only difference from here on is that every operation is shipped to
and executed on the cluster via Spark Connect, then only the result (e.g.
what .show()/.collect() needs) comes back to your machine.

Run:
    python3 databricks_02_dataframe_basics.py
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

schema = StructType([
    StructField("city", StringType(), False),
    StructField("temperature_c", DoubleType(), False),
])

data = [
    ("Toronto", 18.5),
    ("Miami", 29.1),
    ("Reykjavik", 7.2),
    ("Singapore", 31.0),
]

df = spark.createDataFrame(data, schema=schema)

print("--- Schema ---")
df.printSchema()

print("--- All rows ---")
df.show()

print("--- Cities over 20C ---")
df.filter(df.temperature_c > 20).show()

spark.stop()
