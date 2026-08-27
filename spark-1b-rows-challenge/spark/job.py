#!/usr/bin/env python3
"""1BRC PySpark job — capstone, cluster-ready.

Combines job_01 (explicit-schema read), job_02 (native groupBy().agg
min/mean/max), and job_03 (sort + spec-format the small aggregated result)
into the single job that scales unmodified from a 10-row sample up to the
full 1B-row file (Task 5). See PROCESS.md for the progression.

Tuning notes (Task 5 / PROCESS.md step 4):
  - AQE (`spark.sql.adaptive.*`) is left on so Spark coalesces shuffle
    partitions after seeing actual post-aggregation sizes, instead of us
    guessing a fixed `spark.sql.shuffle.partitions` up front.
  - The input read's partition count comes from
    `spark.sql.files.maxPartitionBytes` (default 128MB) splitting the plain
    text file — for a ~15-20GB file that's already a few hundred partitions,
    plenty for a 4-core cluster. Only override it if the Spark UI (:4040)
    shows too few input partitions for the cluster's core count.
  - The aggregated result (one row per station, a few thousand at most) is
    what gets `.collect()`-ed for final formatting — never the raw
    1B-row dataset. Check `.explain()` (`--explain` below) for a single
    partial-then-final `HashAggregate` around one shuffle `Exchange`; more
    than that signals an avoidable extra shuffle.

Usage (on the cluster node, after `make push-job`):
    spark-submit --master spark://<master-host>:7077 job.py \
        --input ~/data/measurements.txt --output ~/results.txt
"""
import argparse

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

MEASUREMENT_SCHEMA = StructType([
    StructField("station", StringType(), False),
    StructField("temperature", DoubleType(), False),
])


def build_spark_session(app_name="1brc"):
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .getOrCreate()
    )


def format_result(rows):
    parts = [
        f"{r.station}={r.min_temp:.1f}/{r.mean_temp:.1f}/{r.max_temp:.1f}"
        for r in rows
    ]
    return "{" + ", ".join(parts) + "}"


def run(spark, input_path, output_path, explain=False):
    df = spark.read.csv(input_path, sep=";", schema=MEASUREMENT_SCHEMA, header=False)

    agg = df.groupBy("station").agg(
        F.min("temperature").alias("min_temp"),
        F.avg("temperature").alias("mean_temp"),
        F.max("temperature").alias("max_temp"),
    ).orderBy("station")

    if explain:
        agg.explain()

    # Rounded with Python's f"{x:.1f}" (round-half-to-even) rather than
    # Spark's round() (HALF_UP), to match tools/verify_sample.py exactly.
    result = format_result(agg.collect())

    print(result)
    with open(output_path, "w") as f:
        f.write(result + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="path to measurements.txt")
    parser.add_argument("--output", required=True, help="path to write the result to")
    parser.add_argument("--explain", action="store_true",
                         help="print the physical plan for the aggregation before running")
    args = parser.parse_args()

    spark = build_spark_session()
    try:
        run(spark, args.input, args.output, explain=args.explain)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
