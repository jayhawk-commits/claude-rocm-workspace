@echo off
REM Launch Claude Code with the workspace Python venv activated.
REM
REM Setup (one-time):
REM   cd C:\Dev\claude-rocm-workspace
REM   py -V:3.12 -m venv 3.12.venv
REM   REM If the py launcher is unavailable, use a local Python instead:
REM   REM C:\Dev\python-3.12.13\python.exe -m venv 3.12.venv
REM   .\3.12.venv\Scripts\activate.bat
REM   pip install -r ..\TheRock-pub\requirements.txt
REM
REM This ensures tools like pytest are available when Claude runs commands.

setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "WORKSPACE_DIR=%%~fI"
set "VENV_ACTIVATE=%WORKSPACE_DIR%\3.12.venv\Scripts\activate.bat"
set "WORKSPACE_TMP=C:\Dev\tmp"

if not exist "%WORKSPACE_TMP%" mkdir "%WORKSPACE_TMP%"
set "TEMP=%WORKSPACE_TMP%"
set "TMP=%WORKSPACE_TMP%"

if exist "%VENV_ACTIVATE%" (
  call "%VENV_ACTIVATE%"
) else (
  echo Warning: workspace venv not found at "%VENV_ACTIVATE%"
  echo Continuing without venv. Create it with: py -V:3.12 -m venv 3.12.venv
)

REM Change to workspace directory and launch Claude
cd /d "%WORKSPACE_DIR%"
claude %*
