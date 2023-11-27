# Provisions a single-node, all-purpose cluster for the progressive scripts
# to connect to via Databricks Connect.
#
#   data.databricks_spark_version.latest_lts   (no deps — queried from the workspace)
#   data.databricks_node_type.smallest         (no deps — queried from the workspace)
#           │
#           ▼
#   databricks_cluster.hello
#     ├─ spark_version = data.databricks_spark_version.latest_lts.id
#     ├─ node_type_id  = data.databricks_node_type.smallest.id
#     └─ autotermination_minutes = var.autotermination_minutes
#
# num_workers = 0 + the spark_conf/custom_tags below is the documented
# "single-node cluster" shape: the driver does double duty as its own
# (only) executor, which is all eight progressive scripts need.

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}

data "databricks_node_type" "smallest" {
  local_disk = true
}

resource "databricks_cluster" "hello" {
  cluster_name            = "hello-databricks"
  spark_version           = data.databricks_spark_version.latest_lts.id
  node_type_id            = data.databricks_node_type.smallest.id
  autotermination_minutes = var.autotermination_minutes
  num_workers             = 0

  spark_conf = {
    "spark.master"                     = "local[*, 4]"
    "spark.databricks.cluster.profile" = "singleNode"
  }

  custom_tags = {
    "ResourceClass" = "SingleNode"
  }
}
