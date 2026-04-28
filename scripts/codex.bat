@echo off
REM Launch Codex with the workspace Python venv activated.
REM
REM Setup (one-time):
REM   cd C:\Dev\claude-rocm-workspace
REM   py -V:3.12 -m venv 3.12.venv
REM   .\3.12.venv\Scripts\activate.bat
REM   pip install -r ..\TheRock-pub\requirements.txt
REM
REM This keeps Python tooling available for Codex command execution.

setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "WORKSPACE_DIR=%%~fI"
set "VENV_ACTIVATE=%WORKSPACE_DIR%\3.12.venv\Scripts\activate.bat"

if exist "%VENV_ACTIVATE%" (
  call "%VENV_ACTIVATE%"
) else (
  echo Warning: workspace venv not found at "%VENV_ACTIVATE%"
  echo Continuing without venv. Create it with: py -V:3.12 -m venv 3.12.venv
)

cd /d "%WORKSPACE_DIR%"
codex %*
