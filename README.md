# suisa_sendemeldung

ACRCloud client that fetches data on our playout history and formats them in a CSV file format containing the data (like Track, Title and ISRC) requested by SUISA. Also takes care of sending the report to SUISA via email for hands-off operations.

## Installation

You can build a Docker image using the included [Dockerfile](Dockerfile):

```bash
git clone https://github.com/radiorabe/suisa_sendemeldung
cd suisa_sendemeldung
podman build -t suisa_sendemeldung .
```

Then you can run it by passing in command line switches:

```bash
podman run --rm suisa_sendemeldung --bearer-token abcdefghijklmnopqrstuvwxyzabcdef --stream_id a-bcdefgh --stdout
```

Or by setting environment variables:

```bash
podman run --rm --env BEARER_TOKEN=abcdefghijklmnopqrstuvwxyzabcdef --env STREAM_ID=a-bcdefgh --env STDOUT=True suisa_sendemeldung
```

A prebuilt image is available from the GitHub Package Registry:

```bash
docker pull ghcr.io/radiorabe/suisasendemeldung:master
```

## Usage

This is the output of `suisa_sendemeldung -h`.
```
usage: suisa_sendemeldung [-h] --bearer-token BEARER_TOKEN --project-id
                          PROJECT_ID --stream-id STREAM_ID
                          [--station-name STATION_NAME]
                          [--station-name-short STATION_NAME_SHORT] [--file]
                          [--filetype {xlsx,csv}] [--email]
                          [--email-from EMAIL_FROM] [--email-to EMAIL_TO]
                          [--email-cc EMAIL_CC] [--email-bcc EMAIL_BCC]
                          [--email-server EMAIL_SERVER]
                          [--email-login EMAIL_LOGIN]
                          [--email-pass EMAIL_PASS]
                          [--email-subject EMAIL_SUBJECT]
                          [--email-text EMAIL_TEXT]
                          [--email-footer EMAIL_FOOTER]
                          [--responsible-email RESPONSIBLE_EMAIL]
                          [--start-date START_DATE] [--end-date END_DATE]
                          [--last-month] --timezone TIMEZONE [--locale LOCALE]
                          [--filename FILENAME] [--stdout]

ACRCloud client for SUISA reporting @ RaBe.

options:
  -h, --help            show this help message and exit
  --bearer-token BEARER_TOKEN
                        the bearer token for ACRCloud (required) [env var:
                        BEARER_TOKEN]
  --project-id PROJECT_ID
                        the id of the project at ACRCloud (required) [env var:
                        PROJECT_ID]
  --stream-id STREAM_ID
                        the id of the stream at ACRCloud (required) [env var:
                        STREAM_ID]
  --station-name STATION_NAME
                        Station name, used in Output and Emails [env var:
                        STATION_NAME]
  --station-name-short STATION_NAME_SHORT
                        Shortname for station as used in Filenames (locally
                        and in attachment) [env var: STATION_NAME_SHORT]
  --file                create file [env var: FILE]
  --filetype {xlsx,csv}
                        filetype to attach to email or write to file [env var:
                        FILETYPE]
  --email               send an email [env var: EMAIL]
  --email-from EMAIL_FROM
                        the sender of the email [env var: EMAIL_FROM]
  --email-to EMAIL_TO   the recipients of the email [env var: EMAIL_TO]
  --email-cc EMAIL_CC   the cc recipients of the email [env var: EMAIL_CC]
  --email-bcc EMAIL_BCC
                        the bcc recipients of the email [env var: EMAIL_BCC]
  --email-server EMAIL_SERVER
                        the smtp server to send the mail with [env var:
                        EMAIL_SERVER]
  --email-login EMAIL_LOGIN
                        the username to logon to the smtp server (default:
                        email_from) [env var: EMAIL_LOGIN]
  --email-pass EMAIL_PASS
                        the password for the smtp server [env var: EMAIL_PASS]
  --email-subject EMAIL_SUBJECT
                        The subject of the email, placeholders are
                        $station_name, $year and $month [env var:
                        EMAIL_SUBJECT]
  --email-text EMAIL_TEXT
                        A template for the Email text, placeholders are
                        $station_name, $month, $year, $previous_year,
                        $responsible_email, and $email_footer. [env var:
                        EMAIL_TEXT]
  --email-footer EMAIL_FOOTER
                        Footer for the Email [env var: EMAIL_FOOTER]
  --responsible-email RESPONSIBLE_EMAIL
                        Used to hint whom to contact in the emails text. [env
                        var: RESPONSIBLE_EMAIL]
  --start-date START_DATE
                        the start date of the interval in format YYYY-MM-DD
                        (default: 30 days before end_date) [env var:
                        START_DATE]
  --end-date END_DATE   the end date of the interval in format YYYY-MM-DD
                        (default: today) [env var: END_DATE]
  --last-month          download data of whole last month [env var:
                        LAST_MONTH]
  --timezone TIMEZONE   set the timezone for localization [env var: TIMEZONE]
  --locale LOCALE       set locale for date and time formatting [env var:
                        LOCALE]
  --filename FILENAME   file to write to (default:
                        <station_name_short>_<year>_<month>.csv when reporting
                        last month, <station_name_short>_<start_date>.csv
                        else) [env var: FILENAME]
  --stdout              also print to stdout [env var: STDOUT]

Args that start with '--' (eg. --bearer-token) can also be set in a config
file (/etc/suisa_sendemeldung.conf or /home/hairmare/suisa_sendemeldung.conf
or suisa_sendemeldung.conf). Config file syntax allows: key=value, flag=true,
stuff=[a,b,c] (for details, see syntax at https://goo.gl/R74nmi). If an arg is
specified in more than one place, then commandline values override environment
variables which override config file values which override defaults.
```

## Configuration

You can configure this script either with a configuration file (default is `suisa_sendemeldung.conf`), environment variables or command line arguments as shown above.

Command line arguments override environment variables which themselves override settings in the configuration file.

### Configuration file

The configuration files will be evaluated in the following order (last takes precedence over first):

  1. `/etc/suisa_sendemeldung.conf`
  2. `$HOME/suisa_sendemeldung.conf`
  3. `./suisa_sendemeldung.conf`

For details on how to set configuration values, have a look at [suisa_sendemeldung.conf](etc/suisa_sendemeldung.conf).

### Environment variables

Environment variables can also be passed as options. The relevant variables are listed in the [Usage](#Usage) part of this document. For example run the script as follows:

```bash
BEARER_TOKEN=abcdefghijklmnopqrstuvwxyzabcdef STREAM_ID=a-bcdefgh STDOUT=True ./suisa_sendemeldung.py
```

### Command line switches

As documented in [Usage](#Usage), you can also pass in options on the command line as arguments. Simply run the script as follows:

```bash
./suisa_sendemeldung.py --bearer-token=abcdefghijklmnopqrstuvwxyzabcdef --stream_id=a-bcdefgh --stdout
```

## Release Management

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
