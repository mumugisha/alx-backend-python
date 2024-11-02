#!/usr/bin/env python3
"""
Unit tests for GithubOrgClient class.
"""

import unittest
from typing import Dict
from parameterized import parameterized, parameterized_class
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
    def test_org(self, org: str, resp: Dict,
                 mocked_function: MagicMock) -> None:
        """Test the org method"""
        mocked_function.return_value = resp
        github_org_client = GithubOrgClient(org)
        self.assertEqual(github_org_client.org(), resp)
        mocked_function.assert_called_once_with(
            "https://api.github.com/orgs/{}".format(org)
        )

    @patch("client.GithubOrgClient.org", new_callable=PropertyMock)
    def test_public_repos_url(self, mocked_org: PropertyMock) -> None:
        """Test the _public_repos_url property"""
        mocked_org.return_value = {
            'repos_url': "https://api.github.com/users/google/repos"
        }
        self.assertEqual(
            GithubOrgClient("google")._public_repos_url,
            "https://api.github.com/users/google/repos"
        )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: MagicMock) -> None:
        """Testing public_repos method"""
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
        """Test the has_license method"""
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
    """Performs integration tests"""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up class before running tests"""
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
        """Test public repos"""
        self.assertEqual(
            GithubOrgClient("google").public_repos(),
            self.expected_repos
        )

    def test_public_repos_with_license(self) -> None:
        """Test public repos with a specific license"""
        self.assertEqual(
            GithubOrgClient("google").public_repos(license="apache-2.0"),
            self.apache2_repos
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Removes class fixtures after all tests"""
        cls.get_patcher.stop()
