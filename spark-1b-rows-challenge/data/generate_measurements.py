#!/usr/bin/env python3
"""Generate a synthetic 1BRC-shaped measurements file.

Produces lines of `<station name>;<temperature>` (temperature: one decimal
place), matching the input format of the original One Billion Row Challenge
(https://github.com/gunnarmorling/1brc). Not the challenge logic itself —
this only builds the test fixture; the PySpark ingestion/aggregation job
lives in ../spark/job.py.

Temperatures are sampled per-station from a normal distribution around a
latitude-derived baseline (roughly: warmer near the equator), so stations
have distinct, realistic-looking min/mean/max spreads rather than one flat
global distribution. Station names/latitudes come from stations.csv; if
--stations exceeds the bundled list, extra synthetic stations are added.

Usage:
    python3 generate_measurements.py --rows 1000000000 --stations 1000 \
        --output measurements.txt
"""
import argparse
import csv
import os
import random
import sys
import time

try:
    import numpy as np
except ImportError:
    np = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STATIONS_FILE = os.path.join(SCRIPT_DIR, "stations.csv")
BATCH_SIZE = 200_000


def load_stations(path, count, seed):
    rng = random.Random(seed)
    with open(path, newline="") as f:
        rows = [(r["station"], float(r["lat"])) for r in csv.DictReader(f)]

    if count <= len(rows):
        return rng.sample(rows, count)

    # Pad with synthetic stations at random latitudes to reach `count`.
    extra = [
        (f"Station_{i:05d}", rng.uniform(-60.0, 70.0))
        for i in range(count - len(rows))
    ]
    return rows + extra


def baselines_from_latitude(stations, seed):
    """Rough climate model: colder towards the poles, plus per-station jitter."""
    rng = random.Random(seed)
    return [
        max(-30.0, min(35.0, 30.0 - 0.55 * abs(lat) + rng.uniform(-4.0, 4.0)))
        for _, lat in stations
    ]


def generate(output_path, rows, stations, seed, batch_size=BATCH_SIZE):
    names = [name for name, _ in stations]
    baselines = baselines_from_latitude(stations, seed)
    n_stations = len(names)

    if np is not None:
        rng = np.random.default_rng(seed)
        baselines_arr = np.array(baselines)
    else:
        rng = random.Random(seed)

    start = time.time()
    written = 0
    with open(output_path, "w") as f:
        while written < rows:
            n = min(batch_size, rows - written)

            if np is not None:
                idx = rng.integers(0, n_stations, size=n)
                temps = rng.normal(baselines_arr[idx], 6.0)
                temps = np.clip(temps, -99.9, 99.9)
                lines = [
                    f"{names[i]};{t:.1f}"
                    for i, t in zip(idx, temps)
                ]
            else:
                lines = []
                for _ in range(n):
                    i = rng.randrange(n_stations)
                    t = max(-99.9, min(99.9, rng.gauss(baselines[i], 6.0)))
                    lines.append(f"{names[i]};{t:.1f}")

            f.write("\n".join(lines) + "\n")
            written += n

            elapsed = time.time() - start
            pct = written / rows * 100
            print(f"\r{pct:5.1f}%  {written:,}/{rows:,} rows  {elapsed:6.1f}s",
                  end="", file=sys.stderr)

    elapsed = time.time() - start
    size_gb = os.path.getsize(output_path) / (1024 ** 3)
    print(f"\ndone: {rows:,} rows, {size_gb:.2f} GiB, {elapsed:.1f}s "
          f"-> {output_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=1_000_000_000,
                         help="total rows to generate (default: 1e9)")
    parser.add_argument("--stations", type=int, default=1000,
                         help="distinct station count (default: 1000)")
    parser.add_argument("--stations-file", default=DEFAULT_STATIONS_FILE,
                         help="CSV of station,lat to sample from")
    parser.add_argument("--output", default="measurements.txt",
                         help="output file path")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if np is None:
        print("note: numpy not found, falling back to pure-python generation "
              "(much slower at 1B rows) — pip install numpy to speed this up",
              file=sys.stderr)

    stations = load_stations(args.stations_file, args.stations, args.seed)
    generate(args.output, args.rows, stations, args.seed)


if __name__ == "__main__":
    main()
