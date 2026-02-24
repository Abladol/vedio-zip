from __future__ import annotations

import shutil
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".wmv", ".m4v"}


@dataclass
class JobState:
    job_id: str
    status: str
    progress: float
    message: str
    source_path: str
    output_dir: str
    target_height: int
    total_files: int
    processed_files: int
    current_file: str | None
    error: str | None
    created_at: float
    updated_at: float

    def to_dict(self) -> dict:
        return asdict(self)


class VideoConvertService:
    def __init__(self) -> None:
        self._jobs: dict[str, JobState] = {}
        self._lock = threading.Lock()

    def start_job(
        self,
        source_path: str,
        output_dir: str,
        height: int,
        crf: int,
        preset: str,
        audio_bitrate: str,
    ) -> str:
        source = Path(source_path).expanduser().resolve()
        target_dir = Path(output_dir).expanduser().resolve()

        if not source.exists():
            raise ValueError(f"输入路径不存在: {source}")
        if not target_dir.exists():
            raise ValueError(f"输出目录不存在: {target_dir}")
        if not target_dir.is_dir():
            raise ValueError(f"输出路径不是目录: {target_dir}")

        files = self._collect_source_files(source)
        if not files:
            raise ValueError("未找到可转换的视频文件。")

        ffmpeg_path = self._resolve_tool_path("ffmpeg")
        ffprobe_path = self._resolve_tool_path("ffprobe")
        if ffmpeg_path is None or ffprobe_path is None:
            raise ValueError("未找到 ffmpeg/ffprobe，请先安装或放到程序目录。")

        now = time.time()
        job_id = uuid.uuid4().hex
        job = JobState(
            job_id=job_id,
            status="queued",
            progress=0.0,
            message="任务已创建",
            source_path=str(source),
            output_dir=str(target_dir),
            target_height=height,
            total_files=len(files),
            processed_files=0,
            current_file=None,
            error=None,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._jobs[job_id] = job

        worker = threading.Thread(
            target=self._run_job,
            args=(job_id, source, target_dir, files, ffmpeg_path, ffprobe_path, height, crf, preset, audio_bitrate),
            daemon=True,
        )
        worker.start()
        return job_id

    def get_job(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return None if job is None else job.to_dict()

    def _run_job(
        self,
        job_id: str,
        source_root: Path,
        output_dir: Path,
        files: list[Path],
        ffmpeg_path: Path,
        ffprobe_path: Path,
        height: int,
        crf: int,
        preset: str,
        audio_bitrate: str,
    ) -> None:
        self._update_job(job_id, status="running", message="正在转换", progress=0.0)

        durations = [self._probe_duration(ffprobe_path, path) for path in files]
        has_all_duration = all(d is not None and d > 0 for d in durations)

        processed_duration = 0.0
        total_duration = sum(d for d in durations if d is not None) if has_all_duration else 0.0

        try:
            for index, input_file in enumerate(files):
                output_file = self._build_output_path(source_root, input_file, output_dir, height)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                duration = durations[index]

                self._update_job(
                    job_id,
                    current_file=str(input_file),
                    message=f"正在转换 ({index + 1}/{len(files)}): {input_file.name}",
                )

                def on_progress(current_seconds: float) -> None:
                    if has_all_duration and duration and total_duration > 0:
                        file_ratio = min(current_seconds / duration, 1.0)
                        value = (processed_duration + duration * file_ratio) / total_duration
                    elif len(files) > 0 and duration and duration > 0:
                        file_ratio = min(current_seconds / duration, 1.0)
                        value = (index + file_ratio) / len(files)
                    elif len(files) > 0:
                        value = index / len(files)
                    else:
                        value = 0.0

                    self._update_job(job_id, progress=max(0.0, min(value, 1.0)))

                self._convert_single_file(
                    ffmpeg_path=ffmpeg_path,
                    input_file=input_file,
                    output_file=output_file,
                    height=height,
                    crf=crf,
                    preset=preset,
                    audio_bitrate=audio_bitrate,
                    on_progress=on_progress,
                )

                if has_all_duration and duration:
                    processed_duration += duration

                completed = index + 1
                self._update_job(
                    job_id,
                    processed_files=completed,
                    progress=completed / len(files),
                )

            self._update_job(
                job_id,
                status="completed",
                progress=1.0,
                message="全部转换完成",
                current_file=None,
            )
        except Exception as exc:
            self._update_job(
                job_id,
                status="failed",
                message="转换失败",
                error=str(exc),
                current_file=None,
            )

    def _update_job(self, job_id: str, **kwargs) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            for key, value in kwargs.items():
                setattr(job, key, value)
            job.updated_at = time.time()

    def _collect_source_files(self, source: Path) -> list[Path]:
        if source.is_file():
            return [source]
        return sorted(path for path in source.rglob("*") if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS)

    def _build_output_path(self, source_root: Path, input_file: Path, output_dir: Path, height: int) -> Path:
        if source_root.is_file():
            return output_dir / f"{input_file.stem}_{height}p.mp4"
        relative = input_file.relative_to(source_root)
        return output_dir / relative.parent / f"{relative.stem}_{height}p.mp4"

    def _resolve_tool_path(self, tool_name: str) -> Path | None:
        from_path = shutil.which(tool_name)
        if from_path:
            return Path(from_path)

        executable_dir = Path(sys.executable).resolve().parent
        candidates = [
            executable_dir / f"{tool_name}.exe",
            Path(sys.prefix) / "Library" / "bin" / f"{tool_name}.exe",
            Path(sys.prefix) / "Scripts" / f"{tool_name}.exe",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _probe_duration(self, ffprobe_path: Path, video_file: Path) -> float | None:
        cmd = [
            str(ffprobe_path),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_file),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode != 0:
            return None
        try:
            duration = float(result.stdout.strip())
            return duration if duration > 0 else None
        except ValueError:
            return None

    def _convert_single_file(
        self,
        ffmpeg_path: Path,
        input_file: Path,
        output_file: Path,
        height: int,
        crf: int,
        preset: str,
        audio_bitrate: str,
        on_progress: Callable[[float], None],
    ) -> None:
        cmd = [
            str(ffmpeg_path),
            "-y",
            "-i",
            str(input_file),
            "-vf",
            f"scale=-2:{height}",
            "-c:v",
            "libx264",
            "-crf",
            str(crf),
            "-preset",
            preset,
            "-c:a",
            "aac",
            "-b:a",
            audio_bitrate,
            "-progress",
            "pipe:1",
            "-nostats",
            "-loglevel",
            "error",
            str(output_file),
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        try:
            while True:
                line = process.stdout.readline() if process.stdout else ""
                if line == "" and process.poll() is not None:
                    break
                if "=" not in line:
                    continue
                key, value = line.strip().split("=", 1)
                if key in {"out_time_ms", "out_time_us"}:
                    try:
                        on_progress(float(value) / 1_000_000.0)
                    except ValueError:
                        continue
                elif key == "progress" and value == "end":
                    on_progress(float("inf"))
        finally:
            return_code = process.wait()
            stderr_text = process.stderr.read() if process.stderr else ""

        if return_code != 0:
            raise RuntimeError(stderr_text.strip() or f"ffmpeg 退出码: {return_code}")
