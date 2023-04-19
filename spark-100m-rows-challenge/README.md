# Spark: 100M Rows Challenge

Scenario
The data engineering team is upgrading the batch ingestion pipeline for the NYC Taxi & Limousine Commission (TLC) trip dataset.
The system processes 1 year of raw trip telemetry (100M+ records, ~10 GB)
and transforms it using a dual-write architecture.
The output must be persisted simultaneously to:
- an ACID-compliant Delta Lakehouse (for long-term historical analytics and machine learning)
- a ClickHouse OLAP cluster (for sub-second real-time dashboarding and ad-hoc querying)

Hardware:
Must execute on a single-node EC2 instance (t3.xlarge: 16 GB RAM, 4 vCPUs)
interacting with a local ClickHouse instance.
The system objective is to achieve maximum processing throughput
without exceeding driver/executor memory limits,
spilling intermediate partition state to disk,
or creating inconsistency between the Lakehouse and ClickHouse storage layers.


Mission Task List & Expected Outcomes

Task 1: Strict Ingestion & Schema Enforcement
- Task: Ingest 12 months of raw NYC Yellow Taxi data without triggering auto-inference scans or lazy schema failures.
- Expected Outcome:
  Explicit PySpark StructType schema defined with correct native data types (TimestampType, DoubleType, IntegerType).
  Raw Parquet files read directly into a DataFrame in under 5 seconds without invoking double-pass execution jobs.

Task 2: Data Cleansing & Business Metric Derivation
- Task: Identify and drop invalid/corrupt records and derive trip duration metrics.
- Expected Outcome:
  Cleaned DataFrame filtering out non-positive passenger counts, zero/negative trip distances, and non-positive fare amounts.
  New column trip_duration_min derived as (tpep_dropoff_datetime - tpep_pickup_datetime) in minutes.
  Outlier records (< 1 minute or > 1440 minutes) removed.

Task 3: Zero-Shuffle Dimension Enrichment (Broadcast Join)
- Task: Enrich trip records with zone metadata (Borough, Zone) using the Taxi Zone Lookup CSV table (~265 records).
- Expected Outcome:
  Join executed using pyspark.sql.functions.broadcast() on PULocationID == LocationID.
  Physical plan (.explain()) displays BroadcastHashJoin with zero network shuffles (Exchange nodes) for the lookup table.

Task 4: Skew-Aware Window Aggregation
- Task: Rank the top 3 highest-spending trips per pickup zone (PULocationID) per month without JVM Garbage Collection (GC) pauses or Out-Of-Memory (OOM) crashes caused by traffic skew.
- Expected Outcome:
  Aggregation implemented using Window.partitionBy("PULocationID", "month").orderBy(col("fare_amount").desc()) with dense_rank().
  Adaptive Query Execution (AQE) enabled (spark.sql.adaptive.skewJoin.enabled=true) to handle high-volume zones (e.g., JFK, Midtown).

Task 5: Delta Lake Storage, Partitioning & Upserts
- Task: Write the primary dataset to Delta Lake format partitioned by year and month, then execute an incremental upsert batch.
- Expected Outcome:
  Dataset written to Delta Lake format without modifying un-partitioned data.
  Atomic MERGE INTO executed using DeltaTable.merge() to update modified trip records based on VendorID and tpep_pickup_datetime keys.
  Target Delta transaction log (_delta_log/) verified for commit entry creation.

Task 6: ClickHouse Dual-Write & JDBC/Connector Sink
- Task: Write the identical cleaned and enriched DataFrame into ClickHouse using the spark-clickhouse-connector or batch JDBC writer.
- Expected Outcome:
  ClickHouse target table configured with ReplacingMergeTree engine to handle duplicate record resolution on (VendorID, tpep_pickup_datetime).
  Spark batch write successfully populates ClickHouse without exhausting socket connections or hitting ClickHouse memory limits.
  Row count and sum aggregation parity verified between Delta Lake and ClickHouse.

Task 7: Storage Maintenance & Small-File Mitigation
- Task: Eliminate small files in Delta Lake and optimize ClickHouse table parts.
- Expected Outcome:
  Delta OPTIMIZE command executed to compact output Parquet files to target file sizes between 100 MB and 512 MB.
  Delta VACUUM command run to clean unreferenced physical Parquet files beyond retention threshold.
  ClickHouse OPTIMIZE TABLE FINAL executed to trigger part merges for ReplacingMergeTree.


System Validation & Acceptance Criteria

Area: Resource Efficiency
- Target Benchmark: Spark UI (localhost:4040) shows Spill (Memory) = 0 B and Spill (Disk) = 0 B during dual-write steps.
- Failure Condition: Executor JVM experiences OutOfMemoryError or heavy disk spilling during window aggregations or ClickHouse write buffers.

Area: Execution Plan & Join Efficiency
- Target Benchmark: df.explain() confirms predicate pushdown and BroadcastHashJoin for dimension lookups.
- Failure Condition: Standard SortMergeJoin triggered for small lookup table, causing unnecessary wide network shuffles.

Area: Dual-Write Consistency & Data Integrity
- Target Benchmark: Delta Lake count equals ClickHouse table count; zero null values in derived duration metric; sums of fare_amount match exactly across both sinks.
- Failure Condition: Data drift between Lakehouse and ClickHouse, unhandled schema drift, or dropped batch partitions.

Area: Storage Quality
- Target Benchmark: Delta directory contains balanced Parquet files (100 MB - 500 MB); ClickHouse parts merged cleanly without active unmerged part bloat.
- Failure Condition: Thousands of KB-sized files in Delta Lake or excessive small parts error in ClickHouse log.


Time Constraints
Total End-to-End: <15 minutes
Stage Breakdown Targets:
- Ingestion: <10 seconds
- Cleaning, Transformation: <3 minutes
- Aggregations: <3 minutes
- Delta Lake Write: <4 minutes
- ClickHouse Write: <4 minutes
- Storage maintenance: <1 minute



## Layout

- `terraform/` — provisions the EC2 node this project runs on and writes its
  address into the Ansible inventory. See `terraform/README.md` for the
  resource graph and the self-termination safety net.
- `ansible/` — setup runtime environment
- `Makefile` — day-to-day commands, wraps Terraform/Ansible/AWS CLI calls
  (see below).

## How to use this

**Automated path** — Terraform provisions the node, Ansible configures it,
the `Makefile` drives both:

```
make deploy-infra       # terraform apply — creates the EC2 node
make deploy-software    # ansible-playbook — installs Java/Spark/pyspark

make start-server       # aws ec2 start-instances (resume a stopped node)
make stop-server        # aws ec2 stop-instances (save cost when idle)
make destroy-infra      # terraform destroy — tear everything down
```

`AWS_PROFILE` defaults to `prod` in the Makefile; override with
`make deploy-infra AWS_PROFILE=<profile>`.

`deploy-software` also starts the Spark cluster itself — 1 master/driver +
2 workers, running as systemd services on the same node (see
`ansible/README.md`). Nothing to start by hand; SSH in
(`terraform -chdir=terraform output ssh_spark_command`) only to run
`spark-submit`/`pyspark` jobs or to check `systemctl status spark-master
spark-worker@8081 spark-worker@8082`.

Master UI: `http://<public-ip>:8080` (`terraform -chdir=terraform output
spark_master_ui`). Worker UIs: `:8081` and `:8082`.

## Self-termination

The node auto-terminates ~2h after creation via a one-time EventBridge
Scheduler rule (cost safety net, no action needed) — see
`terraform/auto_terminate.tf`. If you're still using the node past that
window, re-running `make deploy-infra` does **not** push the deadline out;
you'd need to destroy/recreate it, or extend `auto_terminate.tf` yourself.

## Notes

- Spark version and Java version must stay in lock-step — Spark 4.x requires
  Java 17+. Bump both together in `ansible/roles/spark_runtime/vars/main.yml`,
  `ansible/roles/spark_runtime/tasks/main.yml`, and `manual_build.sh`.
