"""
Step 2: RDD transformations and actions.

Carries forward hello_01_spark_session.py's SparkSession + parallelize
call, then layers on map/filter/reduce — Spark's original (pre-DataFrame)
API. Transformations (map, filter) are lazy; actions (take, count, reduce,
collect) are what actually trigger a job.

Run:
    python3 hello_02_rdd_basics.py
"""
import os

from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("Hello02-RDDBasics")
    .master(os.environ.get("SPARK_MASTER_URL", "local[*]"))
    .getOrCreate()
)
sc = spark.sparkContext

numbers = sc.parallelize(range(1, 1_000_001))

squares = numbers.map(lambda n: n * n)
print(f"First 5 squares: {squares.take(5)}")

evens = numbers.filter(lambda n: n % 2 == 0)
print(f"Even count: {evens.count()}")

total = numbers.reduce(lambda a, b: a + b)
print(f"Sum 1..1,000,000: {total}")

# A tiny word count — flatMap to split lines into words, then reduceByKey
# to sum occurrences per key, the same shape as the canonical Spark example.
word_counts = (
    sc.parallelize(["spark is fast", "spark is distributed", "spark is fun"])
    .flatMap(lambda line: line.split(" "))
    .map(lambda word: (word, 1))
    .reduceByKey(lambda a, b: a + b)
    .collect()
)
print(f"Word counts: {sorted(word_counts)}")

spark.stop()
