"""
Step 6: Window functions — rank rows within a group without a self-join.

Same synthetic dataset as hello_05_aggregations.py; instead of collapsing
each borough into one summary row, this ranks individual trips within
their borough and keeps only the top 3 by fare.

Run:
    python3 hello_06_window_functions.py
"""
import os
import random

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, dense_rank
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = (
    SparkSession.builder
    .appName("Hello06-WindowFunctions")
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

window_spec = Window.partitionBy("borough").orderBy(col("fare_amount").desc())

top_trips = (
    df
    .withColumn("rank", dense_rank().over(window_spec))
    .filter(col("rank") <= 3)
    .select("borough", "rank", "fare_amount", "trip_distance")
    .orderBy("borough", "rank")
)

print("--- Top 3 highest-fare trips per borough ---")
top_trips.show(20)

spark.stop()
