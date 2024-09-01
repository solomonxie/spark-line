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


# Start Master:
/opt/spark/sbin/start-master.sh

# Start at least 1 Worker:
/opt/spark/sbin/start-worker.sh spark://$(hostname):7077


# Verify
spark-submit --version
nc -vz 0.0.0.0 8080
lsof -i :7077
# >> java    3859 ubuntu 298u  IPv6  18172      0t0  TCP ip-myip.ca-central-1.compute.internal:7077 (LISTEN)
# >> java    3859 ubuntu 302u  IPv6  31649      0t0  TCP ip-xxxx.ca-central-1.compute.internal:7077->ip-xxx.ca-central-1.compute.internal:37508 (ESTABLISHED)
# >> java    4951 ubuntu 304u  IPv6  31648      0t0  TCP ip-xxxx.ca-central-1.compute.internal:37508->ip-xxx.ca-central-1.compute.internal:7077 (ESTABLISHED)

# Open Spark Master WebUI in browser:
open http://public_ip:8080/
# >> see the workers/running/completed applications (should see at least 1 worker)
# >> Worker Id ▾	Address	State	Cores	Memory
# >> worker-20260819173832-myip-46727	myip:46727	ALIVE	2 (0 Used)	1024.0 MiB (0.0 B Used)

# Open PySpark-Shell for quick commands
pyspark --master spark://$(hostname):7077
>>> rdd = spark.sparkContext.parallelize(range(1, 1000000))
>>> rdd
# [out] PythonRDD[1] at RDD at PythonRDD.scala:59
>>> print("Total Count:", rdd.count())
# [out] WARN TaskSchedulerImpl: Initial job has not accepted any resources;
# [out] .... it's running until manually cancle...

# Now go to browser http://public_ip:8080/ will see the running tasks:
# >> Application ID	Name	Cores	Memory per Executor
# >> app-20260819172852-0001(kill)	PySparkShell	0	1024.0 MiB


# Now let's play with data
cd ~
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet -O yellow_taxi_2023_01.parquet

>>> df = spark.read.parquet("file:///home/ubuntu/yellow_taxi_2023_01.parquet")
>>> df.printschema()
# [out] root
# [out]  |-- VendorID: long (nullable = true)
# [out]  |-- ...
# [out]  |-- passenger_count: double (nullable = true)
>>> print("Total Rows:", df.count())
# [out] 3066766
>>> df.show(5)
# [out] ...
>>> df.select("VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance").show(5)
# [out] +--------+--------------------+---------------------+---------------+-------------+
# [out] |VendorID|tpep_pickup_datetime|tpep_dropoff_datetime|passenger_count|trip_distance|
# [out] +--------+--------------------+---------------------+---------------+-------------+
# [out] |       2| 2023-01-01 00:32:10|  2023-01-01 00:40:36|            1.0|         0.97|
# [out] |       2| 2023-01-01 00:55:08|  2023-01-01 01:01:27|            1.0|          1.1|
# [out] |       2| 2023-01-01 00:25:04|  2023-01-01 00:37:49|            1.0|         2.51|
# [out] |       1| 2023-01-01 00:03:48|  2023-01-01 00:13:25|            0.0|          1.9|
# [out] |       2| 2023-01-01 00:10:29|  2023-01-01 00:21:19|            1.0|         1.43|
# [out] +--------+--------------------+---------------------+---------------+-------------+
# [out] only showing top 5 rows

# Okay, now let's get out of shell, and execute Python script instead
>>> exit()


