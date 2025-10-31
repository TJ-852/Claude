"""Video generation pipeline orchestrator."""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from .config import settings
from .models import Job, Artifact, JobResult, BatchManifest
from .providers.heygen import HeyGenClient
from .providers.elevenlabs import ElevenLabsTTS
from .providers.errors import ProviderError
from .storage.local import LocalStore
from .utils import get_timestamp, format_duration

logger = logging.getLogger(__name__)
console = Console()


async def process_job(
    job: Job,
    out_dir: Path,
    progress: Optional[Progress] = None,
    task_id: Optional[int] = None
) -> JobResult:
    """
    Process a single video generation job.

    Executes: TTS → Avatar Video → Download

    Args:
        job: Job configuration
        out_dir: Output directory for artifacts
        progress: Optional Rich progress tracker
        task_id: Optional progress task ID

    Returns:
        JobResult with status and artifact paths
    """
    try:
        store = LocalStore(base=out_dir)
        voice = job.voice or settings.default_voice
        avatar = job.avatar or settings.default_avatar

        if progress and task_id is not None:
            progress.update(task_id, description=f"[cyan]{job.id}[/cyan] → TTS")

        # Step 1: Generate TTS audio
        logger.info(f"Job {job.id}: Generating TTS with voice {voice}")
        tts = ElevenLabsTTS(
            api_key=settings.elevenlabs_api_key,
            voice=voice
        )
        tts_path = await tts.synth(
            text=job.script or "",
            language=job.language,
            name=job.id,
            output_dir=out_dir
        )
        await tts.close()

        if progress and task_id is not None:
            progress.update(task_id, description=f"[cyan]{job.id}[/cyan] → Avatar video")

        # Step 2: Create avatar video
        logger.info(f"Job {job.id}: Creating HeyGen video with avatar {avatar}")
        heygen = HeyGenClient(api_key=settings.heygen_api_key)

        # For HeyGen, we need a publicly accessible URL
        # In production, upload to S3 first. For now, use file path
        voice_url = store.public_url(tts_path)

        video_id = await heygen.create_video(
            voice_url=voice_url,
            avatar=avatar,
            script=job.script or "",
            language=job.language
        )

        if progress and task_id is not None:
            progress.update(task_id, description=f"[cyan]{job.id}[/cyan] → Polling video")

        # Step 3: Poll for completion
        logger.info(f"Job {job.id}: Polling video {video_id}")
        video_url = await heygen.poll_video(video_id)

        if progress and task_id is not None:
            progress.update(task_id, description=f"[cyan]{job.id}[/cyan] → Downloading")

        # Step 4: Download video
        logger.info(f"Job {job.id}: Downloading video from {video_url}")
        video_path = await store.download(video_url, f"{job.id}_video.mp4")
        await heygen.close()

        if progress and task_id is not None:
            progress.update(task_id, description=f"[green]✓[/green] {job.id}", completed=100)

        # Success
        result = JobResult(
            id=job.id,
            status="ok",
            tts_path=str(tts_path),
            video_path=str(video_path),
            meta={
                "video_url": video_url,
                "voice": voice,
                "avatar": avatar,
                "language": job.language
            }
        )
        logger.info(f"Job {job.id}: Completed successfully")
        return result

    except ProviderError as e:
        logger.error(f"Job {job.id}: Provider error - {e}")
        if progress and task_id is not None:
            progress.update(task_id, description=f"[red]✗[/red] {job.id} (error)", completed=100)
        return JobResult(
            id=job.id,
            status="error",
            error=f"{e.provider or 'Provider'} error: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Job {job.id}: Unexpected error - {e}", exc_info=True)
        if progress and task_id is not None:
            progress.update(task_id, description=f"[red]✗[/red] {job.id} (error)", completed=100)
        return JobResult(
            id=job.id,
            status="error",
            error=str(e)
        )


async def run_batch(
    jobs: list[Job],
    tag: str = "default",
    concurrency: int = 3,
    show_progress: bool = True
) -> Path:
    """
    Run a batch of video generation jobs.

    Args:
        jobs: List of jobs to process
        tag: Batch tag for identification
        concurrency: Maximum concurrent jobs
        show_progress: Show rich progress bar

    Returns:
        Path to output directory containing manifest
    """
    start_time = time.time()
    timestamp = get_timestamp()
    out_dir = Path("output") / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting batch '{tag}' with {len(jobs)} jobs (concurrency={concurrency})")
    console.print(f"\n[bold cyan]AMP Video Automation Batch: {tag}[/bold cyan]")
    console.print(f"Output directory: {out_dir}")
    console.print(f"Jobs: {len(jobs)} | Concurrency: {concurrency}\n")

    sem = asyncio.Semaphore(concurrency)
    results: list[JobResult] = []

    if show_progress:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        )
    else:
        progress = None

    async def worker(j: Job, prog: Optional[Progress] = None):
        """Worker function to process a single job."""
        async with sem:
            if prog:
                task_id = prog.add_task(f"[cyan]{j.id}[/cyan]", total=100)
                result = await process_job(j, out_dir, progress=prog, task_id=task_id)
            else:
                result = await process_job(j, out_dir)
            results.append(result)

    # Run all jobs
    if progress:
        with progress:
            await asyncio.gather(*(worker(j, progress) for j in jobs))
    else:
        await asyncio.gather(*(worker(j) for j in jobs))

    # Create manifest
    manifest = BatchManifest(
        tag=tag,
        timestamp=timestamp,
        results=results
    )

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")

    # Summary
    elapsed = time.time() - start_time
    success_count = sum(1 for r in results if r.status == "ok")
    error_count = len(results) - success_count

    console.print(f"\n[bold green]Batch Complete![/bold green]")
    console.print(f"Duration: {format_duration(elapsed)}")
    console.print(f"Success: [green]{success_count}[/green] | Errors: [red]{error_count}[/red]")
    console.print(f"Manifest: {manifest_path}\n")

    logger.info(f"Batch '{tag}' completed: {success_count} success, {error_count} errors")

    return out_dir


async def resume_batch(manifest_path: Path) -> Path:
    """
    Resume a batch by retrying failed jobs.

    Args:
        manifest_path: Path to existing manifest.json

    Returns:
        Path to output directory
    """
    logger.info(f"Resuming batch from {manifest_path}")

    # Load manifest
    manifest_data = json.loads(manifest_path.read_text())
    manifest = BatchManifest(**manifest_data)

    # Find failed jobs (need original job data)
    failed_ids = [r.id for r in manifest.results if r.status == "error"]

    if not failed_ids:
        console.print("[green]No failed jobs to resume![/green]")
        return manifest_path.parent

    console.print(f"[yellow]Found {len(failed_ids)} failed jobs to retry:[/yellow]")
    for job_id in failed_ids:
        console.print(f"  - {job_id}")

    # Note: In a full implementation, you'd need to store original job configs
    # For now, just report what needs to be retried
    console.print("\n[yellow]To retry these jobs, re-run with the original CSV[/yellow]")

    return manifest_path.parent
