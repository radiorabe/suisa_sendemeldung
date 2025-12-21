import pytest

from suisa_sendemeldung.settings import (
    ACR,
    LocalizationSettings,
    OutputMode,
    Settings,
    StationSettings,
)


@pytest.fixture
def args():
    return Settings(
        output=OutputMode.file,
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
