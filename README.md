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
usage: suisa_sendemeldung.py [-h] --bearer-token BEARER_TOKEN --stream_id STREAM_ID [--station-name STATION_NAME] [--station-name-short STATION_NAME_SHORT] [--file] [--filetype {xlsx,csv}] [--email] [--email_from EMAIL_FROM] [--email_to EMAIL_TO] [--email_cc EMAIL_CC] [--email_bcc EMAIL_BCC] [--email_server EMAIL_SERVER] [--email_login EMAIL_LOGIN] [--email_pass EMAIL_PASS] [--email_subject EMAIL_SUBJECT] [--email_text EMAIL_TEXT] --responsible-email RESPONSIBLE_EMAIL --responsible-phone RESPONSIBLE_PHONE [--start_date START_DATE] [--end_date END_DATE] [--last_month] [--timezone TIMEZONE] [--filename FILENAME] [--stdout]

ACRCloud client for SUISA reporting @ RaBe.

options:
  -h, --help            show this help message and exit
  --bearer-token BEARER_TOKEN
                        the bearer token for ACRCloud (required) [env var: BEARER_TOKEN]
  --stream_id STREAM_ID
                        the id of the stream at ACRCloud (required) [env var: STREAM_ID]
  --station-name STATION_NAME
                        Station name, used in Output and Emails [env var: STATION_NAME]
  --station-name-short STATION_NAME_SHORT
                        Shortname for station as used in Filenames (locally and in attachment) [env var: STATION_NAME_SHORT]
  --file                create file [env var: FILE]
  --filetype {xlsx,csv}
                        filetype to attach to email or write to file [env var: FILETYPE]
  --email               send an email [env var: EMAIL]
  --email_from EMAIL_FROM
                        the sender of the email [env var: EMAIL_FROM]
  --email_to EMAIL_TO   the recipients of the email [env var: EMAIL_TO]
  --email_cc EMAIL_CC   the cc recipients of the email [env var: EMAIL_CC]
  --email_bcc EMAIL_BCC
                        the bcc recipients of the email [env var: EMAIL_BCC]
  --email_server EMAIL_SERVER
                        the smtp server to send the mail with [env var: EMAIL_SERVER]
  --email_login EMAIL_LOGIN
                        the username to logon to the smtp server (default: email_from) [env var: EMAIL_LOGIN]
  --email_pass EMAIL_PASS
                        the password for the smtp server [env var: EMAIL_PASS]
  --email_subject EMAIL_SUBJECT
                        the subject of the email [env var: EMAIL_SUBJECT]
  --email_text EMAIL_TEXT
                        A template for the Email text, placeholders are $station_name, $month, $year, $previous_year, $responsible_email, and $resonsible_phone. [env var: EMAIL_TEXT]
  --responsible-email RESPONSIBLE_EMAIL
                        Used to hint whom to contact in the emails text. [env var: RESPONSIBLE_EMAIL]
  --responsible-phone RESPONSIBLE_PHONE
                        Used to hint whom to contact if you like phones in the emails text. [env var: RESPONSIBLE_PHONE]
  --start_date START_DATE
                        the start date of the interval in format YYYY-MM-DD (default: 30 days before end_date) [env var: START_DATE]
  --end_date END_DATE   the end date of the interval in format YYYY-MM-DD (default: today) [env var: END_DATE]
  --last_month          download data of whole last month [env var: LAST_MONTH]
  --timezone TIMEZONE   set the timezone for localization [env var: TIMEZONE]
  --filename FILENAME   file to write to (default: <station_name_short>_<year>_<month>.csv when reporting last month, <station_name_short>_<start_date>.csv else) [env var: FILENAME]
  --stdout              also print to stdout [env var: STDOUT]

Args that start with '--' (eg. --access_key) can also be set in a config file (/etc/suisa_sendemeldung.conf or $HOME/suisa_sendemeldung.conf or suisa_sendemeldung.conf). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see syntax at https://goo.gl/R74nmi). If an arg is specified in more than one place, then commandline values override environment variables which override config file values which override defaults.
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
