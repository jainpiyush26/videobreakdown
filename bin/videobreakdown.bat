@echo off
TITLE Video Breakdown Application

IF [%2]==[] (
    python %~dp0\videobreakdown_app.py --path %1
) ELSE (
    python %~dp0\videobreakdown_app.py --path %1 --export-path %2
)

pause