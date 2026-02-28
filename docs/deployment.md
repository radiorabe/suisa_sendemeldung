# Deployment

This guide shows how to run SUISA Sendemeldung in production so that the
monthly report is generated and sent **automatically** on a schedule.

## Supported deployment models

| Model | Recommended for |
| ----- | --------------- |
| [systemd timer](#systemd-timer) | Self-hosted Linux servers (bare metal or VM) |
| [Container (one-shot)](#container-one-shot) | Any host with rootless Podman |
| [Cron job](#cron-job) | Minimal setups without systemd |

---

## systemd timer

The `etc/systemd/` directory in this repository ships a ready-to-use template
unit pair.

### Quick setup

```bash
# 1. Copy configuration
sudo mkdir -p /etc/suisa_sendemeldung
sudo cp etc/suisa_sendemeldung.toml /etc/suisa_sendemeldung/production.toml
# edit the file and fill in your credentials
sudo $EDITOR /etc/suisa_sendemeldung/production.toml

# 2. Install units
sudo cp etc/systemd/suisa_sendemeldung@.service /etc/systemd/system/
sudo cp etc/systemd/suisa_sendemeldung@.timer   /etc/systemd/system/

# 3. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable --now 'suisa_sendemeldung@production.timer'

# 4. Verify
systemctl list-timers suisa_sendemeldung@production.timer
```

### How the units work

**`suisa_sendemeldung@.service`** is a *template* service that:

- Pulls the latest container image before each run.
- Mounts `/etc/suisa_sendemeldung/%i.toml` as `/etc/suisa_sendemeldung.toml`
  inside the container (where `%i` is the instance name — `production` in the
  example above).
- Runs the container as a one-shot job and exits when done.

**`suisa_sendemeldung@.timer`** triggers the service on the 14th of each month
at 09:00. RaBe runs the script on the 1st and 14th; adjust the `OnCalendar`
value to suit your schedule.

!!! tip "Multiple stations"
    Because the units are template units you can run several instances in
    parallel, one per station configuration file:

    ```bash
    systemctl enable --now suisa_sendemeldung@station-a.timer
    systemctl enable --now suisa_sendemeldung@station-b.timer
    ```

### Customising the schedule

Edit the timer's `OnCalendar` value to change when the report runs:

```ini
[Timer]
# Run on the 1st and 14th of every month at 09:00
OnCalendar=
OnCalendar=*-*-1,14 09:00:00
Persistent=true
```

After editing, reload the daemon and restart the timer:

```bash
sudo systemctl daemon-reload
sudo systemctl restart suisa_sendemeldung@production.timer
```

---

## Container (one-shot)

Run the container once for a specific month using
[rootless Podman](https://podman.io/):

```bash
podman run --rm \
  -v /etc/suisa_sendemeldung/production.toml:/etc/suisa_sendemeldung.toml:ro \
  ghcr.io/radiorabe/suisasendemeldung:latest \
  suisa_sendemeldung --last-month
```

!!! note "Docker"
    Docker works as a drop-in replacement — substitute `docker` for `podman`
    in any of the commands above. Rootless Podman is strongly recommended.

All configuration can also be passed as environment variables without a
mounted config file:

```bash
podman run --rm \
  -e SENDEMELDUNG_ACR_BEARER_TOKEN=ey... \
  -e SENDEMELDUNG_ACR_STREAM_ID=a-bcdefgh \
  -e SENDEMELDUNG_ACR_PROJECT_ID=1234 \
  -e SENDEMELDUNG_OUTPUT=email \
  -e SENDEMELDUNG_EMAIL_SERVER=smtp.example.org \
  -e SENDEMELDUNG_EMAIL_SENDER=report@example.org \
  -e SENDEMELDUNG_EMAIL_TO=sendemeldung@suisa.ch \
  -e SENDEMELDUNG_EMAIL_PASSWORD=s3cr3t \
  -e SENDEMELDUNG_DATE_LAST_MONTH=true \
  ghcr.io/radiorabe/suisasendemeldung:latest
```

---

## Cron job

If systemd is not available, use cron:

```cron
# Run on the 14th of every month at 09:00
0 9 14 * * podman run --rm \
  -v /etc/suisa_sendemeldung/production.toml:/etc/suisa_sendemeldung.toml:ro \
  ghcr.io/radiorabe/suisasendemeldung:latest \
  suisa_sendemeldung --last-month
```

---

## Monitoring

The systemd service file contains a commented-out `ExecStartPost` line that
sends a Zabbix heartbeat after a successful run. Uncomment and adapt it to
your monitoring stack:

```ini
ExecStartPost=-/bin/sh -c 'zabbix_sender \
  -c /etc/zabbix/zabbix_agent2.conf \
  -s sendemeldung.example.org \
  -k rabe.suisa_sendemeldung.run.success \
  -o "$$(date +%%s)"'
```

!!! note "Double `%` in systemd units"
    systemd unit files use `%%` to produce a literal `%`. If you adapt this
    command for a plain shell script, replace `%%s` with `%s`.
