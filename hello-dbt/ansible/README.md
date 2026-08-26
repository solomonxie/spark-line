# Ansible

Optional: configures the node Terraform created as a bare Postgres
warehouse for step 8. Skip this entirely if you're only running the
DuckDB-backed steps 1-7 — see `../README.md`.

```
site.yml                          → applies role `admin` to host group `dbt_nodes`
  └─ roles/admin
       └─ tasks/main.yml          → apt install postgresql → start it
                                     → create role `dbt` + database `hello_dbt`
                                     → listen on all interfaces, allow
                                       password auth from any host
inventory.ini                     → written by terraform/ansible_inventory.tf
                                     (host + postgres_password), not hand-edited
```

Run through the repo-root `Makefile`:

```
make deploy-software
```

which runs `ansible-playbook -i inventory.ini site.yml`. Requires
`deploy-infra` to have run first.

Tasks are written to be re-run safely: the role/database creation checks
`pg_roles`/`pg_database` first, and the config edits are idempotent
`lineinfile` changes.

## Notes

- `pg_hba.conf` is opened to password auth from any host — the security
  group (port 5432 only) is what actually restricts access, matching this
  repo's other throwaway-sandbox projects. Don't point this node at
  anything you care about.
- The Postgres major version is auto-detected from `/etc/postgresql/` at
  apply time (whatever Ubuntu 26.04's `postgresql` apt package installs),
  not hardcoded.
