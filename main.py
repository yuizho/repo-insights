import fire
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime


def lead_time(repo_name="", token="", base="master"):
    """
    this command will fetch relese frequency of specified repos
    :param repo_name: the target repository name (e.g. yuizho/repo-insights)
    :param token: your github token
    :param base: the base branch of PR
    """
    client = Client(
        transport=RequestsHTTPTransport(
            url="https://api.github.com/graphql",
            use_json=True,
            headers={
                "Content-type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            retries=3,
        )
    )

    owner, name = repo_name.split("/")
    variables = {"owner": owner, "name": name, "base": base}
    query = gql(
        """
        query ($owner: String!, $name: String!, $base: String!) {
            repository(owner: $owner, name: $name) {
                pullRequests(last: 30, states: MERGED, baseRefName: $base) {
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
    resp = client.execute(
        query,
        variable_values=variables,
    )

    format = "%Y-%m-%dT%H:%M:%SZ"

    print("title\turl\tlead time(days)")
    for pr in resp["repository"]["pullRequests"]["edges"]:
        title = pr["node"]["title"]
        url = pr["node"]["url"]
        mergedAt = datetime.strptime(pr["node"]["mergedAt"], format)
        firstCommitedAt = datetime.strptime(
            pr["node"]["commits"]["nodes"][0]["commit"]["committedDate"], format
        )

        print(f"{title}\t{url}\t{mergedAt - firstCommitedAt}")


if __name__ == "__main__":
    fire.Fire()
