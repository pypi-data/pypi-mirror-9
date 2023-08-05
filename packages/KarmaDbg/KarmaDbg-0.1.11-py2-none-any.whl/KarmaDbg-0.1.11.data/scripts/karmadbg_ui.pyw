

from PySide.QtGui import QApplication

from karmadbg.uicore.uimanager import UIManager

def main():
    app = QApplication( [] )
    uimanager = UIManager(app)
    exitres = app.exec_()

if __name__ == "__main__":
    main()
