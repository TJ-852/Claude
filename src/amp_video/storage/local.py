"""Local file storage backend."""

import logging
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class LocalStore:
    """
    Local filesystem storage for video artifacts.

    Manages output directories and file downloads.
    """

    def __init__(self, base: Path):
        """
        Initialize local storage.

        Args:
            base: Base directory for outputs
        """
        self.base = Path(base)
        self.base.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized local storage at {self.base}")

    def get_path(self, filename: str) -> Path:
        """
        Get full path for a filename.

        Args:
            filename: Filename within base directory

        Returns:
            Full path
        """
        return self.base / filename

    async def download(self, url: str, filename: str) -> Path:
        """
        Download a file from URL to local storage.

        Args:
            url: Source URL
            filename: Destination filename

        Returns:
            Path to downloaded file

        Raises:
            httpx.HTTPError: If download fails
        """
        output_path = self.get_path(filename)
        logger.info(f"Downloading {url} to {output_path}")

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            output_path.write_bytes(response.content)

        logger.info(f"Downloaded {len(response.content)} bytes to {output_path}")
        return output_path

    def save_text(self, content: str, filename: str) -> Path:
        """
        Save text content to file.

        Args:
            content: Text content
            filename: Destination filename

        Returns:
            Path to saved file
        """
        output_path = self.get_path(filename)
        output_path.write_text(content, encoding="utf-8")
        logger.debug(f"Saved text to {output_path}")
        return output_path

    def save_json(self, data: dict | list, filename: str) -> Path:
        """
        Save JSON data to file.

        Args:
            data: JSON-serializable data
            filename: Destination filename

        Returns:
            Path to saved file
        """
        import json
        output_path = self.get_path(filename)
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info(f"Saved JSON to {output_path}")
        return output_path

    def public_url(self, path: Path) -> str:
        """
        Generate a public URL for a local file.

        Note: This returns a file:// URL for local development.
        In production, you should serve files via HTTP and return actual URLs.

        Args:
            path: File path

        Returns:
            File URL
        """
        # For local development, return file:// URL
        # In production, you'd upload to a web server and return HTTP URL
        return f"file://{path.absolute()}"

    def list_files(self, pattern: str = "*") -> list[Path]:
        """
        List files matching a pattern.

        Args:
            pattern: Glob pattern

        Returns:
            List of matching file paths
        """
        return sorted(self.base.glob(pattern))

    def cleanup(self, keep_count: int = 10):
        """
        Clean up old batch directories, keeping only recent ones.

        Args:
            keep_count: Number of recent batches to keep
        """
        # Get all timestamped directories
        dirs = sorted([d for d in self.base.iterdir() if d.is_dir()], reverse=True)

        # Remove old directories
        for old_dir in dirs[keep_count:]:
            logger.info(f"Cleaning up old batch: {old_dir}")
            for file in old_dir.glob("*"):
                file.unlink()
            old_dir.rmdir()
