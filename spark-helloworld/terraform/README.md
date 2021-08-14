# Terraform

Provisions a single EC2 node for the Spark master/worker and hands its
address off to Ansible. Terraform builds an execution plan by resolving
attribute references between resources into a dependency graph — file order
doesn't matter, reference order does. See each file's head comment for its
place in that graph.

```
terraform apply
  ├─ providers.tf         → auth against AWS
  ├─ variables.tf         → resolve inputs
  ├─ ec2.tf                → sg + key pair + ami lookup → aws_instance
  ├─ ansible_inventory.tf → write ansible/inventory.ini
  └─ outputs.tf            → print IPs / URLs / ssh command
        │
        ▼
ansible-playbook -i ansible/inventory.ini ansible/site.yml   (deploy-software)
```
