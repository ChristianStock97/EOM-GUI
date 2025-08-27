from __future__ import annotations
import os
from pathlib import Path
from typing import Tuple, Optional
import ctypes
from ctypes import c_void_p, c_short, c_double, c_bool, POINTER
import configparser

class EOMConfig:
    SECTION = "EOM"
    DLL_SECTION = "EOM_DLL"

    def __init__(
        self,
        board_idx: int,
        dac_min: float,
        dac_max: float,
        adc_min: float,
        adc_max: float,
        min_threshold: float,
        max_threshold: float,
        dll_path: str | None = None,
        use_stdcall: bool = False,
    ):
        self.board_idx = int(board_idx)
        self.dac_min = float(dac_min)
        self.dac_max = float(dac_max)
        self.adc_min = float(adc_min)
        self.adc_max = float(adc_max)
        self.min_threshold = float(min_threshold)
        self.max_threshold = float(max_threshold)
        self.dll_path = dll_path
        self.use_stdcall = bool(use_stdcall)

    @classmethod
    def from_config_file(cls, path: os.PathLike | str) -> "EOMConfig":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {p}")
        cfg = configparser.ConfigParser()
        with p.open("r", encoding="utf-8") as f:
            cfg.read_file(f)
        if cls.SECTION not in cfg:
            raise KeyError(f"Missing section [{cls.SECTION}] in {p}")

        s = cfg[cls.SECTION]
        dll_path = cfg.get(cls.DLL_SECTION, "dll_path", fallback="").strip() or None
        use_stdcall = cfg.getboolean(cls.DLL_SECTION, "use_stdcall", fallback=False)

        return cls(
            board_idx=s.getint("board_idx"),
            dac_min=s.getfloat("dac_min"),
            dac_max=s.getfloat("dac_max"),
            adc_min=s.getfloat("adc_min"),
            adc_max=s.getfloat("adc_max"),
            min_threshold=s.getfloat("min_threshold"),
            max_threshold=s.getfloat("max_threshold"),
            dll_path=dll_path,
            use_stdcall=use_stdcall,
        )

    def save(self, path: os.PathLike | str) -> None:
        cfg = configparser.ConfigParser()
        cfg[self.SECTION] = {
            "board_idx": str(self.board_idx),
            "dac_min": repr(self.dac_min),
            "dac_max": repr(self.dac_max),
            "adc_min": repr(self.adc_min),
            "adc_max": repr(self.adc_max),
            "min_threshold": repr(self.min_threshold),
            "max_threshold": repr(self.max_threshold),
        }
        cfg[self.DLL_SECTION] = {
            "dll_path": self.dll_path or "",
            "use_stdcall": "yes" if self.use_stdcall else "no",
        }
        with Path(path).open("w", encoding="utf-8") as f:
            cfg.write(f)


class EOMController:
    def __init__(self, dll_path: os.PathLike | str, config: EOMConfig, use_stdcall: bool = False):
        self._config = config
        self._dll_path = str(dll_path)
        self._lib = self._load_library(self._dll_path, use_stdcall or config.use_stdcall)
        self._bind_signatures()
        self._handle: Optional[int] = None

        self._handle = self._lib.EOM_Create(
            c_short(self._config.board_idx),
            c_double(self._config.dac_min),
            c_double(self._config.dac_max),
            c_double(self._config.adc_min),
            c_double(self._config.adc_max),
            c_double(self._config.min_threshold),
            c_double(self._config.max_threshold),
        )
        if not self._handle:
            raise RuntimeError("EOM_Create returned NULL (failed to create EOM_Regulator instance).")

    @classmethod
    def from_config(cls, dll_path: os.PathLike | str, config_path: os.PathLike | str, use_stdcall: bool = False) -> "EOMController":
        cfg = EOMConfig.from_config_file(config_path)
        return cls(dll_path, cfg, use_stdcall=use_stdcall)

    @classmethod
    def from_config_path(cls, config_path: os.PathLike | str) -> "EOMController":
        cfg = EOMConfig.from_config_file(config_path)
        if not cfg.dll_path:
            raise ValueError("dll_path is missing in [EOM_DLL] section of eom.ini")
        return cls(cfg.dll_path, cfg, use_stdcall=cfg.use_stdcall)

    @staticmethod
    def _load_library(dll_path: str, use_stdcall: bool = False):
        p = Path(dll_path)
        if not p.exists():
            raise FileNotFoundError(f"DLL not found: {p.resolve()}")
        return ctypes.WinDLL(str(p)) if use_stdcall else ctypes.CDLL(str(p))

    def _bind_signatures(self) -> None:
        # void* EOM_Create(short, double, double, double, double, double, double)
        self._lib.EOM_Create.argtypes = [c_short, c_double, c_double, c_double, c_double, c_double, c_double]
        self._lib.EOM_Create.restype = c_void_p

        # bool EOM_Start(void*)
        self._lib.EOM_Start.argtypes = [c_void_p]
        self._lib.EOM_Start.restype = c_bool

        # void EOM_Stop(void*)
        self._lib.EOM_Stop.argtypes = [c_void_p]
        self._lib.EOM_Stop.restype = None

        # void EOM_GetValue(void*, double*, double*, bool*)
        self._lib.EOM_GetValue.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_bool)]
        self._lib.EOM_GetValue.restype = None

        # void EOM_Destroy(void*)
        self._lib.EOM_Destroy.argtypes = [c_void_p]
        self._lib.EOM_Destroy.restype = None

    def start(self) -> bool:
        self._require_handle()
        return bool(self._lib.EOM_Start(self._handle))

    def stop(self) -> None:
        if self._handle:
            self._lib.EOM_Stop(self._handle)

    def get_value(self) -> Tuple[float, float, bool]:
        self._require_handle()
        diode = c_double(0.0)
        bias = c_double(0.0)
        laser = c_bool(False)
        self._lib.EOM_GetValue(self._handle, ctypes.byref(diode), ctypes.byref(bias), ctypes.byref(laser))
        return float(diode.value), float(bias.value), bool(laser.value)

    def close(self) -> None:
        if self._handle:
            try:
                self._lib.EOM_Stop(self._handle)
            except Exception:
                pass
            try:
                self._lib.EOM_Destroy(self._handle)
            finally:
                self._handle = None

    def __enter__(self) -> "EOMController":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def _require_handle(self) -> None:
        if not self._handle:
            raise RuntimeError("EOM controller has been closed or not initialized.")
