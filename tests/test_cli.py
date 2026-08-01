import pytest

from manufacturing_stock_tracker._version import __version__
from manufacturing_stock_tracker.cli import DEFAULT_SYMBOLS, build_parser, selected_symbols


def test_selected_symbols_uses_single_symbol_when_provided() -> None:
    assert selected_symbols("cat", DEFAULT_SYMBOLS) == ["CAT"]


def test_selected_symbols_uses_watchlist_when_single_symbol_missing() -> None:
    assert selected_symbols(None, "cat,de,hon") == ["CAT", "DE", "HON"]


def test_default_symbols_are_manufacturing_watchlist() -> None:
    assert DEFAULT_SYMBOLS == "CAT,DE,HON,GE,MMM"


def test_version_option_prints_package_version(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["--version"])

    assert exc_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_parser_accepts_database_save_options() -> None:
    args = build_parser().parse_args(["--save-db", "--db-path", "data/custom.db"])

    assert args.save_db is True
    assert args.db_path == "data/custom.db"