# Leaf nodes — each output just reads an attribute off the already-created
# instance, so these are the last things evaluated in the plan.
output "dagster_node_public_ip" {
  value       = aws_instance.dagster_hello_node.public_ip
  description = "Public IP of the Dagster node"
}

output "dagster_node_public_dns" {
  value       = aws_instance.dagster_hello_node.public_dns
  description = "Public DNS name of the Dagster node"
}

output "dagster_webserver_url" {
  value       = "http://${aws_instance.dagster_hello_node.public_ip}:3000"
  description = "Dagster webserver UI"
}

output "ssh_dagster_command" {
  value       = "ssh -i ${var.private_key_path} ubuntu@${aws_instance.dagster_hello_node.public_ip}"
  description = "Command to SSH into the Dagster node"
}

output "instance_id" {
  value       = aws_instance.dagster_hello_node.id
  description = "EC2 instance ID"
}

output "aws_profile" {
  value       = var.aws_profile
  description = "Active AWS Profile"
}
