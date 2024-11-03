#!/usr/bin/env python3
"""
Unit tests for the GithubOrgClient class, focusing on methods related
to organization information, public repository URLs, public repositories,
and license verification.
"""

import unittest
from typing import Dict
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, MagicMock, PropertyMock, Mock
from client import (
    GithubOrgClient
    )

from requests import HTTPError


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class functionality."""

    @parameterized.expand([
        ("google", {'login': "google"}),
        ("abc", {'login': "abc"}),
    ])
    @patch("client.get_json")
    def test_org(self, org: str, resp: Dict,
                 mocked_function: MagicMock) -> None:
        """
        Test that GithubOrgClient.org() returns the expected value
        based on the mocked API response.
        """
        mocked_function.return_value = resp
        github_org_client = GithubOrgClient(org)
        self.assertEqual(github_org_client.org(), resp)
        mocked_function.assert_called_once_with(
            "https://api.github.com/orgs/{}".format(org)
        )

    @patch("client.GithubOrgClient.org", new_callable=PropertyMock)
    def test_public_repos_url(self, mocked_org: PropertyMock) -> None:
        """
        Test that _public_repos_url property correctly returns the repos URL
        based on the mocked organization response.
        """
        mocked_org.return_value = {
            'repos_url': "https://api.github.com/users/google/repos"
        }
        self.assertEqual(
            GithubOrgClient("google")._public_repos_url,
            "https://api.github.com/users/google/repos"
        )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: MagicMock) -> None:
        """
        Test that public_repos method returns the expected list of
        repository names based on a mocked response.
        """
        test_payload = {
            'repos_url': "https://api.github.com/users/google/repos",
            'repos': [
                {
                    "id": 7697149,
                    "name": "episodes.dart",
                    "full_name": "google/episodes.dart",
                    "private": False,
                    "owner": {"login": "google", "id": 1342004}
                },
                {
                    "id": 9060347,
                    "name": "traceur-compiler",
                    "full_name": "google/traceur-compiler",
                    "private": False,
                    "owner": {"login": "google", "id": 1342004}
                }
            ]
        }
        mock_get_json.return_value = test_payload["repos"]
        with patch("client.GithubOrgClient._public_repos_url",
                   new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = test_payload["repos_url"]
            self.assertEqual(
                GithubOrgClient("google").public_repos(),
                ["episodes.dart", "traceur-compiler"]
            )
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "bsd-3-clause"}}, "bsd-3-clause", True),
        ({"license": {"key": "bsl-1.0"}}, "bsd-3-clause", False),
    ])
    def test_has_license(self, repo: Dict, key: str, expected: bool) -> None:
        """
        Test has_license method to verify if the given repository has
        the specified license.
        """
        github_org_client = GithubOrgClient("google")
        has_license = github_org_client.has_license(repo, key)
        self.assertEqual(has_license, expected)


@parameterized_class([
    {
        'org_payload': {'login': "google"},
        'repos_payload': [
            {"id": 7697149, "name": "episodes.dart"},
            {"id": 9060347, "name": "traceur-compiler"}
        ],
        'expected_repos': ["episodes.dart", "traceur-compiler"],
        'apache2_repos': ["traceur-compiler"]
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test cases for GithubOrgClient class, focusing on the
    public_repos method and license filtering.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up mock responses before tests to simulate Github API responses
        using fixtures.
        """
        route_payload = {
            "https://api.github.com/orgs/google": cls.org_payload,
            "https://api.github.com/orgs/google/repos": cls.repos_payload
        }

        def get_payload(url):
            if url in route_payload:
                return Mock(**{'json.return_value': route_payload[url]})
            return HTTPError

        cls.get_patcher = patch("requests.get", side_effect=get_payload)
        cls.get_patcher.start()

    def test_public_repos(self) -> None:
        """
        Test public_repos method to confirm it returns expected repository
        names based on the fixtures.
        """
        self.assertEqual(
            GithubOrgClient("google").public_repos(),
            self.expected_repos
        )

    def test_public_repos_with_license(self) -> None:
        """
        Test public_repos method with license filtering by apache-2.0 license,
        confirming it returns only repositories with the specified license.
        """
        self.assertEqual(
            GithubOrgClient("google").public_repos(license="apache-2.0"),
            self.apache2_repos
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop all patches started during setUpClass."""
        cls.get_patcher.stop()
