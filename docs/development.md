# Development

Thank you for contributing to SUISA Sendemeldung! This page covers everything
you need to get a local development environment running and to make changes
with confidence.

## Prerequisites

- **Python 3.12** or later
- [**Poetry**](https://python-poetry.org/) for dependency management

## Set up the development environment

```bash
# Clone the repository
git clone https://github.com/radiorabe/suisa_sendemeldung.git
cd suisa_sendemeldung

# Install all dependencies (including dev extras)
poetry install

# Verify everything works
poetry run pytest
```

## Running the tests

The test suite uses [pytest](https://pytest.org/) with several plugins:

| Plugin | Purpose |
| ------ | ------- |
| `pytest-cov` | Coverage reporting (100 % required) |
| `pytest-mypy` | Static type checking |
| `pytest-ruff` | Lint checks via Ruff |
| `syrupy` | Snapshot tests for CLI help output |
| `freezegun` | Deterministic date/time in tests |
| `requests-mock` | HTTP request mocking |

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Update snapshots after intentional output changes
poetry run pytest --snapshot-update
```

!!! warning "100 % coverage required"
    The CI pipeline enforces `--cov-fail-under=100`. Every new code path
    must have a corresponding test.

## Linting & formatting

```bash
# Lint and auto-fix with Ruff
poetry run ruff check --fix .
poetry run ruff format .

# Type-check with mypy
poetry run mypy suisa_sendemeldung/
```

Both linters also run automatically as part of `pytest`.

## Building the documentation

```bash
# Serve docs locally with live reload
poetry run mkdocs serve

# Build a static copy
poetry run mkdocs build
```

Open <http://127.0.0.1:8000> in your browser while `mkdocs serve` is running.

## Project structure

```
suisa_sendemeldung/
├── acrclient.py          # ACRCloud API wrapper (interval fetch + TZ localisation)
├── settings.py           # typed-settings definitions (all config knobs)
└── suisa_sendemeldung.py # Main application logic and CLI entry point

tests/
├── conftest.py           # Shared fixtures
├── __snapshots__/        # Syrupy snapshot files
└── test_*.py             # Test modules

docs/
├── overrides/            # MkDocs Material theme overrides (home template)
├── css/style.css         # Custom styles
├── gen_ref_pages.py      # Auto-generates API reference pages
└── *.md                  # Hand-written documentation pages
```

## Commit messages

This project follows the
[Conventional Commits](https://www.conventionalcommits.org/) standard.
Commit messages drive automated version bumps and changelog generation via
[go-semantic-release](https://go-semantic-release.xyz/).

| Prefix | Effect |
| ------ | ------ |
| `fix:` | Patch version bump |
| `feat:` | Minor version bump |
| `BREAKING CHANGE:` footer | Major version bump |
| Anything else | No release |

## Release process

Merging to `main` with a qualifying commit message automatically:

1. Creates a GitHub Release via the semantic-release workflow.
2. Publishes the package to [PyPI](https://pypi.org/project/suisa_sendemeldung/).
3. Builds and pushes the container image to
   [GitHub Packages](https://github.com/radiorabe/suisa_sendemeldung/pkgs/container/suisasendemeldung).

Releases are intentionally made only in the second half of each month so they
are available before the 1st-of-month reporting run.
