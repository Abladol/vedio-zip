from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from video_service import VideoConvertService

app = FastAPI(title="VedioZip")
service = VideoConvertService()


def _resolve_static_dir() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    else:
        base = Path(__file__).resolve().parent
    static_dir = base / "static"
    if not static_dir.exists():
        raise RuntimeError(f"静态资源目录不存在: {static_dir}")
    return static_dir


STATIC_DIR = _resolve_static_dir()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class PickPathRequest(BaseModel):
    kind: Literal["source_file", "source_folder", "output_folder"]


class StartJobRequest(BaseModel):
    source_path: str = Field(..., description="输入文件或文件夹路径")
    output_dir: str = Field(..., description="输出目录")
    height: int = Field(320, ge=120, le=2160)
    crf: int = Field(23, ge=0, le=51)
    preset: str = Field("medium")
    audio_bitrate: str = Field("128k")


def _pick_path(kind: str) -> str:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()
    try:
        if kind == "source_file":
            value = filedialog.askopenfilename(
                title="选择视频文件",
                filetypes=[
                    ("Video Files", "*.mp4 *.mov *.mkv *.avi *.wmv *.m4v"),
                    ("All Files", "*.*"),
                ],
            )
        elif kind == "source_folder":
            value = filedialog.askdirectory(title="选择视频文件夹")
        elif kind == "output_folder":
            value = filedialog.askdirectory(title="选择输出目录")
        else:
            value = ""
    finally:
        root.destroy()
    return value or ""


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/pick-path")
async def pick_path(request: PickPathRequest) -> dict:
    path = _pick_path(request.kind)
    return {"path": path}


@app.post("/api/start")
def start_job(request: StartJobRequest) -> dict:
    try:
        job_id = service.start_job(
            source_path=request.source_path,
            output_dir=request.output_dir,
            height=request.height,
            crf=request.crf,
            preset=request.preset,
            audio_bitrate=request.audio_bitrate,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job = service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=500, detail="任务创建失败")
    return job


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    job = service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return job


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
