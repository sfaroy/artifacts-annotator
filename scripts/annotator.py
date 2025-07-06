# src/my_package_name/main.py
from PyQt5.QtWidgets import QApplication
from artifacts_annotator.app import (MainWindow)
import sys

def main() -> None:
    """Entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
