# repo-insights

[![Actions Status](https://github.com/yuizho/repo-insights/workflows/build/badge.svg)](https://github.com/yuizho/repo-insights/actions)
![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)

A CLI tool to get Release Frequency and Lead Time for Changes by GitHub repository activity.
A result is output in TSV format. you can put the result into some spreadsheet application.

## Getting Started

```sh
pip install git+https://github.com/yuizho/repo-insights
```

## Usage

```
Usage: repo-insights [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  lead-time          This command allows you to get a lead time of a...
  release-frequency  This command allows you to get a release frequency...
```

### lead-time

```
Usage: repo-insights lead-time [OPTIONS] REPOSITORY_NAME PERSONAL_TOKEN

  This command allows you to get a lead time of a specified GitHub repository
  by PR activity. The lead time is calculated by (merged datetime - first
  commit datetime on the PR). A result is output in TSV format. you can put
  the result into some spreadsheet application.

  Usage: repo-insights lead-time "yuizho/repo-insights" "<your personal token
  of GitHub>"

Options:
  -f, --first-merged-date TEXT  first merged date to filter PRs (format: yyyy-
                                mm-dd)  [default: 30 days before]
  -b, --base TEXT               a base branch of PR  [default: master]
  -l, --label TEXT              a label name to filter PR
  --help                        Show this message and exit.
```

### release-frequency

```
Usage: repo-insights release-frequency [OPTIONS] REPOSITORY_NAME
                                       PERSONAL_TOKEN

  This command allows you to get a release frequency of a specified GitHub
  repository by Release activity. A result is output in TSV format. you can
  put the result into some spreadsheet application.

  Usage: repo-insights release-frequency "yuizho/repo-insights" "<your
  personal token of GitHub>"

Options:
  -f, --first-date TEXT  first date to filter Releases  [default: 30 days before]
  --help                 Show this message and exit.
```

## For Developers

### Setup

```
$ pipenv sync --dev
```

### Run repo-insights via pipenv

```
$ pipenv run repo-insights --help
```

### Run tests

```
$ pipenv run test
```

## License

MIT
