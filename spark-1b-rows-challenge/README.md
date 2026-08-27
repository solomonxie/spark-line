# Spark: One Billion Row Challenge (1BRC)

Scenario
This project adapts the community [One Billion Row Challenge](https://github.com/gunnarmorling/1brc)
— originally a single-machine Java benchmark — into a distributed PySpark
exercise. The input is a ~1 billion line text file of weather station
temperature readings, one measurement per line:

```
<station name>;<temperature>
```

`temperature` is a signed decimal with exactly one fractional digit (e.g.
`Rio de Janeiro;24.3`), across up to a few thousand distinct station names.

The mission: read the file and compute, per station, the minimum, mean, and
maximum temperature, then emit a single line in the challenge's required
format — stations sorted alphabetically, each value rounded to one decimal
place:

```
{Station1=min1/mean1/max1, Station2=min2/mean2/max2, ...}
```

Hardware:
A single-node EC2 instance (t3.xlarge: 16 GB RAM, 4 vCPUs) running a
standalone Spark cluster — 1 master/driver + 2 workers (2 cores / 6g each)
— on that one box. See `ansible/`.

The original 1BRC's ~10 second target assumes 8 dedicated bare-metal cores
and a hand-tuned single-process program — that's not the bar here. The bar
is: process the full 1 billion rows on this modest, shared, memory-
constrained cluster, correctly, without OOM-killing an executor or blowing
the disk/memory budget on an avoidable shuffle.


Mission Task List & Expected Outcomes

Task 1: Generate the dataset
- Task: Produce the ~1 billion row `measurements.txt` fixture. Tooling is
  provided (`data/generate_measurements.py`) — nothing to build here.
- Expected Outcome: A `station;temperature` text file on the node, sized to
  whatever you're testing (start at 1M–10M rows while iterating, scale to
  1B once the job below is correct).

Task 2: Strict Ingestion & Schema Enforcement
- Task: Read the semicolon-delimited text file into a DataFrame with an
  explicit schema — no inference, no double-pass scan over a billion rows.
- Expected Outcome: A two-column DataFrame (station: string, temperature:
  double) produced by a single read job.

Task 3: Per-Station Aggregation
- Task: Group by station and compute min, mean, and max temperature.
- Expected Outcome: One output row per distinct station, all three stats
  correct to one decimal place, computed via native `groupBy().agg(...)` —
  not a row-at-a-time UDF or a driver-side collect-then-reduce.

Task 4: Deterministic, Spec-Shaped Output
- Task: Sort the aggregated result alphabetically by station name and
  format it as `{Station=min/mean/max, ...}`.
- Expected Outcome: Output format matches the challenge spec exactly;
  correctness checked against `tools/verify_sample.py` on a small sample
  before trusting a full-scale run.

Task 5: Scale to One Billion Rows Under the Resource Budget
- Task: Run the same job, unmodified, against the full 1B-row file.
- Expected Outcome: Completes without an executor OOM-kill. Spark UI
  (`:4040`) inspected for spill/skew, and partitioning/AQE settings tuned
  in response — document what you saw and what you changed.


System Validation & Acceptance Criteria

Area: Correctness
- Target Benchmark: Output format and values match
  `tools/verify_sample.py`'s brute-force result on the same sample file.
- Failure Condition: Wrong rounding, wrong sort order, or missing/duplicate
  stations in the output.

Area: Resource Efficiency
- Target Benchmark: The full 1B-row run completes on the 16 GB / 4 vCPU
  node with no executor lost to OOM.
- Failure Condition: Executor OOM-kill, or the driver ever materializes the
  full (ungrouped) dataset instead of aggregating on the executors.

Area: Execution Plan
- Target Benchmark: `.explain()` shows partial (map-side) aggregation —
  `HashAggregate` before the shuffle `Exchange` — feeding a single shuffle
  for the group-by.
- Failure Condition: Multiple avoidable shuffles, or aggregation expressed
  as a Python UDF instead of the built-in `min`/`mean`/`max` functions.


Time Constraints
No fixed SLA — the original 10-second target doesn't transfer to this
hardware or to PySpark's overhead, so there's no pass/fail wall clock here.
As a rough guide, expect low-single-digit minutes once the job is properly
partitioned; a run taking much longer than that is a signal to check for
shuffle spill or a bad partition count before just letting it run.


## Layout

- `terraform/` — provisions the EC2 node this project runs on and writes its
  address into the Ansible inventory. See `terraform/README.md` for the
  resource graph and the self-termination safety net.
- `ansible/` — sets up the runtime environment (Java, Spark, PySpark), starts
  the standalone cluster, and stands up JupyterLab. See Jupyter below.
- `notebooks/` — seeded onto the node's JupyterLab instance; starter
  notebook lives here, committed. See Jupyter below.
- `data/` — `generate_measurements.py` produces the input file;
  `stations.csv` is the bundled real station-name/latitude list it samples
  from (no network access needed on the node).
- `spark/job_01_schema_read.py` → `job_03_format_output.py` — progressive
  lessons (Tasks 2-4), each runnable standalone against a tiny inline
  sample, no cluster needed.
- `spark/job.py` — the capstone: combines the three lessons into the single
  job that scales unmodified to the full 1B rows (Task 5).
- `spark/solve_01_10k_rows.py` → `solve_04_1b_rows.py` — the challenge
  actually solved, at each scale tier: self-contained (generates its own
  real data if missing, solves, reports wall-clock time), the same
  read/aggregate/format solve as `job.py` pinned to one fixed size, so you
  can run/compare 10K → 1M → 100M → 1B without hand-managing input files.
- `tools/verify_sample.py` — small, non-Spark brute-force reference for
  checking your job's output on a sample file.
- `PROCESS.md` — step-by-step progression from a handful of rows on your
  laptop to the full 1B-row run on the cluster.
- `Makefile` — day-to-day commands, wraps Terraform/Ansible/AWS CLI/scp
  calls (see below).

## How to use this

**Automated path** — Terraform provisions the node, Ansible configures it,
the `Makefile` drives both:

```
make deploy-infra       # terraform apply — creates the EC2 node
make deploy-software    # ansible-playbook — installs Java/Spark/pyspark/JupyterLab

make start-server       # aws ec2 start-instances (resume a stopped node)
make stop-server        # aws ec2 stop-instances (save cost when idle)
make destroy-infra      # terraform destroy — tear everything down
```

`AWS_PROFILE` defaults to `prod` in the Makefile; override with
`make deploy-infra AWS_PROFILE=<profile>`.

`deploy-software` also starts the Spark cluster itself — 1 master/driver +
2 workers, running as systemd services on the same node (see
`ansible/README.md`). Nothing to start by hand; SSH in
(`terraform -chdir=terraform output ssh_spark_command`) only to run
`spark-submit`/`pyspark` jobs or to check `systemctl status spark-master
spark-worker@8081 spark-worker@8082`.

Master UI: `http://<public-ip>:8080` (`terraform -chdir=terraform output
spark_master_ui`). Worker UIs: `:8081` and `:8082`.

**Data & job prep** — once the node is up:

```
make generate-data ROWS=1000000 STATIONS=200   # small run first, to iterate
make generate-data                             # full 1B rows (defaults)
make push-job                                  # copy spark/job.py to the node
make push-solve                                # copy spark/solve_*.py + data/ to the node
make fetch-results                             # copy ~/results.txt back
```

Then SSH in and drive `spark-submit` yourself against whatever file/flags
you're testing — see `PROCESS.md` for the progression, or run the
`solve_*.py` scale ladder directly (each generates its own tier's data on
first run, so no separate `generate-data` call needed):

```
spark-submit --master spark://<master-host>:7077 solve_01_10k_rows.py
spark-submit --master spark://<master-host>:7077 solve_02_1m_rows.py
spark-submit --master spark://<master-host>:7077 solve_03_100m_rows.py
spark-submit --master spark://<master-host>:7077 solve_04_1b_rows.py
```

## Jupyter

`deploy-software` also stands up a public JupyterLab instance — no SSH
needed to use it, similar in spirit to attaching a notebook to a
Databricks cluster:

```
open "$(terraform -chdir=terraform output -raw jupyter_url)"
terraform -chdir=terraform output -raw jupyter_password
```

Log in with that password. `notebooks/` (seeded with `00_getting_started.
ipynb`, `job_01_schema_read.py` → `job.py`, and `solve_01_10k_rows.py` →
`solve_04_1b_rows.py`, for reference) is the JupyterLab home directory —
the data generator is seeded alongside them at `~/1brc-data-gen`, so the
`solve_*.py` files' self-generate-if-missing step works out of the box.

Every new notebook kernel already has a `spark` SparkSession, created
automatically by an IPython startup script — no cell needed to build one.
It defaults to `local[*]` (this node, no cluster required), the same
default the `job_*.py` scripts use. To attach it to the real standalone
master/worker cluster instead: start the cluster per the section above,
then on the node, `export SPARK_MASTER_URL=spark://$(hostname):7077` and
restart the service (`sudo systemctl restart jupyter`) before opening a
new notebook.

The password is generated by Terraform and only ever leaves the node
hashed (`ansible/roles/jupyter`); the security group exposes port 8888 to
`0.0.0.0/0` like every other port in this repo — the password is what's
actually standing between the internet and code execution on this box,
so treat it accordingly (don't leave the node up longer than you're using
it — see Self-termination below).

## Self-termination

The node auto-terminates ~2h after creation via a one-time EventBridge
Scheduler rule (cost safety net, no action needed) — see
`terraform/auto_terminate.tf`. If you're still using the node past that
window, re-running `make deploy-infra` does **not** push the deadline out;
you'd need to destroy/recreate it, or extend `auto_terminate.tf` yourself.

## Notes

- Spark version and Java version must stay in lock-step — Spark 4.x requires
  Java 17+. Bump both together in `ansible/roles/spark_runtime/vars/main.yml`,
  `ansible/roles/spark_runtime/tasks/main.yml`, and `manual.sh`.
