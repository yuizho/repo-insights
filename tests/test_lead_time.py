from datetime import datetime
from lead_time import LeadTimeRecord


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

    def test_get_fields(self):
        actual = LeadTimeRecord(
            "title",
            "url",
            ["bug", "improvement"],
            datetime.strptime("2021-01-02", "%Y-%m-%d"),
            datetime.strptime("2021-01-01", "%Y-%m-%d"),
        ).get_fields_name()

        assert actual == ["merged at", "title", "url", "labels", "lead time(day)"]
