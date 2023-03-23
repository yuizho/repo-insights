from repoinsights.github_api import DATETIME_FORMAT
from repoinsights.github_api import Client
from gql import gql
from datetime import datetime, timedelta


def create_pr_metrics_records(json):
    result = []
    for pr in json["repository"]["pullRequests"]["edges"]:
        title = pr["node"]["title"]
        base_branch = pr["node"]["baseRefName"]
        author = pr["node"]["author"]["login"]
        url = pr["node"]["url"]
        labels = [nodes["name"] for nodes in pr["node"]["labels"]["nodes"]]
        created_at = datetime.strptime(pr["node"]["createdAt"], DATETIME_FORMAT)
        merged_at = datetime.strptime(pr["node"]["mergedAt"], DATETIME_FORMAT)
        first_committed_at = datetime.strptime(
            pr["node"]["commits"]["nodes"][0]["commit"]["committedDate"],
            DATETIME_FORMAT,
        )
        total_comments_count = pr["node"]["totalCommentsCount"]
        changed_files = pr["node"]["changedFiles"]
        code_additions = pr["node"]["additions"]
        code_deletions = pr["node"]["deletions"]
        repository_name = pr["node"]["repository"]["nameWithOwner"]
        result.append(
            PrMetricsRecord(
                title,
                base_branch,
                author,
                url,
                labels,
                total_comments_count,
                changed_files,
                code_additions,
                code_deletions,
                created_at,
                merged_at,
                first_committed_at,
                repository_name
            )
        )
    return result


def get_next_cursor(json):
    edges = json["repository"]["pullRequests"]["edges"]
    return edges[0]["cursor"] if edges else None


def fetch_pr_metrics_records(repo_name, token, from_date, base, per_page=50):
    query = gql(
        """
        query ($per_page: Int!, $owner: String!, $name: String!, $base: String, $cursor: String) {
            repository(owner: $owner, name: $name) {
                pullRequests(
                    orderBy: {field: CREATED_AT, direction: ASC},
                    last: $per_page,
                    states: MERGED,
                    baseRefName: $base,
                    before: $cursor
                ) {
                    edges {
                        cursor
                        node {
                            createdAt
                            mergedAt
                            baseRefName
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
                            repository {
                                nameWithOwner
                            }
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
            if record.created_at >= datetime.strptime(from_date, "%Y-%m-%d")
        ]
        records += records_this_time
        if len(records_this_time) < per_page:
            break

        cursor = get_next_cursor(resp)

    return records


def hoge(p: str) -> int:
    return int(p)


def fuga():
    v: str = hoge("1")
    v.split(",")


class PrMetricsRecord:
    def __init__(
        self,
        title,
        base_branch,
        author,
        url,
        labels,
        total_comments_count,
        changed_files,
        code_additions,
        code_deletions,
        created_at,
        merged_at,
        first_committed_at,
        repository_name
    ):
        self.title = title
        self.base_branch = base_branch
        self.author = author
        self.url = url
        self.labels = labels
        self.total_comments_count = total_comments_count
        self.changed_files = changed_files
        self.code_additions = code_additions
        self.code_deletions = code_deletions
        self.created_at = created_at
        self.merged_at = merged_at
        self.first_committed_at = first_committed_at
        self.repository_name = repository_name

    def get_fields(self):
        time_taken_to_merge = self.merged_at - self.created_at
        return [
            str(self.created_at),
            str(self.merged_at),
            self.title,
            self.base_branch,
            self.author,
            self.url,
            ",".join(self.labels),
            self.total_comments_count,
            self.changed_files,
            self.code_additions,
            self.code_deletions,
            str(round(time_taken_to_merge / timedelta(days=1), 2)),
            self.repository_name,
        ]

    @classmethod
    def get_fields_name(cls):
        return [
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
