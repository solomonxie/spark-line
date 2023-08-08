# Process: working through the 1BRC

A progressive checklist. Each step should work end-to-end before moving to
the next — don't jump straight to 1B rows, the failure modes (wrong
rounding, OOM, shuffle spill) are much cheaper to find and fix at small
scale.

## 0. Infra up

```
make deploy-infra
make deploy-software
```

Confirm the cluster is alive: Master UI (`terraform -chdir=terraform
output spark_master_ui`) shows 2 workers registered.

## 1. Tiny local sample, no cluster needed

Generate a few thousand rows on your own machine (not the node) and eyeball
the format:

```
python3 -m venv venv && venv/bin/pip install numpy
venv/bin/python data/generate_measurements.py --rows 10000 --stations 20 \
    --output /tmp/sample.txt --seed 1
head /tmp/sample.txt
```

Run the brute-force reference on it so you know what "correct" looks like
before you write any Spark code:

```
venv/bin/python tools/verify_sample.py /tmp/sample.txt
```

Keep this `/tmp/sample.txt` — you'll compare your Spark job's output
against this exact reference in step 3.

## 2. Write the job against the tiny sample

Copy `/tmp/sample.txt` to the node (or regenerate it there with `make
generate-data ROWS=10000 STATIONS=20`), then implement `spark/job.py`:

1. Read the file with an explicit schema (`station: string, temperature:
   double`) — split on `;`, don't let Spark infer types over the whole file.
2. `groupBy("station").agg(min, avg, max)`.
3. Round each value to 1 decimal, sort by station name, format the
   `{Station=min/mean/max, ...}` string.
4. Write it to the output path (and print it — useful for a quick look).

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
output (same underlying sample). They should match. If they don't: check
rounding (half-even vs. half-up at exact `.x5` values is a common mismatch)
and sort order before suspecting the aggregation itself.

## 4. Scale up incrementally

Regenerate on the node at increasing sizes, re-running the same job each
time, watching the Spark UI (`http://<node-ip>:4040` while a job is
running) for:

- **Spill (Memory) / Spill (Disk)** on the aggregation stage — should stay
  at or near 0.
- **Task skew** — one task taking far longer than its peers in the same
  stage (a sign a station, or a partition, is disproportionately large).
- **Shuffle read/write size** — sanity-check it's in the right ballpark for
  the data size, not the whole dataset being re-shuffled repeatedly.

```
make generate-data ROWS=1000000    STATIONS=200   # 1M
make generate-data ROWS=10000000   STATIONS=500   # 10M
make generate-data ROWS=100000000  STATIONS=1000  # 100M
```

Re-run `spark-submit` after each regeneration. If spill/skew shows up,
before going further:

- Check `spark.sql.shuffle.partitions` against the data size and core count
  (2 workers × 2 cores = 4 slots total).
- Confirm AQE is doing something useful (`spark.sql.adaptive.enabled`,
  `spark.sql.adaptive.coalescePartitions.enabled`) rather than leaving it on
  defaults and hoping.
- Look at whether the read step is producing too many/too few input
  partitions for a plain-text file this size (`spark.sql.files.
  maxPartitionBytes`, or repartition explicitly after reading).

## 5. The full 1 billion rows

```
make generate-data          # defaults: ROWS=1000000000 STATIONS=1000
```

This takes a while (I/O-bound, one-time cost) — let it finish before
submitting. Then run the same job unmodified:

```
spark-submit --master spark://<master-host>:7077 job.py \
    --input ~/data/measurements.txt --output ~/results.txt
```

Watch `:4040` and `:8080` while it runs. Record:

- Wall clock time.
- Whether any executor was lost/restarted.
- Spill (memory/disk) on the aggregation stage.
- Whatever config you changed to get here from step 4, and why.

## 6. Tear down

```
make stop-server     # if you'll resume later
make destroy-infra   # if you're done
```

(The node also self-terminates ~2h after creation regardless — see the
README's Self-termination section.)
