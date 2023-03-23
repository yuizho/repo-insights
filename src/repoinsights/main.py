import click
from repoinsights.pr import fetch_pull_requests, PullRequest
from repoinsights.releases import Release, fetch_releases
from datetime import datetime, timedelta
from io import StringIO
import csv

ONE_MONTH_BEFORE = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")


def to_csv(headers, rows, delimiter):
    delimiter = delimiter.replace("\\t", "\t").replace("\\n", "\n")
    with StringIO() as string_io:
        writer = csv.writer(string_io, delimiter=delimiter)
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
    "--first-created-date",
    "-f",
    default=ONE_MONTH_BEFORE,
    show_default=True,
    help="first created date to filter PRs (format: yyyy-mm-dd)",
)
@click.option("--base", "-b", default=None, help="a base branch to filter PR")
@click.option("--label", "-l", help="a label name to filter PR")
@click.option("--delimiter", "-d", default=",", show_default=True, help="a delimiter character to separate fields of a result")
def pr(repository_name, personal_token, first_created_date, base, label, delimiter):
    """
    This command allows you to get activity data of a GitHub Pull Reuqst.
    Time taken to merge field of a result is calculated by (merged datetime - created datetime of the PR).
    A result is output in CSV format.

    Usage: repo-insights pr "yuizho/repo-insights" "<your personal token of GitHub>"
    """
    records = fetch_pull_requests(
        repository_name,
        personal_token,
        first_created_date,
        base
    )

    filtered_records = records if label is None else [
        r for r in records if label in r.labels]

    print(
        to_csv(
            PullRequest.get_fields_name(),
            [r.get_fields()
             for r in sorted(filtered_records, key=lambda r: r.created_at)],
            delimiter
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
@click.option("--delimiter", "-d", default=",", show_default=True, help="a delimiter character to separate fields of a result")
def releases(repository_name, personal_token, first_date, delimiter):
    """
    This command allows you to get a releases data of a specified GitHub repository.
    A result is output in CSV format.

    Usage: repo-insights releases "yuizho/repo-insights" "<your personal token of GitHub>"
    """
    releases = fetch_releases(
        repository_name,
        personal_token,
        first_date
    )

    print(
        to_csv(
            Release.get_fields_name(),
            [r.get_fields() for r in sorted(releases, key=lambda r: r.published_at)],
            delimiter
        )
    )


def main():
    cli()


if __name__ == "__main__":
    main()
