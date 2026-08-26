"""
Step 6: partitioned assets — materializing a slice at a time.

A partitioned asset represents many logical slices of the same dataset
(one per region, one per day, ...) under one definition. Materializing
picks which slice to run; the asset body reads which one via
`context.partition_key`.

Run:
    python3 dagster_06_partitions.py
"""
from dagster import AssetExecutionContext, Definitions, StaticPartitionsDefinition, asset, materialize

regions = StaticPartitionsDefinition(["us", "eu", "apac"])


@asset(partitions_def=regions)
def region_signups(context: AssetExecutionContext) -> int:
    region = context.partition_key
    counts = {"us": 120, "eu": 80, "apac": 45}
    value = counts[region]
    print(f"{region}: {value} signups")
    return value


defs = Definitions(assets=[region_signups])


if __name__ == "__main__":
    result = materialize([region_signups], partition_key="eu")
    assert result.success
