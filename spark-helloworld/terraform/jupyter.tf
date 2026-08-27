# Generates the JupyterLab login password so nothing has to be invented
# or committed by hand. Flows: this resource's .result -> written into
# ansible/inventory.ini by ansible_inventory.tf -> hashed on the box by
# ansible/roles/jupyter -> readable back here via `terraform output
# -raw jupyter_password` (see outputs.tf).
#
# special = false avoids characters that need escaping when the value
# passes through the ansible inventory file, Jinja2, and a systemd unit.
resource "random_password" "jupyter_password" {
  length  = 20
  special = false
}
