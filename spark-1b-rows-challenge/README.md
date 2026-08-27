# Spark: One Billion Row Challenge (1BRC)

Adapts the community [One Billion Row Challenge](https://github.com/gunnarmorling/1brc)
— originally a single-machine Java benchmark — into a distributed PySpark
exercise. Input: a ~1 billion line `<station>;<temperature>` file
(temperature always one decimal place, e.g. `Rio de Janeiro;24.3`, across
up to a few thousand stations).

Goal: compute per-station min/mean/max temperature and emit one line,
stations sorted alphabetically, values rounded to one decimal:

```
{Station1=min1/mean1/max1, Station2=min2/mean2/max2, ...}
```

Hardware: one EC2 t3.xlarge (16GB RAM, 4 vCPUs) running a standalone Spark
cluster — 1 master/driver + 2 workers (2 cores / 6g each) — on that one
box. See `ansible/`.

The original's ~10s target assumes 8 dedicated bare-metal cores and
doesn't transfer here. The bar instead: process the full 1B rows on this
modest, shared, memory-constrained cluster correctly, without OOM-killing
an executor or blowing the budget on an avoidable shuffle.

## Tasks

1. **Generate the dataset** — `data/generate_measurements.py` produces
   `measurements.txt` at whatever size you're testing (start small, scale
   to 1B once correct).
2. **Strict ingestion** — read the semicolon-delimited file with an
   explicit schema (`station: string, temperature: double`), no inference,
   no double-pass scan.
3. **Per-station aggregation** — `groupBy().agg(min, avg, max)`, not a
   row-at-a-time UDF or driver-side collect-then-reduce.
4. **Deterministic output** — sort alphabetically, format as
   `{Station=min/mean/max, ...}`; check against `tools/verify_sample.py`
   on a small sample first.
5. **Scale to 1B rows** — run the same job unmodified against the full
   file. No executor OOM-kill; check the Spark UI (`:4040`) for
   spill/skew and tune partitioning/AQE in response.

## Acceptance criteria

- **Correctness**: output matches `tools/verify_sample.py`'s brute-force
  result on the same sample.
- **Resource efficiency**: the full 1B-row run completes on 16GB/4vCPU
  with no executor OOM, and the driver never materializes the ungrouped
  dataset.
- **Execution plan**: `.explain()` shows partial (map-side)
  `HashAggregate` before the shuffle `Exchange`, feeding one shuffle for
  the group-by — not a Python UDF, not multiple avoidable shuffles.

No fixed time SLA (the original's 10s target doesn't transfer). As a
guide, expect low-single-digit minutes once properly partitioned — much
longer than that signals shuffle spill or a bad partition count.

`make deploy-infra && make deploy-software` provisions the node and starts
the Spark cluster (master UI `http://<public-ip>:8080`, workers
`:8081`/`:8082`); `make generate-data` / `make push-job` / `make
push-solve` / `make fetch-results` handle data + job prep, then SSH in
(`terraform -chdir=terraform output ssh_spark_command`) and run
`spark-submit` — see `PROCESS.md` for the full progression, or run the
`solve_01_10k_rows.py` → `solve_04_1b_rows.py` scale ladder directly (each
generates its own tier's data on first run). `make destroy-infra` tears
down; node self-terminates ~2h after creation regardless — see
`terraform/auto_terminate.tf`.

## Jupyter

`deploy-software` also stands up a public JupyterLab instance:

```
open "$(terraform -chdir=terraform output -raw jupyter_url)"
terraform -chdir=terraform output -raw jupyter_password
```

`notebooks/` (seeded with `00_getting_started.ipynb`, the `job_*.py`
lessons, and the `solve_*.py` scale ladder) is the JupyterLab home
directory; the data generator is seeded alongside at `~/1brc-data-gen`.
Every new kernel already has a `spark` SparkSession, defaulting to
`local[*]` — export `SPARK_MASTER_URL` and restart (`sudo systemctl
restart jupyter`) to attach it to the real cluster.

The Jupyter password is Terraform-generated; port 8888 is open to
`0.0.0.0/0` like everything else in this repo, so it's the only thing
standing between the internet and code execution here.

## Notes

- Spark and Java versions must stay in lock-step — Spark 4.x requires Java
  17+. Bump both together in `ansible/roles/spark_runtime/vars/main.yml`,
  `ansible/roles/spark_runtime/tasks/main.yml`, and `manual.sh`.
