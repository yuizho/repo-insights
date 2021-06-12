from datetime import datetime, timedelta
from repoinsights.github_api import Client
from repoinsights.release_frequency import ReleaseRecord, fetch_release_records
import pytest


class TestReleaseRecord:
    def test_get_fields(self):
        actual = ReleaseRecord("title", "url", datetime.strptime("2021-01-01", "%Y-%m-%d"), timedelta(1)).get_fields()

        assert actual == ["2021-01-01 00:00:00", "title", "url", "1.0"]

    def test_get_fields_name(self):
        actual = ReleaseRecord(
            "title", "url", datetime.strptime("2021-01-01", "%Y-%m-%d"), timedelta(1)
        ).get_fields_name()

        assert actual == ["published at", "title", "url", "release frequency(day)"]


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
                            },
                        },
                        {
                            "cursor": "cursor2",
                            "node": {
                                "isDraft": False,
                                "publishedAt": "2020-02-01T00:00:00Z",
                                "name": "title2",
                                "url": "url2",
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
                            },
                        },
                    ],
                }
            }
        },
    ]

    yield execute_mock


def test_fetch_release_records_just_one_time_request(mocker, github_client_mocks):
    # when
    actual = fetch_release_records("yuizho/my-repo", "my-token", "2020-01-01", 3)

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
    assert actual[0].published_at == datetime.strptime("2020-01-30T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].frequency == timedelta(0)
    assert actual[1].title == "title2"
    assert actual[1].url == "url2"
    assert actual[1].published_at == datetime.strptime("2020-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].frequency == timedelta(2)


def test_fetch_release_records_multiple_time_request(mocker, github_client_mocks):
    # when
    actual = fetch_release_records("yuizho/my-repo", "my-token", "2020-01-01", 2)

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
    assert actual[0].published_at == datetime.strptime("2020-01-30T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].frequency == timedelta(0)
    assert actual[1].title == "title2"
    assert actual[1].url == "url2"
    assert actual[1].published_at == datetime.strptime("2020-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].frequency == timedelta(2)
    assert actual[2].title == "title3"
    assert actual[2].url == "url3"
    assert actual[2].published_at == datetime.strptime("2020-02-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[2].frequency == timedelta(1)
