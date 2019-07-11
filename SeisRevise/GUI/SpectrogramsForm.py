import os
from datetime import datetime
from datetime import timedelta

from PyQt5.QtWidgets import *
from PyQt5.uic import *
from PyQt5.QtCore import QThread, pyqtSignal

from SeisCore.BinaryFile.BinaryFile import BinaryFile
from SeisCore.Functions.Spectrogram import create_spectrogram
from SeisCore.Plotting.Plotting import plot_signal

from SeisRevise.GUI.Dialogs import show_folder_dialog


class External(QThread):
    finished_percent = pyqtSignal(float)
    parts_count = None
    files_info = None
    parameters=None

    def run(self):
        finished_parts_count = 0
        params = self.parameters
        for index, key in enumerate(self.files_info):
            cur_file_data = self.files_info[key]
            dt_start = cur_file_data['datetime_start']
            dt_stop = cur_file_data['datetime_stop']
            record_type = cur_file_data['record_type']
            file_path = cur_file_data['path']
            file_name = os.path.basename(file_path).split('.')[0]

            cross_dt_start = max(params['dt_start'], dt_start)
            cross_dt_stop = min(params['dt_stop'], dt_stop)

            bin_data = BinaryFile()
            bin_data.path = file_path
            bin_data.record_type = record_type
            bin_data.use_avg_values = True
            bin_data.resample_frequency = params['resample_frequency']

            part_count = int(round(
                (cross_dt_stop - cross_dt_start).total_seconds() // (
                        params['interval_size'] * 60)))

            for i in range(part_count):
                read_dt_start = cross_dt_start + timedelta(
                    minutes=params['interval_size'] * i)
                read_dt_stop = read_dt_start + timedelta(
                    minutes=params['interval_size'])

                read_dt_start_label = datetime.strftime(read_dt_start,
                                                        '%Y-%m-%d_%H-%M-%S')

                bin_data.read_date_time_start = read_dt_start
                bin_data.read_date_time_stop = read_dt_stop

                signals = bin_data.signals

                for component in params['components']:
                    component_signal=signals[:, record_type.index(component)]
                    output_folder = os.path.join(params['output_folder'],
                                                 file_name,
                                                 f'{component}Component')

                    if not os.path.exists(output_folder):
                        os.makedirs(output_folder)

                    output_name = f'SP_{component}Component_{file_name}_{read_dt_start_label}'
                    create_spectrogram(signal_data=component_signal,
                                       frequency=params['resample_frequency'],
                                       output_folder=output_folder,
                                       output_name=output_name,
                                       min_frequency=params['visual_min_frequency'],
                                       max_frequency=params['visual_max_frequency'],
                                       time_start=0)

                    output_name = f'SIG_{component}Component_{file_name}_{read_dt_start_label}'
                    plot_signal(time_start_sec=0,
                                frequency=params['resample_frequency'],
                                signal=component_signal, label=output_name,
                                output_folder=output_folder,
                                output_name=output_name)
                finished_parts_count += 1
                percent_value = finished_parts_count / self.parts_count * 100
                self.finished_percent.emit(percent_value)


class SpectrogramsForm:
    def __init__(self, parent):
        self.__window_type = 'spectrograms_form'
        self.__parent = parent

        self.__parameters = None
        self.__calc_thread = None

        self.__window = QMainWindow()
        self.__forms_folder = parent.form_folder
        ui_path = os.path.join(self.__forms_folder, 'SpectrogramsForm.ui')
        self.__ui = loadUi(ui_path, self.__window)

        self.__ui.pbOpenFolder.clicked.connect(self.set_export_folder)
        self.__ui.pbStartProcess.clicked.connect(self.processing)

    @property
    def window(self):
        return self.__window

    @property
    def parent(self):
        return self.__parent

    @property
    def files_info(self):
        return self.parent.files_info

    @property
    def ui(self):
        return self.__ui

    def set_export_folder(self):
        self.ui.leFolderPath.clear()
        path = show_folder_dialog()
        if path is not None:
            self.ui.leFolderPath.setText(path)

    def collect_parameters(self):
        ui = self.ui
        params = dict()
        params['resample_frequency'] = ui.sbResampleFrequency.value()
        params['dt_start'] = ui.dtStartTime.dateTime().toPyDateTime()
        params['dt_stop'] = ui.dtStopTime.dateTime().toPyDateTime()
        params['interval_size'] = ui.sbIntervalSize.value()
        components = list()
        if ui.cbXComponent.isChecked():
            components.append('X')
        if ui.cbYComponent.isChecked():
            components.append('Y')
        if ui.cbZComponent.isChecked():
            components.append('Z')
        params['components'] = components
        params['visual_min_frequency'] = ui.dsMinFrequency.value()
        params['visual_max_frequency'] = ui.dsMaxFrequency.value()
        params['output_folder'] = ui.leFolderPath.text()
        self.__parameters = params

    def thread_function(self):
        if self.__calc_thread is not None and self.__calc_thread.isFinished():
            self.__calc_thread = None

        if self.__calc_thread is not None:
            return

        self.set_progress_value(0)
        self.collect_parameters()
        params=self.__parameters

        part_count = 0
        files_for_processing = dict()
        for key in self.files_info:
            cur_file_data = self.files_info[key]
            dt_start = cur_file_data['datetime_start']
            dt_stop = cur_file_data['datetime_stop']

            cross_dt_start = max(params['dt_start'], dt_start)
            cross_dt_stop = min(params['dt_stop'], dt_stop)
            if cross_dt_stop <= cross_dt_start:
                continue
            files_for_processing[key] = self.files_info[key]
            part_count += int(round(
                (cross_dt_stop - cross_dt_start).total_seconds() // (
                        params['interval_size'] * 60)))

        self.__calc_thread = External()
        self.__calc_thread.files_info = files_for_processing
        self.__calc_thread.parts_count = part_count
        self.__calc_thread.parameters = self.__parameters
        self.__calc_thread.finished_percent.connect(self.set_progress_value)
        self.__calc_thread.start()

    def set_progress_value(self, value):
        self.ui.progressBar.setValue(value)

    def processing(self):
        self.thread_function()
