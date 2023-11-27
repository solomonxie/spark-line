# A schema (and a managed Volume inside it) for the progressive scripts to
# read/write against — steps 3-6 all target catalog.schema.table or
# /Volumes/catalog/schema/volume paths built from these.
#
#   databricks_schema.hello
#     └─ databricks_volume.hello_data   (MANAGED — Databricks owns the storage)
#
# Requires var.catalog_name to already exist (the default, "main", exists
# by default in most workspaces) — creating a catalog itself needs
# metastore-admin privileges this project doesn't assume you have.

resource "databricks_schema" "hello" {
  catalog_name = var.catalog_name
  name         = var.schema_name
  comment      = "Schema for the hello-databricks progressive study path"
}

resource "databricks_volume" "hello_data" {
  catalog_name = var.catalog_name
  schema_name  = databricks_schema.hello.name
  name         = "hello_data"
  volume_type  = "MANAGED"
  comment      = "File I/O sandbox for hello_databricks step 5"
}
