$ErrorActionPreference = "Stop"

$envName = "vediozip-ffmpeg"
$appName = "VedioZip"

Write-Host "==> Clean old artifacts"
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "$appName.spec") { Remove-Item -Force "$appName.spec" }

Write-Host "==> Build executable with PyInstaller"
conda run -n $envName pyinstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name $appName `
  --hidden-import ffmpeg `
  --add-data "static;static" `
  launcher.py

Write-Host "==> Copy ffmpeg binaries to dist"
$prefix = conda env list `
  | Where-Object { $_ -match "^\s*$envName\s" } `
  | ForEach-Object { ($_ -split "\s+")[-1] } `
  | Select-Object -First 1

if ([string]::IsNullOrWhiteSpace($prefix)) {
  throw "Cannot resolve conda env path for $envName"
}

$ffmpeg = Join-Path $prefix "Library\bin\ffmpeg.exe"
$ffprobe = Join-Path $prefix "Library\bin\ffprobe.exe"

if (-not (Test-Path $ffmpeg) -or -not (Test-Path $ffprobe)) {
  throw "Cannot find ffmpeg/ffprobe. Run: conda env update -n $envName -f environment.yml --prune"
}

Copy-Item $ffmpeg "dist\ffmpeg.exe" -Force
Copy-Item $ffprobe "dist\ffprobe.exe" -Force

Write-Host "==> Build completed"
Write-Host "Output dir: dist"
Write-Host "Run file : dist\$appName.exe"
