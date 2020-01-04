#!/usr/bin/env python3
from csv import writer
from datetime import datetime, date, timedelta, timezone
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import StringIO
from os.path import basename, expanduser
from smtplib import SMTP

from configargparse import ArgumentParser
import requests


class ACRClient:
    # format of timestamp in api answer
    TS_FMT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, access_key):
        """ACRCloud client to fetch metadata

        Args:
            access_key: The access key for ACRCloud.
        """
        self.access_key = access_key
        self.default_date = date.today()-timedelta(days=1)
        self.url = ('https://api.acrcloud.com/v1/'
                    'monitor-streams/{stream_id}/results')

    def get_data(self, stream_id, requested_date=None,
                 localize_timestamps=True):
        """Fetch metadata from ACRCloud for `stream_id`.
        Args:
            stream_id: The ID of the stream.
            requested_date (optional): The date of the entries you want.
            localize_timestamps (optional): If True add an additional field
                `timestamp_local` to the response.

        Returns:
            json: The ACR data from date
        """
        if requested_date is None:
            requested_date = self.default_date
        url_params = dict(
            access_key=self.access_key,
            date=requested_date.strftime('%Y%m%d')
        )
        url = self.url.format(stream_id=stream_id)
        response = requests.get(url=url, params=url_params)
        response.raise_for_status()

        if localize_timestamps:
            data = response.json()
            for entry in data:
                metadata = entry.get('metadata')
                ts_utc = datetime.strptime(metadata.get('timestamp_utc'),
                                           ACRClient.TS_FMT)
                ts_local = ts_utc.replace(tzinfo=timezone.utc) \
                                 .astimezone(tz=None)
                metadata.update({
                    'timestamp_local': ts_local.strftime(ACRClient.TS_FMT)
                })
            return data

        return response.json()

    def get_interval_data(self, stream_id, start, end,
                          localize_timestamps=True):
        """Get data specified by interval from start to end

        Args:
            stream_id: The ID of the stream.
            start: The start date of the interval.
            end: The end date of the interval.
            localize_timestamps: will be passed to `get_data()`.

        Returns:
            json: The ACR data from start to end.
        """
        trim = False
        # if we have to localize the timestamps we may need more data
        if localize_timestamps:
            # compute utc offset
            offset = datetime.now(timezone.utc).astimezone().utcoffset()
            # decrease start by 1 day if we're ahead of utc
            if offset > timedelta(seconds=1):
                computed_start = start - timedelta(days=1)
                computed_end = end
                trim = True
            # increase end by 1 day if we're behind of utc
            elif offset < timedelta(seconds=1):
                computed_start = start
                computed_end = end + timedelta(days=1)
                trim = True
        else:
            computed_start = start
            computed_end = end

        data = []
        ptr = computed_start
        while ptr <= computed_end:
            data += self.get_data(stream_id, requested_date=ptr,
                                  localize_timestamps=localize_timestamps)
            ptr += timedelta(days=1)

        if trim:
            # if timestamps are localized we will have to removed the unneeded
            # entries.
            data = self.trim_data(data, start, end)

        return data

    def trim_data(self, data, start, end):
        """Trim overlapping entries by start end end date

        Args:
            data: The data to trim.
            start: The start date to trim by. Older entries will be removed
                from data.
            end: The end date to trim by. Newer entries will be removed from
                data.

        Returns:
            The data without removed entries.
        """
        # traverse data in reversed order so we are not altering the flow
        # https://stackoverflow.com/questions/14267722/
        for entry in reversed(data):
            metadata = entry.get('metadata')
            if metadata.get('timestamp_local'):
                ts = metadata.get('timestamp_local')
            else:
                ts = metadata.get('timestamp_utc')
            date = datetime.strptime(ts, ACRClient.TS_FMT).date()
            if date < start or date > end:
                data.remove(entry)

        return data


def get_csv(data):
    """Create SUISA compatible csv data

    Arguments:
        data: To data to create csv from

    Returns:
        csv: The converted data
    """
    header = [
        'Sendedatum',
        'Sendezeit',
        'Sendedauer',
        'Titel',
        'Künstler',
        'ISRC',
        'Label'
    ]
    csv = StringIO()
    csv.write('sep=,\n')

    csv_writer = writer(csv, dialect='excel')
    csv_writer.writerow(header)

    for entry in data:
        metadata = entry.get('metadata')
        # parse timestamp
        timestamp = datetime.strptime(metadata.get('timestamp_local'),
                                      ACRClient.TS_FMT)

        date = timestamp.strftime('%d/%m/%y')
        time = timestamp.strftime('%H:%M:%S')
        duration = timedelta(seconds=metadata.get('played_duration'))

        music = metadata.get('music')[0]
        title = music.get('title')
        if music.get('artists') is not None:
            artist = ', '.join([a.get('name') for a in music.get('artists')])
        else:
            artist = ''
        if len(music.get('external_ids')) > 0:
            isrc = music.get('external_ids').get('isrc')
        else:
            isrc = ''
        label = music.get('label')

        csv_writer.writerow([date, time, duration,
                             title, artist, isrc, label])
    return csv.getvalue()


def write_csv(filename, csv):
    """Write contents of `csv` to file

    Arguments:
        filename: The file to write to.
        csv: The data to write to `filename`.
    """
    with open(filename, mode='w') as csvfile:
        csvfile.write(csv)


def send_email(sender, to, subject, text, filename, csv,
               server='127.0.0.1', password=None):
    """Send email

    Arguments:
        sender: The sender of the email. Login will be made with this user.
        to: The recipient of the email. Can be a list.
        subject: The subject of the email.
        text: The body of the email.
        filename: The filename to attach `csv` by.
        csv: The attachment data.
        server: The SMTP server to use to send the email.
        password: The password for `sender`@`server`.
    """
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ', '.join(to)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    part = MIMEBase('text', 'csv')
    part.set_payload(csv.encode('utf-8'))
    encode_base64(part)
    part.add_header('Content-Disposition',
                    'attachment; filename="{}"'.format(basename(filename)))
    msg.attach(part)

    with SMTP(server) as smtp:
        smtp.starttls()
        if password:
            smtp.login(sender, password)
        smtp.sendmail(sender, to, msg.as_string())


def main():
    default_config_file = basename(__file__).replace('.py', '.conf')
    # config file in /etc gets overriden by the one in $HOME which gets
    # overriden by the one in the current directory
    default_config_files = [
        '/etc/' + default_config_file,
        expanduser('~') + '/' + default_config_file,
        default_config_file
    ]
    parser = ArgumentParser(
                default_config_files=default_config_files,
                description='ACRCloud client for SUISA reporting @ RaBe.')

    parser.add_argument('--access_key', env_var='ACCESS_KEY',
                        help='the access key for ACRCloud (required)',
                        required=True)
    parser.add_argument('--stream_id', env_var='STREAM_ID',
                        help='the id of the stream at ACRCloud (required)',
                        required=True)
    parser.add_argument('--csv', env_var='CSV', help='create a csv file',
                        action='store_true')
    parser.add_argument('--email', env_var='EMAIL', help='send an email',
                        action='store_true')
    parser.add_argument('--email_from', env_var='EMAIL_FROM',
                        help='the sender of the email')
    parser.add_argument('--email_to', env_var='EMAIL_TO',
                        help='the recipient of the email')
    parser.add_argument('--email_server', env_var='EMAIL_SERVER',
                        help='the smtp server to send the mail with')
    parser.add_argument('--email_pass', env_var='EMAIL_PASS',
                        help='the password for the smtp server')
    parser.add_argument('--email_subject', env_var='EMAIL_SUBJECT',
                        help='the subject of the email',
                        default='SUISA Sendemeldung')
    parser.add_argument('--email_text', env_var='EMAIL_TEXT',
                        help='the text of the email', default='')
    parser.add_argument('--start_date', env_var='START_DATE',
                        help='the start date of the interval in format \
                              YYYY-MM-DD (defaults to 30 days before \
                              end_date)')
    parser.add_argument('--end_date', env_var='END_DATE',
                        help='the end date of the interval in format \
                              YYYY-MM-DD (defaults to today)')
    parser.add_argument('--last_month', env_var='LAST_MONTH',
                        action='store_true',
                        help='download data of whole last month')
    parser.add_argument('--filename', env_var='FILENAME',
                        help='file to write to (defaults to \
                              <script_name>_<start_date>.csv)')
    parser.add_argument('--stdout', env_var='STDOUT',
                        help='also print to stdout', action='store_true')

    args = parser.parse_args()

    # validate arguments
    if not len(args.access_key) == 32:
        parser.error('wrong format on access_key, expected 32 characters '
                     'but got {}.'.format(len(args.access_key)))
    if not len(args.stream_id) == 9:
        parser.error('wrong format on stream_id, expected 9 characters '
                     'but got {}.'.format(len(args.stream_id)))
    # one output option has to be set
    if not (args.csv or args.email or args.stdout):
        parser.error('no output option has been set, specify one of --csv, '
                     '--email or --stdout')

    # date parsing logic
    if args.last_month:
        if args.start_date or args.end_date:
            parser.error('argument --last_month not allowed with '
                         '--start_date or --end_date')
        today = date.today()
        # get first of this month
        this_month = today.replace(day=1)
        # last day of last month = first day of this month - 1 day
        end_date = this_month - timedelta(days=1)
        start_date = end_date.replace(day=1)
    else:
        if args.end_date:
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
        else:
            # if no end_date was set, default to today
            end_date = date.today()
        if args.start_date:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
        else:
            # if no start_date was set, default to 30 days before end_date
            start_date = end_date - timedelta(days=30)

    if args.filename:
        filename = args.filename
    # depending on date args either append the month or the start_date
    elif args.last_month:
        filename = (__file__.replace('.py', '_{}.csv')
                            .format(start_date.strftime('%B')))
    else:
        filename = __file__.replace('.py', '_{}.csv').format(start_date)

    client = ACRClient(args.access_key)
    data = client.get_interval_data(args.stream_id, start_date, end_date)
    csv = get_csv(data)
    if args.email:
        send_email(args.email_from, args.email_to.split(','),
                   args.email_subject, args.email_text, filename, csv,
                   server=args.email_server, password=args.email_pass)
    if args.csv:
        write_csv(filename, csv)
    if args.stdout:
        print(csv)


if __name__ == '__main__':
    main()
