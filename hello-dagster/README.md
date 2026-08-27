# hello-dagster

Experiments on Dagster — software-defined assets, resources, IO managers,
partitions, and schedules/sensors. Infra is throwaway: spin up, poke at
it, tear down.

`make deploy-infra && make deploy-software` provisions the node and starts
Dagster's dev server with the study-path assets loaded as separate code
locations (webserver: `http://<public-ip>:3000`); `make destroy-infra`
tears down. The node also self-terminates ~2h after creation regardless.

A progressive, self-contained set of scripts walks through one Dagster
concept at a time, each runnable on its own once Dagster is installed
locally.
