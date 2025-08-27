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


> **Important:** The batch files assume they are run from the project folder. They set the working directory correctly.

---

## Dependencies

This GUI depends on the **EOM_Controller_NI** DLL project, which provides the C++ implementation of the regulator.  
The source code for the DLL is available here:

👉 [EOM_Controller_NI (GitHub)](https://github.com/ChristianStock97/EOM_Controller_NI)

You need to build the DLL from that repository (Visual Studio recommended) and set its path in your `eom.ini`:

```ini
[EOM_DLL]
dll_path = D:/Programmierung/EOM_Controller_NI/x64/Debug/EOM_Controller_NI.dll
use_stdcall = no

- **Windows**
- **Python 3.11+** (tested with 3.12)
- Your EOM **DLL** must export the following C API (cdecl by default):
  ```c
  void* EOM_Create(short, double, double, double, double, double, double);
  bool  EOM_Start(void*);
  void  EOM_Stop(void*);
  void  EOM_GetValue(void*, double* /*diode*/, double* /*bias*/, bool* /*laser_on*/);
  void  EOM_Destroy(void*);