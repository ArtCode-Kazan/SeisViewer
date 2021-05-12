# Импортируем системый модуль для корректного закрытия программы
import sys
# Импортируем минимальный набор виджетов
from PyQt5.QtWidgets import QApplication, QWidget
# Импортируем созданный нами класс со слотами
from test_slots import MainWindowSlots


# Создаём ещё один класс, наследуясь от класса со слотами
class MainWindow(MainWindowSlots):

    # При инициализации класса нам необходимо выпонить некоторые операции
    def __init__(self, form):
        # Сконфигурировать интерфейс методом из базового класса Ui_Form
        self.setupUi(form)
        # Подключить созданные нами слоты к виджетам
        self.connect_slots()

    # Подключаем слоты к виджетам
    def connect_slots(self):
        self.pushButton.clicked.connect(self.set_time)
        return None


import os
import PyQt5
from PyQt5 import QtCore


def get_lib_path() -> list:
    return [os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins')]


if __name__ == '__main__':
    # Создаём экземпляр приложения
    QtCore.QCoreApplication.setLibraryPaths(get_lib_path())
    app = QApplication(sys.argv)
    # Создаём базовое окно, в котором будет отображаться наш UI
    window = QWidget()
    # Создаём экземпляр нашего UI
    ui = MainWindow(window)
    # Отображаем окно
    window.show()
    # Обрабатываем нажатие на кнопку окна "Закрыть"
    sys.exit(app.exec_())