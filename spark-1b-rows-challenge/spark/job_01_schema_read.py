"""
Step 1 (Task 2): strict ingestion — explicit schema, no inference.

Reads `station;temperature` lines against a StructType schema instead of
`inferSchema=True`, which would force Spark to scan the whole file once just
to guess types before the real job even starts. On a 1B-row file that
throwaway pass costs as much as the job itself.

Runs against a tiny inline sample — no cluster, no generated fixture needed.

Run:
    python3 job_01_schema_read.py
"""
import os
import random
import tempfile

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

MEASUREMENT_SCHEMA = StructType([
    StructField("station", StringType(), False),
    StructField("temperature", DoubleType(), False),
])


def write_sample(path, seed=1):
    random.seed(seed)
    stations = ["Rio de Janeiro", "Tokyo", "Oslo", "Cairo", "Wellington"]
    with open(path, "w") as f:
        for _ in range(200):
            station = random.choice(stations)
            temp = round(random.uniform(-20.0, 40.0), 1)
            f.write(f"{station};{temp}\n")


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
