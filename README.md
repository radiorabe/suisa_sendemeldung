# suisa_sendemeldung
```
usage: suisa_sendemeldung.py [-h] --access_key ACCESS_KEY --stream_id
                             STREAM_ID --email_from EMAIL_FROM --email_to
                             EMAIL_TO --email_server EMAIL_SERVER --email_pass
                             EMAIL_PASS [--email_subject EMAIL_SUBJECT]
                             [--email_text EMAIL_TEXT]
                             [--start_date START_DATE] [--end_date END_DATE]
                             [--last_month] [--filename FILENAME]

ACRCloud client for SUISA reporting @ RaBe.

optional arguments:
  -h, --help            show this help message and exit
  --access_key ACCESS_KEY
                        the access key for ACRCloud (required)
  --stream_id STREAM_ID
                        the id of the stream at ACRCloud (required)
  --email_from EMAIL_FROM
                        the sender of the email
  --email_to EMAIL_TO   the recipient of the email
  --email_server EMAIL_SERVER
                        the smtp server to send the mail with
  --email_pass EMAIL_PASS
                        the password for the smtp server
  --email_subject EMAIL_SUBJECT
                        the subject of the email
  --email_text EMAIL_TEXT
                        the text of the email
  --start_date START_DATE
                        the start date of the interval in format YYYY-MM-DD
                        (defaults to 30 days before end_date)
  --end_date END_DATE   the end date of the interval in format YYYY-MM-DD
                        (defaults to today)
  --last_month          download data of whole last month
  --filename FILENAME   file to write to (defaults to
                        <script_name>_<start_date>.csv)
```
