"""Storage service for file operations using MinIO or S3."""

import io
import uuid
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Optional

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class StorageService:
    """Service for file storage operations using MinIO."""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Ensure the bucket exists, create if not."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            # Log error but don't fail - bucket might already exist
            print(f"Warning: Could not create bucket: {e}")

    def _generate_path(self, prefix: str, filename: str) -> str:
        """Generate a unique file path with date-based organization."""
        today = datetime.now()
        unique_id = str(uuid.uuid4())[:8]
        ext = Path(filename).suffix or ""
        return f"{prefix}/{today.year}/{today.month:02d}/{today.day:02d}/{unique_id}{ext}"

    async def upload_audio(
        self,
        file_data: BinaryIO | bytes,
        filename: str,
        content_type: str = "audio/wav",
    ) -> str:
        """Upload an audio file and return the object path."""
        object_name = self._generate_path("recordings", filename)

        if isinstance(file_data, bytes):
            file_data = io.BytesIO(file_data)

        # Get file size
        file_data.seek(0, 2)  # Seek to end
        file_size = file_data.tell()
        file_data.seek(0)  # Seek back to start

        self.client.put_object(
            self.bucket,
            object_name,
            file_data,
            file_size,
            content_type=content_type,
        )

        return object_name

    async def upload_report(
        self,
        file_data: BinaryIO | bytes,
        filename: str,
        content_type: str = "application/pdf",
    ) -> str:
        """Upload a report file and return the object path."""
        object_name = self._generate_path("reports", filename)

        if isinstance(file_data, bytes):
            file_data = io.BytesIO(file_data)

        file_data.seek(0, 2)
        file_size = file_data.tell()
        file_data.seek(0)

        self.client.put_object(
            self.bucket,
            object_name,
            file_data,
            file_size,
            content_type=content_type,
        )

        return object_name

    async def download_file(self, object_name: str) -> bytes:
        """Download a file from storage."""
        try:
            response = self.client.get_object(self.bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise FileNotFoundError(f"File not found: {object_name}") from e

    async def delete_file(self, object_name: str) -> bool:
        """Delete a file from storage."""
        try:
            self.client.remove_object(self.bucket, object_name)
            return True
        except S3Error:
            return False

    async def get_presigned_url(
        self,
        object_name: str,
        expiry_hours: int = 1,
    ) -> str:
        """Get a presigned URL for temporary access to a file."""
        from datetime import timedelta

        url = self.client.presigned_get_object(
            self.bucket,
            object_name,
            expires=timedelta(hours=expiry_hours),
        )
        return url

    async def get_file_info(self, object_name: str) -> Optional[dict]:
        """Get file metadata."""
        try:
            stat = self.client.stat_object(self.bucket, object_name)
            return {
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "etag": stat.etag,
            }
        except S3Error:
            return None


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get the storage service singleton."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
