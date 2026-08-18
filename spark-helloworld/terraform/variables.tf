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
