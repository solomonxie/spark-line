# Declares the AWS provider and pins the Terraform/provider versions.
# Every other file depends on this implicitly (no explicit references).
#
# Optional: only needed for step 8's `--target postgres`. Every other
# progressive step runs against local DuckDB with zero infra — see
# ../README.md.
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    # Used by auto_terminate.tf to pin the self-terminate deadline.
    time = {
      source  = "hashicorp/time"
      version = "~> 0.11"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}
