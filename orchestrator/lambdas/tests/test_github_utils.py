import copy
import json
import unittest
from collections import namedtuple
from unittest.mock import patch

from heimdall_repos import github_utils
from heimdall_repos.repo_layer_env import GITHUB_RATE_ABUSE_FLAG

TEST_ABUSE_RESPONSE = {
    "documentation_url": "https://developer.github.com/v3/#abuse-rate-limits",
    "message": "You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.",
}

TEST_RATE_LIMIT_RESPONSE = {
    "documentation_url": "https://docs.github.com/en/free-pro-team@latest/rest/overview/"
    "resources-in-the-rest-api#secondary-rate-limits",
    "message": "You have exceeded a secondary rate limit. Please wait a few minutes before you try again.",
}

TEST_EMPTY_NODE = {
    "name": "analytics-kit-typescript",
    "defaultBranchRef": None,
    "diskUsage": 0,
    "isPrivate": True,
    "refs": {"nodes": [], "pageInfo": {"endCursor": None, "hasNextPage": False}},
}

TEST_SERVICE = "github"
TEST_ORG = "wm-test"
TEST_URL = "www.example.com"
TEST_KEY = "test_key"
TEST_REPO = "athena"
TEST_CURSOR = "4"
TEST_SERVICE_DICT = {"url": TEST_URL, "branch_url": None}
TEST_PLUGINS = ["eslint"]

TEST_EXTERNAL_ORGS = [f"github/{TEST_ORG}"]

TEST_BATCH_ID = "4886eea8-ebca-4bcf-bf22-063ca255067c"

Response = namedtuple("Response", ["text", "status_code"])


class TestGithubUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.process_github_repos = github_utils.ProcessGithubRepos(
            queue=None,
            service=TEST_SERVICE,
            org=TEST_ORG,
            service_dict=TEST_SERVICE_DICT,
            api_key=TEST_KEY,
            cursor=TEST_CURSOR,
            default_branch_only=False,
            plugins=TEST_PLUGINS,
            external_orgs=TEST_EXTERNAL_ORGS,
            batch_id=TEST_BATCH_ID,
        )

    def test_analyze_error_response_none(self):
        result = self.process_github_repos._analyze_error_response(None)

        self.assertIsNone(result)

    def test_analyze_error_response_string(self):
        response = Response("I am an error response.", 400)
        result = self.process_github_repos._analyze_error_response(response)

        self.assertEqual(response.text, result)

    def test_analyze_error_response_dict(self):
        response = Response('{"message": "error!"}', 400)
        expected_result = json.loads(response.text)
        result = self.process_github_repos._analyze_error_response(response)

        self.assertEqual(expected_result, result)

    def test_analyze_error_response_rate_abuse_dict(self):
        response = Response(json.dumps(TEST_ABUSE_RESPONSE), 403)
        result = self.process_github_repos._analyze_error_response(response)

        self.assertEqual(GITHUB_RATE_ABUSE_FLAG, result)

    def test_analyze_error_response_rate_limit_dict(self):
        response = Response(json.dumps(TEST_RATE_LIMIT_RESPONSE), 403)
        result = self.process_github_repos._analyze_error_response(response)

        self.assertEqual(GITHUB_RATE_ABUSE_FLAG, result)

    @patch.object(github_utils, "queue_service_and_org")
    @patch.object(github_utils.ProcessGithubRepos, "_query_github_api")
    def test_query_gitlab_rate_abuse(self, query_mock, queue_mock):
        self.assertEqual(self.process_github_repos._query_github_api, query_mock)
        query_mock.return_value = GITHUB_RATE_ABUSE_FLAG
        self.assertEqual(github_utils.queue_service_and_org, queue_mock)

        self.process_github_repos.query_github()

        self.assertTrue(queue_mock.called)

    def test_process_nodes_repo_no_branches(self):
        expected_response = []

        response = self.process_github_repos._process_nodes([TEST_EMPTY_NODE])

        self.assertEqual(expected_response, response)

    def test_validate_repo_no_branches(self):
        test_repo = copy.deepcopy(TEST_EMPTY_NODE)
        test_repo["diskUsage"] = 1000
        expected_response = False

        response = self.process_github_repos._is_repo_valid(test_repo)

        self.assertEqual(expected_response, response)

    def test_validate_repo_success(self):
        test_repo = copy.deepcopy(TEST_EMPTY_NODE)
        test_repo["refs"]["nodes"] = [{"name": "master"}]
        test_repo["diskUsage"] = 1000
        expected_response = True

        response = self.process_github_repos._is_repo_valid(test_repo)

        self.assertEqual(expected_response, response)
