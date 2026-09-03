"""
Kapsel logging module.
Writes structured diagnostic logs to ~/.kapsel/logs/kapsel.log.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_kapsel_dir() -> Path:
    """Return the base ~/.kapsel directory, respecting KAPSEL_HOME if set."""
    env_dir = os.environ.get("KAPSEL_HOME")
    if env_dir:
        path = Path(env_dir).expanduser().resolve()
    else:
        path = Path.home() / ".kapsel"
    path.mkdir(parents=True, exist_ok=True)
    return path


def setup_logger(name: str = "kapsel") -> logging.Logger:
    """Setup and return a sandboxed rotating file logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    log_dir = get_kapsel_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "kapsel.log"

    handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # Avoid propagating to root console by default
    logger.propagate = False
    return logger


logger = setup_logger()
