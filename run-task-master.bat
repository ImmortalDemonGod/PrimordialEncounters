@echo off
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Node.js is not installed or not in PATH.
    exit /b 1
)
set PATH=%PATH%;C:\Program Files\nodejs;C:\Users\Shadow\AppData\Roaming\npm
C:\Users\Shadow\AppData\Roaming\npm\task-master.cmd %*

