# 📻 suisa_sendemeldung

ACRCloud client that fetches data on our playout history and formats them in a
CSV/XLSX file containing the data (like Track, Title and ISRC) requested by
SUISA. Also takes care of sending the report to SUISA via email for hands-off
operations.

## 🚀 Usage

We provide the SUISA Sendemeldung script as a container image or as a Python
package.

These usage instructions show how to install the script and how to configure it.
There are different ways to run it at a schedule. We recommend using
[systemd-timers](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html);
an example is provided in the `etc/` directory.

To see all available options, check out the `--help` output:

```bash
# Using Podman
podman run --rm -ti ghcr.io/radiorabe/suisasendemeldung:latest suisa_sendemeldung --help

# Using Docker
docker run --rm -ti ghcr.io/radiorabe/suisasendemeldung:latest suisa_sendemeldung --help
```

While we recommend running the script in its container, you can also install
the script in any Python environment using [pip](https://pip.pypa.io/).

We recommend using a dedicated [venv](https://docs.python.org/3/library/venv.html):

```bash
python -mvenv .venv
. .venv/bin/activate

pip install suisa_sendemeldung

# Show all available options
suisa_sendemeldung --help
```

### ⚙️ Configuration

You can configure this script with a configuration file (default is
`suisa_sendemeldung.toml`), environment variables, or command line arguments.

Command line arguments override environment variables which themselves override
settings in the configuration file.

#### 📄 Configuration file

The configuration files will be evaluated in the following order (last takes
precedence over first):

  1. `/etc/suisa_sendemeldung.toml`
  2. `./suisa_sendemeldung.toml`

For details on how to set configuration values, have a look at
[suisa_sendemeldung.toml](etc/suisa_sendemeldung.toml).

#### 🌍 Environment variables

Environment variables can also be passed as options. The relevant variables are
listed in the output of `suisa_sendemeldung --help`.

For example, run the script as follows:

```bash
podman run --rm -ti \
  -e SENDEMELDUNG_ACR_BEARER_TOKEN=abcdefghijklmnopqrstuvwxyzabcdef \
  -e SENDEMELDUNG_ACR_STREAM_ID=a-bcdefgh \
  -e SENDEMELDUNG_OUTPUT=stdout \
  ghcr.io/radiorabe/suisasendemeldung:latest suisa_sendemeldung
```

#### 💻 Command line switches

As documented in [Usage](#usage), you can also pass options directly on the
command line:

```bash
podman run --rm -ti ghcr.io/radiorabe/suisasendemeldung:latest \
  suisa_sendemeldung \
  --acr-bearer-token=abcdefghijklmnopqrstuvwxyzabcdef \
  --acr-stream-id=a-bcdefgh \
  --output=stdout
```

## 🤝 Support

We support users where reasonably possible on a best-efforts basis.

The following versions of SUISA Sendemeldung are actively supported:

| Version | Supported | Supported GST | Python Version | Description |
| ------- | --------- | ------------- | ---------------| ----------- |
| 0.x | (✅) | GST 2020 | | Developed during the GST lifetime, internal use at RaBe |
| 1.x | ✅ | GST 2026 | >=3.12 | Cleanup and first release with features for external use |

> Old versions are supported on a case-by-case basis if we need to regenerate historical reports.

## ⬆️ Upgrading

### Upgrade from 0.x to 1.0

* The config file was renamed from `suisa_sendemeldung.conf` to `suisa_sendemeldung.toml`
* The config file format has been changed from `ini` style to TOML.
* The command line arguments have been reworked to match the new config file format — check `suisa_sendemeldung --help` for the new flags.
* The "last 30 days from today" mode has been dropped; use `--by-date` with `--date-start` and `--date-end` instead.

## 🛠️ Development

Snapshot testing is used to test the help output. Update snapshots after
intentional output changes like so:

```bash
poetry run pytest -- --snapshot-update
```

## 🏷️ Release Management

At RaBe we run the script on the 1st and 14th of each month. Matching this, we
only release new versions of the script in the second half of each month.

The CI/CD setup uses semantic commit messages following the [conventional commits standard](https://www.conventionalcommits.org/en/v1.0.0/).
There is a GitHub Action in [.github/workflows/semantic-release.yaml](./.github/workflows/semantic-release.yaml)
that uses [go-semantic-commit](https://go-semantic-release.xyz/) to create new
releases.

The commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The commit contains the following structural elements, to communicate intent to
the consumers of your library:

1. **fix:** a commit of the type `fix` patches a bug and gets released with a PATCH version bump
1. **feat:** a commit of the type `feat` adds a feature and gets released as a MINOR version bump
1. **BREAKING CHANGE:** a commit that has a footer `BREAKING CHANGE:` gets released as a MAJOR version bump
1. Types other than `fix:` and `feat:` are allowed and don't trigger a release

If a commit does not contain a conventional commit style message you can fix
it during the squash and merge operation on the PR.

Once a commit has landed on the `main` branch a release will be created and
automatically published to [PyPI](https://pypi.org/) using the GitHub Action in
[.github/workflows/release.yaml](./.github/workflows/release.yaml) which uses
[twine](https://twine.readthedocs.io/) to publish the package. The
`release.yaml` action also takes care of pushing a [container](https://opencontainers.org/)
image to [GitHub Packages](https://github.com/features/packages).
