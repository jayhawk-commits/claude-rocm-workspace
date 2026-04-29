param(
  [string]$PythonVersion = "3.12.13",
  [string]$BuildDate = "20260414",
  [string]$InstallDir = "C:\Dev\python-3.12.13",
  [string]$VenvDir = "",
  [string]$DownloadDir = "C:\Dev\python-downloads",
  [string]$TmpDir = "C:\Dev\tmp"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceDir = Resolve-Path (Join-Path $scriptDir "..")
if (-not $VenvDir) {
  $VenvDir = Join-Path $workspaceDir "3.12.venv"
}

$asset = "cpython-$PythonVersion+$BuildDate-x86_64-pc-windows-msvc-install_only_stripped.tar.gz"
$archive = Join-Path $DownloadDir $asset
$pythonExe = Join-Path $InstallDir "python.exe"
$venvPython = Join-Path $VenvDir "Scripts\python.exe"
$siteCustomize = Join-Path $scriptDir "python-sitecustomize.py"

New-Item -ItemType Directory -Force -Path $DownloadDir, $TmpDir | Out-Null
$env:TEMP = $TmpDir
$env:TMP = $TmpDir

if (-not (Test-Path $pythonExe)) {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "gh CLI is required to download the standalone Python archive."
  }
  if (-not (Test-Path $archive)) {
    gh release download $BuildDate `
      --repo astral-sh/python-build-standalone `
      --pattern $asset `
      --dir $DownloadDir `
      --clobber
  }
  New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
  tar -xzf $archive -C $InstallDir --strip-components=1
}

function Install-SiteCustomize($sitePackagesDir) {
  New-Item -ItemType Directory -Force -Path $sitePackagesDir | Out-Null
  Copy-Item -Path $siteCustomize -Destination (Join-Path $sitePackagesDir "sitecustomize.py") -Force
}

Install-SiteCustomize (Join-Path $InstallDir "Lib\site-packages")

if (-not (Test-Path $venvPython)) {
  & $pythonExe -m venv --without-pip $VenvDir
}

Install-SiteCustomize (Join-Path $VenvDir "Lib\site-packages")
& $venvPython -m ensurepip --upgrade --default-pip

Write-Host "Workspace Python ready:"
& $venvPython --version
& $venvPython -m pip --version
