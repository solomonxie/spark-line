# Input declarations only — no resources, nothing to plan. Values are
# supplied by terraform.tfvars (gitignored — see ../README.md for what to
# put in it).
variable "databricks_host" {
  type        = string
  description = "Workspace URL, e.g. https://<workspace-id>.cloud.databricks.com"
}

variable "databricks_token" {
  type        = string
  description = "Personal access token (Settings > Developer > Access tokens)"
  sensitive   = true
}

variable "catalog_name" {
  type        = string
  default     = "main"
  description = "Existing Unity Catalog catalog to create the schema/volume under"
}

variable "schema_name" {
  type        = string
  default     = "hello_databricks"
  description = "Schema created for this project's tables/volume"
}

variable "autotermination_minutes" {
  type        = number
  default     = 30
  description = "Cluster self-terminates after this many idle minutes (cost safety net — Databricks' built-in equivalent of the other projects' EventBridge auto-terminate)"
}
