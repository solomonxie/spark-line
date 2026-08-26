# hello-dbt

Sandbox for experimenting with dbt — models, `ref()`, incremental builds,
tests, and macros — against local DuckDB, with an optional EC2 Postgres
warehouse for going beyond that. No infra required for the core path:
`pip install dbt-duckdb` and you're running models in seconds.

## Layout

- `dbt_project.yml` / `profiles.yml` — a single project-local profile with
  two targets: `duckdb` (default, zero infra) and `postgres` (the optional
  EC2 node below).
- `models/dbt_01_hello_model.sql` ... `models/dbt_08_postgres_target.sql`
  — a progressive study path, one dbt concept per file. See below.
- `macros/celsius_to_fahrenheit.sql` — the custom macro step 7 calls.
- `terraform/` + `ansible/` — **optional**: provisions a bare EC2 Postgres
  node for step 8's `--target postgres`. See `terraform/README.md`. Skip
  entirely if you're only doing steps 1-7.
- `Makefile` — wraps Terraform/Ansible/AWS CLI calls for the optional
  Postgres node (see below).

## How to use this

Core path, no infra:

```
pip install dbt-duckdb
dbt run --select dbt_01_hello_model
```

(all commands below assume you're in this directory, with `dbt` on your
`PATH` and `DBT_PROFILES_DIR` unset — `profiles.yml` living right next to
`dbt_project.yml` is enough for dbt to find it.)

Optional Postgres warehouse, for step 8:

```
make deploy-infra       # terraform apply — creates the EC2 node
make deploy-software    # ansible-playbook — installs & configures Postgres

make start-server       # aws ec2 start-instances (resume a stopped node)
make stop-server        # aws ec2 stop-instances (save cost when idle)
make destroy-infra      # terraform destroy — tear everything down
```

`AWS_PROFILE` defaults to `prod` in the Makefile; override with
`make deploy-infra AWS_PROFILE=<profile>`. `terraform.tfvars` needs a
`postgres_password` in addition to the usual `ssh_key_name` /
`public_key_path` / `private_key_path` — see `terraform/README.md`.

## Progressive study path

Nine models (step 5 is two files — see below), each covering one dbt
concept. Every model builds its own data inline via `VALUES` rather than
reading a shared seed, so — with one deliberate exception — each stands
alone: no `ref()` chain to build first, no fixtures to set up.

| Step | File(s) | Concept |
| --- | --- | --- |
| 1 | `dbt_01_hello_model.sql` | The simplest model — a view over a literal row |
| 2 | `dbt_02_inline_data.sql` | An inline dataset via `VALUES` |
| 3 | `dbt_03_transformations.sql` | Derived columns, `CASE WHEN` |
| 4 | `dbt_04_aggregation.sql` | `GROUP BY` + `count`/`avg`/`max` |
| 5 | `dbt_05a_upstream_orders.sql` + `dbt_05b_downstream_summary.sql` | `ref()` — dbt's core idea (the one exception to "stands alone") |
| 6 | `dbt_06_incremental_model.sql` | Incremental materialization + `is_incremental()` |
| 7 | `dbt_07_macros.sql` | A custom Jinja macro |
| 8 | `dbt_08_postgres_target.sql` | Capstone: the same model, run against a real warehouse |

Plus `models/schema.yml`, which adds `not_null`/`unique` tests on steps 1
and 4 — run with `dbt test`.

Run any step directly:

```
dbt run --select dbt_01_hello_model
dbt run --select dbt_02_inline_data
dbt run --select dbt_03_transformations
dbt run --select dbt_04_aggregation
dbt run --select +dbt_05b_downstream_summary   # `+` builds 05a first
dbt run --select dbt_06_incremental_model      # run twice — 2nd run adds 0 rows
dbt run --select dbt_07_macros
dbt test
```

Step 8 needs the optional Postgres node (see above) and:

```
export PGHOST=$(terraform -chdir=terraform output -raw dbt_node_public_ip)
export PGPASSWORD=<the postgres_password from terraform.tfvars>
dbt run --select dbt_08_postgres_target --target postgres
```

All nine models plus `dbt test` were run end to end against `dbt-duckdb`
1.11.0 / dbt-core 1.12.3 while writing this, including step 6's two-run
incremental behavior.

## Self-termination

Only relevant if you provisioned the optional Postgres node — it
auto-terminates ~2h after creation via a one-time EventBridge Scheduler
rule (cost safety net, no action needed). See `terraform/auto_terminate.tf`.

## Notes

- `target/`, `logs/`, and `*.duckdb` are gitignored — dbt regenerates all
  of them; there's nothing to commit there.
