from github_api import DATETIME_FORMAT
from github_api import Client
from gql import gql
from datetime import datetime
from yaspin import yaspin


def create_release_records(json):
    result = []
    for pr in json["repository"]["releases"]["edges"]:
        if pr["node"]["isDraft"]:
            continue
        title = pr["node"]["name"]
        url = pr["node"]["url"]
        published_at = datetime.strptime(pr["node"]["publishedAt"], DATETIME_FORMAT)
        result.append(ReleaseRecord(title, url, published_at))
    return result


def get_next_cursor(json):
    edges = json["repository"]["releases"]["edges"]
    return edges[0]["cursor"] if edges else None


@yaspin(text="Fetching Release data...")
def fetch_release_records(repo_name, token, from_date, per_page=100):
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
            "cursor": cursor,
        }

        resp = client.execute(query, variables)
        records_this_time = [
            record
            for record in create_release_records(resp)
            if record.published_at > datetime.strptime(from_date, "%Y-%m-%d")
        ]
        records += records_this_time
        if len(records_this_time) < per_page:
            break

        cursor = get_next_cursor(resp)

    return records


class ReleaseRecord:
    def __init__(self, title, url, published_at):
        self.title = title
        self.url = url
        self.published_at = published_at

    def get_fields(self):
        return [str(self.published_at), self.title, self.url]

    @classmethod
    def get_fields_name(cls):
        return ["published at", "title", "url"]
