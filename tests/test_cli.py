from manufacturing_stock_tracker.cli import DEFAULT_SYMBOLS, selected_symbols


def test_selected_symbols_uses_single_symbol_when_provided() -> None:
    assert selected_symbols("cat", DEFAULT_SYMBOLS) == ["CAT"]


def test_selected_symbols_uses_watchlist_when_single_symbol_missing() -> None:
    assert selected_symbols(None, "cat,de,hon") == ["CAT", "DE", "HON"]


def test_default_symbols_are_manufacturing_watchlist() -> None:
    assert DEFAULT_SYMBOLS == "CAT,DE,HON,GE,MMM"
