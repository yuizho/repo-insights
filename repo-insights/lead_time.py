from github_api import DATETIME_FORMAT
from github_api import Client
from gql import gql
from datetime import datetime, timedelta
from yaspin import yaspin


def create_to_load_time_records(json):
    result = []
    for pr in json["repository"]["pullRequests"]["edges"]:
        title = pr["node"]["title"]
        url = pr["node"]["url"]
        labels = [l["name"] for l in pr["node"]["labels"]["nodes"]]
        mergedAt = datetime.strptime(pr["node"]["mergedAt"], DATETIME_FORMAT)
        firstCommitedAt = datetime.strptime(
            pr["node"]["commits"]["nodes"][0]["commit"]["committedDate"],
            DATETIME_FORMAT,
        )
        result.append(
            LeadTimeRecord(
                title,
                url,
                labels,
                mergedAt,
                firstCommitedAt))
    return result


def get_next_cursor(json):
    edges = json["repository"]["pullRequests"]["edges"]
    return edges[0]["cursor"] if edges else None


@yaspin(text="Fetching PR data...")
def fetch_lead_time_record(repo_name, token, from_date, base):
    query = gql(
        """
        query ($per_page: Int!, $owner: String!, $name: String!, $base: String!, $cursor: String) {
            repository(owner: $owner, name: $name) {
                pullRequests(orderBy: {field: CREATED_AT, direction: ASC}, last: $per_page, states: MERGED, baseRefName: $base, before: $cursor) {
                    edges {
                        cursor
                        node {
                            mergedAt
                            title
                            url
                            labels(first: 100) {
                                nodes {
                                    name
                                }
                            }
                            commits(first: 1) {
                                nodes {
                                    commit {
                                        committedDate
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
    )
    owner, name = repo_name.split("/")
    per_page = 100
    cursor = None
    records = []

    while True:
        variables = {
            "per_page": per_page,
            "owner": owner,
            "name": name,
            "base": base,
            "cursor": cursor,
        }

        resp = Client(token).execute(query, variables)
        records_this_time = [
            record
            for record in create_to_load_time_records(resp)
            if record.mergedAt > datetime.strptime(from_date, "%Y-%m-%d")
        ]
        records += records_this_time
        if len(records_this_time) < per_page:
            break

        cursor = get_next_cursor(resp)

    return records


class LeadTimeRecord:
    def __init__(self, title, url, labels, mergedAt, firstCommitedAt):
        self.title = title
        self.url = url
        self.labels = labels
        self.mergedAt = mergedAt
        self.firstCommitedAt = firstCommitedAt

    def get_fields(self):
        lead_time = self.mergedAt - self.firstCommitedAt
        return [
            str(self.mergedAt),
            self.title,
            self.url,
            ', '.join(self.labels),
            str(round(lead_time / timedelta(days=1), 2))
        ]

    @classmethod
    def get_fields_name(cls):
        return ["merged at", "title", "url", "labels", "lead time(day)"]
