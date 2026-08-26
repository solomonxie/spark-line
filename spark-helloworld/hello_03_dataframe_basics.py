"""
Step 3: DataFrames — Spark's structured, higher-level API over RDDs.

Same SparkSession setup as before; this time the data is a small in-memory
table with an explicit schema instead of a raw RDD of numbers.

Run:
    python3 hello_03_dataframe_basics.py
"""
import os

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

spark = (
    SparkSession.builder
    .appName("Hello03-DataFrameBasics")
    .master(os.environ.get("SPARK_MASTER_URL", "local[*]"))
    .getOrCreate()
)

schema = StructType([
    StructField("rider", StringType(), False),
    StructField("borough", StringType(), False),
    StructField("trip_distance", DoubleType(), False),
    StructField("passenger_count", IntegerType(), False),
])

data = [
    ("Alice", "Manhattan", 2.4, 1),
    ("Bob", "Brooklyn", 5.1, 2),
    ("Carol", "Queens", 0.8, 1),
    ("Dan", "Manhattan", 12.3, 4),
    ("Eve", "Bronx", 3.6, 1),
]

df = spark.createDataFrame(data, schema=schema)

print("--- Schema ---")
df.printSchema()

print("--- All rows ---")
df.show()

print("--- select + filter (trips over 2 miles) ---")
df.select("rider", "trip_distance").filter(df.trip_distance > 2.0).show()

spark.stop()
