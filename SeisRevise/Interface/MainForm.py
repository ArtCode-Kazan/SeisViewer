from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys
import os

from SeisRevise.Interface.QTForms.MainForm import Ui_MainWindow


class SpectrogramForm(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # вкладка Расчет 2D-спектрограмм
        # ------------------------------------------------------------------
        # событие при нажатии кнопки выбора папки
        self.pbSelectDirectory.clicked.connect(self.select_directory)
        # событие при смене типа файлов
        self.cbFiletype.currentIndexChanged.connect(self.change_file_type)
        # событие при нажатии кнопки расчета
        self.pbCalculate.clicked.connect(self.spectrogram_calc)

    def select_directory(self):
        """
        вкладка Расчет 2D-спектрограмм
        Событие нажатия кнопки выбора папки сверки
        :return: None
        """
        select_directory = QFileDialog.getExistingDirectory(
            None, 'Выберите папку сверки:', 'C:/', QFileDialog.ShowDirsOnly)
        self.leDirectoryPath.setText(select_directory)

    def change_file_type(self):
        """
        вкладка Расчет 2D-спектрограмм
        событие при смене типа файлов
        :return: None
        """
        if self.cbFiletype.currentText() == "Baikal7":
            self.sbSignalFrequency.setDisabled(True)
        else:
            self.sbSignalFrequency.setDisabled(False)

    def spectrogram_calc(self):
        """
        вкладка Расчет 2D-спектрограмм
        событие при нажатии кнопки расчета
        :return: None
        """
        # получение введенных параметров
        # папка с bin-файлами сверки
        directory_path = self.leDirectoryPath.text()
        # тип файлов
        file_type = self.cbFiletype.currentText()
        # тип записи
        record_type = self.leRecordType_2.text()

        # частота записи сигнала
        signal_frequency = None
        if file_type == "Baikal7":
            signal_frequency = None
        else:
            signal_frequency = self.sbSignalFrequency.value()

        # частота ресемплирования сигнала
        resample_frequency = None
        if self.cbNoResampleSignal.isChecked():
            resample_frequency = self.sbSignalFrequency.value()
        else:
            resample_frequency = self.sbResampleFrequency.value()

        # шаг построения спектрограмм (часы)
        time_interval = None
        if self.cbFullSpectrogram.isChecked():
            time_interval = None
        else:
            time_interval = self.dsbTimeInterval.value()

        # список компонент, для которых нужно построить спектрограммы
        components = list()
        if self.cbXComponent.isChecked():
            components.append('X')
        if self.cbYComponent.isChecked():
            components.append('Y')
        if self.cbZComponent.isChecked():
            components.append('Z')

        # окно расчета спектрограмм
        window_size = self.sbWindowSize.value()
        # размер сдвига окна
        noverlap_size = self.sbNoverlapSize.value()
        # минимальная частота визуализации
        min_frequncy = self.sbMinFrequency.value()
        # максимальная частота визуализации
        max_frequency = self.sbMaxFrequency.value()

        # проверка введенных параметров
        errors = list()
        if not os.path.isdir(directory_path):
            errors.append('Неверно указан путь к папкам сверки')

        if record_type not in ['XYZ', 'ZXY']:
            errors.append('Неверно указан тип записи')

        if file_type == 'Baikal8':
            if signal_frequency % resample_frequency != 0:
                errors.append('Неверно указана частота ресемплирования')

        if len(components) == 0:
            errors.append('Не выбрано ни одной компоненты для построения '
                          'спектрограмм')

        if window_size % noverlap_size != 0:
            errors.append('Неверно заданы параметры окна и сдвига окон')

        if len(errors)!=0:
            text='\n'.join(errors)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(text)
            msg.setWindowTitle("Errors")
            msg.exec_()
            pass

        # если ошибок нет, то продолжается дальнейшая работа


def run():
    """
    функция для запуска окна расчета
    :return: None

    """
    app = QApplication(sys.argv)
    form = SpectrogramForm()
    form.show()
    app.exec()

# if __name__ == '__main__':
# app = QApplication(sys.argv)
#     form = SpectrogramForm()
#     form.show()
#     app.exec()
