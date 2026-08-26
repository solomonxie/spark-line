# Input declarations only — no resources, nothing to plan. Values are
# supplied by terraform.tfvars (gitignored, holds ssh_key_name,
# public_key_path, private_key_path) and by TF_VAR_aws_profile, which the
# root Makefile exports from AWS_PROFILE.
variable "aws_region" {
  type        = string
  default     = "ca-central-1"
  description = "Target AWS region for resources"
}

variable "ssh_key_name" {
  type        = string
  description = "Name of the AWS key pair"
}

variable "public_key_path" {
  type        = string
  description = "Path to local OpenSSH public key file"
}

variable "private_key_path" {
  type        = string
  description = "Path to local SSH private key file for output command"
}

variable "aws_profile" {
  type        = string
  description = "Which AWS Profile to use for deployment"
}

variable "postgres_password" {
  type        = string
  description = "Password for the 'dbt' Postgres role step 8 connects as"
  sensitive   = true
}
