"""Public package entry point for the Manufacturing Stock Tracker CLI."""

from manufacturing_stock_tracker._version import __version__
from manufacturing_stock_tracker.cli import main

__all__ = ["__version__", "main"]
