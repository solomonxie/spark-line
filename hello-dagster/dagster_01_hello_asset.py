"""
Step 1: the smallest software-defined asset.

`materialize()` runs a set of assets in-process — no dagster-webserver, no
daemon, no other infra required. That's what makes every file in this
study path runnable on its own with a plain `python3`.

Run:
    python3 dagster_01_hello_asset.py
"""
from dagster import Definitions, asset, materialize


@asset
def hello() -> str:
    value = "hello from Dagster"
    print(value)
    return value


# `dagster dev -f <this file>` looks for this — a real deployment needs a
# module-level Definitions object, not just the `if __name__` block below.
defs = Definitions(assets=[hello])


if __name__ == "__main__":
    result = materialize([hello])
    assert result.success
