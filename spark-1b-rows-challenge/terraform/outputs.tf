# Leaf nodes — each output just reads an attribute off the already-created
# instance, so these are the last things evaluated in the plan:
#
#  aws_instance.spark_hello_node ──┬─▶ output.spark_node_public_ip
#                                  ├─▶ output.spark_node_public_dns
#                                  ├─▶ output.spark_master_url   (dns:7077)
#                                  ├─▶ output.spark_master_ui    (ip:8080)
#                                  ├─▶ output.ssh_spark_command
#                                  └─▶ output.instance_id
#  var.aws_profile ────────────────────▶ output.aws_profile
#  var.private_key_path ───────────────▶ output.ssh_private_key_path
#
# instance_id is consumed back out-of-band by the Makefile
# (`terraform output -raw instance_id`) for start-server / stop-server.
# spark_node_public_ip / ssh_private_key_path are likewise consumed by the
# Makefile's generate-data / push-job / fetch-results targets.
output "spark_node_public_ip" {
  value       = aws_instance.spark_hello_node.public_ip
  description = "Public IP of Ubuntu spark Node"
}

output "spark_node_public_dns" {
  value       = aws_instance.spark_hello_node.public_dns
  description = "Public DNS name of Ubuntu spark Node"
}

output "spark_master_url" {
  value       = "spark://${aws_instance.spark_hello_node.public_dns}:7077"
  description = "Spark Master URL for workers/spark-submit to connect to"
}

output "spark_master_ui" {
  value       = "http://${aws_instance.spark_hello_node.public_ip}:8080"
  description = "Spark Master Web UI"
}

output "ssh_spark_command" {
  value       = "ssh -i ${var.private_key_path} ubuntu@${aws_instance.spark_hello_node.public_ip}"
  description = "Command to SSH into the spark node"
}

output "ssh_private_key_path" {
  value       = var.private_key_path
  description = "Local path to the SSH private key, for scp/ssh in the Makefile"
}

output "instance_id" {
  value       = "${aws_instance.spark_hello_node.id}"
  description = "EC2 instance ID"
}

output "aws_profile" {
  value       = "${var.aws_profile}"
  description = "Active AWS Profile"
}
