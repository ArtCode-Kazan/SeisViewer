import os
import sys
from datetime import datetime

from PyQt5.QtWidgets import *

from SeisRevise.Interface.QTForms.MainForm import Ui_MainWindow

from SeisPars import rsf7
from SeisPars import rsf8
from SeisRevise.Functions.MomentsIntervals import moments_intervals
from SeisRevise.Functions.PlottingSpectrogram import plot_spectrogram


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
        # событие при нажатии на флаг не ресемплировать сигнал
        self.cbNoResampleSignal.clicked.connect(self.click_no_resample_signal)
        # событие при нажатии на флаг строить спектрограмму полностью
        self.cbFullSpectrogram.clicked.connect(self.click_full_spectrogram)
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

    def click_no_resample_signal(self):
        """
        вкладка Расчет 2D-спектрограмм
        событие при нажатии на флаг не ресемплировать сигнал
        :return: None
        """
        if self.cbNoResampleSignal.isChecked():
            self.sbResampleFrequency.setDisabled(True)
        else:
            self.sbResampleFrequency.setDisabled(False)

    def click_full_spectrogram(self):
        """
        вкладка Расчет 2D-спектрограмм
        событие при нажатии на флаг строить спектрограмму полностью
        :return: None
        """
        if self.cbFullSpectrogram.isChecked():
            self.dsbTimeInterval.setDisabled(True)
        else:
            self.dsbTimeInterval.setDisabled(False)

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
        if file_type == "Baikal7":
            signal_frequency = None
        if file_type == 'Baikal8':
            signal_frequency = self.sbSignalFrequency.value()

        # частота ресемплирования сигнала
        if self.cbNoResampleSignal.isChecked():
            if file_type == 'Baikal7':
                resample_frequency = None
            if file_type == 'Baikal8':
                resample_frequency = signal_frequency
        else:
            resample_frequency = self.sbResampleFrequency.value()

        # шаг построения спектрограмм (часы)
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

        if len(errors) != 0:
            text = '\n'.join(errors)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(text)
            msg.setWindowTitle("Errors")
            msg.exec_()
            return False

        # если ошибок нет, то продолжается дальнейшая работа
        self.teLog.clear()
        self.teLog.append('{}\tНачат процесс построения '
                          'спектрограмм...'.format(datetime.now()))
        QApplication.processEvents()

        # анализ папки с данными сверки - получение полных путей к bin-файлам
        bin_files_list = list()
        folder_struct = os.walk(directory_path)
        for root_folder, folders, files in folder_struct:
            for file in files:
                name, extention = file.split('.')
                # поиск bin-файла
                if extention in ['00', 'xx']:
                    # получение полного пути к bin-файлу
                    bin_file_path = os.path.join(root_folder, file)
                    bin_files_list.append(bin_file_path)

        if len(bin_files_list) == 0:
            self.teLog.append('{}\tАнализ папки завершен. Bin-файлов '
                              'не найдено. Обработка прервана'.format(
                datetime.now()))
            QApplication.processEvents()
            return False

        # Если bin-файлы есть, то работа продолжается
        self.teLog.append('{}\tАнализ папки завершен. Всего найдено {} файлов'
                          ''.format(datetime.now(), len(bin_files_list)))
        QApplication.processEvents()

        # создание папки с результатами расчетов
        for i in range(99):
            folder_name = '2DSpectrograms_vers_{}'.format(i + 1)
            folder_with_result = os.path.join(directory_path, folder_name)
            if not os.path.exists(folder_with_result):
                os.mkdir(folder_with_result)
                break

        # запись файла с параметрами вычислений
        option_file_name = 'options.dat'
        option_file_path = os.path.join(folder_with_result, option_file_name)
        f = open(option_file_path, 'w')
        s = '[Revise Folder]={}\n'.format(directory_path)
        f.write(s)
        s = '[File Types]={}\n'.format(file_type)
        f.write(s)
        s = '[Record Type]={}\n'.format(record_type)
        f.write(s)
        s = '[Signal Frequency, Hz]={}\n'.format(signal_frequency)
        f.write(s)
        s = '[Resample Frequency, Hz]={}\n'.format(resample_frequency)
        f.write(s)
        s = '[Time Interval, Hour]={}\n'.format(time_interval)
        f.write(s)
        s = '[X Component]={}\n'.format(self.cbXComponent.isChecked())
        f.write(s)
        s = '[Y Component]={}\n'.format(self.cbYComponent.isChecked())
        f.write(s)
        s = '[Z Component]={}\n'.format(self.cbZComponent.isChecked())
        f.write(s)
        s = '[Windows Size, Moment]={}\n'.format(window_size)
        f.write(s)
        s = '[Noverlap Size, Moment]={}\n'.format(noverlap_size)
        f.write(s)
        s = '[Min frequency visualize, Hz]={}\n'.format(min_frequncy)
        f.write(s)
        s = '[Max frequency visualize, Hz]={}\n'.format(max_frequency)
        f.write(s)
        f.close()

        # парсинг типа записи
        x_channel_number = record_type.index('X')
        y_channel_number = record_type.index('Y')
        z_channel_number = record_type.index('Z')

        # запуск процесса построения спектрограмм
        for file_path in bin_files_list:
            # считывание файла
            if file_type == 'Baikal7':
                bin_data = rsf7(file_path=file_path,
                                resample_frequency=resample_frequency)
            if file_type == 'Baikal8':
                bin_data = rsf8(file_path=file_path,
                                signal_frequency=signal_frequency,
                                resample_frequency=resample_frequency)

            # получение имени файла
            bin_file_name = os.path.split(file_path)[-1].split('.')[0]

            # проверка, что данные считались корректно
            if bin_data is not None:
                self.teLog.append(
                    '{}\tФайл {} успешно считан'.format(datetime.now(), bin_file_name))
                QApplication.processEvents()
            else:
                self.teLog.append(
                    '{}\tОшибка считывания файла {} - исключен из '
                    'обработки'.format(
                        datetime.now(), bin_file_name))
                QApplication.processEvents()
                continue


            # получение границ отсчетов для каждого временного интервала
            # в случае, если временной интервал задан
            if time_interval is not None:
                time_steps = moments_intervals(
                    array_length=bin_data.signals.shape[0],
                    frequency=bin_data.frequency,
                    step_time=time_interval)
            # в случае, если временной интервал НЕ задан
            else:
                time_steps = moments_intervals(
                    array_length=bin_data.signals.shape[0],
                    frequency=bin_data.frequency,
                    step_time=None)

            # обработка идет по каждому временному интервалу
            for left_edge, right_edge in time_steps:
                # выборка сигнала (всех трех компонент) для текущего
                # временного интервала
                selection_signal = bin_data.signals[left_edge:right_edge,:]
                # вычисление времени в секундах начала временного интервала
                start_time_sec = left_edge//bin_data.frequency
                # вычисление времени в секундах конца временного интервала
                end_time_sec = right_edge//bin_data.frequency

                # построение спектрограмм для компоненты X (если она выбрана)
                if self.cbXComponent.isChecked():
                    # имя для png-файла складывается как имя
                    # bin-файла+начальная секудна интервала+конечная секунда
                    #  интервала
                    output_file_name='X_Component_{}_{}-{}_sec'.format(
                        bin_file_name,start_time_sec,end_time_sec)
                    plot_spectrogram(
                        signal=selection_signal[:,x_channel_number],
                        frequency=bin_data.frequency,
                        window_size=window_size,
                        noverlap_size=noverlap_size,
                        min_frequency_visulize=min_frequncy,
                        max_frequency_visualize=max_frequency,
                        output_folder=folder_with_result,
                        output_name=output_file_name,
                        time_start_sec=start_time_sec
                    )

                # построение спектрограмм для компоненты Y (если она выбрана)
                if self.cbYComponent.isChecked():
                    # имя для png-файла складывается как имя
                    # bin-файла+начальная секудна интервала+конечная секунда
                    #  интервала
                    output_file_name='Y_Component_{}_{}-{}_sec'.format(
                        bin_file_name,start_time_sec,end_time_sec)
                    plot_spectrogram(
                        signal=selection_signal[:,y_channel_number],
                        frequency=bin_data.frequency,
                        window_size=window_size,
                        noverlap_size=noverlap_size,
                        min_frequency_visulize=min_frequncy,
                        max_frequency_visualize=max_frequency,
                        output_folder=folder_with_result,
                        output_name=output_file_name,
                        time_start_sec=start_time_sec
                    )

                # построение спектрограмм для компоненты Z (если она выбрана)
                if self.cbZComponent.isChecked():
                    # имя для png-файла складывается как имя
                    # bin-файла+начальная секудна интервала+конечная секунда
                    #  интервала
                    output_file_name='Z_Component_{}_{}-{}_sec'.format(
                        bin_file_name,start_time_sec,end_time_sec)
                    plot_spectrogram(
                        signal=selection_signal[:,x_channel_number],
                        frequency=bin_data.frequency,
                        window_size=window_size,
                        noverlap_size=noverlap_size,
                        min_frequency_visulize=min_frequncy,
                        max_frequency_visualize=max_frequency,
                        output_folder=folder_with_result,
                        output_name=output_file_name,
                        time_start_sec=start_time_sec
                    )
                self.teLog.append(
                    '{}\t    - Спектрограммы {} - {} сек построены'.format(
                    datetime.now(), start_time_sec, end_time_sec))
                QApplication.processEvents()
        self.teLog.append('{}\t обработка завершена'.format(datetime.now()))
        QApplication.processEvents()

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
