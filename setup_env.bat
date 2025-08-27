@echo off
setlocal

REM Determine project root (folder of this script)
set "PROJDIR=%~dp0"
pushd "%PROJDIR%"

echo Creating virtual environment in .venv ...
py -3 -m venv .venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

echo Upgrading pip ...
".venv\Scripts\python.exe" -m pip install --upgrade pip

echo Installing requirements ...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo pip install failed.
    pause
    exit /b 1
)

echo Done. You can now run start_gui.vbs (hidden) or start_gui.bat
popd
endlocal