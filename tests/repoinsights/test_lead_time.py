from datetime import datetime
from repoinsights.lead_time import LeadTimeRecord, create_lead_time_records, fetch_lead_time_records
from repoinsights.github_api import Client
import pytest


class TestLeadTimeRecord:
    def test_get_fields(self):
        actual = LeadTimeRecord(
            "title",
            "url",
            ["bug", "improvement"],
            datetime.strptime("2021-01-02", "%Y-%m-%d"),
            datetime.strptime("2021-01-01", "%Y-%m-%d"),
        ).get_fields()

        assert actual == ["2021-01-02 00:00:00", "title", "url", "bug, improvement", "1.0"]

    def test_get_fields_name(self):
        actual = LeadTimeRecord(
            "title",
            "url",
            ["bug", "improvement"],
            datetime.strptime("2021-01-02", "%Y-%m-%d"),
            datetime.strptime("2021-01-01", "%Y-%m-%d"),
        ).get_fields_name()

        assert actual == ["merged at", "title", "url", "labels", "lead time(day)"]


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
                                "title": "title1",
                                "url": "url1",
                                "labels": {"nodes": [{"name": "label-1-1"}, {"name": "label-1-2"}]},
                                "commits": {"nodes": [{"commit": {"committedDate": "2020-01-02T00:00:00Z"}}]},
                            },
                        },
                        {
                            "cursor": "cursor2",
                            "node": {
                                "mergedAt": "2020-02-03T00:00:00Z",
                                "createdAt": "2020-02-01T00:00:00Z",
                                "title": "title2",
                                "url": "url2",
                                "labels": {"nodes": []},
                                "commits": {"nodes": [{"commit": {"committedDate": "2020-02-02T00:00:00Z"}}]},
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
                                "title": "title3",
                                "url": "url3",
                                "labels": {"nodes": [{"name": "label-3-1"}]},
                                "commits": {"nodes": [{"commit": {"committedDate": "2020-03-02T00:00:00Z"}}]},
                            },
                        },
                    ],
                }
            }
        },
    ]

    yield execute_mock


def test_fetch_lead_time_records_just_one_time_request(mocker, github_client_mocks):
    # when
    actual = fetch_lead_time_records("yuizho/my-repo", "my-token", "2020-01-01", "master", 3)

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
    assert actual[0].url == "url1"
    assert actual[0].labels == ["label-1-1", "label-1-2"]
    assert actual[0].merged_at == datetime.strptime("2020-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].first_committed_at == datetime.strptime("2020-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].title == "title2"
    assert actual[1].url == "url2"
    assert actual[1].labels == []
    assert actual[1].merged_at == datetime.strptime("2020-02-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].first_committed_at == datetime.strptime("2020-02-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")


def test_fetch_lead_time_records_multiple_times_request(mocker, github_client_mocks):
    # when
    actual = fetch_lead_time_records("yuizho/my-repo", "my-token", "2020-01-01", "master", 2)

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
    assert actual[0].url == "url1"
    assert actual[0].labels == ["label-1-1", "label-1-2"]
    assert actual[0].merged_at == datetime.strptime("2020-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[0].first_committed_at == datetime.strptime("2020-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].title == "title2"
    assert actual[1].url == "url2"
    assert actual[1].labels == []
    assert actual[1].merged_at == datetime.strptime("2020-02-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[1].first_committed_at == datetime.strptime("2020-02-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[2].title == "title3"
    assert actual[2].url == "url3"
    assert actual[2].labels == ["label-3-1"]
    assert actual[2].merged_at == datetime.strptime("2020-03-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    assert actual[2].first_committed_at == datetime.strptime("2020-03-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")


def test_create_lead_time_records_empty():
    # when
    actual = create_lead_time_records({"repository": {"pullRequests": {"edges": []}}})

    # then
    assert actual == []