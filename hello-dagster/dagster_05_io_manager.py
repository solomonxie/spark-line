"""
Step 5: a custom IO manager — controlling *how* asset outputs are stored.

The default IO manager pickles outputs to a temp dir; this one writes each
asset's output as a plain JSON file instead, keyed by asset name. Assets
never call this directly — Dagster calls `handle_output`/`load_input` for
them, so swapping storage (JSON here, S3/a database in a real project)
never touches the asset functions themselves.

Run:
    python3 dagster_05_io_manager.py
"""
import json
import os
import tempfile

from dagster import ConfigurableIOManager, Definitions, InputContext, OutputContext, asset, materialize

OUT_DIR = os.path.join(tempfile.gettempdir(), "dagster_05_io_manager")


class JSONIOManager(ConfigurableIOManager):
    base_dir: str

    def _path(self, context) -> str:
        return os.path.join(self.base_dir, f"{context.asset_key.path[-1]}.json")

    def handle_output(self, context: OutputContext, obj) -> None:
        os.makedirs(self.base_dir, exist_ok=True)
        path = self._path(context)
        with open(path, "w") as f:
            json.dump(obj, f)
        context.log.info(f"wrote {path}")

    def load_input(self, context: InputContext):
        with open(self._path(context)) as f:
            return json.load(f)


@asset
def numbers() -> list[int]:
    return [1, 2, 3]


@asset
def numbers_squared(numbers: list[int]) -> list[int]:
    return [n * n for n in numbers]


# Same reasoning as step 4: the IO manager has to be bound here, not just
# passed to materialize() below, for `dagster dev -f <this file>` to work.
defs = Definitions(assets=[numbers, numbers_squared], resources={"io_manager": JSONIOManager(base_dir=OUT_DIR)})


if __name__ == "__main__":
    result = materialize(
        [numbers, numbers_squared],
        resources={"io_manager": JSONIOManager(base_dir=OUT_DIR)},
    )
    assert result.success

    with open(os.path.join(OUT_DIR, "numbers_squared.json")) as f:
        print(f"on disk: {f.read()}")
