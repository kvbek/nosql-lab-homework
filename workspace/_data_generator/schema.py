from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class Field:
    """
    Defines single column in schema.
    generator: function that returns value
    """
    name: str
    generator: Callable[[], Any]


@dataclass
class Schema:
    """
    Logical schema definition.
    """
    name: str
    fields: list[Field]
