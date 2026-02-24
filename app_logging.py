from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

_INITIALIZED = False
_LOG_FILE: Path | None = None


def get_runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_log_file_path() -> Path:
    global _LOG_FILE
    if _LOG_FILE is None:
        log_dir = get_runtime_root() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        _LOG_FILE = log_dir / "vediozip.log"
    return _LOG_FILE


def setup_logging() -> Path:
    global _INITIALIZED
    if _INITIALIZED:
        return get_log_file_path()

    log_file = get_log_file_path()
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    if getattr(sys, "stderr", None) is not None and hasattr(sys.stderr, "write"):
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(formatter)
        root.addHandler(stream_handler)

    _INITIALIZED = True
    root.info("Logging initialized. log_file=%s", log_file)
    return log_file


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
