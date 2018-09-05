#!/usr/bin/env python3
from argparse import ArgumentParser
from csv import writer
from datetime import datetime, date, timedelta, timezone

import requests


class ACRClient:
    # format of timestamp in api answer
    TS_FMT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, access_key):
        self.access_key = access_key
        self.default_date = date.today()-timedelta(days=1)
        self.url = ('https://api.acrcloud.com/v1/'
                    'monitor-streams/{stream_id}/results')

    def get_data(self, stream_id, requested_date=None,
                 localize_timestamps=True):
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

    def trim_data(self, data, start, end):
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

    def get_interval_data(self, stream_id, start, end,
                          localize_timestamps=True):
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
            data = self.trim_data(data, start, end)

        return data


def write_csv(filename, data):
    header = [
        'Sendedatum',
        'Sendezeit',
        'Sendedauer',
        'Titel',
        'Künstler',
        'ISRC',
        'Label'
    ]
    with open(filename, mode='w') as csvfile:
        csvfile.write('sep=,\n')

        csv_writer = writer(csvfile, dialect='excel')
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
            artist = ', '.join([a.get('name') for a in music.get('artists')])
            if len(music.get('external_ids')) > 0:
                isrc = music.get('external_ids').get('isrc')
            else:
                isrc = ""
            label = music.get('label')

            csv_writer.writerow([date, time, duration,
                                 title, artist, isrc, label])


if __name__ == '__main__':
    parser = ArgumentParser(
                description='ACRCloud client for SUISA reporting @ RaBe.')
    parser.add_argument('--access_key',
                        help='the access key for ACRCloud (required)',
                        required=True)
    parser.add_argument('--stream_id',
                        help='the id of the stream at ACRCloud (required)',
                        required=True)
    parser.add_argument('--start_date',
                        help='the start date of the interval in format \
                              YYYY-MM-DD (defaults to 30 days before \
                              end_date)')
    parser.add_argument('--end_date',
                        help='the end date of the interval in format \
                              YYYY-MM-DD (defaults to today)')
    parser.add_argument('--last_month',
                        action='store_true',
                        help='download data of whole last month')
    parser.add_argument('--output',
                        help='file to write to (defaults to \
                              <script_name>_<start_date>.csv)')
    args = parser.parse_args()

    # validate inputs
    if not len(args.access_key) == 32:
        parser.error('wrong format on access_key, expected 32 characters '
                     'but got {}.'.format(len(args.access_key)))
    if not len(args.stream_id) == 9:
        parser.error('wrong format on stream_id, expected 9 characters '
                     'but got {}.'.format(len(args.stream_id)))

    # date parsing logic
    if args.last_month:
        if args.start_date or args.end_date:
            parser.error('argument --last_month not allowed with '
                         '--start_date or --end_date')
        today = date.today()
        # get first of last month
        start_date = date(today.year, today.month-1, 1)
        # get first of this month
        this_month = today.replace(day=1)
        # last day of last month = first day of this month - 1 day
        end_date = this_month - timedelta(days=1)
    else:
        if args.end_date:
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
        else:
            end_date = date.today()
        if args.start_date:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
        else:
            start_date = end_date - timedelta(days=30)

    if args.output:
        output = args.output
    else:
        output = __file__.replace('.py', '_{}.csv').format(start_date)

    client = ACRClient(args.access_key)
    data = client.get_interval_data(args.stream_id, start_date, end_date)
    write_csv(output, data)
