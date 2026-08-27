# Process: working through the 1BRC

A progressive checklist. Each step should work end-to-end before the
next — failure modes (wrong rounding, OOM, shuffle spill) are cheaper to
find at small scale.

## 0. Infra up

```
make deploy-infra
make deploy-software
```

Confirm the cluster is alive: Master UI (`terraform -chdir=terraform
output spark_master_ui`) shows 2 workers registered.

## 1. Tiny local sample, no cluster needed

Generate a few thousand rows on your own machine and eyeball the format:

```
python3 -m venv venv && venv/bin/pip install numpy
venv/bin/python data/generate_measurements.py --rows 10000 --stations 20 \
    --output /tmp/sample.txt --seed 1
head /tmp/sample.txt
```

Run the brute-force reference so you know what "correct" looks like
before writing any Spark code:

```
venv/bin/python tools/verify_sample.py /tmp/sample.txt
```

Keep `/tmp/sample.txt` — you'll compare against this exact reference in
step 3.

## 2. Walk the job, then run it against the sample

`spark/job.py` is built from three standalone lessons — read each before
trusting the capstone:

1. `job_01_schema_read.py` — explicit schema vs. `inferSchema` (which
   costs a throwaway full pass over the file).
2. `job_02_aggregate.py` — `groupBy("station").agg(min, avg, max)`, plus
   `.explain()` to see the partial/final `HashAggregate` around one
   shuffle.
3. `job_03_format_output.py` — sort by station, format the
   `{Station=min/mean/max, ...}` string.

Each runs standalone against its own tiny inline sample.

Copy `/tmp/sample.txt` to the node (or regenerate it there with `make
generate-data ROWS=10000 STATIONS=20`), then run the capstone:

```
make push-job
# on the node:
spark-submit --master spark://<master-host>:7077 job.py \
    --input ~/data/measurements.txt --output ~/results.txt
```

## 3. Check correctness

```
make fetch-results
cat results.txt
```

Diff against `venv/bin/python tools/verify_sample.py /tmp/sample.txt`'s
output — they should match. If not: check rounding (half-even vs.
half-up at exact `.x5` values) and sort order before suspecting the
aggregation itself.

## 4. Scale up incrementally

`spark/solve_01_10k_rows.py` → `solve_04_1b_rows.py` are this exact
progression, self-contained (each generates its own tier's data, solves,
times itself):

```
make push-solve   # copies spark/solve_*.py + data/ to the node
# on the node:
spark-submit --master spark://<master-host>:7077 solve_02_1m_rows.py
spark-submit --master spark://<master-host>:7077 solve_03_100m_rows.py
```

Or regenerate manually at increasing sizes, re-running the same job each
time:

```
make generate-data ROWS=1000000    STATIONS=200   # 1M
make generate-data ROWS=10000000   STATIONS=500   # 10M
make generate-data ROWS=100000000  STATIONS=1000  # 100M
```

Watch the Spark UI (`:4040`) for:

- **Spill (Memory/Disk)** on the aggregation stage — should stay near 0.
- **Task skew** — one task much slower than its peers in the same stage.
- **Shuffle read/write size** — sanity-check against the data size.

If spill/skew shows up, check `spark.sql.shuffle.partitions` against data
size and core count (2 workers × 2 cores = 4 slots), confirm AQE
(`spark.sql.adaptive.enabled`, `...coalescePartitions.enabled`) is doing
something, and check input partition count
(`spark.sql.files.maxPartitionBytes`, or repartition explicitly).

## 5. The full 1 billion rows

```
make generate-data          # defaults: ROWS=1000000000 STATIONS=1000
```

I/O-bound, one-time cost — let it finish, then run unmodified:

```
spark-submit --master spark://<master-host>:7077 job.py \
    --input ~/data/measurements.txt --output ~/results.txt
```

Or `solve_04_1b_rows.py` (generates the file itself if missing):

```
spark-submit --master spark://<master-host>:7077 solve_04_1b_rows.py
```

Watch `:4040` and `:8080`. Record: wall clock time, any executor
lost/restarted, spill on the aggregation stage, and whatever config you
changed from step 4.

## 6. Tear down

```
make stop-server     # if you'll resume later
make destroy-infra   # if you're done
```

(The node also self-terminates ~2h after creation regardless.)
