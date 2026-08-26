"""
Step 8 (capstone): a real extract-transform-load pipeline, as assets.

Same dataset and shape as
../hello-airflow/hello_airflow_08_real_pipeline.py — downloads a small
real CSV, aggregates it, loads the result into local SQLite — this time
as three dependent assets instead of an Airflow DAG.

Run:
    python3 dagster_08_real_pipeline.py
"""
import csv
import io
import sqlite3
import urllib.request

from dagster import Definitions, asset, materialize

DATA_URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
DB_PATH = "/tmp/hello_dagster_08.db"


@asset
def raw_iris_csv() -> str:
    with urllib.request.urlopen(DATA_URL) as response:
        return response.read().decode()


@asset
def species_counts(raw_iris_csv: str) -> dict:
    rows = csv.DictReader(io.StringIO(raw_iris_csv))
    counts: dict[str, int] = {}
    for row in rows:
        species = row["species"]
        counts[species] = counts.get(species, 0) + 1
    return counts


@asset
def species_counts_table(species_counts: dict) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS species_counts")
    conn.execute("CREATE TABLE species_counts (species TEXT, count INTEGER)")
    conn.executemany("INSERT INTO species_counts VALUES (?, ?)", species_counts.items())
    conn.commit()
    print(f"--- {DB_PATH} ---")
    for row in conn.execute("SELECT * FROM species_counts"):
        print(row)
    conn.close()


defs = Definitions(assets=[raw_iris_csv, species_counts, species_counts_table])


if __name__ == "__main__":
    result = materialize([raw_iris_csv, species_counts, species_counts_table])
    assert result.success
