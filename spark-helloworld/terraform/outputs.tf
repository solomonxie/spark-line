output "spark_node_public_ip" {
  value       = aws_instance.spark_hello_node.public_ip
  description = "Public IP of Ubuntu spark Node"
}

output "spark_node_public_dns" {
  value       = aws_instance.spark_hello_node.public_dns
  description = "Public DNS name of Ubuntu spark Node"
}

output "spark_bootstrap_server" {
  value       = "${aws_instance.spark_hello_node.public_ip}:9092"
  description = "spark Bootstrap Server endpoint"
}

output "ssh_spark_command" {
  value       = "ssh -i ${var.private_key_path} ubuntu@${aws_instance.spark_hello_node.public_ip}"
  description = "Command to SSH into the spark node"
}

output "instance_id" {
  value       = "${aws_instance.spark_hello_node.id}"
  description = "EC2 instance ID"
}

output "aws_profile" {
  value       = "${var.aws_profile}"
  description = "Active AWS Profile"
}
