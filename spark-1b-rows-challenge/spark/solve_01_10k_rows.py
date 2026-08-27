#!/usr/bin/env python3
"""1BRC, actually solved — tier 1: 10K rows.

Self-contained: generates its own real (station-name + latitude-baseline)
sample if it isn't already on disk, runs the full read/aggregate/format
solve against it, and reports wall-clock time + row/station counts.

This is the same read → groupBy(min/mean/max) → sort/format solve as
`job.py`, just pinned to one fixed, tiny input size — the first rung of
the scale ladder (see `solve_02_1m_rows.py` .. `solve_04_1b_rows.py`) that
proves the solve is correct before it has to also be fast and memory-safe.

Run (on the node, after `make push-solve`):
    spark-submit --master spark://<master-host>:7077 solve_01_10k_rows.py
    # or, for this small a size, plain:
    python3 solve_01_10k_rows.py
"""
import os
import sys
import time

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROWS = 10_000
STATIONS = 20
SEED = 42
DATA_PATH = os.path.expanduser("~/data/measurements_10k.txt")
OUTPUT_PATH = os.path.expanduser("~/results_10k.txt")

MEASUREMENT_SCHEMA = StructType([
    StructField("station", StringType(), False),
    StructField("temperature", DoubleType(), False),
])


def _find_data_gen_dir():
    """`data/generate_measurements.py`, found either in a repo checkout
    (../data next to this file) or at the fixed path `make push-solve`
    copies it to on the node (~/1brc-data-gen)."""
    for candidate in (
        os.path.join(SCRIPT_DIR, "..", "data"),
        os.path.expanduser("~/1brc-data-gen"),
    ):
        if os.path.exists(os.path.join(candidate, "generate_measurements.py")):
            return candidate
    raise FileNotFoundError(
        "generate_measurements.py not found — run this from a repo checkout, "
        "or `make push-solve` on the node first."
    )


def ensure_data(path, rows, stations, seed=SEED):
    """Generate the real (station.csv-sourced) sample if it isn't already
    there — idempotent, like `make generate-data`."""
    if os.path.exists(path):
        return
    sys.path.insert(0, _find_data_gen_dir())
    from generate_measurements import load_stations, generate, DEFAULT_STATIONS_FILE

    os.makedirs(os.path.dirname(path), exist_ok=True)
    picked = load_stations(DEFAULT_STATIONS_FILE, stations, seed)
    generate(path, rows, picked, seed)


def solve(spark, input_path, output_path):
    df = spark.read.csv(input_path, sep=";", schema=MEASUREMENT_SCHEMA, header=False)

    # count("*") rides along on the same map-side aggregation — no separate
    # df.count() pass over the raw input just to report a row total.
    agg = df.groupBy("station").agg(
        F.min("temperature").alias("min_temp"),
        F.avg("temperature").alias("mean_temp"),
        F.max("temperature").alias("max_temp"),
        F.count("*").alias("n"),
    ).orderBy("station")

    rows = agg.collect()
    result = "{" + ", ".join(
        f"{r.station}={r.min_temp:.1f}/{r.mean_temp:.1f}/{r.max_temp:.1f}" for r in rows
    ) + "}"
    total_rows = sum(r.n for r in rows)

    with open(output_path, "w") as f:
        f.write(result + "\n")

    return total_rows, len(rows), result


def main():
    ensure_data(DATA_PATH, ROWS, STATIONS)

    spark = (
        SparkSession.builder.appName("1brc-solve-10k")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .getOrCreate()
    )
    try:
        start = time.time()
        total_rows, n_stations, result = solve(spark, DATA_PATH, OUTPUT_PATH)
        elapsed = time.time() - start
    finally:
        spark.stop()

    print(f"rows={total_rows:,}  stations={n_stations}  elapsed={elapsed:.1f}s")
    print(result)


if __name__ == "__main__":
    main()
