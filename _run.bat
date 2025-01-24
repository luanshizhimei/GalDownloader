@echo off
setlocal

:: 执行执行脚本目录
set "batchPath=%~dp0"
:: 执行python环境目录
set "PYTHON_ENV_PATH=%batchPath%\venv"
:: 执行脚本目录
set "PYTHON_SCRIPT_PATH=%batchPath%\src\app.py"

cd /d "%batchPath%"

call "%PYTHON_ENV_PATH%\Scripts\activate.bat"
python "%PYTHON_SCRIPT_PATH%"

endlocal
exit /b 0