"""
Step 2 (Task 3): per-station aggregation via native groupBy().agg(...).

Not a row-at-a-time UDF, not a driver-side collect-then-reduce — min/mean/max
computed by Spark's built-in aggregate functions so the work happens as a
map-side partial aggregation on the executors, with only one shuffle to
combine partial results per station.

`.explain()` on the result should show `HashAggregate` (partial) before the
shuffle `Exchange`, then a second `HashAggregate` (final) after it — that's
the plan shape Task 5's acceptance criteria checks for at full scale.

The sample is built by the project's own `data/generate_measurements.py`
against the real station/latitude list in `data/stations.csv` — same
generator the full 1B-row run uses, just a handful of rows.

Run:
    python3 job_02_aggregate.py
"""
import os
import sys
import tempfile

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
from generate_measurements import load_stations, generate, DEFAULT_STATIONS_FILE  # noqa: E402

MEASUREMENT_SCHEMA = StructType([
    StructField("station", StringType(), False),
    StructField("temperature", DoubleType(), False),
])


def write_sample(path, rows=2000, stations=10, seed=2):
    picked = load_stations(DEFAULT_STATIONS_FILE, stations, seed)
    generate(path, rows, picked, seed)


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
