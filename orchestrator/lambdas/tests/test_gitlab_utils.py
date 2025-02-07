import json
import unittest
from unittest.mock import patch

from heimdall_repos import gitlab_utils

TEST_BRANCH_RESPONSE = [
    {
        "name": "master",
        "commit": {
            "id": "617badcd8d08716b71eace84a47f8dfd19fd8f0e",
            "short_id": "617badcd",
            "created_at": "2020-01-07T15:46:11.000+00:00",
            "parent_ids": None,
            "title": "Fixed Yangaroo Config Section",
            "message": "Fixed Yangaroo Config Section",
            "author_name": "",
            "author_email": "",
            "authored_date": "2020-01-07T15:46:11.000+00:00",
            "committer_name": "",
            "committer_email": "",
            "committed_date": "2020-01-07T15:46:11.000+00:00",
        },
        "merged": False,
        "protected": True,
        "developers_can_push": True,
        "developers_can_merge": False,
        "can_push": True,
        "default": True,
    },
    {
        "name": "production",
        "commit": {
            "id": "8f1b8b2ba0da185612a4bdbce6c5314d77bf3ed8",
            "short_id": "8f1b8b2b",
            "created_at": "2018-06-08T05:24:22.000+00:00",
            "parent_ids": None,
            "title": "Test",
            "message": "Test",
            "author_name": "",
            "author_email": "",
            "authored_date": "2018-06-08T05:24:22.000+00:00",
            "committer_name": "",
            "committer_email": "",
            "committed_date": "2018-06-08T05:24:22.000+00:00",
        },
        "merged": True,
        "protected": False,
        "developers_can_push": False,
        "developers_can_merge": False,
        "can_push": True,
        "default": False,
    },
    {
        "name": "rollback",
        "commit": {
            "id": "af074fbbeadbb6559fa59b8a51267de4b2777267",
            "short_id": "af074fbb",
            "created_at": "2017-08-16T21:16:38.000+00:00",
            "parent_ids": None,
            "title": "Merge remote-tracking branch 'origin/production' into rollback",
            "message": "Merge remote-tracking branch 'origin/production' into rollback",
            "author_name": "",
            "author_email": "",
            "authored_date": "2017-08-16T21:16:38.000+00:00",
            "committer_name": "",
            "committer_email": "",
            "committed_date": "2017-08-16T21:16:38.000+00:00",
        },
        "merged": False,
        "protected": False,
        "developers_can_push": False,
        "developers_can_merge": False,
        "can_push": True,
        "default": False,
    },
]

TEST_NODES = [
    {
        "fullPath": "legacy/entertainment/mts",
        "id": "gid://gitlab/Project/1885",
        "visibility": "private",
        "repository": {"rootRef": "master"},
    }
]

TEST_SERVICE = "gitlab"
TEST_ORG = "wm-test"
TEST_URL = "www.example.com"
TEST_KEY = "test_key"
TEST_REPO = "athena"
TEST_CURSOR = "4"
TEST_SERVICE_DICT = {"url": TEST_URL, "branch_url": None}
TEST_PLUGINS = ["eslint"]

TEST_EXTERNAL_ORGS = [f"gitlab/{TEST_ORG}"]

TEST_BATCH_ID = "4886eea8-ebca-4bcf-bf22-063ca255067c"


class TestGitlabUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.process_gitlab_repos = gitlab_utils.ProcessGitlabRepos(
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

    @patch.object(gitlab_utils.ProcessGitlabRepos, "_get_project_branches")
    def test_process_nodes_one_branch(self, get_project_branches):
        self.assertEqual(self.process_gitlab_repos._get_project_branches, get_project_branches)
        get_project_branches.return_value = json.dumps([TEST_BRANCH_RESPONSE[0]])

        expected_response = [
            {
                "branch": "master",
                "org": TEST_ORG,
                "repo": "entertainment/mts",
                "service": TEST_SERVICE,
                "plugins": TEST_PLUGINS,
            }
        ]

        response = self.process_gitlab_repos._process_nodes(TEST_NODES)

        self.assertEqual(expected_response, response)

    @patch.object(gitlab_utils.ProcessGitlabRepos, "_get_project_branches")
    def test_process_nodes_multiple_branches(self, get_project_branches):
        self.assertEqual(self.process_gitlab_repos._get_project_branches, get_project_branches)
        get_project_branches.return_value = json.dumps(TEST_BRANCH_RESPONSE)
        expected_response = [
            {
                "branch": "master",
                "org": TEST_ORG,
                "repo": "entertainment/mts",
                "service": TEST_SERVICE,
                "plugins": TEST_PLUGINS,
            },
            {
                "branch": "rollback",
                "org": TEST_ORG,
                "repo": "entertainment/mts",
                "service": TEST_SERVICE,
                "plugins": TEST_PLUGINS,
            },
            {
                "branch": "production",
                "org": TEST_ORG,
                "repo": "entertainment/mts",
                "service": TEST_SERVICE,
                "plugins": TEST_PLUGINS,
            },
        ]

        response = self.process_gitlab_repos._process_nodes(TEST_NODES)

        self.assertCountEqual(expected_response, response)

    def test_validate_input_no_url(self):
        gitlab_processor = gitlab_utils.ProcessGitlabRepos(queue=None, service="", service_dict={})

        self.assertFalse(gitlab_processor.validate_input())

    @patch.object(gitlab_utils.ProcessGitlabRepos, "_get_project_branches")
    def test_get_ref_names_no_branch_response(self, get_project_branches):
        self.assertEqual(self.process_gitlab_repos._get_project_branches, get_project_branches)
        get_project_branches.return_value = ""
        expected_response = []

        response = self.process_gitlab_repos._get_ref_names("foo")

        self.assertEqual(expected_response, response)

    @patch.object(gitlab_utils.ProcessGitlabRepos, "_get_project_branches")
    def test_get_ref_names_success(self, get_project_branches):
        self.assertEqual(self.process_gitlab_repos._get_project_branches, get_project_branches)
        get_project_branches.return_value = json.dumps(TEST_BRANCH_RESPONSE)
        expected_response = ["rollback", "master", "production"]

        response = self.process_gitlab_repos._get_ref_names("foo")

        self.assertEqual(sorted(expected_response), sorted(response))

    def test_process_refs_success(self):
        test_resp = [{"name": "bar"}, {"name": "foo"}]
        expected_response = ["bar", "foo"]

        response = self.process_gitlab_repos._process_refs(test_resp)

        self.assertEqual(sorted(expected_response), sorted(response))

    def test_process_refs_no_resp(self):
        test_resp = {}
        expected_response = []

        response = self.process_gitlab_repos._process_refs(test_resp)

        self.assertEqual(expected_response, response)
