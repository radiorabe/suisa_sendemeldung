# suisa_sendemeldung

ACRCloud client that fetches data on our playout history and formats them in a CSV file format containing the data (like Track, Title and ISRC) requested by SUISA. Also takes care of sending the report to SUISA via email for hands-off operations.

## Installation

### [Open Build Service](https://openbuildservice.org/)

There are pre-built binary packages for CentOS 7 available on [Radio RaBe's OBS sendemeldungs package repository](https://build.opensuse.org/project/show/home:radiorabe:sendemeldung), which can be installed as follows:

```bash
curl -o /etc/yum.repos.d/home:radiorabe:sendemeldung.repo \
     http://download.opensuse.org/repositories/home:/radiorabe:/sendemeldung/CentOS_7/home:radiorabe:sendemeldung.repo

yum install suisa_sendemeldung
```

### Docker

You can build a Docker image using the included [Dockerfile](Dockerfile):

```bash
git clone https://github.com/radiorabe/suisa_sendemeldung
cd suisa_sendemeldung
sudo docker build -t suisa_sendemeldung .
```

Then you can run it by passing in command line switches:

```bash
sudo docker run --rm suisa_sendemeldung --access_key abcdefghijklmnopqrstuvwxyzabcdef --stream_id a-bcdefgh --stdout
```

Or by setting environment variables:

```bash
sudo docker run --rm --env ACCESS_KEY=abcdefghijklmnopqrstuvwxyzabcdef --env STREAM_ID=a-bcdefgh --env STDOUT=True suisa_sendemeldung
```

## Usage

This is the output of `suisa_sendemeldung -h`.
```
usage: suisa_sendemeldung.py [-h] --access_key ACCESS_KEY --stream_id STREAM_ID [--csv] [--email]
                             [--email_from EMAIL_FROM] [--email_to EMAIL_TO] [--email_cc EMAIL_CC]
                             [--email_bcc EMAIL_BCC] [--email_server EMAIL_SERVER]
                             [--email_login EMAIL_LOGIN] [--email_pass EMAIL_PASS]
                             [--email_subject EMAIL_SUBJECT] [--email_text EMAIL_TEXT]
                             [--start_date START_DATE] [--end_date END_DATE] [--last_month]
                             [--filename FILENAME] [--stdout]

ACRCloud client for SUISA reporting @ RaBe. Args that start with '--' (eg. --access_key) can also be set in
a config file (/etc/suisa_sendemeldung.conf or $HOME/suisa_sendemeldung.conf or
suisa_sendemeldung.conf). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see
syntax at https://goo.gl/R74nmi). If an arg is specified in more than one place, then commandline values
override environment variables which override config file values which override defaults.

optional arguments:
  -h, --help            show this help message and exit
  --access_key ACCESS_KEY
                        the access key for ACRCloud (required) [env var: ACCESS_KEY]
  --stream_id STREAM_ID
                        the id of the stream at ACRCloud (required) [env var: STREAM_ID]
  --csv                 create a csv file [env var: CSV]
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
                        the username to logon to the smtp server (default: email_from) [env var:
                        EMAIL_LOGIN]
  --email_pass EMAIL_PASS
                        the password for the smtp server [env var: EMAIL_PASS]
  --email_subject EMAIL_SUBJECT
                        the subject of the email [env var: EMAIL_SUBJECT]
  --email_text EMAIL_TEXT
                        the text of the email [env var: EMAIL_TEXT]
  --start_date START_DATE
                        the start date of the interval in format YYYY-MM-DD (default: 30 days before
                        end_date) [env var: START_DATE]
  --end_date END_DATE   the end date of the interval in format YYYY-MM-DD (default: today) [env var:
                        END_DATE]
  --last_month          download data of whole last month [env var: LAST_MONTH]
  --filename FILENAME   file to write to (default: <script_name>_<start_date>.csv) [env var: FILENAME]
  --stdout              also print to stdout [env var: STDOUT]
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
ACCESS_KEY=abcdefghijklmnopqrstuvwxyzabcdef STREAM_ID=a-bcdefgh STDOUT=True ./suisa_sendemeldung.py
```

### Command line switches

As documented in [Usage](#Usage), you can also pass in options on the command line as arguments. Simply run the script as follows:

```bash
./suisa_sendemeldung.py --access_key=abcdefghijklmnopqrstuvwxyzabcdef --stream_id=a-bcdefgh --stdout
```
