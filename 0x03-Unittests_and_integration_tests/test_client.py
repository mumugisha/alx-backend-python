#!/usr/bin/env python3
"""
Unit tests for the GithubOrgClient class, focusing on methods related
to organization information, public repository URLs, public repositories,
and license verification.
"""

import unittest
from typing import Dict
from unittest.mock import MagicMock, Mock, PropertyMock, patch
from parameterized import parameterized, parameterized_class
from requests import HTTPError

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class functionality."""

    @parameterized.expand([
        ("google", {'login': "google"}),
        ("abc", {'login': "abc"}),
    ])
    @patch("client.get_json")
    def test_org(self, org: str, resp: Dict, mocked_fxn: MagicMock) -> None:
        """
        Test that GithubOrgClient.org() returns the expected value
        based on the mocked API response.
        """
        mocked_fxn.return_value = resp
        gh_org_client = GithubOrgClient(org)
        self.assertEqual(gh_org_client.org(), resp)
        mocked_fxn.assert_called_once_with(
            "https://api.github.com/orgs/{}".format(org)
        )

    def test_public_repos_url(self) -> None:
        """
        Test that _public_repos_url property correctly returns the repos URL
        based on the mocked organization response.
        """
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock,
        ) as mock_org:
            mock_org.return_value = {
                'repos_url': "https://api.github.com/users/google/repos",
            }
            self.assertEqual(
                GithubOrgClient("google")._public_repos_url,
                "https://api.github.com/users/google/repos",
            )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: MagicMock) -> None:
        """
        Test that public_repos method returns the expected list of
        repository names based on a mocked response.
        """
        test_payload = [
            {
                "id": 7697149,
                "name": "episodes.dart",
                "private": False,
                "owner": {"login": "google", "id": 1342004},
                "fork": False,
                "url": "https://api.github.com/repos/google/episodes.dart",
                "created_at": "2013-01-19T00:31:37Z",
                "updated_at": "2019-09-23T11:53:58Z",
                "has_issues": True,
                "forks": 22,
                "default_branch": "master",
            },
            {
                "id": 8566972,
                "name": "kratu",
                "private": False,
                "owner": {"login": "google", "id": 1342004},
                "fork": False,
                "url": "https://api.github.com/repos/google/kratu",
                "created_at": "2013-03-04T22:52:33Z",
                "updated_at": "2019-11-15T22:22:16Z",
                "has_issues": True,
                "forks": 22,
                "default_branch": "master",
            },
        ]
        mock_get_json.return_value = test_payload
        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock,
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = "https://api.github.com/orgs/google/repos"
            self.assertEqual(
                GithubOrgClient("google").public_repos(),
                ["episodes.dart", "kratu"],
            )
            mock_get_json.assert_called_once()
            mock_public_repos_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "bsd-3-clause"}}, "bsd-3-clause", True),
        ({"license": {"key": "bsl-1.0"}}, "bsd-3-clause", False),
    ])
    def test_has_license(self, repo: Dict, key: str, expected: bool) -> None:
        """
        Test has_license method to verify if the given repository has
        the specified license.
        """
        gh_org_client = GithubOrgClient("google")
        client_has_license = gh_org_client.has_license(repo, key)
        self.assertEqual(client_has_license, expected)


@parameterized_class([
    {
        'org_payload': TEST_PAYLOAD[0][0],
        'repos_payload': TEST_PAYLOAD[0][1],
        'expected_repos': TEST_PAYLOAD[0][2],
        'apache2_repos': TEST_PAYLOAD[0][3],
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test cases for GithubOrgClient class, focusing on the
    public_repos method and license filtering.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up class fixtures before running tests."""
        route_payload = {
            'https://api.github.com/orgs/google': cls.org_payload,
            'https://api.github.com/orgs/google/repos': cls.repos_payload,
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
            self.expected_repos,
        )

    def test_public_repos_with_license(self) -> None:
        """
        Test public_repos method with license filtering by apache-2.0 license,
        confirming it returns only repositories with the specified license.
        """
        self.assertEqual(
            GithubOrgClient("google").public_repos(license="apache-2.0"),
            self.apache2_repos,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop all patches started during setUpClass."""
        cls.get_patcher.stop()
