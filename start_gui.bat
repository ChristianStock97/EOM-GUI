:: start_gui.bat
@echo off
setlocal
set "PROJDIR=%~dp0"
pushd "%PROJDIR%"

if not exist ".venv\Scripts\pythonw.exe" (
    echo Virtual environment not found. Run setup_env.bat first.
    pause
    exit /b 1
)

start "" ".venv\Scripts\pythonw.exe" "%PROJDIR%launcher.py"

popd
endlocal
