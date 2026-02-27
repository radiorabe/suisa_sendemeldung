"""Pytest fixtures for suisa_sendemeldung tests."""

import pytest

from suisa_sendemeldung.settings import (
    ACR,
    IdentifierMode,
    LocalizationSettings,
    OutputMode,
    Settings,
    StationSettings,
)


@pytest.fixture
def settings():
    """Return a Settings instance for testing."""
    return Settings(
        output=OutputMode.file,
        crid_mode=IdentifierMode.cridlib,
        acr=ACR(
            bearer_token="butaisheeph6sewoo8aiDa8ieyaethoo",
            project_id=123456789,
            stream_id="123456789",
        ),
        l10n=LocalizationSettings(timezone="UTC"),
        station=StationSettings(
            name="Station Name",
            name_short="stationname",
        ),
    )
