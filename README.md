# VedioZip

VedioZip is an open-source Windows video conversion tool.

- Full source code is included in this repository.
- You can run from source in one command.
- You can also download a portable executable or installer from GitHub Releases.

## Source Code

- Backend API: `server.py`
- Conversion engine: `video_service.py`
- App launcher: `launcher.py`
- Frontend UI: `static/`
- Build scripts:
  - `build_windows.ps1` (portable exe)
  - `build_installer.ps1` (installer exe)
- CI release workflow: `.github/workflows/release.yml`

## Quick Start (Run from source)

1. Create or update environment:

```powershell
conda env update -n vediozip-ffmpeg -f environment.yml --prune
```

2. Start app:

```powershell
.\run_dev.ps1
```

The app opens in your browser automatically.

## Download and Use (No development environment required)

Go to **GitHub Releases** and download either:

- `VedioZip-portable-win64-<version>.zip`
  - Unzip and run `VedioZip.exe`
- `VedioZip-setup-win64-<version>.exe`
  - Run installer and start from Start Menu/Desktop shortcut

## How to Use in App

1. Choose input file or input folder.
2. Choose output folder.
3. Set target resolution (for example 320p).
4. Click **Start Conversion**.
5. Check real-time progress and current file status.

## Build Portable Exe (Local)

```powershell
.\build_windows.ps1
```

Output:

- `dist/VedioZip.exe`
- `dist/ffmpeg.exe`
- `dist/ffprobe.exe`

## Build Installer Exe (Local)

Install Inno Setup first:

```powershell
choco install innosetup -y
```

Then build installer:

```powershell
.\build_installer.ps1 1.0.0
```

Output:

- `installer/Output/VedioZip-Setup-1.0.0.exe`

## Automated Release

When you push a tag like `v1.0.0`, GitHub Actions will:

1. Build portable executable.
2. Build installer executable.
3. Create a GitHub Release.
4. Upload both files to Release assets.

Example:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

## License

MIT
