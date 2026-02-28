"""End-to-end tests verifying that the MkDocs documentation builds correctly."""

import pathlib

import pytest
from mkdocs.commands.build import build as mkdocs_build
from mkdocs.config import load_config

_ROOT = pathlib.Path(__file__).parent.parent


@pytest.fixture(scope="session")
def site(tmp_path_factory):
    """Build the MkDocs site once for the whole test session."""
    site_dir = tmp_path_factory.mktemp("site")
    cfg = load_config(config_file=str(_ROOT / "mkdocs.yml"), site_dir=str(site_dir))
    mkdocs_build(cfg)
    return site_dir


def test_home_page_contains_headline(site):
    assert "SUISA Sendemeldung" in (site / "index.html").read_text(encoding="utf-8")


def test_getting_started_recommends_podman(site):
    html = (site / "getting-started" / "index.html").read_text(encoding="utf-8")
    assert "podman" in html


def test_configuration_page_exists(site):
    assert "TOML" in (site / "configuration" / "index.html").read_text(encoding="utf-8")


def test_deployment_recommends_podman(site):
    assert "podman" in (site / "deployment" / "index.html").read_text(encoding="utf-8")


def test_development_page_mentions_pytest(site):
    assert "pytest" in (site / "development" / "index.html").read_text(encoding="utf-8")


def test_upgrading_page_exists(site):
    html = (site / "upgrading" / "index.html").read_text(encoding="utf-8")
    assert "Upgrading" in html


def test_api_reference_is_generated(site):
    assert (site / "reference" / "suisa_sendemeldung" / "index.html").is_file()
