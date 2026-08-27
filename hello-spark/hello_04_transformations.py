"""
Step 4: DataFrame transformations — derived columns, sorting, renaming.

Carries forward the same in-memory dataset as hello_03_dataframe_basics.py
and builds on it: new columns computed from existing ones, conditional
labeling, renaming, and ordering.

Run:
    python3 hello_04_transformations.py
"""
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, round as spark_round, when
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

spark = (
    SparkSession.builder
    .appName("Hello04-Transformations")
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

df_enriched = (
    df
    .withColumn("distance_per_rider", spark_round(col("trip_distance") / col("passenger_count"), 2))
    .withColumn(
        "trip_length",
        when(col("trip_distance") < 2, "short")
        .when(col("trip_distance") < 8, "medium")
        .otherwise("long"),
    )
    .withColumnRenamed("rider", "passenger_name")
)

print("--- Enriched + renamed ---")
df_enriched.show()

print("--- Sorted by trip_distance desc ---")
df_enriched.orderBy(col("trip_distance").desc()).show()

print("--- Distinct boroughs ---")
df_enriched.select("borough").distinct().show()

spark.stop()
