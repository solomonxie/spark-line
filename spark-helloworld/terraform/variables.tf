# Input declarations only — no resources, nothing to plan. Values are
# supplied by terraform.tfvars (gitignored, holds ssh_key_name,
# public_key_path, private_key_path) and by TF_VAR_aws_profile, which the
# root Makefile exports from AWS_PROFILE.
#
#   terraform.tfvars ──┐
#   TF_VAR_aws_profile ─┴─▶ var.* ──▶ referenced by providers.tf, ec2.tf, outputs.tf
variable "aws_region" {
  type        = string
  default     = "ca-central-1"
  description = "Target AWS region for resources"
}

# Sensitive variables, get them from Environment injection, go to .tf_vars
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
