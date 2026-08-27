export
AWS_PROFILE := prod
TF_VAR_aws_profile := ${AWS_PROFILE}
EC2_ID := "$$(terraform -chdir=terraform output -raw instance_id)"
NODE_IP := "$$(terraform -chdir=terraform output -raw spark_node_public_ip)"
SSH_KEY := "$$(terraform -chdir=terraform output -raw ssh_private_key_path)"
NODE_SSH := ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ubuntu@${NODE_IP}
NODE_SCP := scp -i ${SSH_KEY} -o StrictHostKeyChecking=no

# generate-data defaults: 1B rows across 1000 stations. Override e.g.
# `make generate-data ROWS=1000000 STATIONS=200` for a fast local-scale run.
ROWS ?= 1000000000
STATIONS ?= 1000


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


# Ships data/ to the node and runs the generator there — the file (~15-20GB
# at 1B rows) is never transferred over the network, only produced on-box.
generate-data:
	${NODE_SCP} -r data ubuntu@${NODE_IP}:~/1brc-data-gen
	${NODE_SSH} 'mkdir -p ~/data && python3 ~/1brc-data-gen/generate_measurements.py --rows ${ROWS} --stations ${STATIONS} --output ~/data/measurements.txt'

# Copies your local spark/job.py to the node for spark-submit.
push-job:
	${NODE_SCP} spark/job.py ubuntu@${NODE_IP}:~/job.py

# Copies the solve_*.py scale ladder AND data/ (each solve_*.py generates
# its own tier's input on first run via ~/1brc-data-gen) to the node.
push-solve:
	${NODE_SCP} -r data ubuntu@${NODE_IP}:~/1brc-data-gen
	${NODE_SCP} spark/solve_*.py ubuntu@${NODE_IP}:~/

# Pulls a results file back from the node's home directory.
fetch-results:
	${NODE_SCP} ubuntu@${NODE_IP}:~/results.txt ./results.txt
