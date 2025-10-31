"""Pydantic models for job configuration and artifacts."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Job(BaseModel):
    """Represents a single video generation job."""

    id: str
    name: str
    language: str
    voice: Optional[str] = None
    avatar: Optional[str] = None
    script: Optional[str] = None
    variables: Dict[str, str] = Field(default_factory=dict)

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "001",
                "name": "Tariq",
                "language": "English",
                "voice": "Rachel",
                "avatar": "SantaFe_v2",
                "script": "Hello {{name}}, welcome to {{product}}!",
                "variables": {"product": "OnboardIQ"}
            }
        }


class Artifact(BaseModel):
    """Represents the output artifacts from a completed job."""

    tts_path: Optional[str] = None
    video_path: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "tts_path": "output/2025-10-31T14-30-45Z/001_tts.mp3",
                "video_path": "output/2025-10-31T14-30-45Z/001_video.mp4",
                "meta": {
                    "video_url": "https://heygen.com/v/abc123",
                    "duration_sec": 42.5,
                    "cost_usd": 0.15
                }
            }
        }


class JobResult(BaseModel):
    """Represents the result of a job execution."""

    id: str
    status: str  # "ok" or "error"
    tts_path: Optional[str] = None
    video_path: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "001",
                "status": "ok",
                "tts_path": "output/2025-10-31T14-30-45Z/001_tts.mp3",
                "video_path": "output/2025-10-31T14-30-45Z/001_video.mp4",
                "meta": {"video_url": "https://heygen.com/v/abc123"}
            }
        }


class BatchManifest(BaseModel):
    """Represents a complete batch execution manifest."""

    tag: str
    timestamp: str
    results: list[JobResult] = Field(default_factory=list)

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "tag": "sunlife-pilot-batch-1",
                "timestamp": "2025-10-31T14:30:45Z",
                "results": [
                    {
                        "id": "001",
                        "status": "ok",
                        "tts_path": "output/2025-10-31T14-30-45Z/001_tts.mp3",
                        "video_path": "output/2025-10-31T14-30-45Z/001_video.mp4"
                    }
                ]
            }
        }
