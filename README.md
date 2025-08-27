# EOM-GUI

A minimal Qt GUI for controlling the EOM regulator via a Windows DLL.

## Quick start (Windows)

1. Put your DLL path into `eom.ini` under `[EOM_DLL] -> dll_path`.
2. Double-click **setup_env.bat** (creates `.venv` and installs requirements).
3. Start the app:
   - Silent (no console): double-click **start_gui.vbs**.
   - Or minimal batch: double-click **start_gui.bat** (uses `pythonw.exe`).

## Files

- `main.py` – App entry point.
- `eom_gui.py` – Qt widget and timer loop.
- `eom_regulator.py` – ctypes wrapper for DLL + INI config.
- `eom.ini` – Runtime config (EOM params + DLL path).
- `requirements.txt` – Python deps.
- `setup_env.bat` – Creates virtualenv and installs deps.
- `start_gui.bat` – Launches app with `pythonw.exe`.
- `start_gui.vbs` – Launches the batch **hidden** (no console).

## Notes

- If your DLL uses `__stdcall`, set `use_stdcall = yes` in `[EOM_DLL]`.
- If Qt backend errors, install an alternative like `PySide6` and update `requirements.txt` and code imports if needed.


A DLL exporting:
    EOM_Create(short, double, double, double, double, double, double) -> void*
    EOM_Start(void*) -> bool
    EOM_Stop(void*) -> void
    EOM_GetValue(void*, double*, double*, bool*) -> void
    EOM_Destroy(void*) -> v