# Getting Started

ACRCloud client that fetches data on your playout history and formats it into
a CSV/XLSX file containing the data (like Track, Title, and ISRC) requested by
[SUISA](https://www.suisa.ch/). Also takes care of sending the report to SUISA
via email for hands-off operations.

## Installation

We provide SUISA Sendemeldung as a **container image** or as a **Python package**.

### Container (recommended)

The easiest way to run SUISA Sendemeldung is with the official container image
via [rootless Podman](https://podman.io/):

```bash
podman run --rm -ti \
  ghcr.io/radiorabe/suisasendemeldung:latest \
  suisa_sendemeldung --help
```

!!! note "Docker"
    Docker works as a drop-in replacement — substitute `docker` for `podman`
    in any of the commands above. Rootless Podman is strongly recommended.

### Python package

If you prefer a plain Python install, use `pip` in a dedicated virtual
environment:

```bash
python -m venv .venv
. .venv/bin/activate

pip install suisa_sendemeldung
suisa_sendemeldung --help
```

## Quick start

1. **Obtain your ACRCloud credentials** — bearer token, stream ID, and
   project ID from the [ACRCloud console](https://console.acrcloud.com/).

2. **Create a minimal configuration file** at `suisa_sendemeldung.toml`:

    ```toml
    [sendemeldung]
    output = "stdout"

    acr.bearer-token = "ey..."
    acr.stream-id    = "a-bcdefgh"
    acr.project-id   = "1234"
    ```

3. **Run the script** for the previous month:

    ```bash
    suisa_sendemeldung --last-month
    ```

    The report is printed to standard output. Change `output` to `"file"` or
    `"email"` when you're ready for production.

!!! tip "Date selection"
    Use `--last-month` for the most common case. For custom ranges pass
    `--by-date` with explicit `--date-start YYYY-MM-DD` and `--date-end YYYY-MM-DD`.

## Next steps

- Read the [Configuration](configuration.md) reference for all available
  options.
- Set up [automated deployment](deployment.md) with systemd timers or a
  container orchestrator.
- Check the [Python API Reference](reference/) if you want to use
  the library programmatically.
