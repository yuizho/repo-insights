# repo-insights

[![Actions Status](https://github.com/yuizho/repo-insights/workflows/build/badge.svg)](https://github.com/yuizho/repo-insights/actions)
![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)

A CLI tool to get metrics, activity data of the GitHub repository.

## Getting Started

```sh
pip install git+https://github.com/yuizho/repo-insights@0.0.5
```

## Usage

```
Usage: repo-insights [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  pr        This command allows you to get activity data of a GitHub Pull...
  releases  This command allows you to get a releases data of a...
```

### Pull Request

```
Usage: repo-insights pr [OPTIONS] REPOSITORY_NAME PERSONAL_TOKEN

  This command allows you to get activity data of a GitHub Pull Reuqst.
  Time taken to merge field of a result is calculated by (merged datetime - created datetime of the PR).
  A result is output in CSV format.

  Usage: repo-insights pr "yuizho/repo-insights" "<your personal token of GitHub>"

Options:
  -f, --first-created-date TEXT  first created date to filter PRs (format: yyyy-
                                mm-dd)  [default: 30 days before]
  -b, --base TEXT               a base branch to filter PR
  -l, --label TEXT              a label name to filter PR
  -d, --delimiter TEXT          a delimiter character to separate fields of a result  [default: ,]
  --help                        Show this message and exit.
```

### releases

```
Usage: repo-insights releases [OPTIONS] REPOSITORY_NAME PERSONAL_TOKEN

  This command allows you to get a releases data of a specified GitHub
  repository. A result is output in CSV format.

  Usage: repo-insights releases "yuizho/repo-insights" "<your personal token of GitHub>"

Options:
  -f, --first-date TEXT  first date to filter Releases  [default: 30 days before]
  -d, --delimiter TEXT   a delimiter character to separate fields of a result  [default: ,]
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
