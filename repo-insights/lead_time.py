from github_api import DATETIME_FORMAT
from github_api import Client
from gql import gql
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


def get_next_cursor(json):
    edges = json["repository"]["pullRequests"]["edges"]
    return edges[0]["cursor"] if edges else None


def fetch_lead_time_record(repo_name, token, from_date, base):
    # TODO: ソートして取ってこないと冪等性がなくなってしまう気がする。
    query = gql(
        """
        query ($per_page: Int!, $owner: String!, $name: String!, $base: String!, $cursor: String) {
            repository(owner: $owner, name: $name) {
                pullRequests(last: $per_page, states: MERGED, baseRefName: $base, before: $cursor) {
                    totalCount
                    edges {
                        cursor
                        node {
                            mergedAt
                            title
                            url
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
    per_page = 30
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
    def __init__(self, title, url, mergedAt, firstCommitedAt):
        self.title = title
        self.url = url
        self.mergedAt = mergedAt
        self.firstCommitedAt = firstCommitedAt

    def __str__(self):
        return f"{self.title}\t{self.url}\t{self.mergedAt}\t{self.mergedAt - self.firstCommitedAt}"

    @classmethod
    def get_fields_name(cls):
        return ["title", "url", "merged at", "lead time(days)"]
