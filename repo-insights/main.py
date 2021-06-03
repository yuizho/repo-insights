import fire
from github_api import Client
from lead_time import create_to_load_time_records, get_next_cursor, LeadTimeRecord
from gql import gql
from datetime import datetime


# TODO: from_dateのデフォルト値は仮 (一ヶ月前とかがデフォルトだといいかもね)
def lead_time(repo_name="", token="", from_date="2021-05-01", base="master"):
    """
    this command will fetch relese frequency of specified repos
    :param repo_name: the target repository name (e.g. yuizho/repo-insights)
    :param token: your github token
    :param base: the base branch of PR
    """
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

    # TODO: ラベルのフィルターするならここで実施
    print("\t".join(LeadTimeRecord.get_fields_name()))
    for record in sorted(records, key=lambda r: r.mergedAt):
        print(record)


if __name__ == "__main__":
    fire.Fire()
