# Declares the Databricks provider and pins the Terraform/provider versions.
# Every other file depends on this implicitly (no explicit references).
#
# Unlike the AWS-based projects in this repo, there's no cloud account to
# provision from scratch here — this authenticates against a Databricks
# workspace that already exists (a free trial or Community Edition works
# fine) and manages objects inside it.
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.55"
    }
  }
}

provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}
