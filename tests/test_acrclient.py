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


def test_get_interval_data():
    """Test ACRClient.get_interval_data."""
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
        acr.get_interval_data(
            project_id, stream_id, date(1993, 3, 1), date(1993, 3, 31)
        )

    # ahead of UTC
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(bearer_token)
    with requests_mock.Mocker() as mock:
        data["data"][0]["metadata"]["timestamp_utc"] = "1993-03-01 00:00:00"
        mock.get(
            _ACR_URL,
            json=data,
        )
        acr.get_interval_data(
            project_id, stream_id, date(1993, 3, 1), date(1993, 3, 31), "Europe/Zurich"
        )

    # behind UTC
    with freeze_time("1993-03-02"):
        acr = acrclient.ACRClient(bearer_token)
    with requests_mock.Mocker() as mock:
        mock.get(
            _ACR_URL,
            json=data,
        )
        acr.get_interval_data(
            project_id, stream_id, date(1993, 3, 1), date(1993, 3, 31), "America/Nuuk"
        )
