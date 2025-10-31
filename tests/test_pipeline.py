"""Tests for pipeline functionality."""

import pytest
from pathlib import Path

from amp_video.models import Job, JobResult, BatchManifest


class TestModels:
    """Test Pydantic models."""

    def test_job_model(self):
        """Test Job model creation."""
        job = Job(
            id="001",
            name="Alice",
            language="English",
            voice="Rachel",
            avatar="SantaFe_v2",
            script="Hello Alice!",
            variables={"product": "TestProd"}
        )

        assert job.id == "001"
        assert job.name == "Alice"
        assert job.variables["product"] == "TestProd"

    def test_job_model_defaults(self):
        """Test Job model with defaults."""
        job = Job(
            id="001",
            name="Alice",
            language="English"
        )

        assert job.voice is None
        assert job.avatar is None
        assert job.variables == {}

    def test_job_result_success(self):
        """Test JobResult for successful job."""
        result = JobResult(
            id="001",
            status="ok",
            tts_path="/path/to/tts.mp3",
            video_path="/path/to/video.mp4",
            meta={"duration": 30}
        )

        assert result.status == "ok"
        assert result.error is None
        assert result.meta["duration"] == 30

    def test_job_result_error(self):
        """Test JobResult for failed job."""
        result = JobResult(
            id="001",
            status="error",
            error="API rate limit exceeded"
        )

        assert result.status == "error"
        assert result.error is not None
        assert result.tts_path is None

    def test_batch_manifest(self):
        """Test BatchManifest model."""
        manifest = BatchManifest(
            tag="test-batch",
            timestamp="2025-10-31T14-30-45Z",
            results=[
                JobResult(id="001", status="ok", tts_path="/path/to/001.mp3"),
                JobResult(id="002", status="error", error="Failed")
            ]
        )

        assert manifest.tag == "test-batch"
        assert len(manifest.results) == 2
        assert manifest.results[0].status == "ok"
        assert manifest.results[1].status == "error"


class TestPipelineHelpers:
    """Test pipeline helper functions."""

    def test_timestamp_format(self):
        """Test timestamp format."""
        from amp_video.utils import get_timestamp

        timestamp = get_timestamp()

        # Should match format: 2025-10-31T14-30-45Z
        assert len(timestamp) == 20
        assert timestamp.endswith("Z")
        assert "T" in timestamp

    def test_format_duration(self):
        """Test duration formatting."""
        from amp_video.utils import format_duration

        assert format_duration(30.5) == "30.5s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(125.7) == "2m 6s"

    def test_safe_filename(self):
        """Test safe filename generation."""
        from amp_video.utils import safe_filename

        assert safe_filename("Hello World!") == "Hello_World"
        assert safe_filename("test@#$%file.txt") == "test_file.txt"
        assert safe_filename("file___name") == "file_name"
