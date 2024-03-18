# Terraform

Optional: provisions a bare EC2 node running Postgres for step 8's
`--target postgres`. Every other progressive step runs against local
DuckDB — see `../README.md` — so you only need this if you want to try
dbt against a real remote warehouse.

Run through the repo-root `Makefile` (`make deploy-infra`), not `terraform
apply` directly.

```
terraform apply
  ├─ providers.tf         → auth against AWS
  ├─ variables.tf         → resolve inputs (including postgres_password)
  ├─ ec2.tf                → sg + key pair + ami lookup → aws_instance
  ├─ auto_terminate.tf     → schedule one-time termination ~2h out
  ├─ ansible_inventory.tf → write ansible/inventory.ini (+ postgres_password)
  └─ outputs.tf            → print IP / ssh command
        │
        ▼
ansible-playbook -i ansible/inventory.ini ansible/site.yml   (deploy-software)
        │
        ▼
PGHOST=<ip> PGPASSWORD=<password> dbt run --select dbt_08_postgres_target --target postgres
```

## Self-termination

`auto_terminate.tf` schedules a one-time EventBridge Scheduler rule that
terminates `aws_instance.dbt_hello_node` ~2h after creation — a cost
safety net for a sandbox that's easy to forget about. It's pinned to the
instance's id (`triggers`), so re-running `apply` doesn't push the deadline
out; the schedule fires once and deletes itself
(`action_after_completion = DELETE`). To keep a node alive longer, remove
`auto_terminate.tf`'s resources from state or bump `offset_hours` before
applying.

State (`terraform.tfstate*`) and the last plan (`tfplan.out`) live in this
directory and are gitignored per-environment — don't hand-edit them.
