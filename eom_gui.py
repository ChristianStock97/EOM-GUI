import numpy as np
import ctypes
from qtpy.QtWidgets import QApplication, QPushButton, QWidget, QGridLayout
from qtpy.QtCore import QTimer
from eom_functions import configure_eom, start_controller, stop_controller, get_values
import configparser
import sys

class EOM_GUI(QWidget):
    def __init__(self, config_direction, parent=None):
        super().__init__(parent)

        self._timer = None
        config = configparser.ConfigParser()
        config.read(config_direction)

        self.dAC_idx = int(config.get("EOMValues", "DAC_idx"))
        self.dac_min = float(config.get("EOMValues", "DAC_min"))
        self.dac_max = float(config.get("EOMValues", "DAC_max"))
        self.DAC_Reg_threshold = float(config.get("EOMValues", "DAC_Reg_threshold"))
        self.laser_running = ctypes.c_bool(False)
        self.diode_value = ctypes.c_double(0.0)

        self.laser_running_pointer = ctypes.pointer(self.laser_running)
        self.diode_value_pointer = ctypes.pointer(self.diode_value)
        self.laser_gui = None

    def return_window(self):

        self.start_button = QPushButton("PD: 0.000", self)
        self.start_button.setStyleSheet("background-color: red")
        self.start_button.setFixedSize(200, 30)
        layout = QGridLayout()
        layout.addWidget(self.start_button, 0, 0)

        self.laser_gui = QWidget()
        self.laser_gui.setLayout(layout)
        self.laser_gui.setWindowTitle("MOPA")
        self.laser_gui.destroyed.connect(self.if_window_closed)
        self.start_regulation()
        return self.laser_gui

    def if_window_closed(self):
        self._timer.stop()
        stop_controller()
        print("Windows closed")
        
    def start_regulation(self):
        dac = np.array((self.dac_min, self.dac_max), dtype=np.double)
        adc = np.array((-10.0, 10.0), dtype=np.double)
        configure_eom(self.dAC_idx, dac, adc, self.DAC_Reg_threshold)
        start_controller()
        self._timer = QTimer()
        self._timer.timeout.connect(self.set_gui_values)
        self._timer.start(int(100))
        self.start_button.setStyleSheet("background-color: yellow")
        
    def restartRegulation(self):
        self.start_button.setStyleSheet("background-color: yellow")
        if (-10 <= self.dac_min < self.dac_max) and (self.dac_max <= 10):
            self._timer.stop()
            stop_controller()
            self.start_regulation()

    def set_gui_values(self):
        get_values(self.diode_value_pointer, self.laser_running_pointer)
        if self.laser_running.value:
            self.start_button.setStyleSheet("background-color: green")
        else:
            self.start_button.setStyleSheet("background-color: yellow")
        self.start_button.setText(f"PD: {round(self.diode_value.value, 3)}")

if __name__ == '__main__':

    app = QApplication(sys.argv)
    # Create a Qt widget, which will be our window.
    eom = EOM_GUI('config.ini')
    window = eom.return_window()
    window.show()

    # Start the event loop.
    app.exec()
