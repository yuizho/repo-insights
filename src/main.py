import click
from lead_time import fetch_lead_time_records, LeadTimeRecord
from datetime import datetime, timedelta

ONE_MONTH_BEFORE = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("repository_name")
@click.argument("personal_token")
@click.option(
    "--first-merged-date",
    "-f",
    default=ONE_MONTH_BEFORE,
    show_default=True,
    help="first merged date to filter PR (format: yyyy-mm-dd)",
)
@click.option("--base", "-b", default="master", show_default=True, help="a base branch of PR")
@click.option("--label", "-l", help="a label name to filter PR")
def lead_time(repository_name, personal_token, first_merged_date, base, label):
    """
    This command allows you to get a lead time of a specified GitHub repository by PR activity.
    The lead time is calculated by (merged datetime - first commit datetime on the PR).
    A result is output in TSV format. you can put the result into some spreadsheet application.

    Usage: src lead-time "yuizho/src" "<your personal token of GitHub>"
    """
    records = fetch_lead_time_records(repository_name, personal_token, first_merged_date, base)

    filtered_records = records if label is None else [r for r in records if label in r.labels]
    print("\t".join(LeadTimeRecord.get_fields_name()))
    for record in sorted(filtered_records, key=lambda r: r.merged_at):
        print("\t".join(record.get_fields()))


def main():
    cli()


if __name__ == "__main__":
    main()
