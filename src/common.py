"""
common.py
通用工具方法文件。可在此添加 logger、通用校验、格式化、转换等方法。
"""

import logging
import logging.handlers

def setup_logger(name="REEFING"):
    """Configure and return a logger with syslog handler."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Remove any existing handlers
    logger.handlers = []

    # Create syslog handler
    syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
    syslog_handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter("%(name)s: %(levelname)s - %(message)s")
    syslog_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(syslog_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger

# Global logger instance
logger = setup_logger()
