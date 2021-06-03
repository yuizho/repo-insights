import fire
from lead_time import fetch_lead_time_record, LeadTimeRecord


# TODO: from_dateのデフォルト値は仮 (一ヶ月前とかがデフォルトだといいかもね)
def lead_time(repo_name="", token="", from_date="2021-05-01", base="master"):
    """
    this command will fetch relese frequency of specified repos
    :param repo_name: the target repository name (e.g. yuizho/repo-insights)
    :param token: your github token
    :param base: the base branch of PR
    """
    records = fetch_lead_time_record(repo_name, token, from_date, base)

    # TODO: ラベルのフィルターするならここで実施
    print("\t".join(LeadTimeRecord.get_fields_name()))
    for record in sorted(records, key=lambda r: r.mergedAt):
        print(record)


if __name__ == "__main__":
    fire.Fire()
