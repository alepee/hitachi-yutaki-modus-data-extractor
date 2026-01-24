@echo off
REM
REM Get Unique ID from Hitachi ATW-MBS-02 Gateway
REM
REM Usage:
REM   scripts\get_unique_id.bat
REM

REM Go to project root
cd /d "%~dp0\.."

echo.
echo ======================================================================
echo Hitachi ATW-MBS-02 Gateway - Unique ID Reader
echo ======================================================================
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 'uv' is not installed.
    echo.
    echo Install it with:
    echo   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    pause
    exit /b 1
)

REM Ask for gateway IP address
set "gateway_ip=192.168.0.4"
set /p gateway_ip="Enter your gateway IP address [192.168.0.4]: "

echo.
echo Connecting to %gateway_ip%...
echo.

REM Run the script with uv
uv run python get_gateway_unique_id.py --ip %gateway_ip%

set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% equ 0 (
    echo ======================================================================
    echo Please share the unique ID above on GitHub issue #162
    echo https://github.com/alepee/hass-hitachi_yutaki/issues/162
    echo ======================================================================
)

echo.
pause
exit /b %EXIT_CODE%
