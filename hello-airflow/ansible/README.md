# Ansible

Configures the node Terraform created: a Python venv, Apache Airflow, the
metadata database, an admin user, the progressive study-path DAGs, and
`airflow standalone` running as a systemd service.

```
site.yml                          → applies role `admin` to host group `airflow_nodes`
  └─ roles/admin
       ├─ vars/main.yml           → Airflow version, install path, DAG file list
       └─ tasks/main.yml          → apt packages → venv → pip install (constrained)
                                     → db migrate → admin user → deploy DAGs
                                     → systemd unit → enable/start
inventory.ini                     → written by terraform/ansible_inventory.tf,
                                     not hand-edited (regenerated on every apply)
```

Run through the repo-root `Makefile`:

```
make deploy-software
```

which runs `ansible-playbook -i inventory.ini site.yml` (host key checking
off, since the node's IP is new every time it's recreated). Requires
`deploy-infra` to have run first.

Tasks are written to be re-run safely: package installs are idempotent,
the venv/db-migrate steps skip once their `creates:` target exists, the
admin user is only created if `airflow users list` doesn't already show
one, and the systemd unit is declarative — re-applying just redeploys it
and restarts the service.

## Notes

- `apache-airflow` isn't `pip install`-able on its own — it needs a
  constraints file pinning every transitive dependency to a combination
  the Airflow project tested for that (Airflow version, Python version)
  pair. `tasks/main.yml` detects the venv's Python version at apply time
  and builds the matching constraints URL; bump `airflow_version` in
  `vars/main.yml` and it picks the right one automatically.
- Default login is `admin` / `admin` (`tasks/main.yml`) — fine for a
  throwaway sandbox behind a security group you control, change it if
  you're leaving the node up for a while.
- Webserver logs land under `{{ airflow_home }}/logs`;
  `journalctl -u airflow-standalone` also works since it runs under
  systemd.
