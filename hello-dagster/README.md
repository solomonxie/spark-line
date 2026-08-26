# hello-dagster

Sandbox for experimenting with Dagster — software-defined assets,
resources, IO managers, partitions, and schedules/sensors. Infra is
throwaway by design: spin up, poke at it, tear down.

## Layout

- `terraform/` — provisions the EC2 node this project runs on and writes
  its address into the Ansible inventory. See `terraform/README.md` for
  the resource graph and the self-termination safety net.
- `ansible/` — installs a Python venv, Dagster + the webserver, and runs
  `dagster dev` as a systemd service. See `ansible/README.md`.
- `dagster_01_hello_asset.py` ... `dagster_08_real_pipeline.py` — a
  progressive study path, one Dagster concept per file. See below.
- `Makefile` — day-to-day commands, wraps Terraform/Ansible/AWS CLI calls
  (see below).

## How to use this

```
make deploy-infra       # terraform apply — creates the EC2 node
make deploy-software    # ansible-playbook — installs & starts dagster dev

make start-server       # aws ec2 start-instances (resume a stopped node)
make stop-server        # aws ec2 stop-instances (save cost when idle)
make destroy-infra      # terraform destroy — tear everything down
```

`AWS_PROFILE` defaults to `prod` in the Makefile; override with
`make deploy-infra AWS_PROFILE=<profile>`.

`deploy-software` also deploys the progressive study-path files onto the
node and loads all eight as separate code locations in one `dagster dev`
process (`-f` per file — see `ansible/README.md` for why that matters).
Webserver: `http://<public-ip>:3000` (`terraform -chdir=terraform output
dagster_webserver_url`).

## Progressive study path

Eight standalone scripts, `dagster_01_...py` through `dagster_08_...py`,
each covering one Dagster concept. Every file is fully self-contained —
its own assets/ops, no imports between them — and runs on its own via
`materialize()` or `execute_in_process()`, which execute in-process
against a throwaway local DB. No webserver, no daemon, no EC2 node
required to work through the path.

| Step | File | Concept |
| --- | --- | --- |
| 1 | `dagster_01_hello_asset.py` | The smallest software-defined asset; `materialize()` |
| 2 | `dagster_02_asset_dependencies.py` | Dependencies inferred from function signatures |
| 3 | `dagster_03_ops_and_jobs.py` | The lower-level ops/jobs API underneath assets |
| 4 | `dagster_04_resources.py` | Injectable, swappable resources |
| 5 | `dagster_05_io_manager.py` | A custom IO manager controlling *how* outputs are stored |
| 6 | `dagster_06_partitions.py` | Partitioned assets; materializing one slice |
| 7 | `dagster_07_schedules_and_sensors.py` | Testing schedules/sensors without a running daemon |
| 8 | `dagster_08_real_pipeline.py` | Capstone: a real extract/transform/load pipeline as assets |

One-time setup (any machine with `dagster` installed — a local venv, or
SSH'd into the node):

```
python3 -m venv venv && venv/bin/pip install dagster dagster-webserver
```

Then run any step directly:

```
venv/bin/python dagster_01_hello_asset.py
```

Each file also defines a module-level `defs = Definitions(...)` in
addition to its `if __name__ == "__main__"` block — that's what lets
`dagster dev -f <file>` (used by `ansible/`) load it as a real deployment,
not just run it as a script. Steps 4 and 5 specifically need this: their
resource/IO-manager bindings only exist inside `defs`, so loading the file
without it fails with a missing-resource error (found the hard way while
writing this — see the comment in `dagster_04_resources.py`).

All eight were run standalone and as a combined `dagster dev -f ... -f
...` deployment (matching what `ansible/` does) against Dagster 1.13.19 /
dagster-webserver while writing this.

## Self-termination

The node auto-terminates ~2h after creation via a one-time EventBridge
Scheduler rule (cost safety net, no action needed) — see
`terraform/auto_terminate.tf`. If you're still using the node past that
window, re-running `make deploy-infra` does **not** push the deadline out;
you'd need to destroy/recreate it, or extend `auto_terminate.tf` yourself.
