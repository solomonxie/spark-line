# spark-helloworld

## Layout

- `terraform/` — provisions the EC2 node this project runs on and writes its
  address into the Ansible inventory. See `terraform/README.md` for the
  resource graph and the self-termination safety net.
- `ansible/` — automates what `manual_build.sh` does by hand (Java, Spark,
  pyspark) against the node Terraform created. See `ansible/README.md`.
- `Makefile` — day-to-day commands, wraps Terraform/Ansible/AWS CLI calls
  (see below).

## How to use this

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

`deploy-software` also starts the Spark cluster itself — 1 master/driver +
2 workers, running as systemd services on the same node (see
`ansible/README.md`). Nothing to start by hand; SSH in
(`terraform -chdir=terraform output ssh_spark_command`) only to run
`spark-submit`/`pyspark` jobs or to check `systemctl status spark-master
spark-worker@8081 spark-worker@8082`.

Master UI: `http://<public-ip>:8080` (`terraform -chdir=terraform output
spark_master_ui`). Worker UIs: `:8081` and `:8082`.

## Self-termination

The node auto-terminates ~2h after creation via a one-time EventBridge
Scheduler rule (cost safety net, no action needed) — see
`terraform/auto_terminate.tf`. If you're still using the node past that
window, re-running `make deploy-infra` does **not** push the deadline out;
you'd need to destroy/recreate it, or extend `auto_terminate.tf` yourself.

## Notes

- Spark version and Java version must stay in lock-step — Spark 4.x requires
  Java 17+. Bump both together in `ansible/roles/spark_runtime/vars/main.yml`,
  `ansible/roles/spark_runtime/tasks/main.yml`, and `manual_build.sh`.
