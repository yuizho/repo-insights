from datetime import datetime
from repoinsights.pr import PullRequest, create_pull_requests, fetch_pull_requests
from repoinsights.github_api import Client
import pytest


class TestPullRequest:
    def test_get_fields(self):
        actual = PullRequest(
            "title",
            "main",
            "user",
            "url",
            ["bug", "improvement"],
            3,
            1,
            11,
            10,
            datetime.strptime("2020-12-31", "%Y-%m-%d"),
            datetime.strptime("2021-01-02", "%Y-%m-%d"),
            datetime.strptime("2021-01-01", "%Y-%m-%d"),
            "yuizho/hoge",
        ).get_fields()

        assert actual == [
            "2020-12-31 00:00:00",
            "2021-01-02 00:00:00",
            "title",
            "main",
            "user",
            "url",
            "bug,improvement",
            3,
            1,
            11,
            10,
            "2.0",
            "yuizho/hoge",
        ]

    def test_get_fields_name(self):
        actual = PullRequest(
            "title",
            "main",
            "user",
            "url",
            ["bug", "improvement"],
            3,
            1,
            11,
            10,
            datetime.strptime("2020-12-31", "%Y-%m-%d"),
            datetime.strptime("2021-01-02", "%Y-%m-%d"),
            datetime.strptime("2021-01-01", "%Y-%m-%d"),
            "yuizho/hoge",
        ).get_fields_name()

        assert actual == [
            "created at",
            "merged at",
            "title",
            "base branch",
            "author",
            "url",
            "labels",
            "total comments count",
            "changed files",
            "code additions",
            "code deletions",
            "time taken to merge(day)",
            "repository name",
        ]


@pytest.fixture
def github_client_mocks(mocker):
    client_mock = mocker.Mock(spec=Client)
    mocker.patch("repoinsights.github_api.Client", return_value=client_mock)
    execute_mock = mocker.patch.object(Client, "execute")
    execute_mock.side_effect = [
        # first records
        {
            "repository": {
                "pullRequests": {
                    "edges": [
                        {
                            "cursor": "cursor1",
                            "node": {
                                "mergedAt": "2020-01-03T00:00:00Z",
                                "createdAt": "2020-01-01T00:00:00Z",
                                "baseRefName": "branch1",
                                "title": "title1",
                                "author": {
                                    "login": "user1"
                                },
                                "url": "url1",
                                "labels": {"nodes": [{"name": "label-1-1"}, {"name": "label-1-2"}]},
                                "commits": {"nodes": [{"commit": {"committedDate": "2020-01-02T00:00:00Z"}}]},
                                "totalCommentsCount": 1,
                                "changedFiles": 11,
                                "additions": 111,
                                "deletions": 1111,
                                "repository": {
                                    "nameWithOwner": "yuizho/hoge1"
                                },
                            },
                        },
                        {
                            "cursor": "cursor2",
                            "node": {
                                "mergedAt": "2020-02-03T00:00:00Z",
                                "createdAt": "2020-02-01T00:00:00Z",
                                "baseRefName": "branch2",
                                "title": "title2",
                                "author": {
                                    "login": "user2"
                                },
                                "url": "url2",
                                "labels": {"nodes": []},
                                "commits": {"nodes": [{"commit": {"committedDate": "2020-02-02T00:00:00Z"}}]},
                                "totalCommentsCount": 2,
                                "changedFiles": 22,
                                "additions": 222,
                                "deletions": 2222,
                                "repository": {
                                    "nameWithOwner": "yuizho/hoge2"
                                },
                            },
                        },
                    ],
                }
            }
        },
        # second records
        {
            "repository": {
                "pullRequests": {
                    "edges": [
                        {
                            "cursor": "cursor3",
                            "node": {
                                "mergedAt": "2020-03-03T00:00:00Z",
                                "createdAt": "2020-03-01T00:00:00Z",
                                "baseRefName": "branch3",
                                "title": "title3",
                                "author": {
                                    "login": "user3"
                                },
                                "url": "url3",
                                "labels": {"nodes": [{"name": "label-3-1"}]},
                                "commits": {"nodes": [{"commit": {"committedDate": "2020-03-02T00:00:00Z"}}]},
                                "totalCommentsCount": 3,
                                "changedFiles": 33,
                                "additions": 333,
                                "deletions": 3333,
                                "repository": {
                                    "nameWithOwner": "yuizho/hoge3"
                                },
                            },
                        },
                    ],
                }
            }
        },
    ]

    yield execute_mock


def test_fetch_pull_requests_just_one_time_request(mocker, github_client_mocks):
    # when
    actual = fetch_pull_requests(
        "yuizho/my-repo", "my-token", "2020-01-01", "master", 3)

    # then
    assert github_client_mocks.call_count == 1
    assert github_client_mocks.call_args_list == [
        mocker.call(
            mocker.ANY,
            {
                "per_page": 3,
                "owner": "yuizho",
                "name": "my-repo",
                "base": "master",
                "cursor": None,
            },
        )
    ]
    assert actual[0].title == "title1"
    assert actual[0].base_branch == "branch1"
    assert actual[0].author == "user1"
    assert actual[0].url == "url1"
    assert actual[0].labels == ["label-1-1", "label-1-2"]
    assert actual[0].total_comments_count == 1
    assert actual[0].changed_files == 11
    assert actual[0].code_additions == 111
    assert actual[0].code_deletions == 1111
    assert actual[0].created_at == datetime.strptime(
        "2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].merged_at == datetime.strptime(
        "2020-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].first_committed_at == datetime.strptime(
        "2020-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].repository_name == "yuizho/hoge1"
    assert actual[1].title == "title2"
    assert actual[1].base_branch == "branch2"
    assert actual[1].author == "user2"
    assert actual[1].url == "url2"
    assert actual[1].labels == []
    assert actual[1].total_comments_count == 2
    assert actual[1].changed_files == 22
    assert actual[1].code_additions == 222
    assert actual[1].code_deletions == 2222
    assert actual[1].created_at == datetime.strptime(
        "2020-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].merged_at == datetime.strptime(
        "2020-02-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].first_committed_at == datetime.strptime(
        "2020-02-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].repository_name == "yuizho/hoge2"


def test_fetch_pull_requests_records_multiple_times_request(mocker, github_client_mocks):
    # when
    actual = fetch_pull_requests(
        "yuizho/my-repo", "my-token", "2020-01-01", "master", 2)

    # then
    assert github_client_mocks.call_count == 2
    assert github_client_mocks.call_args_list == [
        mocker.call(
            mocker.ANY,
            {
                "per_page": 2,
                "owner": "yuizho",
                "name": "my-repo",
                "base": "master",
                "cursor": None,
            },
        ),
        mocker.call(
            mocker.ANY,
            {
                "per_page": 2,
                "owner": "yuizho",
                "name": "my-repo",
                "base": "master",
                "cursor": "cursor1",
            },
        ),
    ]
    assert actual[0].title == "title1"
    assert actual[0].base_branch == "branch1"
    assert actual[0].author == "user1"
    assert actual[0].url == "url1"
    assert actual[0].labels == ["label-1-1", "label-1-2"]
    assert actual[0].total_comments_count == 1
    assert actual[0].changed_files == 11
    assert actual[0].code_additions == 111
    assert actual[0].code_deletions == 1111
    assert actual[0].created_at == datetime.strptime(
        "2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].merged_at == datetime.strptime(
        "2020-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].first_committed_at == datetime.strptime(
        "2020-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].repository_name == "yuizho/hoge1"
    assert actual[1].title == "title2"
    assert actual[1].base_branch == "branch2"
    assert actual[1].author == "user2"
    assert actual[1].url == "url2"
    assert actual[1].labels == []
    assert actual[1].total_comments_count == 2
    assert actual[1].changed_files == 22
    assert actual[1].code_additions == 222
    assert actual[1].code_deletions == 2222
    assert actual[1].created_at == datetime.strptime(
        "2020-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].merged_at == datetime.strptime(
        "2020-02-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].first_committed_at == datetime.strptime(
        "2020-02-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].repository_name == "yuizho/hoge2"
    assert actual[2].title == "title3"
    assert actual[2].base_branch == "branch3"
    assert actual[2].author == "user3"
    assert actual[2].url == "url3"
    assert actual[2].labels == ["label-3-1"]
    assert actual[2].total_comments_count == 3
    assert actual[2].changed_files == 33
    assert actual[2].code_additions == 333
    assert actual[2].code_deletions == 3333
    assert actual[2].created_at == datetime.strptime(
        "2020-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[2].merged_at == datetime.strptime(
        "2020-03-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[2].first_committed_at == datetime.strptime(
        "2020-03-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[2].repository_name == "yuizho/hoge3"


def test_create_pull_requests_records_empty():
    # when
    actual = create_pull_requests(
        {"repository": {"pullRequests": {"edges": []}}})

    # then
    assert actual == []
