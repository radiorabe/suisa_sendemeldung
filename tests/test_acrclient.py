"""Tests for the ACR client module."""

from datetime import date

import requests_mock
from freezegun import freeze_time

from suisa_sendemeldung import acrclient

_ACR_URL = "https://eu-api-v2.acrcloud.com/api/bm-cs-projects/project-id/streams/stream-id/results"


def test_init():
    """Test ACRClient.__init__."""
    bearer_token = "secret-key"
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(bearer_token)

    assert acr.default_date == date(1993, 3, 1)


def test_get_data():
    """Test ACRClient.get_data."""
    bearer_token = "secret-key"
    project_id = "project-id"
    stream_id = "stream-id"
    data = {"data": [{"metadata": {"timestamp_utc": "1993-03-01 13:12:00"}}]}
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(bearer_token)
    with requests_mock.Mocker() as mock:
        mock.get(
            _ACR_URL,
            json=data,
        )
        acr.get_data(project_id, stream_id)

    # calling without requested_date uses the default date (yesterday)
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(bearer_token)
    with requests_mock.Mocker() as mock:
        mock.get(
            _ACR_URL,
            json=data,
        )
        result = acr.get_data(project_id, stream_id, requested_date=None)
    assert len(result) == 1


def test_get_interval_data():
    """Test ACRClient.get_interval_data."""
    bearer_token = "secret-key"
    project_id = "project-id"
    stream_id = "stream-id"

    # UTC timezone (no trim): one entry per day for 31 days
    data = {"data": [{"metadata": {"timestamp_utc": "1993-03-15 13:12:00"}}]}
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(bearer_token)
    with requests_mock.Mocker() as mock:
        mock.get(_ACR_URL, json=data)
        result = acr.get_interval_data(
            project_id,
            stream_id,
            date(1993, 3, 1),
            date(1993, 3, 31),
        )
    assert len(result) == 31  # noqa: PLR2004

    # ahead of UTC (Europe/Zurich, UTC+1): entries localized to [start, end] are kept
    # "1993-03-01 00:00:00 UTC" = "1993-03-01 01:00:00 Zurich" → kept
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(bearer_token)
    with requests_mock.Mocker() as mock:
        data["data"][0]["metadata"]["timestamp_utc"] = "1993-03-01 00:00:00"
        mock.get(_ACR_URL, json=data)
        result = acr.get_interval_data(
            project_id,
            stream_id,
            date(1993, 3, 1),
            date(1993, 3, 31),
            "Europe/Zurich",
        )
    assert len(result) > 0

    # ahead of UTC (Europe/Zurich): out-of-range entries are trimmed
    # "1993-03-31 23:30:00 UTC" = "1993-04-01 00:30:00 Zurich" → outside end, trimmed
    with freeze_time("1993-04-02"):
        acr = acrclient.ACRClient(bearer_token)
    with requests_mock.Mocker() as mock:
        data["data"][0]["metadata"]["timestamp_utc"] = "1993-03-31 23:30:00"
        mock.get(_ACR_URL, json=data)
        result = acr.get_interval_data(
            project_id,
            stream_id,
            date(1993, 3, 1),
            date(1993, 3, 31),
            "Europe/Zurich",
        )
    assert len(result) == 0

    # behind UTC (America/Nuuk, UTC-3): entries localized to [start, end] are kept
    # "1993-03-15 12:00:00 UTC" = "1993-03-15 09:00:00 Nuuk" → kept
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(bearer_token)
    with requests_mock.Mocker() as mock:
        data["data"][0]["metadata"]["timestamp_utc"] = "1993-03-15 12:00:00"
        mock.get(_ACR_URL, json=data)
        result = acr.get_interval_data(
            project_id,
            stream_id,
            date(1993, 3, 1),
            date(1993, 3, 31),
            "America/Nuuk",
        )
    assert len(result) > 0

    # behind UTC (America/Nuuk): out-of-range entries are trimmed
    # "1993-03-01 00:00:00 UTC" = "1993-02-28 21:00:00 Nuuk" → before start, trimmed
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(bearer_token)
    with requests_mock.Mocker() as mock:
        data["data"][0]["metadata"]["timestamp_utc"] = "1993-03-01 00:00:00"
        mock.get(_ACR_URL, json=data)
        result = acr.get_interval_data(
            project_id,
            stream_id,
            date(1993, 3, 1),
            date(1993, 3, 31),
            "America/Nuuk",
        )
    assert len(result) == 0
