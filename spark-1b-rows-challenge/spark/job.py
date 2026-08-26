#!/usr/bin/env python3
"""1BRC PySpark job — entry point skeleton.

Wiring only: SparkSession + CLI args. The actual challenge —
reading `station;temperature`, aggregating min/mean/max per station, and
formatting the result — is not implemented here. See PROCESS.md.

Usage (on the cluster node, after `make push-job`):
    spark-submit --master spark://<master-host>:7077 job.py \
        --input ~/data/measurements.txt --output ~/results.txt
"""
import argparse

from pyspark.sql import SparkSession


def build_spark_session(app_name="1brc"):
    return SparkSession.builder.appName(app_name).getOrCreate()


def run(spark, input_path, output_path):
    # TODO: read `input_path` with an explicit schema (station: string,
    #   temperature: double) — avoid schema inference on a 1B-row file.
    #
    # TODO: aggregate min / mean / max temperature grouped by station.
    #
    # TODO: sort by station name and format as
    #   `{Station1=min/mean/max, Station2=min/mean/max, ...}`
    #   with each value rounded to one decimal place.
    #
    # TODO: write the formatted line to `output_path` (and/or print it).
    raise NotImplementedError("implement the 1BRC read/aggregate/format steps above")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="path to measurements.txt")
    parser.add_argument("--output", required=True, help="path to write the result to")
    args = parser.parse_args()

    spark = build_spark_session()
    try:
        run(spark, args.input, args.output)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
