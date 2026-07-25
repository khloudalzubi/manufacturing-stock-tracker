import logging
import sys
from pathlib import Path


LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
PACKAGE_LOGGER_NAME = "manufacturing_stock_tracker"


class LoggingSetupError(RuntimeError):
    """Raised when the requested logging destination cannot be created."""


def configure_logging(level: str = "INFO", log_file: str | None = None) -> None:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    package_logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    _reset_handlers(package_logger)

    package_logger.setLevel(logging.DEBUG)
    package_logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    package_logger.addHandler(console_handler)

    if log_file:
        path = Path(log_file)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(path, encoding="utf-8")
        except OSError as exc:
            raise LoggingSetupError(f"Could not open log file {path}: {exc}") from exc

        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        package_logger.addHandler(file_handler)

    # Third-party HTTP debug logs can include full URLs with query parameters.
    # Keep them quieter so API keys never appear in console or file logs.
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def _reset_handlers(logger: logging.Logger) -> None:
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
