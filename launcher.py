# launcher.py
from __future__ import annotations
import sys, traceback
from pathlib import Path
import datetime
from configparser import ConfigParser

LOGDIR = Path(__file__).resolve().parent / "logs"
LOGDIR.mkdir(exist_ok=True)
LOGFILE = LOGDIR / "app.log"

def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOGFILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

def show_error_box(title: str, text: str):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x10)  # MB_ICONERROR
    except Exception:
        log(f"(fallback) {title}: {text}")

def main():
    try:
        # Preflight: ini + dll path
        cfgp = Path("eom.ini")
        if not cfgp.exists():
            raise FileNotFoundError("eom.ini was not found next to the launcher.")
        cfg = ConfigParser()
        cfg.read(cfgp, encoding="utf-8")
        if "EOM_DLL" in cfg:
            dll_path = (cfg["EOM_DLL"].get("dll_path") or "").strip()
            if not dll_path:
                raise FileNotFoundError("dll_path missing in [EOM_DLL] section of eom.ini")
            if not Path(dll_path).exists():
                raise FileNotFoundError(f"dll_path not found: {dll_path}")

        # Run the real app
        import main as app_main
        app_main.main()
    except Exception as e:
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        log(tb)
        show_error_box("EOM-GUI failed to start", f"{e}\n\nSee logs\\app.log for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
