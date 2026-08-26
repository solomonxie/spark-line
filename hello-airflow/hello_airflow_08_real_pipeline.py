"""
Step 8 (capstone): a real extract-transform-load pipeline, TaskFlow style.

Downloads a small, real CSV, aggregates it, and loads the result into a
local SQLite database — three `@task`s, orchestrated the same way as
step 5, using nothing beyond the standard library and Airflow itself.

Run:
    python3 hello_airflow_08_real_pipeline.py
"""
import csv
import io
import sqlite3
import urllib.request
from datetime import datetime

from airflow.decorators import dag, task

DATA_URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
DB_PATH = "/tmp/hello_airflow_08.db"


@dag(dag_id="hello_airflow_08", start_date=datetime(2024, 1, 1), schedule=None, catchup=False)
def real_pipeline():
    @task
    def extract() -> str:
        with urllib.request.urlopen(DATA_URL) as response:
            return response.read().decode()

    @task
    def transform(raw_csv: str) -> dict:
        rows = csv.DictReader(io.StringIO(raw_csv))
        counts: dict[str, int] = {}
        for row in rows:
            species = row["species"]
            counts[species] = counts.get(species, 0) + 1
        return counts

    @task
    def load(species_counts: dict) -> None:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DROP TABLE IF EXISTS species_counts")
        conn.execute("CREATE TABLE species_counts (species TEXT, count INTEGER)")
        conn.executemany("INSERT INTO species_counts VALUES (?, ?)", species_counts.items())
        conn.commit()
        print(f"--- {DB_PATH} ---")
        for row in conn.execute("SELECT * FROM species_counts"):
            print(row)
        conn.close()

    load(transform(extract()))


dag_instance = real_pipeline()

if __name__ == "__main__":
    dag_instance.test()
