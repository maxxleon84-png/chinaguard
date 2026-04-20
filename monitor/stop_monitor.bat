@echo off
REM Останавливает все фоновые процессы pythonw.exe (включая монитор).
REM ВАЖНО: если параллельно запущены другие pythonw-скрипты — они тоже умрут.
REM Точечной остановки конкретного pythonw из bat сделать сложно, поэтому пока так.
taskkill /F /IM pythonw.exe
timeout /t 2 >nul
