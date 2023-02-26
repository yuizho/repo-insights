import click
from repoinsights.lead_time import fetch_lead_time_records, LeadTimeRecord
from repoinsights.release_frequency import ReleaseRecord, fetch_release_records
from datetime import datetime, timedelta
from io import StringIO
import csv

ONE_MONTH_BEFORE = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")


def to_csv(headers, rows):
    with StringIO() as string_io:
        writer = csv.writer(string_io)
        writer.writerow(headers)
        writer.writerows(rows)
        return string_io.getvalue()


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
    help="first merged date to filter PRs (format: yyyy-mm-dd)",
)
@click.option("--base", "-b", default="master", show_default=True, help="a base branch of PR")
@click.option("--label", "-l", help="a label name to filter PR")
def lead_time(repository_name, personal_token, first_merged_date, base, label):
    """
    This command allows you to get a lead time of a specified GitHub repository by PR activity.
    The lead time is calculated by (merged datetime - first commit datetime on the PR).
    A result is output in CSV format.

    Usage: repo-insights lead-time "yuizho/repo-insights" "<your personal token of GitHub>"
    """
    records = fetch_lead_time_records(
        repository_name,
        personal_token,
        first_merged_date,
        base
    )

    filtered_records = records if label is None else [
        r for r in records if label in r.labels]

    print(
        to_csv(
            LeadTimeRecord.get_fields_name(),
            [r.get_fields()
             for r in sorted(filtered_records, key=lambda r: r.merged_at)]
        )
    )


@cli.command()
@click.argument("repository_name")
@click.argument("personal_token")
@click.option(
    "--first-date",
    "-f",
    default=ONE_MONTH_BEFORE,
    show_default=True,
    help="first date to filter Releases",
)
def release_frequency(repository_name, personal_token, first_date):
    """
    This command allows you to get a release frequency of a specified GitHub repository by Release activity.
    A result is output in CSV format.

    Usage: repo-insights release-frequency "yuizho/repo-insights" "<your personal token of GitHub>"
    """
    records = fetch_release_records(
        repository_name,
        personal_token,
        first_date
    )

    print(
        to_csv(
            ReleaseRecord.get_fields_name(),
            [r.get_fields() for r in sorted(records, key=lambda r: r.published_at)]
        )
    )


def main():
    cli()


if __name__ == "__main__":
    main()
