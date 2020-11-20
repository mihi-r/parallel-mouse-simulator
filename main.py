"""Application for Parallel Mouse Simulation."""

import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget


class App(QWidget):
    """Display window of the main app."""

    def __init__(self):
        """Initiate UI elements."""
        super().__init__()

        label = QLabel('Parallel Mouse Simulator')
        label.show()


if __name__ == '__main__':
    app = QApplication([])
    main = App()
    main.show()
    sys.exit(app.exec_())
