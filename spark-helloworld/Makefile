export
AWS_PROFILE := prod
TF_VAR_aws_profile := ${AWS_PROFILE}
EC2_ID := "$$(terraform -chdir=terraform output -raw instance_id)"


deploy-infra:
	terraform -chdir=terraform apply --auto-approve

deploy-software:
	ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i ansible/inventory.ini ansible/site.yml


destroy-infra:
	terraform -chdir=terraform destroy


stop-server:
	aws ec2 stop-instances --instance-ids ${EC2_ID} --profile ${AWS_PROFILE}


start-server:
	aws ec2 start-instances --instance-ids ${EC2_ID} --profile ${AWS_PROFILE}
