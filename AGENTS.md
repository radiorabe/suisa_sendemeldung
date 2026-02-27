# AGENTS.md for `suisa_sendemeldung`

> This document is intended for automated, agentic helpers and human maintainers who
> want to understand how to work with the repository in the **agentic age**.

## 📁 Repository overview

```
Dockerfile
LICENSE
mkdocs.yml
pyproject.toml
README.md
ruff.toml
.
├── docs/          # documentation generator helpers
├── etc/           # configuration samples and systemd units
└── suisa_sendemeldung/  # Python package
    ├── __init__.py
    ├── acrclient.py      # wrapper around ACRCloud SDK
    ├── settings.py      # typed-settings definitions
    └── suisa_sendemeldung.py  # application logic & CLI

tests/                # pytest‑based unit and snapshot tests
```

The code is a command-line utility (exposed via `poetry` script) that
retrieves playout metadata from ACRCloud, transforms it into a CSV/XLSX
compatible with SUISA's reporting format and optionally emails the report.


## 🔧 Build chain & CI

- **Local build** is driven by `python3.12 -m build .` (run inside the
  `Dockerfile`'s `build` stage) and results in a wheel; the container is then
  constructed from a minimal python base image.

- **Dockerfile** uses our internal `radiorabe` base images (`s2i-python` for
  build, `python-minimal` for runtime) and installs the freshly-built wheel.
  It sets `CMD` to `suisa_sendemeldung` and uses `nobody` as user.

- **Continuous Integration** is GitHub Actions based; two workflows are
  referenced from the shared `radiorabe/actions` repository:
  - `.github/workflows/semantic-release.yaml` – triggers on pushes to `main`
    and `release/*`; runs semantic release logic, bumping versions based on
    conventional commit messages.
  - `.github/workflows/release.yaml` – runs on any `pull_request`, on `push`
    to `main` and tags, and on `release` events of type `created`. It
    builds/publishes the container image and uploads the package to PyPI
    using internal reusable workflows (release-container and python-poetry).
    Agents with pipeline access should wait for these workflow results before
    proceeding.

- **Release process** is described in `README.md`; maintainers only need to
  ensure commit messages follow the conventional commit standard and push to
  `main`. An agent could automate bump verification and changelog extraction.


## 🧩 Code analysis

The application pieces are:

1. **Settings (`settings.py`)** – a hierarchy of `@ts.settings` classes that
   define all configuration, with support for TOML files, environment
   variables and command-line options.  Enums are used for constrained values.

2. **ACR client (`acrclient.py`)** – subclass of `acrclient.Client` adding
   timezone localisation and interval fetching. Errors handled implicitly by
   upstream client.

3. **Core logic (`suisa_sendemeldung.py`)** – contains helper functions for
   argument validation, date parsing, file name generation, duplicate removal,
   CSV/XLSX formatting, ISRC normalization, email creation/sending and the
   `main()` entrypoint that orchestrates everything.  The CLI is provided by
   `click` and `typed_settings.cli_click`.

Key characteristics:

- Heavy use of standard library (`csv`, `email`, `pathlib`, `smtplib`) and
  third‑party libs (`openpyxl`, `pytz`, `babel`, `tqdm`, `cridlib`).

- The code is type‑annotated, linted with `ruff` and statically checked
  via `pytest-mypy` integrated into the test run.

- There is logic to handle quirks in the ACRCloud response, e.g. inconsistent
  field names, custom files vs music, malformed ISRCs, timezone offsets etc.


## ✅ Tests & quality

- **Unit tests** use `pytest` with fixtures (see `conftest.py`) and
  `freezegun` for deterministic dates.

- **Snapshot testing** (via `syrupy`) ensures help text and generated CSV/
  XLSX remain stable; update with `--snapshot-update` when intentionally
  changing behaviour.

- External dependencies are mocked (`requests_mock` for HTTP, `unittest.mock`
  for SMTP, `cridlib.get`), enabling fast, offline runs.

- The `pytest` configuration in `pyproject.toml` is aligned with the Poetry
  dependency constraints and runs all static analysis plugins; coverage
  target is **100%**.
## 🧠 Skills & knowledge required

Maintainers (and intelligent agents) should be comfortable with:

- **Python 3.12** – typing, timezone handling, `dataclasses`/`attrs`.
- **Poetry** for dependency management and publishing.
- **GitHub Actions** & conventional commits for CI/CD and releases.
- **Docker** – understanding multi‑stage builds and using container images.
- **pytest** with mocking, snapshot testing, and plugins (`pytest-cov`,
  `pytest-mypy`, `pytest-ruff`).
- **Libraries used**:
  - `openpyxl` for XLSX manipulation.
  - `acrclient` (and the ACRCloud API semantics).
  - `typed-settings` for config management.
  - `click` for CLI and `babel`, `pytz` for localisation.
  - `cridlib` and formats like ISRC.
- Basic SMTP/email formatting and security (TLS, login).
- Handling of timezones and date arithmetic (relativedelta).
- Familiarity with SUISA reporting requirements and CSV layout (optional but
  helpful).

Agents should be provisioned with network access to run against the ACRCloud
API when integration tests are added, but current tests are offline.


## 🤖 Agentic tasks & guidelines

The following actions are good candidates for autonomous agents:

1. **Run the test suite** and verify 100 % coverage; update snapshots when
   expected outputs change.  Always execute `poetry run pytest` (or `poetry shell`
   + `pytest`) rather than attempting to install packages system-wide; this
   avoids environment conflicts and "externally managed" errors.  If
   `pytest-mypy` reports missing library stubs, install the appropriate
   `types-...` packages via `poetry add --dev` or `pip` inside the environment.
2. **Lint and type‑check** with `ruff`, `mypy` and the pytest plugins; propose
   fixes for violations.
3. **Dependency maintenance**: test upgrades and raise PRs or apply fixes.
   An agent can monitor the GitHub Advisory DB for security issues.
4. **Merge request review**: if the agent has access to pull requests, it can
   aid with reviewing them, checking for correctness and style.
5. **Documentation**: regenerate docs via `mkdocs` or `gen_ref_pages.py`,
   ensure `README.md` consistency. Agents may update `AGENTS.md` itself.
6. **Configuration validation**: parse sample `etc/suisa_sendemeldung.toml`,
   ensure options correspond to `settings.py`.
7. **Environment setup**: create reproducible dev container/venv, ensure
   pre-commit hooks work (pre‑commit config via poetry dev deps).
8. **Automated health checks**: run the CLI with a mock ACRCloud server and
   validate output format remains valid for SUISA.

Agents should respect the existing conventional commit rules when pushing
changes.


## 🚀 Getting started (for humans or agents)

```sh
# preferred: use Poetry to manage the environment
# if poetry is not already available you may need to install it first
# inside the environment: `pip install poetry` or use your platform's package
# manager.  See the later "Agent environment" section for details.
poetry install       # creates and populates a virtualenv automatically

# after installation you can execute commands inside it using
poetry run <command>
# e.g.:
poetry run ruff .          # linting
poetry run pytest          # run all tests (including mypy/ruff plugins)

# if you need interactive access, spawn a shell
poetry shell

# if you prefer explicit control (useful for automated agents),
# the virtualenv path is shown by `poetry env info --path` and may
# be activated manually. Avoid installing packages system-wide.

# build wheel
poetry build
# build container (requires podman/docker)
podman build -t suisa_sendemeldung .
```

> **Note:** snapshots are stored under `tests/__snapshots__`.


## 🗂️ Agent environment

Agents should run inside an environment that has:

- Python 3.12 with all `poetry` dev dependencies installed (use `poetry install`).
- Prefer the **`poetry run`** command when executing tests, linters or scripts
  rather than manually creating or activating venvs; the lockfile ensures
  reproducible installs.
- Avoid system‑wide `pip install` to prevent the "externally managed"
  environment errors seen when running the test suite manually.
- Network access to GitHub and PyPI.
- Access to GitHub Actions runner or local `act` for workflow simulation.
- Ability to invoke Docker/Podman.

Credential management (GitHub token, PyPI token) is performed via the
`secrets` mechanism in GitHub Actions; agents should not hardcode them.


---

This file may be updated over time as new responsibilities arise or the
project evolves. See `README.md` for user-facing instructions and refer back
here for agentic assistance guidelines.
