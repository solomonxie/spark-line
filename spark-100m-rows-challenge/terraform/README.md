# Terraform

Provisions a single EC2 node for the Spark master/worker and hands its
address off to Ansible. Terraform builds an execution plan by resolving
attribute references between resources into a dependency graph — file order
doesn't matter, reference order does. See each file's head comment for its
place in that graph.

Run through the repo-root `Makefile` (`make deploy-infra`), not `terraform
apply` directly — the Makefile pins `-chdir=terraform` and the AWS profile.

```
terraform apply
  ├─ providers.tf         → auth against AWS
  ├─ variables.tf         → resolve inputs
  ├─ ec2.tf                → sg + key pair + ami lookup → aws_instance
  ├─ auto_terminate.tf     → schedule one-time termination ~2h out
  ├─ ansible_inventory.tf → write ansible/inventory.ini
  └─ outputs.tf            → print IPs / URLs / ssh command
        │
        ▼
ansible-playbook -i ansible/inventory.ini ansible/site.yml   (deploy-software)
```

## Self-termination

`auto_terminate.tf` schedules a one-time EventBridge Scheduler rule that
terminates `aws_instance.spark_hello_node` ~2h after creation — a cost
safety net for a sandbox that's easy to forget about. It's pinned to the
instance's id (`triggers`), so re-running `apply` doesn't push the deadline
out; the schedule fires once and deletes itself
(`action_after_completion = DELETE`). To keep a node alive longer, remove
`auto_terminate.tf`'s resources from state or bump `offset_hours` before
applying.

State (`terraform.tfstate*`) and the last plan (`tfplan.out`) live in this
directory and are gitignored per-environment — don't hand-edit them.
