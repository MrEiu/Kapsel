"""
Kapsel logging module.
Writes structured diagnostic logs to ~/.kapsel/logs/kapsel.log.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


POINTER_FILE = Path.home() / ".kapsel_location"


def get_default_kapsel_dir() -> Path:
    return Path.home() / ".kapsel"


def get_kapsel_dir() -> Path:
    """
    Return the base data storage directory.
    Resolution priority:
      1. os.environ['KAPSEL_HOME'] (Explicit environment variable override)
      2. ~/.kapsel_location (Persistent custom data location pointer file)
      3. Default: ~/.kapsel
    """
    env_dir = os.environ.get("KAPSEL_HOME")
    if env_dir:
        path = Path(env_dir).expanduser().resolve()
    elif POINTER_FILE.exists():
        try:
            custom_path = POINTER_FILE.read_text(encoding="utf-8").strip()
            if custom_path:
                path = Path(custom_path).expanduser().resolve()
            else:
                path = get_default_kapsel_dir()
        except Exception:
            path = get_default_kapsel_dir()
    else:
        path = get_default_kapsel_dir()

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
