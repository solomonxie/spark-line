# Prepare EC2: t2.small, 1 vCPU, 2GB memory, 64bit x86, Ubuntu 26.04


ssh ubuntu@ec2-xxxxxxxx.compute-1.amazonaws.com -i ~/.ssh/mykeypairxxxxx.pem

sudo apt update && sudo apt upgrade -y
sudo apt install -y openjdk-11-jdk-headless wget tar
sudo apt install python3-pip python3-venv
pip3 install --quiet pyspark pandas

wget -q https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
tar -xzf spark-3.5.0-bin-hadoop3.tgz
sudo mv spark-3.5.0-bin-hadoop3 /opt/spark
rm spark-3.5.0-bin-hadoop3.tgz
chown -R ubuntu:ubuntu /opt/spark

export SPARK_HOME=/opt/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
export PYSPARK_PYTHON=python3


/opt/spark/sbin/start-master.sh

/opt/spark/sbin/start-worker.sh spark://$(hostname):7077

# Verify
spark-submit --version
telnet 0.0.0.0 8080
