# 定义你的 Python 和 aria2c 安装路径
$PYTHON_PATH = Join-Path -Path $PSScriptRoot -ChildPath "venv\Scripts\python.exe"
$ARIA2_PATH = Join-Path -Path $PSScriptRoot -ChildPath "bin\aria2\aria2c.exe"

function KillProcess($PROCESS_NAME, $TARGET_PATH) {
    $processes = Get-WmiObject -Query "SELECT * FROM Win32_Process WHERE Name = '$PROCESS_NAME'"
    foreach ($process in $processes) {
        if ($process.ExecutablePath -eq $TARGET_PATH) {
            Write-Output "Killing Process: $($process.Name)"
            Write-Output "Executable Path: $($process.ExecutablePath)"
            Stop-Process -Id $process.ProcessId -Force
            Write-Output "-----------------------------"
        }
    }
}

KillProcess "python.exe" $PYTHON_PATH
KillProcess "aria2c.exe" $ARIA2_PATH