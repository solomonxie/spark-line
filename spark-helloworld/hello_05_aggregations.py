"""
Step 5: Aggregations — groupBy + agg, the bread and butter of Spark ETL.

Same dataset shape as before, scaled up to 200 synthetic rows (a fixed seed
keeps it reproducible) so the group-by has something more interesting to
summarize than five hand-picked rows.

Run:
    python3 hello_05_aggregations.py
"""
import os
import random

from pyspark.sql import SparkSession
from pyspark.sql.functions import count, avg, max as spark_max, round as spark_round
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = (
    SparkSession.builder
    .appName("Hello05-Aggregations")
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

summary = df.groupBy("borough").agg(
    count("*").alias("total_trips"),
    spark_round(avg("trip_distance"), 2).alias("avg_distance_miles"),
    spark_round(avg("fare_amount"), 2).alias("avg_fare_usd"),
    spark_max("trip_distance").alias("max_distance_miles"),
)

print("--- Per-borough summary ---")
summary.orderBy("borough").show()

spark.stop()
