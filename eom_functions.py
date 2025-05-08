import ctypes
import numpy as np
import time

dll_path =          r"C:\Users\CS-SLIDE\Documents\Programmierung\EOM_Controller_NI\x64\Debug\EOM_Controller_NI.dll"
dll_path = "eom_cpp//EOM_Controller_NI.dll"
dll = ctypes.windll.LoadLibrary(dll_path)

CALLBACK_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_bool ,ctypes.c_double)

dll.connect.argtypes = [ctypes.c_int16, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
dll.start.argtypes = []
dll.stop.argtypes = []
dll.get_EOM_values.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_bool)]


def start_controller():
    dll.start()

def stop_controller():
    dll.stop()

def configure_eom(idx: int, dac_range: np.array, adc_range:np.array, reg_threshold):
    dll.connect(ctypes.c_int16(idx), dac_range.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), adc_range.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), ctypes.c_double(reg_threshold))

def get_values(diode_value, laser_running):
    dll.get_EOM_values(diode_value, laser_running)

if __name__ == '__main__':

    dac = np.array((-10.0, 10.0), dtype=np.double)
    adc = np.array((-10.0, 10.0), dtype=np.double)
    laser_running = ctypes.c_bool(False)
    diode_value = ctypes.c_double(0.0)

    laser_running_pointer = ctypes.pointer(laser_running)
    diode_value_pointer = ctypes.pointer(diode_value)

    configure_eom(1, dac, adc)
    start_controller()
    for k in range(200):
        get_values(diode_value_pointer, laser_running_pointer)
        if laser_running.value:
            print(diode_value.value)
        time.sleep(0.1)
    stop_controller()