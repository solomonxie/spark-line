"""
Step 7: Reading and writing files — the I/O half of ETL.

Writes the same kind of dataset as the previous steps to local Parquet,
partitioned by borough, then reads it back to prove the round trip. Uses a
temp directory and cleans up after itself, so it's safe to re-run.

Run:
    python3 hello_07_read_write_files.py
"""
import os
import random
import shutil
import tempfile

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = (
    SparkSession.builder
    .appName("Hello07-ReadWriteFiles")
    .master(os.environ.get("SPARK_MASTER_URL", "local[*]"))
    .getOrCreate()
)

schema = StructType([
    StructField("borough", StringType(), False),
    StructField("trip_distance", DoubleType(), False),
    StructField("fare_amount", DoubleType(), False),
])

random.seed(7)
boroughs = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
data = [
    (random.choice(boroughs), round(random.uniform(0.5, 20.0), 2), round(random.uniform(5.0, 80.0), 2))
    for _ in range(200)
]

df = spark.createDataFrame(data, schema=schema)

output_dir = os.path.join(tempfile.gettempdir(), "hello_07_trips_parquet")
shutil.rmtree(output_dir, ignore_errors=True)

print(f"--- Writing partitioned Parquet to {output_dir} ---")
df.write.mode("overwrite").partitionBy("borough").parquet(output_dir)

print("--- Reading it back ---")
df_reloaded = spark.read.parquet(output_dir)
print(f"Rows read back: {df_reloaded.count()}")
df_reloaded.show(5)

shutil.rmtree(output_dir, ignore_errors=True)

spark.stop()
