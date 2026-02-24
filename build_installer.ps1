$ErrorActionPreference = "Stop"

$appVersion = "1.0.0"
if ($args.Length -gt 0 -and -not [string]::IsNullOrWhiteSpace($args[0])) {
  $appVersion = $args[0]
}

if (-not (Test-Path "dist\VedioZip.exe")) {
  throw "dist output not found. Run .\\build_windows.ps1 first."
}

$iscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) {
  throw "Inno Setup not found. Install it first: choco install innosetup -y"
}

& $iscc "/DMyAppVersion=$appVersion" "installer\VedioZip.iss"

Write-Host "Installer build completed."
Write-Host "Check output in installer\\Output"
