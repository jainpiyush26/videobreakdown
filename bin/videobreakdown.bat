@echo off
TITLE Video Breakdown Application

set "$py=0"
set firstarg=%1
set secondarg=%2

call:construct

for /f "delims=" %%a in ('python #.py ^| findstr "2"') do set "$py=2"
for /f "delims=" %%a in ('python #.py ^| findstr "3"') do set "$py=3"
del #.py
goto:%$py%

echo python is not installed or python's path Path is not in the %%$path%% env. var
exit/b

:2
set pythonapp=python3
call:videobreakdown
exit/b

:3
set pythonapp=python
call:videobreakdown
exit/b

:videobreakdown

IF [%firstarg%]==[] (
    %pythonapp% %~dp0\videobreakdown_app.py
    GOTO :EOF
)

IF [%secondarg%]==[] (
    %pythonapp% %~dp0\videobreakdown_app.py --path %firstarg%
) ELSE (
    %pythonapp% %~dp0\videobreakdown_app.py --path %firstarg% --export-path %secondarg%
)
pause

exit/b

:construct
echo import sys; print('{0[0]}.{0[1]}'.format(sys.version_info^)^) >#.py