import logging
import sys


def setup_logger(name: str = "Pixerse-LP", level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger instance for local development.
    Logs will be printed to stdout with format:
    [2025-09-25 12:34:56] INFO     core.services.mcp.chatbot_service:42 | Message
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)-7s %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False

    return logger


# Global logger instance
logger = setup_logger()