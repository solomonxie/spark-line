# Leaf nodes — each output just reads an attribute off the already-created
# instance, so these are the last things evaluated in the plan:
#
#  aws_instance.airflow_hello_node ─┬─▶ output.airflow_node_public_ip
#                                   ├─▶ output.airflow_webserver_url (ip:8080)
#                                   ├─▶ output.ssh_airflow_command
#                                   └─▶ output.instance_id
#  var.aws_profile ─────────────────────▶ output.aws_profile
#
# instance_id is consumed back out-of-band by the Makefile
# (`terraform output -raw instance_id`) for start-server / stop-server.
output "airflow_node_public_ip" {
  value       = aws_instance.airflow_hello_node.public_ip
  description = "Public IP of the Airflow node"
}

output "airflow_node_public_dns" {
  value       = aws_instance.airflow_hello_node.public_dns
  description = "Public DNS name of the Airflow node"
}

output "airflow_webserver_url" {
  value       = "http://${aws_instance.airflow_hello_node.public_ip}:8080"
  description = "Airflow webserver UI"
}

output "ssh_airflow_command" {
  value       = "ssh -i ${var.private_key_path} ubuntu@${aws_instance.airflow_hello_node.public_ip}"
  description = "Command to SSH into the Airflow node"
}

output "instance_id" {
  value       = aws_instance.airflow_hello_node.id
  description = "EC2 instance ID"
}

output "aws_profile" {
  value       = var.aws_profile
  description = "Active AWS Profile"
}
