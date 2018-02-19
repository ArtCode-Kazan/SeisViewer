import os
import sys
from datetime import datetime
import numpy as np
from numpy.fft import rfftfreq
import re

from PyQt5.QtWidgets import *

from SeisRevise.Interface.QTForms.MainForm import Ui_MainWindow

from SeisPars import rsf7
from SeisPars import rsf8
from SeisPars.Parsers.BinarySeisReader import get_main_header

from SeisCore import average_spectrum
from SeisCore import checking_name
from SeisCore.VisualFunctions.Colors import random_hex_colors_generators

from SeisRevise.Functions.MomentsIntervals import moments_intervals
from SeisRevise.Functions.PlottingSpectrogram import plot_spectrogram
from SeisRevise.Functions.CrossCorrelate import cross_correlation
from SeisRevise.Functions.WriteSelectionSignal import write_part_of_signal
from SeisRevise.Functions.PlottingSignal import drawing_signal
from SeisRevise.Functions.PlottingSpectrum import drawing_spectrum
from SeisRevise.Functions.PlottingAllSpectrums import \
    drawing_all_smooth_cumulative_spectrums
from SeisRevise.Functions.CorrelationToFile import correlation_to_file
from SeisRevise.Functions.PlottingCorrelation import drawing_correlation
from SeisRevise.Functions.ExportFolder import export_folder_generate


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

        # вкладка Расчет корреляций приборов и кумулятивных спектров
        # ------------------------------------------------------------------
        # событие при нажатии кнопки выбора папки
        self.pbOpenFolder.clicked.connect(self.select_directory2)
        # событие при смене типа файлов
        self.cbFiletype_2.currentIndexChanged.connect(self.change_file_type2)
        # событие при нажатии на флаг не ресемплировать сигнал
        self.cbNoResampleSignal_2.clicked.connect(
            self.click_no_resample_signal2)
        # событие при нажатии на флаг использовать медианный фильтр
        self.cbIsUsingMedianFilter.clicked.connect(self.click_using_median_f)
        # событие при нажатии на флаг использовать marmett фильтр
        self.cbIUsingMarmettFilter.clicked.connect(self.click_using_marmett_f)
        # событие при нажатии кнопки расчета
        self.pbCalculation.clicked.connect(self.correlation_calc)

    # вкладка Расчет 2D-спектрограмм
    # ------------------------------------------------------------------
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
        record_type = self.cbRecordType.currentText()

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

        # структура папок для экспорта
        if self.rbHourStructure.isChecked():
            export_folder_structure = 'HourStructure'
        if self.rbDeviceStructure.isChecked():
            export_folder_structure = 'DeviceStructure'

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
            # имя папки
            root_folder_name = os.path.basename(root_folder)
            # проверка имени папки на допустимые символы
            if not checking_name(root_folder_name):
                # прерывание расчета в случае неверного имени папки
                self.teLog.append('{}\tНеверное имя папки {} - '
                                  'содержит недопустимые символы. '
                                  'Обработка прервана'.format(
                    datetime.now(),root_folder_name))
                QApplication.processEvents()
                return None

            for file in files:
                name, extention = file.split('.')
                # поиск bin-файла
                if extention in ['00', 'xx']:
                    # проверка, что имя файла и папки совпадают
                    if name == root_folder_name:
                        # получение полного пути к bin-файлу
                        bin_file_path = os.path.join(root_folder, file)
                        bin_files_list.append(bin_file_path)
                    else:
                        # прерывание расчета в случае неверной структуры папок
                        self.teLog.append('{}\tНеверная структура '
                                          'папок. Не совпадают имена '
                                          'папок и файлов'.format(
                            datetime.now()))
                        QApplication.processEvents()
                        return None

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

        # запись файла с параметрами вычислений
        option_file_name = 'options_2DSpectrums.dat'
        option_file_path = os.path.join(directory_path, option_file_name)
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
                    '{}\tФайл {} успешно считан'.format(datetime.now(),
                                                        bin_file_name))
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
                selection_signal = bin_data.signals[left_edge:right_edge, :]
                # вычисление времени в секундах начала временного интервала
                start_time_sec = left_edge // bin_data.frequency
                # вычисление времени в секундах конца временного интервала
                end_time_sec = right_edge // bin_data.frequency

                # Построение спектрограмм по компонентам
                for component in components:
                    # имя для png-файла складывается как название компоненты
                    #  имя bin-файла+начальная секудна интервала+конечная
                    # секунда интервала
                    output_file_name = '{}_Component_{}_{}-{}_sec'.format(
                        component, bin_file_name, start_time_sec, end_time_sec)

                    # генерация пути к папке, куда будет сохраняться результат
                    # в зависимости от типа структуры папок экспорта
                    export_folder = export_folder_generate(
                        root_folder=directory_path,
                        structure_type=export_folder_structure,
                        component=component,
                        bin_file_name=bin_file_name,
                        start_time_sec=start_time_sec,
                        end_time_sec=end_time_sec)

                    # проверка создания каталога экспорта
                    if export_folder_structure is None:
                        self.teLog.append(
                            '{}\t Ошибка создания каталога экспорта'.format(
                                datetime.now()))
                        QApplication.processEvents()
                        return None

                    # определение номера канала компоненты исходя из текущей
                    #  компоненты
                    if component == 'X':
                        channel_number = x_channel_number
                    if component == 'Y':
                        channel_number = y_channel_number
                    if component == 'Z':
                        channel_number = z_channel_number

                    # построение спектрограммы
                    is_correct = plot_spectrogram(
                        signal=selection_signal[:, channel_number],
                        frequency=bin_data.frequency,
                        window_size=window_size,
                        noverlap_size=noverlap_size,
                        min_frequency_visulize=min_frequncy,
                        max_frequency_visualize=max_frequency,
                        output_folder=export_folder,
                        output_name=output_file_name,
                        time_start_sec=start_time_sec
                    )

                    # проверка создания спектрограммы
                    if not is_correct:
                        self.teLog.append(
                            '{}\t    - Ошибка построения '
                            'спектрограммы: возможно, неверные '
                            'параметры построения'.format(datetime.now()))
                        QApplication.processEvents()
                        break

                self.teLog.append(
                    '{}\t    - Спектрограммы {} - {} сек построены'.format(
                        datetime.now(), start_time_sec, end_time_sec))
                QApplication.processEvents()
        self.teLog.append('{}\t Обработка завершена'.format(datetime.now()))
        QApplication.processEvents()

    # вкладка Расчет корреляций приборов и кумулятивных спектров
    # ------------------------------------------------------------------
    def select_directory2(self):
        """
        вкладка Расчет корреляций приборов и кумулятивных спектров
        Событие нажатия кнопки выбора папки сверки
        :return: None
        """
        select_directory = QFileDialog.getExistingDirectory(
            None, 'Выберите папку сверки:', 'C:/', QFileDialog.ShowDirsOnly)
        self.leReviseFolder.setText(select_directory)

    def change_file_type2(self):
        """
        вкладка Расчет корреляций приборов и кумулятивных спектров
        событие при смене типа файлов
        :return: None
        """
        if self.cbFiletype_2.currentText() == "Baikal7":
            self.sbSignalFrequency_3.setDisabled(True)
        else:
            self.sbSignalFrequency_3.setDisabled(False)

    def click_no_resample_signal2(self):
        """
        вкладка Расчет корреляций приборов и кумулятивных спектров
        событие при нажатии на флаг не ресемплировать сигнал
        :return: None
        """
        if self.cbNoResampleSignal_2.isChecked():
            self.sbResampleFrequency_3.setDisabled(True)
        else:
            self.sbResampleFrequency_3.setDisabled(False)

    def click_using_median_f(self):
        """
        вкладка Расчет корреляций приборов и кумулятивных спектров
        событие при нажатии на флаг использовать медианный фильтр
        :return: None
        """
        if self.cbIsUsingMedianFilter.isChecked():
            self.sbMedianFilterValue.setDisabled(False)
        else:
            self.sbMedianFilterValue.setDisabled(True)

    def click_using_marmett_f(self):
        """
        вкладка Расчет корреляций приборов и кумулятивных спектров
        событие при нажатии на флаг использовать marmett фильтр
        :return: None
        """
        if self.cbIUsingMarmettFilter.isChecked():
            self.sbMarmettFilterValue.setDisabled(False)
        else:
            self.sbMarmettFilterValue.setDisabled(True)

    def correlation_calc(self):
        """
        вкладка Расчет корреляций приборов и кумулятивных спектров
        событие при нажатии кнопки расчета кумулятивных спектров и корреляций
        :return: None
        """
        # получение введенных параметров
        # папка с bin-файлами сверки
        directory_path = self.leReviseFolder.text()
        # тип файлов
        file_type = self.cbFiletype_2.currentText()
        # тип записи
        record_type = self.cbRecordType_2.currentText()

        # частота записи сигнала
        if file_type == "Baikal7":
            signal_frequency = None
        if file_type == 'Baikal8':
            signal_frequency = self.sbSignalFrequency_3.value()

        # частота ресемплирования сигнала
        if self.cbNoResampleSignal_2.isChecked():
            if file_type == 'Baikal7':
                resample_frequency = None
            if file_type == 'Baikal8':
                resample_frequency = signal_frequency
        else:
            resample_frequency = self.sbResampleFrequency.value()

        # список компонент, для которых нужно построить спектрограммы
        components = list()
        if self.cbXComponent_2.isChecked():
            components.append('X')
        if self.cbYComponent_2.isChecked():
            components.append('Y')
        if self.cbZComponent_2.isChecked():
            components.append('Z')

        # интервал чистого участка, секунды
        left_time_edge = self.sbTimeBegin.value()
        right_time_edge = self.sbTimeEnd.value()

        # размер окна расчета
        window_size = self.sbWindowSize_2.value()
        # размер сдвига окна
        noverlap_size = self.sbNoverlapSize_2.value()

        # параметр медианного фильтра
        if self.cbIsUsingMedianFilter.isChecked():
            median_filter_parameter = self.sbMedianFilterValue.value()
        else:
            median_filter_parameter = None

        # параметр marmett фильтра
        if self.cbIUsingMarmettFilter.isChecked():
            marmett_filter_parameter = self.sbMarmettFilterValue.value()
        else:
            marmett_filter_parameter = None

        # минимальная частота для расчета корреляции
        min_frequency_correlation = self.dsbMinFrequencyCorrelation.value()
        # максимальная частота для расчета корреляции
        max_frequency_correlation = self.dsbMaxFrequencyCorrelation.value()

        # минимальная частота визуализации
        min_frequency_visuality = self.dsbMinFrequencyVisualize.value()
        # максимальная частота визуализации
        max_frequency_visuality = self.dsbMaxFrequencyVisualize.value()

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

        if left_time_edge >= right_time_edge:
            errors.append('Неверно указаны границы чистого участка')

        if window_size % noverlap_size != 0:
            errors.append('Неверно заданы параметры окна и сдвига окон')

        if median_filter_parameter is None and marmett_filter_parameter is \
                None:
            errors.append('Не указан ни один из способов фильтрации')

        if min_frequency_correlation >= max_frequency_correlation:
            errors.append('Неверно указаны пределы частот для расчета '
                          'корреляции')

        if min_frequency_visuality >= max_frequency_visuality:
            errors.append('Неверно указаны пределы частот для визуализации '
                          'спектров')

        # Вывод ошибок, если они есть
        if len(errors) != 0:
            text = '\n'.join(errors)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(text)
            msg.setWindowTitle("Errors")
            msg.exec_()
            return None

        # если ошибок нет, то продолжается дальнейшая работа
        self.teLog_2.clear()
        self.teLog_2.append(
            '{}\tНачат процесс расчета спектров и корреляций...'.format(
                datetime.now()))
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
            self.teLog_2.append('{}\tАнализ папки завершен. Bin-файлов '
                                'не найдено. Обработка прервана'.format(
                datetime.now()))
            QApplication.processEvents()
            return None

        # Если bin-файлы есть, то работа продолжается
        self.teLog_2.append('{}\tАнализ папки завершен. Всего найдено {} '
                            'файлов'.format(datetime.now(),
                                            len(bin_files_list)))
        QApplication.processEvents()

        # создание папки с результатами расчетов
        for i in range(99):
            folder_name = 'Spectrums_vers_{}'.format(i + 1)
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
        s = '[Left Time Edge, seconds]={}\n'.format(left_time_edge)
        f.write(s)
        s = '[Right Time Edge, seconds]={}\n'.format(right_time_edge)
        f.write(s)
        s = '[X Component]={}\n'.format(self.cbXComponent_2.isChecked())
        f.write(s)
        s = '[Y Component]={}\n'.format(self.cbYComponent_2.isChecked())
        f.write(s)
        s = '[Z Component]={}\n'.format(self.cbZComponent_2.isChecked())
        f.write(s)
        s = '[Windows Size, Moment]={}\n'.format(window_size)
        f.write(s)
        s = '[Noverlap Size, Moment]={}\n'.format(noverlap_size)
        f.write(s)
        s = '[Min frequency correlation, Hz]={}\n'.format(
            min_frequency_correlation)
        f.write(s)
        s = '[Max frequency correlation, Hz]={}\n'.format(
            max_frequency_correlation)
        f.write(s)
        s = '[Min frequency visualize, Hz]={}\n'.format(
            min_frequency_visuality)
        f.write(s)
        s = '[Max frequency visualize, Hz]={}\n'.format(
            max_frequency_visuality)
        f.write(s)
        f.close()

        # парсинг типа записи
        x_channel_number = record_type.index('X')
        y_channel_number = record_type.index('Y')
        z_channel_number = record_type.index('Z')

        # расчет длины выборки сигнала в отсчетах

        # если сигнал не будет ресемплироваться, и при этом формат файла
        # Baikal-7, то необходимо извлечь первоначальную частоту записи
        # сигнала из главной шапки файла для последующих расчетов. Для этого
        # берется первый файл из списка bin-файлов
        if self.cbNoResampleSignal_2.isChecked():
            if file_type == 'Baikal7':
                # получение главного заголовка из первого bin-файла в списке
                main_header = get_main_header(file_path=bin_files_list[0])
                # если main_header=None, то первым попался файл не формата
                # Baikal-7. Сообщение об ошибке
                if main_header is not None:
                    resample_frequency = main_header['frequency']
                else:
                    self.teLog_2.append('{}\tОшибка: в папке есть файлы '
                                        'другого типа (Baikal-8). Обработка '
                                        'невозможна'.format(datetime.now(),
                                                            len(
                                                                bin_files_list)))
                    QApplication.processEvents()
                    return None

        # расчет длины выборки чистого сигнала в отсчетах
        left_edge = left_time_edge * resample_frequency
        right_edge = right_time_edge * resample_frequency
        selection_signal_length = right_edge - left_edge

        self.teLog_2.append('{}\tДлина выборки сигналов в отсчетах: {}'.format(
            datetime.now(), selection_signal_length))
        QApplication.processEvents()

        # создание пустого массива для хранения будущих выборок сигналов
        # получается трехмерная матрица с размерами:
        # 3 или 2 или 1 - количество анализируемых компонент
        # selection_signal_length - длина сигнала (по сути строки подматрицы)
        # bin_files_count - количество файлов (по сути столбцы подматрицы)
        component_count = len(components)
        bin_files_count = len(bin_files_list)
        selection_signals = np.empty(
            (component_count, selection_signal_length, bin_files_count),
            dtype=np.int32)

        # запуск процесса извлечения выборок сигналов
        for file_path in bin_files_list:
            if file_type == 'Baikal7':
                bin_data = rsf7(file_path=file_path,
                                resample_frequency=resample_frequency,
                                start_sec=left_time_edge,
                                end_sec=right_time_edge)
            if file_type == 'Baikal8':
                bin_data = rsf8(file_path=file_path,
                                signal_frequency=signal_frequency,
                                resample_frequency=resample_frequency,
                                start_sec=left_time_edge,
                                end_sec=right_time_edge)

            # получение имени файла
            bin_file_name = os.path.split(file_path)[-1].split('.')[0]

            self.teLog_2.append('{}\tФайл {} успешно считан'.format(
                datetime.now(), bin_file_name))
            QApplication.processEvents()

            # заполнение общего массива выборок
            column_number = 0  # переменная для вычисления номера столбца
            # матрицы, так как некоторые компоненты (X, Y,Z) могут быть
            # исключены из анализа
            if 'X' in components:
                column_number += 1
                selection_signals[column_number - 1, :, bin_files_list.index(
                    file_path)] = \
                    bin_data.signals[:, x_channel_number]

            if 'Y' in components:
                column_number += 1
                selection_signals[column_number - 1, :, bin_files_list.index(
                    file_path)] = \
                    bin_data.signals[:, y_channel_number]

            if 'Z' in components:
                column_number += 1
                selection_signals[column_number - 1, :, bin_files_list.index(
                    file_path)] = \
                    bin_data.signals[:, z_channel_number]

        self.teLog_2.append('{}\tВыборка участков сигналов завершена'.format(
            datetime.now()))
        QApplication.processEvents()

        # создание массива для сохранения данных осредненных спектров с
        # размерами:
        # component_count - количество анализируемых компонент
        # 2 - количество типов спектров (сглаженный и несглаженный)
        # frequency_count - длина частотного ряда (по сути строки
        # подматрицы) как вычислятся см. в модуле
        # SeisCore.MSICore.CalcFunctions.Spectrum.py
        # bin_files_count - количество bin-файлов (по сути столбцы
        # подматрицы)

        # генерация ряда частот для кумулятивных спектров
        frequencies_list = rfftfreq(window_size, 1. / resample_frequency)
        frequency_count = frequencies_list.shape[0]

        averspectrum_data = np.empty(
            (component_count, 2, frequency_count, bin_files_count),
            dtype=np.float32)

        # расчет осредненных спектров с параметрами сглаживания и без
        # по каждой компоненте
        for component in range(component_count):
            for file_number in range(bin_files_count):
                signal = selection_signals[component, :, file_number]
                # расчет осредненного спектра без параметров сглаживания
                av_spec_simple_component = average_spectrum(
                    signal=signal,
                    frequency=resample_frequency,
                    window=window_size,
                    overlap=noverlap_size,
                    med_filtr=None,
                    marmett_filtr=None)

                # расчет осредненного спектра с параметрами сглаживания
                av_spec_smooth_component = average_spectrum(
                    signal=signal,
                    frequency=resample_frequency,
                    window=window_size,
                    overlap=noverlap_size,
                    med_filtr=median_filter_parameter,
                    marmett_filtr=marmett_filter_parameter)

                # запись несглаженного осредненного спектра
                averspectrum_data[component, 0, :, file_number] = \
                    av_spec_simple_component[:, 1]

                # запись сглаженного осредненного спектра
                averspectrum_data[component, 1, :, file_number] = \
                    av_spec_smooth_component[:, 1]

        self.teLog_2.append(
            '{}\tРасчет осредненных спектров завершен'.format(datetime.now()))
        QApplication.processEvents()

        # расчет коэф-тов корреляции для каждой компоненты и для каждой пары
        #  приборов
        result_correlate_matrix = np.empty(
            (3, bin_files_count, bin_files_count), dtype=np.float32)
        for component in range(component_count):
            result_correlate_matrix[component, :, :] = cross_correlation(
                frequency=frequencies_list,
                f_min_analysis=min_frequency_correlation,
                f_max_analysis=max_frequency_correlation,
                amplitudes=averspectrum_data[component, 1, :, :])

        self.teLog_2.append('{}\tРасчет корреляционной матрицы '
                            'завершен'.format(datetime.now()))
        QApplication.processEvents()

        # процесс экспорта результатов в виде файлов по каждому прибору
        for file_number in range(bin_files_count):
            # получение имени файла
            file_path = bin_files_list[file_number]
            bin_file_name = os.path.split(file_path)[-1].split('.')[0]
            # создание папки для сохранения результатов обработки файла
            file_processing_result_folder = os.path.join(folder_with_result,
                                                         bin_file_name)
            if not os.path.exists(file_processing_result_folder):
                os.mkdir(file_processing_result_folder)

            # выгрузка осуществляется покомпонентно
            self.teLog_2.append('{}\tЭкспорт результатов расчета по {}'
                                '...'.format(
                datetime.now(), bin_file_name))
            QApplication.processEvents()

            for component_number in range(component_count):
                self.teLog_2.append(
                    '{}\t   - Экспорт результатов по {} компоненте...'.format(
                        datetime.now(), components[component_number]))
                QApplication.processEvents()

                # выгрузка чистых участков сигнала в виде файла
                if self.cbWriteSignalToFile.isChecked():
                    dat_file_name = '{}-ClearSignal {} Component'.format(
                        bin_file_name, components[component_number])
                    write_part_of_signal(
                        signal=selection_signals[component_number, :,
                               file_number],
                        left_edge=left_edge,
                        output_folder=file_processing_result_folder,
                        output_name=dat_file_name)
                    self.teLog_2.append(
                        '{}\t        - Экспорт чистого участка '
                        'завершен'.format(
                            datetime.now()))
                    QApplication.processEvents()

                # сохранение чистых участков сигнала в виде графиков
                if self.cbSignalGraph.isChecked():
                    png_file_name = '{}-ClearSignal {} Component Graph'.format(
                        bin_file_name, components[component_number])
                    drawing_signal(left_edge=left_edge,
                                   frequency=resample_frequency,
                                   signal=selection_signals[
                                          component_number, :, file_number],
                                   label=png_file_name,
                                   output_folder=file_processing_result_folder,
                                   output_name=png_file_name)
                    self.teLog_2.append(
                        '{}\t        - Экспорт графика чистого участка '
                        'завершен'.format(
                            datetime.now()))
                    QApplication.processEvents()

                # сохранение рисунков спектров для каждого прибора
                if self.cbOneSpectrums.isChecked():
                    png_file_name = '{}-Average Spectrum {} Component Graph'.format(
                        bin_file_name, components[component_number])
                    drawing_spectrum(frequency=frequencies_list,
                                     spectrum_begin_amplitudes=averspectrum_data[
                                                               component_number,
                                                               0, :,
                                                               file_number],
                                     spectrum_smooth_amplitudes=averspectrum_data[
                                                                component_number,
                                                                1, :,
                                                                file_number],
                                     f_min=min_frequency_visuality,
                                     f_max=max_frequency_visuality,
                                     output_folder=file_processing_result_folder,
                                     output_name=png_file_name)
                    self.teLog_2.append(
                        '{}\t        - Экспорт графика спектров '
                        'завершен'.format(
                            datetime.now()))
                    QApplication.processEvents()

        # сохранение обобщенных данных для всех приборов

        # генерация набора цветов для каждого прибора
        colors = random_hex_colors_generators(bin_files_count)

        # получение списка с именами файлов без расширения
        bin_file_name_list = list()
        for el in bin_files_list:
            el = os.path.split(el)[-1].split('.')[0]
            bin_file_name_list.append(el)

        # сохранение наборов данных идет покомпонентно
        for component_number in range(component_count):
            # сохранение набора осредненных спектров
            if self.cb_generalSpectrums.isChecked():
                file_name = 'SmoothSpectrums {} Component'.format(
                    components[component_number])
                drawing_all_smooth_cumulative_spectrums(
                    spectrums_name_list=bin_file_name_list,
                    frequency=frequencies_list,
                    spectrum_data=averspectrum_data[component_number, 1, :,
                                  :],
                    f_min_visualize=min_frequency_visuality,
                    f_max_visualize=max_frequency_visuality,
                    colors=colors,
                    output_folder=folder_with_result,
                    output_name=file_name)

            # сохранение матрицы коэ-тов корреляции в файл формата dat
            if self.cbCorrelateToFile.isChecked():
                file_name = 'CorrelationMatrix {} Component'.format(
                    components[component_number])
                correlation_to_file(devices=bin_file_name_list,
                                    correlation_matrix=result_correlate_matrix[
                                        component_number],
                                    output_folder=folder_with_result,
                                    output_name=file_name)

            # сохранение коэф-тов корреляции в виде графиков
            if self.cbGraphCorrelate.isChecked():
                file_name = 'Correlations {} Component'.format(
                    components[component_number])
                drawing_correlation(devices=bin_file_name_list,
                                    colors=colors,
                                    correlation_matrix=result_correlate_matrix[
                                        component_number],
                                    output_folder=folder_with_result,
                                    output_name=file_name)
        self.teLog_2.append('Обработка завершена')
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
