"""
Step 2: dependencies between assets.

Dagster infers the DAG from function *signatures*, not from an explicit
`>>` operator (contrast with ../hello-airflow's hello_airflow_02): an
asset that takes another asset's name as a parameter depends on it, and
receives its materialized value automatically.

Run:
    python3 dagster_02_asset_dependencies.py
"""
from dagster import Definitions, asset, materialize


@asset
def raw_numbers() -> list[int]:
    return [1, 2, 3, 4, 5]


@asset
def doubled(raw_numbers: list[int]) -> list[int]:
    return [n * 2 for n in raw_numbers]


@asset
def total(doubled: list[int]) -> int:
    value = sum(doubled)
    print(f"total: {value}")
    return value


defs = Definitions(assets=[raw_numbers, doubled, total])


if __name__ == "__main__":
    result = materialize([raw_numbers, doubled, total])
    assert result.success
