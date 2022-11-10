import os

import PyQt5
from PyQt5 import QtCore

from seisviewer.gui.main_window_form import MainWindow


def get_lib_path() -> list:
    return [os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins')]


def run():
    QtCore.QCoreApplication.setLibraryPaths(get_lib_path())
    MainWindow()


if __name__ == '__main__':
    run()
