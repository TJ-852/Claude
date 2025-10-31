"""Utility functions for logging, time formatting, and hashing."""

import hashlib
import logging
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

console = Console()


def setup_logging(log_level: str = "INFO", log_file: Path | None = None) -> logging.Logger:
    """
    Configure logging with rich console output and optional file logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file

    Returns:
        Configured logger instance
    """
    handlers: list[logging.Handler] = [
        RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True
        )
    ]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=handlers
    )

    return logging.getLogger("amp_video")


def get_timestamp() -> str:
    """
    Get current UTC timestamp in ISO format.

    Returns:
        Timestamp string like "2025-10-31T14-30-45Z"
    """
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())


def hash_content(content: str | bytes) -> str:
    """
    Generate SHA256 hash of content.

    Args:
        content: String or bytes to hash

    Returns:
        Hexadecimal hash string
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "1m 23s" or "45s"
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}m {remaining_seconds:.0f}s"


def format_size(bytes_size: int) -> str:
    """
    Format file size in bytes to human-readable string.

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted string like "1.5 MB" or "342 KB"
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def safe_filename(text: str, max_length: int = 200) -> str:
    """
    Convert text to safe filename by removing special characters.

    Args:
        text: Input text
        max_length: Maximum filename length

    Returns:
        Safe filename string
    """
    # Replace unsafe characters
    safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text)
    # Remove consecutive underscores
    while "__" in safe:
        safe = safe.replace("__", "_")
    # Trim to max length
    return safe[:max_length].strip("_")
