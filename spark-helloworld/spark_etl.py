from pyspark.sql import SparkSession
from pyspark.sql.functions import col, round, unix_timestamp, count, avg, max, dense_rank
from pyspark.sql.window import Window


# Initialize SparkSession
spark = SparkSession.builder \
    .appName("NYC_Taxi_ETL_Job") \
    .getOrCreate()

input_path = "yellow_taxi_2023_01.parquet"
output_path = "output_top_trips/"

print("\n--- 1. Reading Parquet File ---")
df = spark.read.parquet(input_path)
print(f"Total input records: {df.count()}")

print("\n--- 2. Cleaning Data & Deriving Columns ---")
df_cleaned = df.filter(
    (col("passenger_count") > 0) &
    (col("trip_distance") > 0) &
    (col("fare_amount") > 0)
).withColumn(
    "trip_duration_min",
    round((unix_timestamp("tpep_dropoff_datetime") - unix_timestamp("tpep_pickup_datetime")) / 60, 2)
)

print("\n--- 3. Aggregating Vendor Summary ---")
vendor_summary = df_cleaned.groupBy("VendorID").agg(
    count("*").alias("total_trips"),
    round(avg("trip_distance"), 2).alias("avg_distance_miles"),
    round(avg("fare_amount"), 2).alias("avg_fare_usd"),
    max("trip_distance").alias("max_distance_miles")
)
vendor_summary.show()

print("\n--- 4. Running Window Aggregation ---")
windowSpec = Window.partitionBy("VendorID").orderBy(col("trip_distance").desc())
top_trips = df_cleaned.withColumn("rank", dense_rank().over(windowSpec)) \
    .filter(col("rank") <= 3) \
    .select("VendorID", "rank", "trip_distance", "fare_amount", "trip_duration_min")
top_trips.show()

print(f"\n--- 5. Writing Partitioned Parquet Output to {output_path} ---")
top_trips.write \
    .mode("overwrite") \
    .partitionBy("VendorID") \
    .parquet(output_path)

print("--- Job Completed Successfully ---")
spark.stop()
