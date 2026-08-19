# Declares the AWS provider and pins the Terraform/provider versions.
# Every other file depends on this implicitly (no explicit references).
#
#   terraform { required_providers { aws ~> 5.0 } }
#   provider "aws" { region = var.aws_region, profile = var.aws_profile }
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}
