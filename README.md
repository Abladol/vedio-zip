# VedioZip

English | [简体中文](README.zh-CN.md)

VedioZip is an open-source Windows video conversion tool with a local web UI.

## Features

- Convert a single video file or a whole folder
- Choose output directory
- Set target resolution (for example: 320p)
- Configure CRF, preset, and audio bitrate
- Real-time conversion progress
- Portable `.exe` and installer package support

## Quick Start

1. Create or update environment:

```powershell
conda env update -n vediozip-ffmpeg -f environment.yml --prune
```

2. Run locally:

```powershell
.\run_dev.ps1
```

The browser UI opens automatically.

## Download

From GitHub Releases, download one of:

- `VedioZip-portable-win64-<version>.zip` (portable)
- `VedioZip-setup-win64-<version>.exe` (installer)

## Build (Local)

Build portable executable:

```powershell
.\build_windows.ps1
```

Output:

- `dist/VedioZip.exe`
- `dist/ffmpeg.exe`
- `dist/ffprobe.exe`
- runtime DLLs in `dist/`

Build installer (requires Inno Setup):

```powershell
choco install innosetup -y
.\build_installer.ps1 1.0.0
```

Output:

- `installer/Output/VedioZip-Setup-1.0.0.exe`

## GitHub Release Workflow

Push a tag to build and publish release assets automatically:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

Workflow file:

- `.github/workflows/release.yml`

## Troubleshooting

Runtime logs:

- source mode: `logs/vediozip.log`
- packaged mode: `dist/logs/vediozip.log`

If conversion fails, share the log file for diagnosis.

## Project Structure

- `launcher.py`: app entry point
- `server.py`: FastAPI API and static hosting
- `video_service.py`: conversion task logic
- `static/`: frontend files
- `build_windows.ps1`: build portable package
- `build_installer.ps1`: build installer
- `installer/VedioZip.iss`: Inno Setup script

## License

MIT
