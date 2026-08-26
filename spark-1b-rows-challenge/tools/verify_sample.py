#!/usr/bin/env python3
"""Brute-force, non-Spark reference for checking a 1BRC result on a SMALL sample.

Not a competitive/optimized implementation, and not meant for the full 1B-row
file — it loads nothing lazily and has no parallelism. Use it to sanity-check
spark/job.py's output against a small slice (e.g. `head -n 1000000
measurements.txt > sample.txt`) before trusting a full-scale run.

Usage:
    python3 verify_sample.py sample.txt
    # compare stdout against your spark job's output for the same sample
"""
import sys


def compute(path):
    stats = {}  # station -> [min, max, sum, count]
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            station, temp_str = line.rsplit(";", 1)
            temp = float(temp_str)
            if station not in stats:
                stats[station] = [temp, temp, temp, 1]
            else:
                s = stats[station]
                if temp < s[0]:
                    s[0] = temp
                if temp > s[1]:
                    s[1] = temp
                s[2] += temp
                s[3] += 1
    return stats


def format_result(stats):
    parts = []
    for station in sorted(stats):
        lo, hi, total, count = stats[station]
        mean = total / count
        parts.append(f"{station}={lo:.1f}/{mean:.1f}/{hi:.1f}")
    return "{" + ", ".join(parts) + "}"


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <sample_file>", file=sys.stderr)
        sys.exit(1)

    stats = compute(sys.argv[1])
    print(format_result(stats))
    # Note: rounding here is plain round-half-to-even via `.1f` formatting.
    # If your Spark job rounds differently at exact .x5 boundaries, values
    # may occasionally differ by 0.1 on the last digit — that's a rounding
    # nuance, not proof of a bug in either implementation.


if __name__ == "__main__":
    main()
