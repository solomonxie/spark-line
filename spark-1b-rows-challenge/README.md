# Spark: One Billion Row Challenge (1BRC)

Distributed PySpark take on the [One Billion Row Challenge](https://github.com/gunnarmorling/1brc):
read a ~1 billion line `<station>;<temperature>` file and print one line
per station's min/mean/max, sorted alphabetically, rounded to one
decimal:

```
{Station1=min1/mean1/max1, Station2=min2/mean2/max2, ...}
```

Runs on one EC2 t3.xlarge (16GB/4vCPU) — 1 Spark driver + 2 workers on
that single box. The original's ~10s/bare-metal target doesn't apply
here; the bar is processing the full 1B rows correctly on this modest,
shared cluster, with no executor OOM and no avoidable shuffle.

## Approach

Explicit schema on read (no inference) → `groupBy().agg(min, avg, max)`
(not a UDF, not driver-side collect-then-reduce) → sort + format → verify
against a bundled brute-force reference on a small sample before scaling
to 1B rows. Success: `.explain()` shows one shuffle with a partial
(map-side) `HashAggregate` before it; the full run completes with no
executor OOM and no meaningful spill (check `:4040`). No fixed time SLA —
expect low-single-digit minutes once properly partitioned.

`make deploy-infra && make deploy-software` provisions the node and
starts the cluster (master UI `:8080`, workers `:8081`/`:8082`); `make
generate-data` and related targets handle data/job prep, then SSH in and
run `spark-submit` — a process doc walks through the full progression.
`make destroy-infra` tears down; the node also self-terminates ~2h after
creation regardless.

`deploy-software` also stands up a public JupyterLab instance (`terraform
-chdir=terraform output -raw jupyter_url`/`jupyter_password`) with the
lesson/scale-tier scripts and data generator pre-seeded; every kernel
gets a `spark` SparkSession in `local[*]` mode by default. Port 8888 is
open to the internet, so the password is what's actually protecting it —
don't leave the node up longer than needed.

## Notes

- Spark and Java versions must stay in lock-step — Spark 4.x needs Java
  17+, pinned together in the Ansible role that installs them.
