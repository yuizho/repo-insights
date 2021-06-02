import fire
from github_api import Client, DATETIME_FORMAT
from gql import gql
from datetime import datetime


def lead_time(repo_name="", token="", base="master"):
    """
    this command will fetch relese frequency of specified repos
    :param repo_name: the target repository name (e.g. yuizho/repo-insights)
    :param token: your github token
    :param base: the base branch of PR
    """
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
    owner, name = repo_name.split("/")

    resp = Client(token).execute(
        query,
        {"owner": owner, "name": name, "base": base},
    )

    print("title\turl\tlead time(days)")
    for pr in resp["repository"]["pullRequests"]["edges"]:
        title = pr["node"]["title"]
        url = pr["node"]["url"]
        mergedAt = datetime.strptime(pr["node"]["mergedAt"], DATETIME_FORMAT)
        firstCommitedAt = datetime.strptime(
            pr["node"]["commits"]["nodes"][0]["commit"]["committedDate"],
            DATETIME_FORMAT,
        )

        print(f"{title}\t{url}\t{mergedAt - firstCommitedAt}")


if __name__ == "__main__":
    fire.Fire()
