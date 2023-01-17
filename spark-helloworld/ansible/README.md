# Ansible

Configures the node Terraform created: Java, Spark, and PySpark/pandas.
It's the automated version of `../manual_build.sh` — read that script first
if you want to know what each task below is actually doing on the box.

```
site.yml                          → applies role `admin` to host group `spark_nodes`
  └─ roles/admin
       ├─ vars/main.yml           → Spark/Hadoop version, download URL, install path
       └─ tasks/main.yml          → apt packages → pip installs → download+extract
                                     Spark → chown → /etc/profile.d/spark.sh
inventory.ini                     → written by terraform/ansible_inventory.tf,
                                     not hand-edited (regenerated on every apply)
```

Run through the repo-root `Makefile`:

```
make deploy-software
```

which runs `ansible-playbook -i inventory.ini site.yml` (with host key
checking off, since the node's IP is new every time it's recreated).
Requires `deploy-infra` to have run first — `inventory.ini` won't exist
otherwise.

Tasks are written to be re-run safely: package installs are idempotent, and
the Spark extract/rename steps are skipped if `spark-submit` is already
present (`spark_installed` check in `tasks/main.yml`).

## Notes

- Bump `spark_version`/`hadoop_version` in `roles/admin/vars/main.yml`
  alongside the Java version in `tasks/main.yml` — see the version note in
  the top-level `../README.md`.
