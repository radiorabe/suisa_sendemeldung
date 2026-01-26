# Run SUISA Sendemeldung using SystemD timers

The provided SystemD tempalte units expect the configuration to be stored
in the `/etc/suisa_sendemeldung` directory of the host system.

```bash
# Copy config and SystemD units
cp suisa_sendemeldung.toml /etc/suisa_sendemeldung/production.toml
cp systemd/* /etc/systemd/system/

# Load units and start timer
systemctl daemon-reload
systemctl enable --now 'suisa_sendemeldung@production.timer'

# Check if timer is active
systemctl list-timers
```
