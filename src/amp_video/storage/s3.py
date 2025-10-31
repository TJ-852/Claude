"""S3 cloud storage backend."""

import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class S3Store:
    """
    AWS S3 storage for video artifacts.

    Uploads files to S3 and generates signed URLs.
    """

    def __init__(
        self,
        bucket_url: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region: str = "us-east-1"
    ):
        """
        Initialize S3 storage.

        Args:
            bucket_url: S3 bucket URL (e.g., s3://bucket-name)
            aws_access_key_id: AWS access key
            aws_secret_access_key: AWS secret key
            region: AWS region

        Raises:
            ImportError: If boto3 is not installed
        """
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 is required for S3 storage. Install with: pip install boto3"
            )

        # Parse bucket name from URL
        parsed = urlparse(bucket_url)
        if parsed.scheme != "s3":
            raise ValueError(f"Invalid S3 URL: {bucket_url}. Expected format: s3://bucket-name")

        self.bucket_name = parsed.netloc
        self.prefix = parsed.path.lstrip("/")

        # Initialize S3 client
        session_kwargs = {"region_name": region}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = aws_access_key_id
            session_kwargs["aws_secret_access_key"] = aws_secret_access_key

        self.s3_client = boto3.client("s3", **session_kwargs)
        logger.info(f"Initialized S3 storage: {self.bucket_name}/{self.prefix}")

    def upload_file(self, local_path: Path, key: Optional[str] = None) -> str:
        """
        Upload a file to S3.

        Args:
            local_path: Path to local file
            key: S3 object key (defaults to filename with prefix)

        Returns:
            S3 object key

        Raises:
            Exception: If upload fails
        """
        if key is None:
            key = f"{self.prefix}/{local_path.name}" if self.prefix else local_path.name

        logger.info(f"Uploading {local_path} to s3://{self.bucket_name}/{key}")

        # Determine content type based on extension
        content_type = self._get_content_type(local_path)

        self.s3_client.upload_file(
            str(local_path),
            self.bucket_name,
            key,
            ExtraArgs={"ContentType": content_type}
        )

        logger.info(f"Uploaded to s3://{self.bucket_name}/{key}")
        return key

    def upload_directory(self, local_dir: Path, prefix: Optional[str] = None) -> list[str]:
        """
        Upload all files in a directory to S3.

        Args:
            local_dir: Local directory path
            prefix: S3 prefix for uploaded files

        Returns:
            List of uploaded S3 keys
        """
        uploaded_keys = []

        for file_path in local_dir.rglob("*"):
            if file_path.is_file():
                # Compute relative path for S3 key
                rel_path = file_path.relative_to(local_dir)
                if prefix:
                    key = f"{prefix}/{rel_path}"
                elif self.prefix:
                    key = f"{self.prefix}/{rel_path}"
                else:
                    key = str(rel_path)

                self.upload_file(file_path, key)
                uploaded_keys.append(key)

        logger.info(f"Uploaded {len(uploaded_keys)} files from {local_dir}")
        return uploaded_keys

    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for an S3 object.

        Args:
            key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)

        Returns:
            Presigned URL
        """
        url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expiration
        )
        logger.debug(f"Generated presigned URL for {key}")
        return url

    def get_public_url(self, key: str) -> str:
        """
        Get public URL for an S3 object (requires public bucket).

        Args:
            key: S3 object key

        Returns:
            Public URL
        """
        return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"

    def delete_file(self, key: str):
        """
        Delete a file from S3.

        Args:
            key: S3 object key
        """
        logger.info(f"Deleting s3://{self.bucket_name}/{key}")
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)

    def list_objects(self, prefix: Optional[str] = None) -> list[str]:
        """
        List objects in the bucket.

        Args:
            prefix: Filter by prefix

        Returns:
            List of object keys
        """
        search_prefix = prefix or self.prefix
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=search_prefix
        )

        if "Contents" not in response:
            return []

        return [obj["Key"] for obj in response["Contents"]]

    @staticmethod
    def _get_content_type(path: Path) -> str:
        """
        Determine content type from file extension.

        Args:
            path: File path

        Returns:
            MIME type string
        """
        extension = path.suffix.lower()
        content_types = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".json": "application/json",
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }
        return content_types.get(extension, "application/octet-stream")
