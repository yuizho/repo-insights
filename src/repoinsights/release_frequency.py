from dataclasses import dataclass
from repoinsights.github_api import DATETIME_FORMAT
from repoinsights.github_api import Client
from gql import gql
from datetime import datetime, timedelta
from yaspin import yaspin


def create_releases(json):
    result = []
    for pr in json["repository"]["releases"]["edges"]:
        if pr["node"]["isDraft"]:
            continue
        title = pr["node"]["name"]
        url = pr["node"]["url"]
        author = pr["node"]["author"]["login"]
        published_at = datetime.strptime(
            pr["node"]["publishedAt"],
            DATETIME_FORMAT
        )
        result.append(
            Release(
                title,
                url,
                author,
                published_at
            )
        )
    return result


def get_next_cursor(json):
    edges = json["repository"]["releases"]["edges"]
    return edges[0]["cursor"] if edges else None


def create_releases_records(releases):
    records = []
    prev_published_at = None
    for release in sorted(releases, key=lambda r: r.published_at):
        frequency = release.published_at - \
            prev_published_at if prev_published_at else timedelta()
        records.append(
            ReleaseRecord(
                release.title,
                release.url,
                release.author,
                release.published_at,
                frequency
            )
        )
        prev_published_at = release.published_at
    return records


@yaspin(text="Fetching Release data...")
def fetch_release_records(repo_name, token, from_date, per_page=30):
    query = gql(
        """
        query ($per_page: Int!, $owner: String!, $name: String!, $cursor: String) {
            repository(owner: $owner, name: $name) {
                releases(orderBy: {field: CREATED_AT, direction: ASC}, last: $per_page, before: $cursor) {
                    totalCount
                    edges {
                        cursor
                        node {
                            isDraft
                            publishedAt
                            name
                            url
                            author {
                                login
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
    releases = []

    while True:
        variables = {
            "per_page": per_page,
            "owner": owner,
            "name": name,
            "cursor": cursor,
        }

        resp = client.execute(query, variables)
        release_this_time = [
            release
            for release in create_releases(resp)
            if release.published_at > datetime.strptime(from_date, "%Y-%m-%d")
        ]
        releases += release_this_time
        if len(release_this_time) < per_page:
            break

        cursor = get_next_cursor(resp)

    return create_releases_records(releases)


@dataclass
class Release:
    title: str
    url: str
    author: str
    published_at: datetime


class ReleaseRecord:
    def __init__(self, title, url, author, published_at, frequency):
        self.title = title
        self.url = url
        self.published_at = published_at
        self.author = author
        self.frequency = frequency

    def get_fields(self):
        return [str(self.published_at), self.title, self.url, self.author, str(round(self.frequency / timedelta(days=1), 2))]

    @classmethod
    def get_fields_name(cls):
        return ["published at", "title", "url", "author", "release frequency(day)"]
