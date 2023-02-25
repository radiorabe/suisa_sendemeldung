"""module containing the ACRCloud client."""
from datetime import date, datetime, timedelta

import pytz
from acrclient import Client
from tqdm import tqdm


class ACRClient(Client):
    """ACRCloud client to fetch metadata.

    Args:
        bearer_token: The bearer token for ACRCloud.
    """

    # format of timestamp in api answer
    TS_FMT = "%Y-%m-%d %H:%M:%S"
    # timezone of ACRCloud
    ACR_TIMEZONE = "UTC"

    def __init__(self, bearer_token, base_url="https://eu-api-v2.acrcloud.com"):
        super().__init__(bearer_token=bearer_token, base_url=base_url)
        self.default_date = date.today() - timedelta(days=1)

    def get_data(
        self, project_id, stream_id, requested_date=None, timezone=ACR_TIMEZONE
    ):
        """Fetch metadata from ACRCloud for `stream_id`.

        Args:
            project_id: The Project ID of the stream.
            stream_id: The ID of the stream.
            requested_date (optional): The date of the entries you want (default: yesterday).
            timezone (optional): The timezone to use for localization.

        Returns:
            json: The ACR data from date
        """
        if requested_date is None:
            requested_date = self.default_date
        data = self.get_bm_cs_projects_results(
            project_id=project_id,
            stream_id=stream_id,
            params={
                "date": requested_date.strftime("%Y%m%d"),
            },
        )
        for entry in data:
            metadata = entry.get("metadata")
            ts_utc = pytz.utc.localize(
                datetime.strptime(metadata.get("timestamp_utc"), ACRClient.TS_FMT)
            )
            ts_local = ts_utc.astimezone(pytz.timezone(timezone))
            metadata.update({"timestamp_local": ts_local.strftime(ACRClient.TS_FMT)})

        return data

    def get_interval_data(
        self, project_id, stream_id, start, end, timezone=ACR_TIMEZONE
    ):  # pylint: disable-msg=too-many-locals,too-many-arguments
        """Get data specified by interval from start to end.

        Args:
            project_id: The ID of the project.
            stream_id: The ID of the stream.
            start: The start date of the interval.
            end: The end date of the interval.
            timezone (optional): will be passed to `get_data()`.

        Returns:
            json: The ACR data from start to end.
        """
        trim = False
        # if we have to localize the timestamps we may need more data
        if timezone != ACRClient.ACR_TIMEZONE:
            # compute utc offset
            offset = pytz.timezone(timezone).utcoffset(datetime.now())
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
            data += self.get_data(
                project_id, stream_id, requested_date=ptr, timezone=timezone
            )

        # if timestamps are localized we will have to removed the unneeded entries.
        if trim:
            for entry in reversed(data):
                metadata = entry.get("metadata")
                timestamp = metadata.get("timestamp_local")
                timestamp_date = datetime.strptime(timestamp, ACRClient.TS_FMT).date()
                if timestamp_date < start or timestamp_date > end:
                    data.remove(entry)

        return data
