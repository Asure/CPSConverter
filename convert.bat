@echo off
rem cps2fix - one click: builds the fixed CPS2 sets of Cadillacs and Dinosaurs and The Punisher from the original zips in the roms folder.
rem Needs Python 3. If none is installed this file offers to download the small official embeddable Python from python.org
rem into the runtime folder (nothing is installed). "convert.bat --get-python" does that download on request.
setlocal EnableExtensions
title cps2fix
pushd "%~dp0"
if errorlevel 1 (
    echo Cannot open the folder of this file: %~dp0
    pause
    exit /b 1
)
echo cps2fix - Cadillacs and Dinosaurs / The Punisher CPS2 sets
set "PYVER=3.12.7"
set "PYZIP=runtime\python-%PYVER%-embed-amd64.zip"
set "PYURL=https://www.python.org/ftp/python/%PYVER%/python-%PYVER%-embed-amd64.zip"
set "PYSHA=0d57bb6cb078b74d23dbfe91f77d6780d45bed328911609f1f7ee2ba1606bf44"
set "PY="
set "ARGS=%*"
if /i "%~1"=="--get-python" goto :getpy
if exist "runtime\python.exe" set "PY=runtime\python.exe"
if defined PY goto :run
call :try py -3
if defined PY goto :run
call :try python
if defined PY goto :run
call :try python3
if defined PY goto :run

echo.
echo Python 3 was not found on this computer. This tool needs it.
echo It can download the official embeddable Python %PYVER% from python.org (about 11 MB) into
echo   %~dp0runtime
echo Nothing is installed and nothing else on this PC is changed.
set "ANS="
set /p "ANS=Download it now? [Y/N] "
if /i not "%ANS%"=="Y" goto :nopython

:getpy
set "ARGS="
if not exist runtime mkdir runtime
echo Downloading %PYURL% ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri '%PYURL%' -OutFile '%PYZIP%'; $h=(Get-FileHash '%PYZIP%' -Algorithm SHA256).Hash.ToLower(); if ($h -ne '%PYSHA%') { Write-Host 'The download does not match the expected checksum, not using it.'; Remove-Item '%PYZIP%'; exit 2 }; Expand-Archive -Force -LiteralPath '%PYZIP%' -DestinationPath 'runtime'"
if errorlevel 1 goto :nopython
if exist "runtime\python.exe" set "PY=runtime\python.exe"
if not defined PY goto :nopython

:run
echo Using Python: %PY%
%PY% cps2fix.py %ARGS%
set "RC=%ERRORLEVEL%"
goto :end

:try
%~1 %~2 -c "import sys; sys.exit(0 if sys.version_info[0]==3 else 1)" >nul 2>nul
if not errorlevel 1 set "PY=%~1 %~2"
exit /b 0

:nopython
echo.
echo Python 3 is not available. Install it from https://www.python.org/downloads/ or run convert.bat --get-python, then try again.
set "RC=1"

:end
echo.
popd
pause
exit /b %RC%
