#!/usr/bin/env python3
"""
Write a type-annotated function sum_list
"""
from typing import List


def sum_list(input_list: List[float]) -> float:
    """
    argument and returns their sum as a float
    """
    return float(sum(input_list))
