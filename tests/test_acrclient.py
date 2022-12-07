"""Tests for the ACR client module."""
from datetime import date

import requests_mock
from freezegun import freeze_time

from suisa_sendemeldung import acrclient


def test_init():
    """Test ACRClient.__init__."""
    access_key = "secret-key"
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(access_key)

    assert acr.access_key == access_key
    assert acr.default_date == date(1993, 3, 1)


def test_get_data():
    """Test ACRClient.get_data."""
    access_key = "secret-key"
    stream_id = "stream-id"
    data = [{"metadata": {"timestamp_utc": "1993-03-01 13:12:00"}}]
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(access_key)
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://api.acrcloud.com/v1/monitor-streams/stream-id/results", json=data
        )
        acr.get_data(stream_id)


def test_get_interval_data():
    """Test ACRClient.get_interval_data."""
    access_key = "secret-key"
    stream_id = "stream-id"
    data = [{"metadata": {"timestamp_utc": "1993-03-01 13:12:00"}}]

    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(access_key)
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://api.acrcloud.com/v1/monitor-streams/stream-id/results", json=data
        )
        acr.get_interval_data(stream_id, date(1993, 3, 1), date(1993, 3, 31))

    # ahead of UTC
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(access_key)
    with requests_mock.Mocker() as mock:
        data[0]["metadata"]["timestamp_utc"] = "1993-03-01 00:00:00"
        mock.get(
            "https://api.acrcloud.com/v1/monitor-streams/stream-id/results", json=data
        )
        acr.get_interval_data(
            stream_id, date(1993, 3, 1), date(1993, 3, 31), "Europe/Zurich"
        )

    # behind UTC
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(access_key)
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://api.acrcloud.com/v1/monitor-streams/stream-id/results", json=data
        )
        acr.get_interval_data(
            stream_id, date(1993, 3, 1), date(1993, 3, 31), "America/Nuuk"
        )
