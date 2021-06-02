import fire
from github_api import Client
from lead_time import create_to_load_time_records, LeadTimeRecord
from gql import gql


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

    print("\t".join(LeadTimeRecord.get_fields_name()))
    records = create_to_load_time_records(resp)
    for record in records:
        print(record)


if __name__ == "__main__":
    fire.Fire()
