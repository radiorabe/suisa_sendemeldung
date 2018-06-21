# suisa_sendemeldung
```
usage: suisa_sendemeldung.py [-h] --access_key ACCESS_KEY --stream_id
                             STREAM_ID [--date DATE] [--output OUTPUT]

ACRCloud client for SUISA reporting @ RaBe.

optional arguments:
  -h, --help            show this help message and exit
  --access_key ACCESS_KEY
                        the access key for ACRCloud (required)
  --stream_id STREAM_ID
                        the id of the stream at ACRCloud (required)
  --date DATE           date in format YYYYMMDD to fetch data for (defaults to
                        yesterday)
  --output OUTPUT       file to write to (defaults to
                        <script_name>_<date>.csv)
```
