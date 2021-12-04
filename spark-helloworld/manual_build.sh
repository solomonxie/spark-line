# Prepare EC2: t3.small, 1 vCPU, 2GB memory, 64bit x86, Ubuntu 26.04


ssh ubuntu@ec2-xxxxxxxx.compute-1.amazonaws.com -i ~/.ssh/mykeypairxxxxx.pem

sudo apt update
sudo apt install -y openjdk-17-jdk-headless wget tar
sudo apt install -y python3-pip python3-venv

pip3 install --quiet --break-system-packages --use-pep517 pyspark
pip3 install --quiet pandas

wget https://archive.apache.org/dist/spark/spark-4.2.0/spark-4.2.0-bin-hadoop3.tgz
tar -xzf spark-4.2.0-bin-hadoop3.tgz
sudo mv spark-4.2.0-bin-hadoop3 /opt/spark
rm spark-4.2.0-bin-hadoop3.tgz
ls -lah /opt/spark

export PYSPARK_PYTHON=python3
export SPARK_HOME=/opt/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
echo $PATH


/opt/spark/sbin/start-master.sh

/opt/spark/sbin/start-worker.sh spark://$(hostname):7077

# Verify
spark-submit --version
telnet 0.0.0.0 8080
