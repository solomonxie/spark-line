# Declares the AWS provider and pins the Terraform/provider versions.
# Every other file depends on this implicitly (no explicit references).
#
#   terraform { required_providers { aws ~> 6.0 } }
#   provider "aws" { region = var.aws_region, profile = var.aws_profile }
#
# aws ~> 6.0: auto_terminate.tf needs action_after_completion on
# aws_scheduler_schedule, which only exists from provider v6 onward.
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
