#!/usr/bin/env python3
"""
Unit tests for the GithubOrgClient class
"""

import unittest
from typing import Dict
from parameterized import parameterized
from unittest.mock import patch, MagicMock, PropertyMock
from client import GithubOrgClient
from requests import HTTPError


class TestGithubOrgClient(unittest.TestCase):
    """Testing GithubOrgClient class"""

    @parameterized.expand([
        ("google", {'login': "google"}),
        ("abc", {'login': "abc"}),
    ])
    @patch("client.get_json")
    def test_org(
        self, org: str, resp: Dict, mocked_function: MagicMock
    ) -> None:
        """
        Test the org method for GithubOrgClient
        """
        mocked_function.return_value = resp
        gith_org_client = GithubOrgClient(org)
        self.assertEqual(gith_org_client.org(), resp)
        mocked_function.assert_called_once_with(
            "https://api.github.com/orgs/{}".format(org)
        )

    @patch("client.GithubOrgClient.org", new_callable=PropertyMock)
    def test_public_repos_url(self, mocked_org: PropertyMock) -> None:
        """Test public repos URL function property"""
        mocked_org.return_value = {
            'repos_url': "https://api.github.com/users/google/repos"
        }
        self.assertEqual(
            GithubOrgClient("google")._public_repos_url,
            "https://api.github.com/users/google/repos"
        )


if __name__ == "__main__":
    unittest.main()
