from datetime import datetime, timedelta
from repoinsights.github_api import Client
from repoinsights.release import Release, fetch_releases
import pytest


class TestReleaseRecord:
    def test_get_fields(self):
        actual = Release(
            "title",
            "url",
            "user",
            datetime.strptime("2021-01-01", "%Y-%m-%d"),
            "yuizho/hoge",
        ).get_fields()

        assert actual == [
            "2021-01-01 00:00:00",
            "title",
            "url",
            "user",
            "yuizho/hoge"
        ]

    def test_get_fields_name(self):
        actual = Release(
            "title",
            "url",
            "user",
            datetime.strptime("2021-01-01", "%Y-%m-%d"),
            "yuizho/hoge"
        ).get_fields_name()

        assert actual == [
            "published at",
            "title",
            "url",
            "author",
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
                "releases": {
                    "edges": [
                        {
                            "cursor": "cursor1",
                            "node": {
                                "isDraft": False,
                                "publishedAt": "2020-01-30T00:00:00Z",
                                "name": "title1",
                                "url": "url1",
                                "author": {
                                    "login": "user1"
                                },
                                "repository": {
                                    "nameWithOwner": "yuizho/hoge1",
                                },
                            },
                        },
                        {
                            "cursor": "cursor2",
                            "node": {
                                "isDraft": False,
                                "publishedAt": "2020-02-01T00:00:00Z",
                                "name": "title2",
                                "url": "url2",
                                "author": {
                                    "login": "user2"
                                },
                                "repository": {
                                    "nameWithOwner": "yuizho/hoge2",
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
                "releases": {
                    "edges": [
                        {
                            "cursor": "cursor3",
                            "node": {
                                "isDraft": False,
                                "publishedAt": "2020-02-02T00:00:00Z",
                                "name": "title3",
                                "url": "url3",
                                "author": {
                                    "login": "user3"
                                },
                                "repository": {
                                    "nameWithOwner": "yuizho/hoge3",
                                },
                            },
                        },
                    ],
                }
            }
        },
    ]

    yield execute_mock


def test_fetch_releases_just_one_time_request(mocker, github_client_mocks):
    # when
    actual = fetch_releases(
        "yuizho/my-repo", "my-token", "2020-01-01", 3)

    # then
    assert github_client_mocks.call_count == 1
    assert github_client_mocks.call_args_list == [
        mocker.call(
            mocker.ANY,
            {
                "per_page": 3,
                "owner": "yuizho",
                "name": "my-repo",
                "cursor": None,
            },
        )
    ]
    assert actual[0].title == "title1"
    assert actual[0].url == "url1"
    assert actual[0].author == "user1"
    assert actual[0].published_at == datetime.strptime(
        "2020-01-30T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].repository_name == "yuizho/hoge1"
    assert actual[1].title == "title2"
    assert actual[1].url == "url2"
    assert actual[1].author == "user2"
    assert actual[1].published_at == datetime.strptime(
        "2020-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].repository_name == "yuizho/hoge2"


def test_fetch_releases_multiple_time_request(mocker, github_client_mocks):
    # when
    actual = fetch_releases(
        "yuizho/my-repo", "my-token", "2020-01-01", 2)

    # then
    assert github_client_mocks.call_count == 2
    assert github_client_mocks.call_args_list == [
        mocker.call(
            mocker.ANY,
            {
                "per_page": 2,
                "owner": "yuizho",
                "name": "my-repo",
                "cursor": None,
            },
        ),
        mocker.call(
            mocker.ANY,
            {
                "per_page": 2,
                "owner": "yuizho",
                "name": "my-repo",
                "cursor": "cursor1",
            },
        ),
    ]
    assert actual[0].title == "title1"
    assert actual[0].url == "url1"
    assert actual[0].author == "user1"
    assert actual[0].published_at == datetime.strptime(
        "2020-01-30T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].repository_name == "yuizho/hoge1"
    assert actual[1].title == "title2"
    assert actual[1].url == "url2"
    assert actual[1].author == "user2"
    assert actual[1].published_at == datetime.strptime(
        "2020-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].repository_name == "yuizho/hoge2"
    assert actual[2].title == "title3"
    assert actual[2].url == "url3"
    assert actual[2].author == "user3"
    assert actual[2].published_at == datetime.strptime(
        "2020-02-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[2].repository_name == "yuizho/hoge3"
