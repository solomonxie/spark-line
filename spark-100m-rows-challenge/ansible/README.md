# Ansible

Configures the node Terraform created: Java, Spark, PySpark/pandas, and a
standalone Spark cluster (1 master/driver + 2 workers) running as systemd
services. It's the automated version of `../manual_build.sh` — read that
script first if you want to know what each task below is actually doing
on the box.

```
site.yml                          → applies roles below, in order, to host group `spark_nodes`
  ├─ roles/spark_runtime           → installs the Spark/Java/Python runtime
  │    ├─ vars/main.yml            → Spark/Hadoop version, download URL
  │    └─ tasks/main.yml           → apt packages → pip installs → download+extract
  │                                  Spark → chown → /etc/profile.d/spark.sh
  └─ roles/spark_cluster           → configures & starts the master + workers
       ├─ vars/main.yml            → ports, worker count, cores/memory per worker
       ├─ templates/               → spark-master.service, spark-worker@.service
       └─ tasks/main.yml           → deploy systemd units → enable/start master
                                      → enable/start spark-worker@8081, @8082

group_vars/all.yml                 → spark_home, shared by both roles
inventory.ini                      → written by terraform/ansible_inventory.tf,
                                      not hand-edited (regenerated on every apply)
```

Both roles run on the same node — `spark_cluster` runs the master (driver)
and 2 workers as separate systemd services on one t3.xlarge box rather than
across multiple EC2 instances. Each worker gets 2 cores / 6g RAM (of the
box's 4 vCPUs / 16GB), leaving headroom for the OS and master process; tune
`spark_worker_count`/`spark_worker_cores`/`spark_worker_memory` in
`roles/spark_cluster/vars/main.yml`. Worker N's web UI is on port
`8080 + N` (8081, 8082, ...) — matches the security group's worker UI
port range in `terraform/ec2.tf`.

Run through the repo-root `Makefile`:

```
make deploy-software
```

which runs `ansible-playbook -i inventory.ini site.yml` (with host key
checking off, since the node's IP is new every time it's recreated).
Requires `deploy-infra` to have run first — `inventory.ini` won't exist
otherwise.

Tasks are written to be re-run safely: package installs are idempotent, the
Spark extract/rename steps are skipped if `spark-submit` is already present
(`spark_installed` check in `roles/spark_runtime/tasks/main.yml`), and the
systemd units in `spark_cluster` are declarative — re-applying just
redeploys the unit files and restarts the services.

## Notes

- Bump `spark_version`/`hadoop_version` in `roles/spark_runtime/vars/main.yml`
  alongside the Java version in `roles/spark_runtime/tasks/main.yml` — see
  the version note in the top-level `../README.md`.
- Master/worker logs land under `{{ spark_home }}/logs` and
  `{{ spark_home }}/work/worker-<port>`; `journalctl -u spark-master` /
  `journalctl -u spark-worker@8081` also work since both run under systemd.
