#!/usr/bin/env python3
"""
Unit tests for utility functions.
"""

import unittest
from typing import Dict, Tuple, Union
from unittest.mock import patch, Mock
from parameterized import parameterized

from utils import (
    access_nested_map,
    get_json,
    memoize,
)


class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for the access_nested_map function from utils module."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self,
        nested_map: Dict,
        path: Tuple[str],
        expected: Union[Dict, int],
    ) -> None:
        """Test that access_nested_map returns correct value for valid path."""
        self.assertEqual(
            access_nested_map(nested_map, path),
            expected
        )

    @parameterized.expand([
        ({}, ("a",), KeyError),
        ({"a": 1}, ("a", "b"), KeyError),
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: Dict,
        path: Tuple[str],
        exception: Exception,
    ) -> None:
        """Test that access_nested_map raises KeyError for invalid path."""
        with self.assertRaises(exception):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """Unit tests for get_json function from utils module."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(
        self,
        test_url: str,
        test_payload: Dict,
    ) -> None:
        """Test that get_json returns correct JSON payload."""
        attrs = {'json.return_value': test_payload}
        with patch("requests.get", return_value=Mock(**attrs)) as req_get:
            self.assertEqual(get_json(test_url), test_payload)
            req_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """Unit tests for the memoize decorator from utils module."""

    def test_memoize(self) -> None:
        """Test that memoize caches the result of a method after first call."""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(
            TestClass,
            'a_method',
            return_value=42
        ) as memo_function:
            test_class = TestClass()
            self.assertEqual(test_class.a_property, 42)
            self.assertEqual(test_class.a_property, 42)
            memo_function.assert_called_once()
