# Bridges Terraform to Ansible. local_file depends on the instance's
# public_dns, so it can only run after aws_instance.dagster_hello_node is
# created — Terraform infers this from the reference, no depends_on needed.
#
#   aws_instance.dagster_hello_node.public_dns
#           │
#           ▼
#   local_file.ansible_inventory  ──▶  ../ansible/inventory.ini
#                                         [dagster_nodes]
#                                         dagster_node ansible_host=<public_dns> ...
#
# `make deploy-software` reads that generated file to target the node.

resource "local_file" "ansible_inventory" {
  filename = "${path.module}/../ansible/inventory.ini"
  content  = <<EOF
[dagster_nodes]
dagster_node ansible_host=${aws_instance.dagster_hello_node.public_dns} ansible_user=ubuntu ansible_ssh_private_key_file=${var.private_key_path}
EOF
}
