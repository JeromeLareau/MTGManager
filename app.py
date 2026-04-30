from PySide6.QtWidgets import QApplication
import sys

from db.database import import_bulk, init_db
from ui.main_window import MainWindow

if __name__ == "__main__":
    init_db()
    import_bulk(initial_import=True)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())