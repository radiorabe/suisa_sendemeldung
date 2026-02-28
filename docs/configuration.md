# Configuration

SUISA Sendemeldung can be configured via three layers, evaluated in order from
lowest to highest priority:

1. Configuration files (TOML)
2. Environment variables
3. CLI flags

CLI flags override environment variables, which in turn override the
configuration file. This means you can keep static settings in a file and
supply secrets as environment variables without touching the file.

## Configuration files

The following files are evaluated in order, last value wins:

| Path | Notes |
| ---- | ----- |
| `/etc/suisa_sendemeldung.toml` | System-wide defaults |
| `./suisa_sendemeldung.toml` | Per-directory / per-project overrides |

A full annotated example is available in
[`etc/suisa_sendemeldung.toml`](https://github.com/radiorabe/suisa_sendemeldung/blob/main/etc/suisa_sendemeldung.toml).

## All options

Every option below maps to a TOML key under `[sendemeldung]`, an environment
variable prefixed `SENDEMELDUNG_`, and a CLI flag of the same name.

### ACR settings

These connect the tool to your ACRCloud project.

| Option | Env var | Default | Description |
| ------ | ------- | ------- | ----------- |
| `acr.bearer-token` | `SENDEMELDUNG_ACR_BEARER_TOKEN` | — | ACRCloud API bearer token (**required**) |
| `acr.stream-id` | `SENDEMELDUNG_ACR_STREAM_ID` | — | ACRCloud stream ID (**required**) |
| `acr.project-id` | `SENDEMELDUNG_ACR_PROJECT_ID` | — | ACRCloud project ID (**required**) |
| `acr.url` | `SENDEMELDUNG_ACR_URL` | `https://eu-api-v2.acrcloud.com` | ACRCloud API base URL |

### Date settings

Control the reporting period.

| Option | Env var | Default | Description |
| ------ | ------- | ------- | ----------- |
| `date.start` | `SENDEMELDUNG_DATE_START` | — | Start date (`YYYY-MM-DD`) |
| `date.end` | `SENDEMELDUNG_DATE_END` | — | End date (`YYYY-MM-DD`) |
| `date.last-month` | `SENDEMELDUNG_DATE_LAST_MONTH` | `false` | Fetch the whole previous calendar month |

!!! note "Date modes"
    Either set `date.last-month = true` **or** provide an explicit
    `date.start` / `date.end` pair. The two modes are mutually exclusive.

### Output settings

| Option | Env var | Default | Description |
| ------ | ------- | ------- | ----------- |
| `output` | `SENDEMELDUNG_OUTPUT` | `file` | Output mode: `file`, `email`, or `stdout` |

### File settings

Used when `output = "file"` (or `"email"` as attachment).

| Option | Env var | Default | Description |
| ------ | ------- | ------- | ----------- |
| `file.path` | `SENDEMELDUNG_FILE_PATH` | `suisa_sendemeldung.csv` | Output file path |
| `file.format` | `SENDEMELDUNG_FILE_FORMAT` | `xlsx` | Output format: `xlsx` or `csv` |

### Email settings

Used when `output = "email"`.

| Option | Env var | Default | Description |
| ------ | ------- | ------- | ----------- |
| `email.sender` | `SENDEMELDUNG_EMAIL_SENDER` | — | Sender address |
| `email.to` | `SENDEMELDUNG_EMAIL_TO` | — | Recipient address |
| `email.server` | `SENDEMELDUNG_EMAIL_SERVER` | — | SMTP server hostname |
| `email.password` | `SENDEMELDUNG_EMAIL_PASSWORD` | — | SMTP password |
| `email.subject` | `SENDEMELDUNG_EMAIL_SUBJECT` | `SUISA report` | Email subject |
| `email.text` | `SENDEMELDUNG_EMAIL_TEXT` | *(Swiss German template)* | Email body (`$`-substitution supported) |
| `email.responsible-email` | `SENDEMELDUNG_EMAIL_RESPONSIBLE_EMAIL` | — | Address for SUISA queries (used in email body) |

!!! tip "Email template variables"
    The default email body is a fully SUISA-compliant Swiss German letter that
    automatically substitutes `$station_name`, `$month`, `$year`,
    `$responsible_email`, `$in_three_months`, and `$email_footer`.
    Override individual variables via `l10n` settings below.

### Localisation settings

| Option | Env var | Default | Description |
| ------ | ------- | ------- | ----------- |
| `l10n.timezone` | `SENDEMELDUNG_L10N_TIMEZONE` | `Europe/Zurich` | Timezone for date output |
| `l10n.station-name` | `SENDEMELDUNG_L10N_STATION_NAME` | — | Station name used in email body |
| `l10n.email-footer` | `SENDEMELDUNG_L10N_EMAIL_FOOTER` | — | Footer appended to the email body |

### Identifier settings

Controls how the unique track identifier (`CRID`) is generated.

| Option | Env var | Default | Description |
| ------ | ------- | ------- | ----------- |
| `identifier.mode` | `SENDEMELDUNG_IDENTIFIER_MODE` | `cridlib` | `cridlib` (standard CRID) or `local` (UUID-based) |

## Minimal example

```toml
[sendemeldung]
output = "file"

acr.bearer-token = "ey..."
acr.stream-id    = "a-bcdefgh"
acr.project-id   = "1234"
```

## Full example with email delivery

```toml
[sendemeldung]
output = "email"

acr.bearer-token = "ey..."
acr.stream-id    = "a-bcdefgh"
acr.project-id   = "1234"

date.last-month = true

email.sender            = "sendemeldung@example.org"
email.to                = "sendemeldung@suisa.ch"
email.server            = "smtp.example.org"
email.password          = "s3cr3t"
email.responsible-email = "responsible@example.org"

l10n.timezone     = "Europe/Zurich"
l10n.station-name = "Radio Example"
l10n.email-footer = "Radio Example | Musterstrasse 1 | 3000 Bern"
```

## Environment variables example

```bash
podman run --rm -ti \
  -e SENDEMELDUNG_ACR_BEARER_TOKEN=ey... \
  -e SENDEMELDUNG_ACR_STREAM_ID=a-bcdefgh \
  -e SENDEMELDUNG_ACR_PROJECT_ID=1234 \
  -e SENDEMELDUNG_OUTPUT=stdout \
  ghcr.io/radiorabe/suisasendemeldung:latest
```
