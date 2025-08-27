# main.py  (clean and simple)
from qtpy.QtWidgets import QApplication
import sys
from include.eom_gui import EOM_GUI

def main():
    app = QApplication(sys.argv)
    gui = EOM_GUI()
    window = gui.return_window()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()