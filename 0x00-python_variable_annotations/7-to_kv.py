#!/usr/bin/env python3
"""
Write a type-annotated function to_kv that takes a string k
"""
from typing import List, Tuple, Union


def to_kv(k: str, v: Union[int, float]) -> Tuple[str, float]:
    """
    Takes a string k and an int or float v, and returns a tuple
    with k and the square of v as a float.
    """
    return (k, float(v**2))
