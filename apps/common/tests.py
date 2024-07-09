"""Contains helper and test function for the app."""

from typing import Any


def check_keys_exist_strictly(keys: list[str], input_object: dict[str, Any]):
    """
    Checks the given keys are present in the given dict object.
    No extra keys should be present in the object.

    This is a test helper function.
    """

    assert len(keys) == len(input_object)

    for _ in keys:
        assert _ in input_object
