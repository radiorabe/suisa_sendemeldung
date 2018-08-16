# suisa_sendemeldung
```
usage: suisa_sendemeldung.py [-h] --access_key ACCESS_KEY --stream_id
                             STREAM_ID [--start_date START_DATE]
                             [--end_date END_DATE] [--output OUTPUT]

ACRCloud client for SUISA reporting @ RaBe.

optional arguments:
  -h, --help            show this help message and exit
  --access_key ACCESS_KEY
                        the access key for ACRCloud (required)
  --stream_id STREAM_ID
                        the id of the stream at ACRCloud (required)
  --start_date START_DATE
                        the start date of the interval in format YYYY-MM-DD
                        (defaults to 30 days before end_date)
  --end_date END_DATE   the end date of the interval in format YYYY-MM-DD
                        (defaults to today)
  --output OUTPUT       file to write to (defaults to
                        <script_name>_<start_date>.csv)
```
