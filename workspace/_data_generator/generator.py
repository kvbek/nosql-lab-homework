from typing import Iterable
from schema import Schema


def generate_records(schema: Schema, n: int) -> Iterable[dict]:
    """
    Generates records based on schema definition.

    Returns generator (lazy evaluation)
    """

    for _ in range(n):
        record = {}

        for field in schema.fields:
            record[field.name] = field.generator()

        yield record
