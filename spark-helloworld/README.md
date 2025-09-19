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
- `spark_etl.py` — example PySpark job to run once the node is up.
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
