@echo off

SETLOCAL

SET VENV_DIR=.venv
SET BIN_DIR=.\bin
SET PY_SCRIPT=.\src\app.py
SET PY_OPTIONS=

call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo Error: Virtual environment activation failed
    pause
    exit /b 1
)

set "PATH=%BIN_DIR%;%PATH%"
uv run "%PY_SCRIPT%" %PY_OPTIONS%

ENDLOCAL
