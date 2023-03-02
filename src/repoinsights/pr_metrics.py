from repoinsights.github_api import DATETIME_FORMAT
from repoinsights.github_api import Client
from gql import gql
from datetime import datetime, timedelta


def create_pr_metrics_records(json):
    result = []
    for pr in json["repository"]["pullRequests"]["edges"]:
        title = pr["node"]["title"]
        author = pr["node"]["author"]["login"]
        url = pr["node"]["url"]
        labels = [nodes["name"] for nodes in pr["node"]["labels"]["nodes"]]
        merged_at = datetime.strptime(pr["node"]["mergedAt"], DATETIME_FORMAT)
        first_committed_at = datetime.strptime(
            pr["node"]["commits"]["nodes"][0]["commit"]["committedDate"],
            DATETIME_FORMAT,
        )
        total_comments_count = pr["node"]["totalCommentsCount"]
        changed_files = pr["node"]["changedFiles"]
        code_additions = pr["node"]["additions"]
        code_deletions = pr["node"]["deletions"]
        result.append(
            PrMetricsRecord(
                title,
                author,
                url,
                labels,
                total_comments_count,
                changed_files,
                code_additions,
                code_deletions,
                merged_at,
                first_committed_at,
            )
        )
    return result


def get_next_cursor(json):
    edges = json["repository"]["pullRequests"]["edges"]
    return edges[0]["cursor"] if edges else None


def fetch_pr_metrics_records(repo_name, token, from_date, base, per_page=30):
    query = gql(
        """
        query ($per_page: Int!, $owner: String!, $name: String!, $base: String, $cursor: String) {
            repository(owner: $owner, name: $name) {
                pullRequests(
                    orderBy: {field: UPDATED_AT, direction: ASC},
                    last: $per_page,
                    states: MERGED,
                    baseRefName: $base,
                    before: $cursor
                ) {
                    edges {
                        cursor
                        node {
                            mergedAt
                            title
                            author {
                                login
                            }
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
                            totalCommentsCount
                            changedFiles
                            additions
                            deletions
                        }
                    }
                }
            }
        }
        """
    )
    client = Client(token)
    owner, name = repo_name.split("/")
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

        resp = client.execute(query, variables)
        records_this_time = [
            record
            for record in create_pr_metrics_records(resp)
            if record.merged_at > datetime.strptime(from_date, "%Y-%m-%d")
        ]
        records += records_this_time
        if len(records_this_time) < per_page:
            break

        cursor = get_next_cursor(resp)

    return records


class PrMetricsRecord:
    def __init__(
        self,
        title,
        author,
        url,
        labels,
        total_comments_count,
        changed_files,
        code_additions,
        code_deletions,
        merged_at,
        first_committed_at
    ):
        self.title = title
        self.author = author
        self.url = url
        self.labels = labels
        self.total_comments_count = total_comments_count
        self.changed_files = changed_files
        self.code_additions = code_additions
        self.code_deletions = code_deletions
        self.merged_at = merged_at
        self.first_committed_at = first_committed_at

    def get_fields(self):
        time_taken_to_merge = self.merged_at - self.first_committed_at
        return [
            str(self.merged_at),
            self.title,
            self.author,
            self.url,
            ",".join(self.labels),
            self.total_comments_count,
            self.changed_files,
            self.code_additions,
            self.code_deletions,
            str(round(time_taken_to_merge / timedelta(days=1), 2)),
        ]

    @classmethod
    def get_fields_name(cls):
        return [
            "merged at",
            "title",
            "author",
            "url",
            "labels",
            "total comments count",
            "changed files",
            "code additions",
            "code deletions",
            "time taken to merge(day)"
        ]
