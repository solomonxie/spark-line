# hello-dagster

Sandbox for experimenting with Dagster — software-defined assets,
resources, IO managers, partitions, and schedules/sensors. Infra is
throwaway: spin up, poke at it, tear down.

## How to use this

```
make deploy-infra       # terraform apply — creates the EC2 node
make deploy-software    # ansible-playbook — installs & starts dagster dev

make start-server       # aws ec2 start-instances (resume a stopped node)
make stop-server        # aws ec2 stop-instances (save cost when idle)
make destroy-infra      # terraform destroy — tear everything down
```

`AWS_PROFILE` defaults to `prod`; override with
`make deploy-infra AWS_PROFILE=<profile>`.

`deploy-software` also deploys the progressive study-path files onto the
node and loads all eight as separate code locations in one `dagster dev`
process. Webserver: `http://<public-ip>:3000` (`terraform -chdir=terraform
output dagster_webserver_url`).

## Progressive study path

Eight standalone scripts, `dagster_01_...py` through `dagster_08_...py`,
one Dagster concept each. Self-contained — own assets/ops, no imports
between them — and runnable via `materialize()`/`execute_in_process()`
against a throwaway local DB, no webserver or EC2 node required.

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

One-time setup (local venv or SSH'd into the node):

```
python3 -m venv venv && venv/bin/pip install dagster dagster-webserver
```

Then run any step directly:

```
venv/bin/python dagster_01_hello_asset.py
```

Each file also defines a module-level `defs = Definitions(...)`, which is
what lets `dagster dev -f <file>` load it as a real deployment. Steps 4 and
5 need this — their resource/IO-manager bindings only exist inside `defs`.

## Self-termination

The node auto-terminates ~2h after creation via a one-time EventBridge
rule (see `terraform/auto_terminate.tf`). Re-running `make deploy-infra`
doesn't push the deadline out — destroy/recreate, or extend
`auto_terminate.tf` yourself.
