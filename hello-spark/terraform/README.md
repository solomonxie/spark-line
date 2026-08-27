# Terraform

Provisions a single EC2 node for the Spark master/worker and hands its
address off to Ansible. Reference order (not file order) determines
Terraform's dependency graph — see each file's head comment for its place
in it.

Run through the repo-root `Makefile` (`make deploy-infra`), not `terraform
apply` directly — it pins `-chdir=terraform` and the AWS profile.

```
terraform apply
  ├─ providers.tf         → auth against AWS
  ├─ variables.tf         → resolve inputs
  ├─ ec2.tf                → sg + key pair + ami lookup → aws_instance
  ├─ auto_terminate.tf     → schedule one-time termination ~2h out
  ├─ jupyter.tf             → generate the JupyterLab password
  ├─ ansible_inventory.tf → write ansible/inventory.ini
  └─ outputs.tf            → print IPs / URLs / ssh command / jupyter creds
        │
        ▼
ansible-playbook -i ansible/inventory.ini ansible/site.yml   (deploy-software)
```

## Self-termination

`auto_terminate.tf` schedules a one-time EventBridge rule that terminates
`aws_instance.spark_hello_node` ~2h after creation. Pinned to the
instance's id, so re-running `apply` doesn't push the deadline out — the
schedule fires once and deletes itself. To keep a node alive longer,
remove `auto_terminate.tf`'s resources from state or bump `offset_hours`
before applying.

State (`terraform.tfstate*`) and the last plan (`tfplan.out`) live here,
gitignored — don't hand-edit them.
