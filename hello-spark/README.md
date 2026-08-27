# hello-spark

Experiments on Apache Spark — standalone mode, clustering, and general
data processing. Infra is throwaway: spin up, poke at Spark, tear down.

`make deploy-infra && make deploy-software` provisions the node via
Terraform + Ansible and installs Spark (`make destroy-infra` tears down;
the node also self-terminates ~2h after creation regardless). Master UI:
`http://<public-ip>:8080`.

A progressive, self-contained set of PySpark scripts walks through one
concept at a time — run any of them directly, or against the real cluster
by pointing `SPARK_MASTER_URL` at the master.

## Jupyter

`deploy-software` also stands up a public JupyterLab instance — no SSH
needed:

```
open "$(terraform -chdir=terraform output -raw jupyter_url)"
terraform -chdir=terraform output -raw jupyter_password
```

The study-path scripts are seeded into the JupyterLab home directory.
Every new kernel already has a `spark` SparkSession (via an IPython
startup script), defaulting to `local[*]` — export `SPARK_MASTER_URL` and
restart the Jupyter service to attach it to the real cluster instead.

The Jupyter password is Terraform-generated; port 8888 is open to
`0.0.0.0/0` like everything else in this repo, so it's the only thing
standing between the internet and code execution here.

## Notes

- Spark and Java versions must stay in lock-step — Spark 4.x requires Java
  17+. Both are pinned together in the Ansible role that installs them.
