"""
Step 8 (capstone): a real-world ETL job, end to end.

Downloads a real NYC Yellow Taxi trip file if it's not already present
(the same dataset manual_build.sh introduces by hand), then runs the same
kind of pipeline as the earlier steps against it instead of synthetic
data: schema-driven read, cleaning, a derived column, a groupBy summary,
a window-ranked top-N, and a partitioned Parquet write.

See ../spark_etl.py for a leaner version of this same pipeline that
assumes the file is already downloaded.

Run:
    python3 hello_08_real_world_etl.py
"""
import os
import urllib.request

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    round as spark_round,
    unix_timestamp,
    count,
    avg,
    max as spark_max,
    dense_rank,
)
from pyspark.sql.window import Window

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"
DATA_PATH = os.path.join(SCRIPT_DIR, "yellow_taxi_2023_01.parquet")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "hello_08_top_trips")

if not os.path.exists(DATA_PATH):
    print(f"--- Downloading sample dataset to {DATA_PATH} ---")
    urllib.request.urlretrieve(DATA_URL, DATA_PATH)

spark = (
    SparkSession.builder
    .appName("Hello08-RealWorldETL")
    .master(os.environ.get("SPARK_MASTER_URL", "local[*]"))
    .getOrCreate()
)

print("--- 1. Reading Parquet file ---")
df = spark.read.parquet(f"file://{DATA_PATH}")
print(f"Total input records: {df.count()}")

print("--- 2. Cleaning & deriving trip_duration_min ---")
df_cleaned = df.filter(
    (col("passenger_count") > 0)
    & (col("trip_distance") > 0)
    & (col("fare_amount") > 0)
).withColumn(
    "trip_duration_min",
    spark_round((unix_timestamp("tpep_dropoff_datetime") - unix_timestamp("tpep_pickup_datetime")) / 60, 2),
)

print("--- 3. Per-vendor summary ---")
vendor_summary = df_cleaned.groupBy("VendorID").agg(
    count("*").alias("total_trips"),
    spark_round(avg("trip_distance"), 2).alias("avg_distance_miles"),
    spark_round(avg("fare_amount"), 2).alias("avg_fare_usd"),
    spark_max("trip_distance").alias("max_distance_miles"),
)
vendor_summary.show()

print("--- 4. Top 3 longest trips per vendor ---")
window_spec = Window.partitionBy("VendorID").orderBy(col("trip_distance").desc())
top_trips = (
    df_cleaned
    .withColumn("rank", dense_rank().over(window_spec))
    .filter(col("rank") <= 3)
    .select("VendorID", "rank", "trip_distance", "fare_amount", "trip_duration_min")
)
top_trips.show()

print(f"--- 5. Writing partitioned Parquet output to {OUTPUT_PATH} ---")
top_trips.write.mode("overwrite").partitionBy("VendorID").parquet(OUTPUT_PATH)

print("--- Job completed successfully ---")
spark.stop()
