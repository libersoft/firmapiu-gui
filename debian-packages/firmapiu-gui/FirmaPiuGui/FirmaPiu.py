__author__ = 'svalo'
from FirmaPiu.FirmaPiugui import *
import sys
if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    app = MainWindow()
    app.show()
    qt_app.exec_()
    qt_app.deleteLater()