from qtpy.QtWidgets import QWidget, QPushButton, QGridLayout
from qtpy.QtCore import QTimer
from include.eom_regulator import EOMController, EOMConfig

class EOM_GUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = None
        self.eom = EOMController.from_config_path("eom.ini")

    def return_window(self):
        self.start_button = QPushButton("PD: 0.000  B: 0.000", self)
        self.start_button.setStyleSheet("background-color: red")
        self.start_button.setFixedSize(260, 36)

        layout = QGridLayout()
        layout.addWidget(self.start_button, 0, 0)

        laser_gui = QWidget()
        laser_gui.setLayout(layout)
        laser_gui.setWindowTitle("MOPA")
        laser_gui.destroyed.connect(self.if_window_closed)

        self.start_regulation()
        return laser_gui

    def if_window_closed(self):
        if self._timer is not None:
            self._timer.stop()
        try:
            self.eom.stop()
        except Exception:
            pass

    def start_regulation(self):
        self.eom.start()
        self._timer = QTimer()
        self._timer.timeout.connect(self.set_gui_values)
        self._timer.start(100)
        self.start_button.setStyleSheet("background-color: yellow")

    def set_gui_values(self):
        voltage, bias, running = self.eom.get_value()
        self.start_button.setStyleSheet("background-color: green" if running else "background-color: red")
        self.start_button.setText(f"PD: {voltage:.3f}  B: {bias:.3f}")
