import pytest
from configargparse import ArgumentParser  # type: ignore[import-untyped]

from suisa_sendemeldung.suisa_sendemeldung import get_arguments


@pytest.fixture
def args():
    return get_arguments(
        ArgumentParser(),
        [
            "--bearer-token=butaisheeph6sewoo8aiDa8ieyaethoo",
            "--project-id=123456789",
            "--stream-id=123456789",
            "--timezone=UTC",
            "--file",
            "--station-name=Station Name",
        ],
    )
