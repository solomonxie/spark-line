"""
Step 2 (Task 3): per-station aggregation via native groupBy().agg(...).

Not a row-at-a-time UDF, not a driver-side collect-then-reduce — min/mean/max
computed by Spark's built-in aggregate functions so the work happens as a
map-side partial aggregation on the executors, with only one shuffle to
combine partial results per station.

`.explain()` on the result should show `HashAggregate` (partial) before the
shuffle `Exchange`, then a second `HashAggregate` (final) after it — that's
the plan shape Task 5's acceptance criteria checks for at full scale.

Run:
    python3 job_02_aggregate.py
"""
import os
import random
import tempfile

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

MEASUREMENT_SCHEMA = StructType([
    StructField("station", StringType(), False),
    StructField("temperature", DoubleType(), False),
])


def write_sample(path, seed=2):
    random.seed(seed)
    stations = [f"Station_{i:02d}" for i in range(10)]
    baselines = {s: random.uniform(-10.0, 30.0) for s in stations}
    with open(path, "w") as f:
        for _ in range(2000):
            station = random.choice(stations)
            temp = round(random.gauss(baselines[station], 5.0), 1)
            f.write(f"{station};{temp}\n")


spark = (
    SparkSession.builder
    .appName("1BRC-Step2-Aggregate")
    .master(os.environ.get("SPARK_MASTER_URL", "local[*]"))
    .getOrCreate()
)

sample_path = os.path.join(tempfile.gettempdir(), "1brc_sample_step2.txt")
write_sample(sample_path)

df = spark.read.csv(sample_path, sep=";", schema=MEASUREMENT_SCHEMA, header=False)

agg = df.groupBy("station").agg(
    F.min("temperature").alias("min_temp"),
    F.avg("temperature").alias("mean_temp"),
    F.max("temperature").alias("max_temp"),
)

print("--- Physical plan (look for HashAggregate before/after the Exchange) ---")
agg.explain()

print("--- Aggregated result (unsorted, unformatted — that's Step 3) ---")
agg.show(truncate=False)

spark.stop()
