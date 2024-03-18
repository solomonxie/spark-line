# Leaf nodes — each output just reads an attribute off the already-created
# instance, so these are the last things evaluated in the plan.
output "dbt_node_public_ip" {
  value       = aws_instance.dbt_hello_node.public_ip
  description = "Public IP of the Postgres node — set as PGHOST for step 8"
}

output "dbt_node_public_dns" {
  value       = aws_instance.dbt_hello_node.public_dns
  description = "Public DNS name of the Postgres node"
}

output "ssh_dbt_command" {
  value       = "ssh -i ${var.private_key_path} ubuntu@${aws_instance.dbt_hello_node.public_ip}"
  description = "Command to SSH into the Postgres node"
}

output "instance_id" {
  value       = aws_instance.dbt_hello_node.id
  description = "EC2 instance ID"
}

output "aws_profile" {
  value       = var.aws_profile
  description = "Active AWS Profile"
}
