# hello-spark

Sandbox for experimenting with Apache Spark — standalone mode, clustering,
and general data processing. Infra is throwaway: spin up, poke at Spark,
tear down.

## Two ways to use this

**Manual / learning path** — SSH into any Ubuntu box and follow
`manual_build.sh` top to bottom. Best for understanding what's happening or
debugging a step in isolation.

**Automated path** — Terraform provisions the node, Ansible configures it,
the `Makefile` drives both:

```
make deploy-infra       # terraform apply — creates the EC2 node
make deploy-software    # ansible-playbook — installs Java/Spark/pyspark/JupyterLab

make start-server       # aws ec2 start-instances (resume a stopped node)
make stop-server        # aws ec2 stop-instances (save cost when idle)
make destroy-infra      # terraform destroy — tear everything down
```

`AWS_PROFILE` defaults to `prod`; override with
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

## Jupyter

`deploy-software` also stands up a public JupyterLab instance — no SSH
needed:

```
open "$(terraform -chdir=terraform output -raw jupyter_url)"
terraform -chdir=terraform output -raw jupyter_password
```

`notebooks/` (seeded with `00_getting_started.ipynb` and the `hello_*.py`
study-path files) is the JupyterLab home directory. Every new kernel
already has a `spark` SparkSession (via an IPython startup script),
defaulting to `local[*]`. To attach it to the real cluster instead: start
the cluster per the section above, then on the node `export
SPARK_MASTER_URL=spark://$(hostname):7077` and `sudo systemctl restart
jupyter`.

The Jupyter password is Terraform-generated; port 8888 is open to
`0.0.0.0/0` like everything else in this repo, so it's the only thing
standing between the internet and code execution here — don't leave the
node up longer than you're using it.

## Progressive study path

Eight standalone scripts, `hello_01_...py` through `hello_08_...py`, one
PySpark concept each. Fully self-contained — own `SparkSession`, own data,
no imports between them — run any one on its own, in any order.

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

Run any step directly — no cluster required:

```
python3 hello_01_spark_session.py
```

Against the real cluster instead (SSH into the node first):

```
SPARK_MASTER_URL=spark://$(hostname):7077 python3 hello_01_spark_session.py
```

`hello_08_real_world_etl.py` downloads a real NYC Yellow Taxi Parquet file
(~50MB) the first time it runs; both input and output are gitignored.

Once done, `spark_etl.py` is the same job assuming the dataset's already
there — from there, `spark-1b-rows-challenge/` in the repo root pushes
further.

## Self-termination

The node auto-terminates ~2h after creation via a one-time EventBridge
rule (see `terraform/auto_terminate.tf`). Re-running `make deploy-infra`
doesn't push the deadline out — destroy/recreate, or extend
`auto_terminate.tf` yourself.

## Notes

- Spark and Java versions must stay in lock-step — Spark 4.x requires Java
  17+. Bump both together in `ansible/roles/admin/vars/main.yml`,
  `ansible/roles/admin/tasks/main.yml`, and `manual_build.sh`.
