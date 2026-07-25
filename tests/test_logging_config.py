import logging

from manufacturing_stock_tracker.logging_config import configure_logging


def test_configure_logging_writes_project_logs_to_file(tmp_path) -> None:
    log_file = tmp_path / "tracker.log"
    configure_logging("DEBUG", str(log_file))

    logger = logging.getLogger("manufacturing_stock_tracker.tests")
    logger.info("test log message")

    contents = log_file.read_text(encoding="utf-8")
    assert "test log message" in contents
    assert "INFO" in contents


def test_configure_logging_scopes_logs_to_project_logger() -> None:
    configure_logging("DEBUG")

    package_logger = logging.getLogger("manufacturing_stock_tracker")
    assert package_logger.propagate is False
    assert package_logger.handlers


def test_configure_logging_keeps_http_client_logs_quiet() -> None:
    configure_logging("DEBUG")

    assert logging.getLogger("urllib3").level == logging.WARNING
    assert logging.getLogger("requests").level == logging.WARNING
