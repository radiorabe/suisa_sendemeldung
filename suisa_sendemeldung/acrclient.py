"""module containing the ACRCloud client."""
import logging
from datetime import date, datetime, timedelta

import pytz
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ACRClient:
    """Fetches cached metadata from MinIO.

    Args:
        minio_url: URL to a public MinIO bucket containing raw per-day JSON files.
        timezone (optional): The timezone to use for localization.
    """

    # format of timestamp in api answer
    TS_FMT = "%Y-%m-%d %H:%M:%S"
    # timezone of ACRCloud
    ACR_TIMEZONE = "UTC"

    def __init__(self, minio_url: str, timezone=ACR_TIMEZONE):
        self.minio_url = minio_url
        self.timezone = timezone
        self.default_date = date.today() - timedelta(days=1)

    def get_data(self, requested_date=None):
        """Fetch ACRCloud metadata from MinIO.

        Args:
            requested_date (optional): The date of the entries you want (default: yesterday).

        Returns:
            json: The ACR data from date
        """
        if requested_date is None:
            requested_date = self.default_date
        url = f"{self.minio_url}{requested_date.strftime('%Y-%m-%d')}.json"
        resp = requests.get(url, timeout=10)
        if resp.ok:
            data = resp.json()
        else:  # pragma: no cover
            raise RuntimeError(f"💀 failed to load data from {url}")
        for entry in data:
            metadata = entry.get("metadata")
            ts_utc = pytz.utc.localize(
                datetime.strptime(metadata.get("timestamp_utc"), ACRClient.TS_FMT)
            )
            ts_local = ts_utc.astimezone(pytz.timezone(self.timezone))
            metadata.update({"timestamp_local": ts_local.strftime(ACRClient.TS_FMT)})

        return data

    def get_interval_data(self, start, end):
        """Get data specified by interval from start to end.

        Args:
            start: The start date of the interval.
            end: The end date of the interval.

        Returns:
            json: The ACR data from start to end.
        """
        trim = False
        # if we have to localize the timestamps we may need more data
        if self.timezone != ACRClient.ACR_TIMEZONE:
            # compute utc offset
            offset = pytz.timezone(self.timezone).utcoffset(datetime.now())
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

        dates = []
        ptr = computed_start
        while ptr <= computed_end:
            dates.append(ptr)
            ptr += timedelta(days=1)
        data = []
        # make the prefix longer by this amount so tqdm lines up with the one in the main code
        ljust_amount: int = 27
        for ptr in tqdm(dates, desc="load ACRCloud data".ljust(ljust_amount)):
            data += self.get_data(requested_date=ptr)

        # if timestamps are localized we will have to removed the unneeded entries.
        if trim:
            for entry in reversed(data):
                metadata = entry.get("metadata")
                timestamp = metadata.get("timestamp_local")
                timestamp_date = datetime.strptime(timestamp, ACRClient.TS_FMT).date()
                if timestamp_date < start or timestamp_date > end:
                    data.remove(entry)

        return data
