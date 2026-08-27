"""
Step 1 (Task 2): strict ingestion — explicit schema, no inference.

Reads `station;temperature` lines against a StructType schema instead of
`inferSchema=True`, which would force Spark to scan the whole file once just
to guess types before the real job even starts. On a 1B-row file that
throwaway pass costs as much as the job itself.

The sample is built by the project's own `data/generate_measurements.py`
against the real station/latitude list in `data/stations.csv` — real
station names and a real (latitude-derived) climate model, just a handful
of rows instead of a billion. No cluster, no pre-existing fixture needed.

Run:
    python3 job_01_schema_read.py
"""
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
from generate_measurements import load_stations, generate, DEFAULT_STATIONS_FILE  # noqa: E402

MEASUREMENT_SCHEMA = StructType([
    StructField("station", StringType(), False),
    StructField("temperature", DoubleType(), False),
])


def write_sample(path, rows=500, stations=5, seed=1):
    picked = load_stations(DEFAULT_STATIONS_FILE, stations, seed)
    generate(path, rows, picked, seed)


spark = (
    SparkSession.builder
    .appName("1BRC-Step1-SchemaRead")
    .master(os.environ.get("SPARK_MASTER_URL", "local[*]"))
    .getOrCreate()
)

sample_path = os.path.join(tempfile.gettempdir(), "1brc_sample_step1.txt")
write_sample(sample_path)

print("--- Reading with inferSchema (the thing NOT to do at scale) ---")
inferred = spark.read.csv(sample_path, sep=";", inferSchema=True, header=False)
inferred.printSchema()

print("--- Reading with an explicit schema (single pass, no guessing) ---")
df = spark.read.csv(sample_path, sep=";", schema=MEASUREMENT_SCHEMA, header=False)
df.printSchema()
print(f"row count: {df.count()}")
df.show(5)

spark.stop()
