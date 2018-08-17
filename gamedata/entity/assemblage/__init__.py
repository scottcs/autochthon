from typing import Any

from game.types import ComponentSchema


def schema(component_type: Any, *args: Any, **kwargs: Any) -> ComponentSchema:
    """Define a component schema."""
    return ComponentSchema(component_type, args, kwargs)
