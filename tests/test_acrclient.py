"""Tests for the ACR client module."""
from datetime import date

import requests_mock
from freezegun import freeze_time

from suisa_sendemeldung import acrclient

_MINIO_RAW_URL = "http://minio.example.com/acrcloud.raw/"


def test_init():
    """Test ACRClient.__init__."""
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(minio_url=_MINIO_RAW_URL)

    assert acr.default_date == date(1993, 3, 1)


def test_get_data():
    """Test ACRClient.get_data."""
    data = [{"metadata": {"timestamp_utc": "1993-03-01 13:12:00"}}]
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(minio_url=_MINIO_RAW_URL)
    with requests_mock.Mocker() as mock:
        mock.get(
            f"{_MINIO_RAW_URL}1993-03-01.json",
            json=data,
        )
        acr.get_data()


def test_get_interval_data():
    """Test ACRClient.get_interval_data."""
    data = [{"metadata": {"timestamp_utc": "1993-03-01 13:12:00"}}]

    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(minio_url=_MINIO_RAW_URL)
    with requests_mock.Mocker() as mock:
        mock.get(
            requests_mock.ANY,
            json=data,
        )
        acr.get_interval_data(date(1993, 3, 1), date(1993, 3, 31))

    # ahead of UTC
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(minio_url=_MINIO_RAW_URL, timezone="Europe/Zurich")
    with requests_mock.Mocker() as mock:
        data[0]["metadata"]["timestamp_utc"] = "1993-03-01 00:00:00"
        mock.get(
            requests_mock.ANY,
            json=data,
        )
        acr.get_interval_data(date(1993, 3, 1), date(1993, 3, 31))

    # behind UTC
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(minio_url=_MINIO_RAW_URL, timezone="America/Nuuk")
    with requests_mock.Mocker() as mock:
        mock.get(
            requests_mock.ANY,
            json=data,
        )
        acr.get_interval_data(date(1993, 3, 1), date(1993, 3, 31))
