export
CLUSTER_ID := "$$(terraform -chdir=terraform output -raw cluster_id)"


deploy-infra:
	terraform -chdir=terraform apply --auto-approve

destroy-infra:
	terraform -chdir=terraform destroy


# Requires the `databricks` CLI configured (databricks auth login, or the
# same DATABRICKS_HOST/DATABRICKS_TOKEN env vars the progressive scripts use).
start-cluster:
	databricks clusters start ${CLUSTER_ID}

stop-cluster:
	databricks clusters delete ${CLUSTER_ID}
