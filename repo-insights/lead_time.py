from github_api import DATETIME_FORMAT
from datetime import datetime


def create_to_load_time_records(json):
    result = []
    for pr in json["repository"]["pullRequests"]["edges"]:
        title = pr["node"]["title"]
        url = pr["node"]["url"]
        mergedAt = datetime.strptime(pr["node"]["mergedAt"], DATETIME_FORMAT)
        firstCommitedAt = datetime.strptime(
            pr["node"]["commits"]["nodes"][0]["commit"]["committedDate"],
            DATETIME_FORMAT,
        )
        result.append(LeadTimeRecord(title, url, mergedAt, firstCommitedAt))
    return result


class LeadTimeRecord:
    def __init__(self, title, url, mergedAt, firstCommitedAt):
        self.title = title
        self.url = url
        self.mergedAt = mergedAt
        self.firstCommitedAt = firstCommitedAt

    def __str__(self):
        return f"{self.title}\t{self.url}\t{self.mergedAt - self.firstCommitedAt}"

    @classmethod
    def get_fields_name(cls):
        return ["title", "url", "lead time(days)"]
