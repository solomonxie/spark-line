# The core resource graph.
# 3 independent resources build in parallel, and the instance waits on all
# three:
#
#   aws_security_group.airflow_hello_sg   (no deps — SSH 22, webserver 8080)
#   aws_key_pair.deployer                 (no deps — reads var.public_key_path)
#   data.aws_ami.ubuntu_2604               (no deps — queried from AWS API)
#           │
#           ▼
#   aws_instance.airflow_hello_node
#     ├─ ami                    = data.aws_ami.ubuntu_2604.id
#     ├─ key_name               = aws_key_pair.deployer.key_name
#     └─ vpc_security_group_ids = [aws_security_group.airflow_hello_sg.id]
#
# Self-termination: aws_instance.airflow_hello_node is auto-terminated ~2h
# after creation by an EventBridge Scheduler rule — see auto_terminate.tf.

# --- Security Group for Airflow ---
resource "aws_security_group" "airflow_hello_sg" {
  name        = "airflow-hello-sg"
  description = "Allow inbound traffic for the Airflow webserver and SSH"

  ingress {
    description = "SSH Access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Airflow webserver UI"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "airflow-security-group"
  }
}

# --- Key Pair ---
resource "aws_key_pair" "deployer" {
  key_name   = var.ssh_key_name
  public_key = file(var.public_key_path)
}

# --- AMI Lookup ---

# Ubuntu 26.04 LTS (x86_64)
data "aws_ami" "ubuntu_2604" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-*-26.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# --- EC2 Instance ---
# See auto_terminate.tf: this instance self-terminates ~2h after creation.

# Airflow node: Ubuntu 26.04 (t3.medium, 2 vCPUs, 4GB RAM, 20GB EBS)
# why t3.medium, not t3.small? `airflow standalone` runs the webserver,
# scheduler, and triggerer as one process group — 2GB (t3.small) is tight
# for that plus the DAG parsing overhead; 4GB gives it headroom.
resource "aws_instance" "airflow_hello_node" {
  ami                    = data.aws_ami.ubuntu_2604.id
  instance_type          = "t3.medium"
  key_name               = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.airflow_hello_sg.id]

  # Ubuntu 24.04+ defaults /tmp to tmpfs; keep it on disk like classic Ubuntu.
  user_data_replace_on_change = true
  user_data                   = <<-EOF
    #cloud-config
    runcmd:
      - systemctl mask --now tmp.mount
  EOF

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    Name        = "airflow-ubuntu-node"
    Role        = "airflow-standalone"
    Environment = "sandbox"
  }
}
