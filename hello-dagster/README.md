# hello-dagster

Sandbox for experimenting with Dagster — software-defined assets,
resources, IO managers, partitions, and schedules/sensors. Infra is
throwaway: spin up, poke at it, tear down.

`make deploy-infra && make deploy-software` provisions the node and starts
`dagster dev` with all eight study-path files loaded as separate code
locations (webserver: `http://<public-ip>:3000`); `make destroy-infra`
tears down. Node self-terminates ~2h after creation regardless — see
`terraform/auto_terminate.tf`.

`dagster_01_hello_asset.py` → `dagster_08_real_pipeline.py` are a
progressive, self-contained study path, one Dagster concept per file — run
any directly with `venv/bin/python dagster_01_hello_asset.py`
(`python3 -m venv venv && venv/bin/pip install dagster dagster-webserver`
first). Each also defines a module-level `defs = Definitions(...)`, which
is what lets `dagster dev -f <file>` load it as a real deployment.
