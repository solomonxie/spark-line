# Ansible

Configures the node Terraform created: a Python venv, Dagster + the
webserver, the eight progressive study-path files deployed to
`{{ dagster_home }}/defs/`, and `dagster dev` running as a systemd
service loading all eight as separate code locations.

```
site.yml                          → applies role `admin` to host group `dagster_nodes`
  └─ roles/admin
       ├─ vars/main.yml           → install path, list of study-path files
       └─ tasks/main.yml          → apt packages → venv → pip install
                                     → deploy defs/ → systemd unit → enable/start
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
venv creation skips once it exists, and the systemd unit is declarative —
re-applying just redeploys it and restarts the service.

## Notes

- Each of the eight files is passed to `dagster dev` as its own `-f` flag
  — one code location each, so identical names across files (two define a
  job called `hello_job`) don't collide. See
  `templates/dagster-dev.service.j2`.
- `DAGSTER_HOME` is set to `{{ dagster_home }}` (not the default temp
  directory) so run history survives a service restart.
- Webserver logs land under `journalctl -u dagster-dev`.
