"""
Step 3 (Task 4): sort + format into the challenge's exact output shape.

`{Station1=min1/mean1/max1, Station2=min2/mean2/max2, ...}`, stations sorted
alphabetically, each value rounded to one decimal place.

The aggregated result from Step 2 has one row per station — a few thousand
rows at most, even at 1B input rows — so it's safe to `.collect()` it to the
driver for the final sort/format. That's not the same mistake as collecting
the raw 1B-row dataset: the shuffle/aggregation already did the expensive
part on the executors.

Rounding is done with Python's `f"{x:.1f}"` on the collected rows rather
than Spark's `round()`, to match `tools/verify_sample.py`'s brute-force
reference exactly (Spark's `round()` is HALF_UP; Python's float formatting
is round-half-to-even — they can disagree by 0.1 on exact `.x5` boundaries).

The sample is built by the project's own `data/generate_measurements.py`
against the real station/latitude list in `data/stations.csv` — same
generator the full 1B-row run uses, just a handful of rows.

Run:
    python3 job_03_format_output.py
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


def write_sample(path, rows=2000, stations=10, seed=3):
    picked = load_stations(DEFAULT_STATIONS_FILE, stations, seed)
    generate(path, rows, picked, seed)


def format_result(rows):
    parts = [
        f"{r.station}={r.min_temp:.1f}/{r.mean_temp:.1f}/{r.max_temp:.1f}"
        for r in rows
    ]
    return "{" + ", ".join(parts) + "}"


spark = (
    SparkSession.builder
    .appName("1BRC-Step3-FormatOutput")
    .master(os.environ.get("SPARK_MASTER_URL", "local[*]"))
    .getOrCreate()
)

sample_path = os.path.join(tempfile.gettempdir(), "1brc_sample_step3.txt")
write_sample(sample_path)

df = spark.read.csv(sample_path, sep=";", schema=MEASUREMENT_SCHEMA, header=False)

agg = df.groupBy("station").agg(
    F.min("temperature").alias("min_temp"),
    F.avg("temperature").alias("mean_temp"),
    F.max("temperature").alias("max_temp"),
).orderBy("station")

result = format_result(agg.collect())
print(result)

spark.stop()
