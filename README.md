# suisa_sendemeldung

ACRCloud client that fetches data on our playout history and formats them in a CSV file format containing the data (like Track, Title and ISRC) requested by SUISA. Also takes care of sending the report to SUISA via email for hands-off operations.

## Usage

We provide the SUISA Sendmeldung script as a container image or as a python package.

These usage instructions show how to install the script and how to configure it.
There are different ways to run it at a schedule. We recommend using
[systemd-timers](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html).

To output the scripts usage information, check out it's `--help` output:

```bash
# Using Podman
podman run --rm -ti ghcr.io/radiorabe/suisasendemeldung:latest suisa_sendemeldung --help

# Using Docker
docker run --rm -ti ghcr.io/radiorabe/suisasendemeldung:latest suisa_sendemeldung --help
```

While we recommend running the script in it's container, you can also install the script
in any python environment using [pip](https://pip.pypa.io/).

We recommend using a dedicated [venv](https://docs.python.org/3/library/venv.html) for
running the script hould you go down this route:

```bash
python -mvenv .venv
. venv/bin/activate

pip install suisa_sendemeldung

# Output usage after installation
suisa_sendemeldung
```
### Configuration

You can configure this script with a configuration file (default is `suisa_sendemeldung.conf`),
environment variables, or command line arguments.

Command line arguments override environment variables which themselves override settings in
the configuration file.

#### Configuration file

The configuration files will be evaluated in the following order (last takes precedence over first):

  1. `/etc/suisa_sendemeldung.conf`
  2. `$HOME/suisa_sendemeldung.conf`
  3. `./suisa_sendemeldung.conf`

For details on how to set configuration values, have a look at [suisa_sendemeldung.conf](etc/suisa_sendemeldung.conf).

#### Environment variables

Environment variables can also be passed as options. The relevant variables are listed in the [Usage](#Usage) part of this document. For example run the script as follows:

```bash
podman run --rm -ti -e BEARER_TOKEN=abcdefghijklmnopqrstuvwxyzabcdef -e STREAM_ID=a-bcdefgh -e STDOUT=True ghcr.io/radiorabe/suisasendemeldung:latest suisa_sendemeldung
```

#### Command line switches

As documented in [Usage](#Usage), you can also pass in options on the command line as arguments. Simply run the script as follows:

```bash
podman run --rm -ti ghcr.io/radiorabe/suisasendemeldung:latest suisa_sendemeldung --bearer-token=abcdefghijklmnopqrstuvwxyzabcdef --stream_id=a-bcdefgh --stdout
```

## Development

Snapshot testing is used to test the help output, you can update the snapshots like so:
```
poetry run pytest -- --snapshot-update
```

## Release Management

At RaBe we run the script on the first and 14th of each month. Matching this we only release new versions of the script in the second half of each month.

The CI/CD setup uses semantic commit messages following the [conventional commits standard](https://www.conventionalcommits.org/en/v1.0.0/).
There is a GitHub Action in [.github/workflows/semantic-release.yaml](./.github/workflows/semantic-release.yaml)
that uses [go-semantic-commit](https://go-semantic-release.xyz/) to create new releases.

The commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The commit contains the following structural elements, to communicate intent to the consumers of your library:

1. **fix:** a commit of the type `fix` patches gets released with a PATCH version bump
1. **feat:** a commit of the type `feat` gets released as a MINOR version bump
1. **BREAKING CHANGE:** a commit that has a footer `BREAKING CHANGE:` gets released as a MAJOR version bump
1. types other than `fix:` and `feat:` are allowed and don't trigger a release

If a commit does not contain a conventional commit style message you can fix
it during the squash and merge operation on the PR.

Once a commit has landed on the `main` branch a release will be created and automatically published to [pypi](https://pypi.org/)
using the GitHub Action in [.github/workflows/release.yaml](./.github/workflows/reliease.yaml) which uses [twine](https://twine.readthedocs.io/)
to publish the package to pypi. The `release.yaml` action also takes care of pushing a [container](https://opencontainers.org/)
image to [GitHub Packages](https://github.com/features/packages).
