import tomllib
from pathlib import Path

from manufacturing_stock_tracker._version import __version__


PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def project_metadata() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]


def test_package_version_matches_shared_version() -> None:
    assert project_metadata()["version"] == __version__


def test_package_metadata_includes_release_context() -> None:
    metadata = project_metadata()

    assert metadata["license"] == "MIT"
    assert "manufacturing" in metadata["keywords"]
    assert metadata["urls"]["Repository"].endswith("manufacturing-stock-tracker")
