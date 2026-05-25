import logging

from sbdots.library.logger import (
    LogLevel,
    setup_logging,
    get_caller_logger,
)


class TestLogger:
    """Tests for logger module"""

    def test_log_level_enum_values(self):
        """Test LogLevel enum has correct values"""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"

    def test_setup_logging_with_name(self):
        """Test setup_logging creates a logger with given name"""
        setup_logging("test_logger")
        logger = logging.getLogger("test_logger")
        assert logger.name == "test_logger"
        assert isinstance(logger, logging.Logger)

    def test_get_caller_logger_returns_logger(self):
        """Test get_caller_logger returns a logger instance"""
        logger = get_caller_logger()
        assert isinstance(logger, logging.Logger)
