# spark-helloworld

Sandbox for experimenting with Apache Spark — standalone mode, clustering, and general data processing.
Infra is throwaway by design: spin up, poke at Spark, tear down.

## Layout

- `terraform/` — provisions a single EC2 node (spark master + worker) and
  writes its address into the Ansible inventory. See `terraform/README.md`
  for the resource graph.
- `ansible/` — installs Java, Spark, and Python deps on the node
  (`roles/admin`).
- `manual_build.sh` — reference notes for setting the node up by hand,
  without Terraform/Ansible.
- `Makefile` — day-to-day commands (see below).

## Workflow

```
make deploy-infra      # terraform apply — creates the EC2 node
make deploy-software    # ansible-playbook — installs Java/Spark/pyspark

make start-server       # aws ec2 start-instances (resume a stopped node)
make stop-server         # aws ec2 stop-instances (save cost when idle)
make destroy-infra       # terraform destroy — tear everything down
```

`AWS_PROFILE` defaults to `prod` in the Makefile; override with
`make deploy-infra AWS_PROFILE=<profile>`.

On the node, once provisioned:

```
/opt/spark/sbin/start-master.sh
/opt/spark/sbin/start-worker.sh spark://$(hostname):7077
spark-submit --version
```

Master UI: `http://<public-ip>:8080` (see `terraform output spark_master_ui`).

## Notes

- Spark version and Java version must stay in lock-step — Spark 4.x requires
  Java 17+. Bump both together in `ansible/roles/admin/vars/main.yml`,
  `ansible/roles/admin/tasks/main.yml`, and `manual_build.sh`.
- The node self-terminates ~2h after creation (EventBridge Scheduler, see
  `terraform/auto_terminate.tf`) as a cost safety net.
