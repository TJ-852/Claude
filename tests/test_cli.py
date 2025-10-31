"""Tests for CLI functionality."""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from amp_video.cli import app, load_jobs
from amp_video.models import Job

runner = CliRunner()


class TestLoadJobs:
    """Test job loading from CSV."""

    def test_load_jobs_from_csv(self, tmp_path):
        """Test loading jobs from a valid CSV file."""
        csv_content = """id,name,language,voice,avatar,script,variables
001,Alice,English,Rachel,SantaFe_v2,"Hello Alice","{}"
002,Bob,Spanish,Carlos,SantaFe_v2,"Hola Bob","{}"
"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        jobs = load_jobs(csv_file)

        assert len(jobs) == 2
        assert jobs[0].id == "001"
        assert jobs[0].name == "Alice"
        assert jobs[0].language == "English"
        assert jobs[0].voice == "Rachel"
        assert jobs[1].id == "002"

    def test_load_jobs_with_variables(self, tmp_path):
        """Test loading jobs with JSON variables."""
        csv_content = """id,name,language,voice,avatar,script,variables
001,Alice,English,Rachel,SantaFe_v2,"Hello","{""product"":""TestProd""}"
"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        jobs = load_jobs(csv_file)

        assert len(jobs) == 1
        assert jobs[0].variables == {"product": "TestProd"}

    def test_load_jobs_missing_file(self):
        """Test loading from non-existent CSV file."""
        with pytest.raises(SystemExit):
            load_jobs(Path("nonexistent.csv"))


class TestRenderCommand:
    """Test the render command."""

    def test_render_basic(self, tmp_path):
        """Test basic render command."""
        csv_content = """id,name,language,voice,avatar,script,variables
001,Alice,English,Rachel,SantaFe_v2,"Hello Alice!","{}"
"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        out_dir = tmp_path / "preview"

        result = runner.invoke(app, ["render", str(csv_file), "--out", str(out_dir)])

        assert result.exit_code == 0
        assert out_dir.exists()
        assert (out_dir / "001.txt").exists()
        assert (out_dir / "001.txt").read_text() == "Hello Alice!"


class TestVersionCommand:
    """Test the version command."""

    def test_version(self):
        """Test version command output."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "AMP Video Automation Toolkit" in result.output
