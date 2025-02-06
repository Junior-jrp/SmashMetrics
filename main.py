import sys
from PySide6.QtWidgets import QApplication
from Telas import SmashMetricsUI
from Funcionalidades import Funcionalidades

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmashMetricsUI()

    # Integrar funcionalidades
    window.funcionalidades = Funcionalidades()

    window.show()
    sys.exit(app.exec())
