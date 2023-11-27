# Leaf nodes consumed by the progressive scripts' env vars and the Makefile.
output "cluster_id" {
  value       = databricks_cluster.hello.id
  description = "DATABRICKS_CLUSTER_ID for the progressive scripts / Databricks Connect"
}

output "cluster_name" {
  value       = databricks_cluster.hello.cluster_name
  description = "Cluster display name, for the workspace UI"
}

output "unity_catalog_schema" {
  value       = "${var.catalog_name}.${databricks_schema.hello.name}"
  description = "DATABRICKS_CATALOG.DATABRICKS_SCHEMA for steps 3-6"
}

output "volume_path" {
  value       = "/Volumes/${var.catalog_name}/${databricks_schema.hello.name}/${databricks_volume.hello_data.name}"
  description = "Unity Catalog Volume path for step 5's file I/O"
}
