# hello-spark

Sandbox for experimenting with Apache Spark — standalone mode, clustering,
and general data processing. Infra is throwaway: spin up, poke at Spark,
tear down.

`manual_build.sh` walks the manual setup by hand; `make deploy-infra &&
make deploy-software` does the same via Terraform + Ansible (`make
destroy-infra` tears down; node self-terminates ~2h after creation
regardless — see `terraform/auto_terminate.tf`). Master UI:
`http://<public-ip>:8080`.

`hello_01_spark_session.py` → `hello_08_real_world_etl.py` are a
progressive, self-contained study path, one PySpark concept per file — run
any directly (`python3 hello_01_spark_session.py`), or against the real
cluster with `SPARK_MASTER_URL=spark://$(hostname):7077`. `spark_etl.py`
is the same job assuming the dataset's already there.

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
defaulting to `local[*]` — export `SPARK_MASTER_URL` and restart
(`sudo systemctl restart jupyter`) to attach it to the real cluster.

The Jupyter password is Terraform-generated; port 8888 is open to
`0.0.0.0/0` like everything else in this repo, so it's the only thing
standing between the internet and code execution here.

## Notes

- Spark and Java versions must stay in lock-step — Spark 4.x requires Java
  17+. Bump both together in `ansible/roles/admin/vars/main.yml`,
  `ansible/roles/admin/tasks/main.yml`, and `manual_build.sh`.
