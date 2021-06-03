import click
from lead_time import fetch_lead_time_record, LeadTimeRecord
from datetime import datetime, timedelta

ONE_MONTH_BEFORE = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("repository_name")
@click.argument("token")
@click.option(
    "--first-merged-date",
    "-f",
    default=ONE_MONTH_BEFORE,
    show_default=True,
    help="first merged date to filter PR data (format: yyyy-mm-dd)",
)
@click.option(
    "--base", "-b", default="master", show_default=True, help="the base branch of PR"
)
def lead_time(repository_name, token, first_merged_date, base):
    """
    This command allows you to calculate lead time of specified GitHub repository by PR activity.

    Usage: repo-insights lead-time "yuizho/repo-insights" "<your personal token of GitHub>"
    """
    records = fetch_lead_time_record(repository_name, token, first_merged_date, base)

    # TODO: ラベルのフィルターするならここで実施
    print("\t".join(LeadTimeRecord.get_fields_name()))
    for record in sorted(records, key=lambda r: r.mergedAt):
        print(record)


def main():
    cli()


if __name__ == "__main__":
    main()
