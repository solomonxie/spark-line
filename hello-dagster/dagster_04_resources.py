"""
Step 4: resources — injectable, swappable dependencies.

A resource models something external an asset needs (an API client, a
database connection, ...) without hardcoding it into the asset's body.
Swap `GreetingService` for a fake in tests, or reconfigure `greeting` per
environment, without touching `greet` at all.

Run:
    python3 dagster_04_resources.py
"""
from dagster import ConfigurableResource, Definitions, asset, materialize


class GreetingService(ConfigurableResource):
    greeting: str = "hello"

    def greet(self, name: str) -> str:
        return f"{self.greeting}, {name}!"


@asset
def greet(greeting_service: GreetingService) -> str:
    message = greeting_service.greet("Dagster")
    print(message)
    return message


# The resource has to be bound in a module-level Definitions, not just
# passed to materialize() below — `dagster dev -f <this file>` loads this
# object directly and needs to know how to satisfy `greet`'s dependency.
defs = Definitions(assets=[greet], resources={"greeting_service": GreetingService(greeting="hi")})


if __name__ == "__main__":
    result = materialize(
        [greet],
        resources={"greeting_service": GreetingService(greeting="hi")},
    )
    assert result.success
