#!/usr/bin/env python3
"""
Parameters and return values with type annotations.
"""
from typing import Any, Mapping, Union, TypeVar

TVar = TypeVar('T')
Respond = Union[Any, TVar]


def safely_get_value(
    dct: Mapping, key: Any, default: Union[TVar, None] = None
) -> Respond:
    """
    Safely get a value from a dictionary.
    If the key is not present, return the default value.
    """
    if key in dct:
        return dct[key]
    else:
        return default
