"""Command-line interface using Typer."""

import asyncio
import csv
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from jinja2 import Template, TemplateError
from rich.console import Console

from .config import settings
from .models import Job
from .pipeline import run_batch, resume_batch
from .utils import setup_logging

app = typer.Typer(
    name="amp-video",
    help="AMP Video Automation Toolkit - Batch video generation with TTS and AI avatars",
    add_completion=False
)
console = Console()


def load_jobs(csv_path: Path) -> list[Job]:
    """
    Load jobs from CSV file.

    Args:
        csv_path: Path to CSV file

    Returns:
        List of Job objects

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV is malformed
    """
    if not csv_path.exists():
        console.print(f"[red]Error: CSV file not found: {csv_path}[/red]")
        raise typer.Exit(1)

    jobs = []
    template_path = Path("data/templates/script.j2")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            console.print(f"[red]Error: CSV file is empty or malformed[/red]")
            raise typer.Exit(1)

        # Validate required columns
        required = {"id", "name", "language"}
        missing = required - set(reader.fieldnames)
        if missing:
            console.print(f"[red]Error: Missing required columns: {missing}[/red]")
            raise typer.Exit(1)

        for row_num, row in enumerate(reader, start=2):
            try:
                # Parse variables JSON
                variables_str = row.get("variables", "{}")
                try:
                    variables = json.loads(variables_str) if variables_str else {}
                except json.JSONDecodeError as e:
                    console.print(f"[yellow]Warning: Row {row_num} has invalid JSON in variables, using empty dict[/yellow]")
                    variables = {}

                # Determine script
                script = row.get("script", "").strip()

                if not script and template_path.exists():
                    # Render from template
                    try:
                        template = Template(template_path.read_text())
                        script = template.render(**variables, name=row["name"])
                    except TemplateError as e:
                        console.print(f"[yellow]Warning: Row {row_num} template error: {e}[/yellow]")
                        script = f"Hello {row['name']}"

                elif not script:
                    # No script and no template, use default
                    script = f"Hello {row['name']}, welcome!"

                # Create job
                job = Job(
                    id=row["id"],
                    name=row["name"],
                    language=row["language"],
                    voice=row.get("voice") or None,
                    avatar=row.get("avatar") or None,
                    script=script,
                    variables=variables
                )
                jobs.append(job)

            except Exception as e:
                console.print(f"[red]Error processing row {row_num}: {e}[/red]")
                raise typer.Exit(1)

    if not jobs:
        console.print("[yellow]Warning: No jobs loaded from CSV[/yellow]")

    return jobs


@app.command()
def render(
    csv_path: str = typer.Argument(..., help="Path to input CSV file"),
    out: str = typer.Option("output/preview", help="Output directory for preview"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """
    Render scripts from CSV (dry run, no API calls).

    Validates CSV and templates, writes rendered scripts to output directory.
    """
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)

    csv_file = Path(csv_path)
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold cyan]Rendering Scripts[/bold cyan]")
    console.print(f"Input: {csv_file}")
    console.print(f"Output: {out_dir}\n")

    try:
        jobs = load_jobs(csv_file)
        console.print(f"Loaded {len(jobs)} jobs\n")

        for job in jobs:
            script_file = out_dir / f"{job.id}.txt"
            script_file.write_text(job.script or "", encoding="utf-8")
            console.print(f"[green]✓[/green] {job.id} → {script_file.name}")

        console.print(f"\n[bold green]Rendered {len(jobs)} scripts to {out_dir}[/bold green]\n")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        raise typer.Exit(1)


@app.command()
def run(
    csv_path: str = typer.Argument(..., help="Path to input CSV file"),
    concurrency: int = typer.Option(3, "--concurrency", "-c", help="Maximum concurrent jobs"),
    tag: str = typer.Option("default", "--tag", "-t", help="Batch tag for identification"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    no_progress: bool = typer.Option(False, "--no-progress", help="Disable progress bar")
):
    """
    Run full video generation pipeline (TTS → Avatar → Export).

    Processes all jobs in the CSV file and creates timestamped output directory.
    """
    log_level = "DEBUG" if verbose else "INFO"
    log_file = Path("output") / "pipeline.log"
    setup_logging(log_level, log_file)

    csv_file = Path(csv_path)

    try:
        jobs = load_jobs(csv_file)

        if not jobs:
            console.print("[yellow]No jobs to process[/yellow]")
            raise typer.Exit(0)

        # Run batch
        out_dir = asyncio.run(
            run_batch(
                jobs=jobs,
                tag=tag,
                concurrency=concurrency,
                show_progress=not no_progress
            )
        )

        console.print(f"[green]✓ Batch complete: {out_dir}[/green]\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]\n")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        raise typer.Exit(1)


@app.command()
def resume(
    manifest: str = typer.Argument(..., help="Path to manifest.json from previous run"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """
    Resume a batch by retrying failed jobs.

    Reads manifest.json and re-processes jobs with "status": "error".
    """
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)

    manifest_path = Path(manifest)

    if not manifest_path.exists():
        console.print(f"[red]Error: Manifest not found: {manifest_path}[/red]")
        raise typer.Exit(1)

    try:
        asyncio.run(resume_batch(manifest_path))
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        raise typer.Exit(1)


@app.command()
def export(
    manifest: str = typer.Argument(..., help="Path to manifest.json"),
    dest: str = typer.Option("s3", "--dest", "-d", help="Export destination (s3)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """
    Export batch outputs to cloud storage (S3).

    Uploads all files from the batch directory to configured S3 bucket.
    """
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)

    manifest_path = Path(manifest)

    if not manifest_path.exists():
        console.print(f"[red]Error: Manifest not found: {manifest_path}[/red]")
        raise typer.Exit(1)

    if dest != "s3":
        console.print(f"[red]Error: Unsupported destination: {dest}[/red]")
        raise typer.Exit(1)

    if not settings.output_bucket:
        console.print("[red]Error: OUTPUT_BUCKET not configured in .env[/red]")
        raise typer.Exit(1)

    try:
        from .storage.s3 import S3Store

        s3 = S3Store(
            bucket_url=settings.output_bucket,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region=settings.aws_default_region
        )

        batch_dir = manifest_path.parent
        console.print(f"\n[cyan]Exporting {batch_dir} to S3...[/cyan]\n")

        keys = s3.upload_directory(batch_dir, prefix=batch_dir.name)

        console.print(f"\n[green]✓ Exported {len(keys)} files to {settings.output_bucket}[/green]\n")

    except ImportError:
        console.print("[red]Error: boto3 not installed. Install with: pip install boto3[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"AMP Video Automation Toolkit v{__version__}")


if __name__ == "__main__":
    app()
