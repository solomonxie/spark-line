# spark-helloworld

Sandbox for experimenting with Apache Spark — standalone mode, clustering, and general data processing.
Infra is throwaway by design: spin up, poke at Spark, tear down.

## Layout

- `manual_build.sh` — step-by-step shell commands for setting up Spark on a
  bare EC2 node by hand. Not a script to run as-is — read it top to bottom
  as the reference for what "standing up Spark" actually involves, and for
  a worked example of loading a parquet file and running PySpark commands.
  Start here if you want to understand the pieces before automating them.
- `terraform/` — provisions the EC2 node this project runs on and writes its
  address into the Ansible inventory. See `terraform/README.md` for the
  resource graph and the self-termination safety net.
- `ansible/` — automates what `manual_build.sh` does by hand (Java, Spark,
  pyspark) against the node Terraform created. See `ansible/README.md`.
- `hello_01_spark_session.py` ... `hello_08_real_world_etl.py` — a
  progressive study path, one PySpark concept per file. See below.
- `spark_etl.py` — example PySpark job to run once the node is up (a leaner
  version of `hello_08_real_world_etl.py`'s pipeline, assuming the data
  file is already downloaded).
- `Makefile` — day-to-day commands, wraps Terraform/Ansible/AWS CLI calls
  (see below).

## Two ways to use this

**Manual / learning path** — no infra automation, just SSH into any Ubuntu
box (yours or one you launched by hand) and follow `manual_build.sh`
top to bottom. Best for understanding what's happening or debugging a step
in isolation.

**Automated path** — Terraform provisions the node, Ansible configures it,
the `Makefile` drives both:

```
make deploy-infra       # terraform apply — creates the EC2 node
make deploy-software    # ansible-playbook — installs Java/Spark/pyspark

make start-server       # aws ec2 start-instances (resume a stopped node)
make stop-server        # aws ec2 stop-instances (save cost when idle)
make destroy-infra      # terraform destroy — tear everything down
```

`AWS_PROFILE` defaults to `prod` in the Makefile; override with
`make deploy-infra AWS_PROFILE=<profile>`.

Once `deploy-software` finishes, SSH in (`terraform -chdir=terraform output
ssh_spark_command`) and start Spark:

```
/opt/spark/sbin/start-master.sh
/opt/spark/sbin/start-worker.sh spark://$(hostname):7077
spark-submit --version
```

Master UI: `http://<public-ip>:8080` (`terraform -chdir=terraform output
spark_master_ui`).

## Progressive study path

Eight standalone scripts, `hello_01_...py` through `hello_08_...py`, each
covering one PySpark concept. Every file is fully self-contained — its own
`SparkSession`, its own data, no imports between them — so you can run any
one of them on its own, in any order, and read it top to bottom without
chasing definitions across files. Later steps do reuse earlier steps'
*code* where it makes sense (the same synthetic dataset shows up in steps
3–7, building up one transformation at a time) — that's copied in, not
imported, on purpose.

| Step | File | Concept |
| --- | --- | --- |
| 1 | `hello_01_spark_session.py` | Create a `SparkSession`, run a distributed count |
| 2 | `hello_02_rdd_basics.py` | RDDs: `map` / `filter` / `reduce` / `reduceByKey` |
| 3 | `hello_03_dataframe_basics.py` | DataFrames: explicit schema, `select`, `filter` |
| 4 | `hello_04_transformations.py` | `withColumn`, `when`, renaming, sorting |
| 5 | `hello_05_aggregations.py` | `groupBy().agg()` |
| 6 | `hello_06_window_functions.py` | `Window` + `dense_rank()` for top-N per group |
| 7 | `hello_07_read_write_files.py` | Writing/reading partitioned Parquet |
| 8 | `hello_08_real_world_etl.py` | Capstone: same pipeline against a real, auto-downloaded dataset |

Run any step directly — no cluster required, it defaults to `local[*]`:

```
python3 hello_01_spark_session.py
```

To run a step against the real standalone cluster from `terraform/` +
`ansible/` instead, point it at the master with an env var (SSH into the
node first):

```
SPARK_MASTER_URL=spark://$(hostname):7077 python3 hello_01_spark_session.py
```

`hello_08_real_world_etl.py` downloads a real NYC Yellow Taxi Parquet file
(~50MB) into this directory the first time it runs, and writes its output
next to it — both are gitignored, safe to delete and re-run.

Once you've been through all eight, `spark_etl.py` is the same style of
job assuming the dataset's already there — and from there,
`spark-1b-rows-challenge/` in the repo root pushes further (see the root
`README.md`).

## Self-termination

The node auto-terminates ~2h after creation via a one-time EventBridge
Scheduler rule (cost safety net, no action needed) — see
`terraform/auto_terminate.tf`. If you're still using the node past that
window, re-running `make deploy-infra` does **not** push the deadline out;
you'd need to destroy/recreate it, or extend `auto_terminate.tf` yourself.

## Notes

- Spark version and Java version must stay in lock-step — Spark 4.x requires
  Java 17+. Bump both together in `ansible/roles/admin/vars/main.yml`,
  `ansible/roles/admin/tasks/main.yml`, and `manual_build.sh`.
