@echo off
REM Запускает ChinaGuard Monitor в фоне без видимого окна.
REM Все логи пишутся в logs/monitor.log — смотри его, чтобы понять, что происходит.
cd /d "%~dp0"
start "" pythonw main.py
echo Monitor started in background. Logs: %~dp0logs\monitor.log
timeout /t 3 >nul
