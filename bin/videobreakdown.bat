@echo off
TITLE Video Breakdown Application

IF [%1]==[] (
    python3 %~dp0\videobreakdown_app.py
    GOTO :EOF
)

IF [%2]==[] (
    python3 %~dp0\videobreakdown_app.py --path %1
) ELSE (
    python3 %~dp0\videobreakdown_app.py --path %1 --export-path %2
)

pause