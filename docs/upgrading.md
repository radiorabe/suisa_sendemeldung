# Upgrading

## Upgrade from 0.x to 1.0

Version 1.0 is a significant cleanup release. Review the breaking changes
below before upgrading.

### Configuration file

| | 0.x | 1.0 |
|---|---|---|
| **File name** | `suisa_sendemeldung.conf` | `suisa_sendemeldung.toml` |
| **Format** | INI-style (`[section]` / `key = value`) | [TOML](https://toml.io/) |

Migrate your existing configuration by renaming the file and converting the
syntax. Example:

=== "0.x (INI)"

    ```ini
    [settings]
    bearer_token = ey...
    stream_id    = a-bcdefgh
    ```

=== "1.0 (TOML)"

    ```toml
    [sendemeldung]
    acr.bearer-token = "ey..."
    acr.stream-id    = "a-bcdefgh"
    ```

### CLI flags

All command-line flags have been renamed to match the new TOML key hierarchy.
Run `suisa_sendemeldung --help` to see the current list of flags.

### Removed features

The **"last 30 days from today"** mode has been dropped. Use
`--date-last-month` (or `date.last-month = true` in the config file) to
report on the previous calendar month, or pass explicit `--date-start` /
`--date-end` values for a custom range.

### Python version

Python 3.12 or later is now required.

---

## Support matrix

| Version | Supported | GST | Python | Notes |
| ------- | :-------: | --- | ------ | ----- |
| 0.x | ✅ | GST 2020 | — | Internal use at RaBe; maintained on a best-efforts basis for historical reports |
| 1.x | ✅ | GST 2026 | ≥ 3.12 | First public release; actively maintained |

> Old versions are supported on a case-by-case basis when regenerating
> historical reports.
