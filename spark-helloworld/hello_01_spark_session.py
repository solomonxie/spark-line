"""
Step 1: create a SparkSession and run your first distributed job.

A SparkSession is the entry point to everything else in this study path.
`master()` picks where the work actually runs — "local[*]" here means "on
this machine, using all cores", no cluster required.

Run:
    python3 hello_01_spark_session.py

Against the real standalone cluster from ../terraform + ../ansible instead:
    SPARK_MASTER_URL=spark://<master-host>:7077 python3 hello_01_spark_session.py
"""
import os

from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("Hello01-SparkSession")
    .master(os.environ.get("SPARK_MASTER_URL", "local[*]"))
    .getOrCreate()
)

print(f"Spark version: {spark.version}")
print(f"Master: {spark.sparkContext.master}")

# The classic distributed count: a million numbers spread across partitions
# and counted in parallel.
rdd = spark.sparkContext.parallelize(range(1, 1_000_001))
print(f"Total count: {rdd.count()}")

spark.stop()
