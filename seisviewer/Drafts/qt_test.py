import os
import PyQt5
from PyQt5 import QtCore


def get_lib_path() -> list:
    return [os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins')]


if __name__ == '__main__':
    QtCore.QCoreApplication.setLibraryPaths(get_lib_path())

