from dataclasses import dataclass
from repoinsights.github_api import DATETIME_FORMAT
from repoinsights.github_api import Client
from gql import gql
from datetime import datetime, timedelta


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
        repository_name = pr["node"]["repository"]["nameWithOwner"]
        result.append(
            Release(
                title,
                url,
                author,
                published_at,
                repository_name
            )
        )
    return result


def get_next_cursor(json):
    edges = json["repository"]["releases"]["edges"]
    return edges[0]["cursor"] if edges else None


def fetch_releases(repo_name, token, from_date, per_page=30):
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

    return releases



class Release:
    def __init__(
            self,
            title,
            url,
            author,
            published_at,
            repository_name
    ):
        self.title = title
        self.url = url
        self.published_at = published_at
        self.author = author
        self.repository_name = repository_name

    def get_fields(self):
        return [
            str(self.published_at),
            self.title,
            self.url,
            self.author,
            self.repository_name
        ]

    @classmethod
    def get_fields_name(cls):
        return [
            "published at",
            "title",
            "url",
            "author",
            "repository name"
        ]
