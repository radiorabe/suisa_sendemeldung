"""module containing the ACRCloud client"""
from datetime import date, datetime, timedelta, timezone

import requests

class ACRClient:
    """ACRCloud client to fetch metadata

    Args:
        access_key: The access key for ACRCloud.
    """
    # format of timestamp in api answer
    TS_FMT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, access_key):
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

        # if timestamps are localized we will have to removed the unneeded entries.
        if trim:
            for entry in reversed(data):
                metadata = entry.get('metadata')
                if metadata.get('timestamp_local'):
                    timestamp = metadata.get('timestamp_local')
                else:
                    timestamp = metadata.get('timestamp_utc')
                timestamp_date = datetime.strptime(timestamp, ACRClient.TS_FMT).date()
                if timestamp_date < start or timestamp_date > end:
                    data.remove(entry)

        return data
