# Dynamically generate latest server info for Ansible to access

resource "local_file" "ansible_inventory" {
  filename = "${path.module}/../ansible/inventory.ini"
  content  = <<EOF
[spark_nodes]
spark_node ansible_host=${aws_instance.spark_hello_node.public_dns} ansible_user=ubuntu ansible_ssh_private_key_file=${var.private_key_path}
EOF
}
