import os
from datetime import datetime
from datetime import timedelta
from typing import NamedTuple, List

from PyQt5.QtWidgets import *
from PyQt5.uic import *
from PyQt5.QtCore import QThread, pyqtSignal

from seiscore import BinaryFile
from seiscore import Spectrogram
from seiscore.binaryfile.binaryfile import FileInfo

from seiscore.plotting.plotting import plot_signal

from seisviewer.gui.dialogs import show_folder_dialog
from seisviewer.gui.dialogs import show_message


class FormParameters(NamedTuple):
    resample_frequency: int
    dt_start: datetime
    dt_stop: datetime
    interval_size: int
    components: list
    frequency_limits: list
    is_save_signal_graph: bool
    output_folder: str

    @property
    def is_dates_correct(self):
        return self.dt_start < self.dt_stop


SIGNAL_DURATION_UNIT_SECONDS = 60
MINIMAL_PERCENT_SIGNAL_PART = 0.25
X_COMPONENT, Y_COMPONENT, Z_COMPONENT = 'X', 'Y', 'Z'


class External(QThread):
    finished_percent = pyqtSignal(float)
    status = pyqtSignal(str)
    files_info = List[FileInfo]
    parameters = None   # type: FormParameters

    def run(self):
        params = self.parameters
        part_duration = params.interval_size * SIGNAL_DURATION_UNIT_SECONDS
        total_duration = (params.dt_stop - params.dt_start).total_seconds()
        parts_count = int(total_duration / part_duration) + 1
        total_parts_count = parts_count * len(self.files_info) * \
            len(params.components)
        finished_parts_count = 0

        self.status.emit('Wait please...')
        for file_data in self.files_info:
            file_path = file_data.path

            file_base_name = os.path.basename(file_path).split('.')[0]
            bin_data = BinaryFile(file_path, params.resample_frequency, True)
            for i in range(parts_count):
                read_dt_start = params.dt_start + timedelta(
                    seconds=part_duration * i)
                read_dt_stop = params.dt_start + timedelta(
                    seconds=part_duration * (i + 1))

                read_dt_start = max(read_dt_start, bin_data.datetime_start)
                read_dt_stop = min(read_dt_stop, bin_data.datetime_stop)
                if read_dt_stop > params.dt_stop:
                    read_dt_stop = params.dt_stop

                record_duration = (read_dt_stop - read_dt_start).total_seconds()
                percent_value = record_duration / part_duration
                if percent_value < MINIMAL_PERCENT_SIGNAL_PART:
                    finished_parts_count += len(params.components)
                    percent_value = finished_parts_count / total_parts_count
                    self.finished_percent.emit(percent_value)
                    continue

                read_dt_start_label = \
                    datetime.strftime(read_dt_start, '%Y-%m-%d_%H-%M-%S')

                bin_data.read_date_time_start = read_dt_start
                bin_data.read_date_time_stop = read_dt_stop

                for component in params.components:
                    component_signal = bin_data.read_signal(component)
                    output_folder = \
                        os.path.join(params.output_folder, file_base_name,
                                     f'{component}Component')

                    if not os.path.exists(output_folder):
                        os.makedirs(output_folder)

                    output_name = f'SP_{component}_{file_base_name}_{read_dt_start_label}'
                    sp = Spectrogram(component_signal,
                                     params.resample_frequency,
                                     part_duration * i,
                                     params.frequency_limits)
                    sp.save_spectrogram(output_folder, output_name)

                    if params.is_save_signal_graph:
                        output_name = f'SIG_{component}_{file_base_name}_{read_dt_start_label}'
                        plot_signal(time_start_sec=part_duration * i,
                                    frequency=params.resample_frequency,
                                    signal=component_signal,
                                    label=output_name,
                                    output_folder=output_folder,
                                    output_name=output_name)

                    finished_parts_count += 1
                    percent_value = finished_parts_count / total_parts_count
                    self.finished_percent.emit(percent_value)
        self.status.emit('Done')


class SpectrogramsExportForm:
    def __init__(self, parent):
        self.__parent = parent

        self.__calc_thread = None

        self.__window = QMainWindow()
        self.__forms_folder = parent.parent.forms_folder
        ui_path = os.path.join(self.__forms_folder,
                               'SpectrogramExportForm.ui')
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
    def files_info(self) -> List[FileInfo]:
        return self.parent.files_info

    @property
    def ui(self):
        return self.__ui

    def set_export_folder(self):
        self.ui.leFolderPath.clear()
        path = show_folder_dialog()
        if path is not None:
            self.ui.leFolderPath.setText(path)

    @property
    def form_parameters(self) -> FormParameters:
        ui = self.ui
        components = list()
        if ui.cbXComponent.isChecked():
            components.append(X_COMPONENT)
        if ui.cbYComponent.isChecked():
            components.append(Y_COMPONENT)
        if ui.cbZComponent.isChecked():
            components.append(Z_COMPONENT)
        freq_lims = [ui.dsMinFrequency.value(), ui.dsMaxFrequency.value()]
        params = FormParameters(ui.sbResampleFrequency.value(),
                                ui.dtStartTime.dateTime().toPyDateTime(),
                                ui.dtStopTime.dateTime().toPyDateTime(),
                                ui.sbIntervalSize.value(), components,
                                freq_lims, ui.cbSaveSignalGraph.isChecked(),
                                ui.leFolderPath.text())
        return params

    def thread_function(self):
        if self.__calc_thread is not None and self.__calc_thread.isFinished():
            self.__calc_thread = None

        if self.__calc_thread is not None:
            return
        self.ui.statusBar.showMessage('Wait please...')

        self.set_progress_value(0)
        if len(self.files_info) == 0:
            self.ui.statusBar.showMessage('No data for processing')
            return

        self.__calc_thread = External()
        self.__calc_thread.files_info = self.files_info
        self.__calc_thread.parameters = self.form_parameters
        self.__calc_thread.finished_percent.connect(self.set_progress_value)
        self.__calc_thread.status.connect(self.set_progress_status)
        self.__calc_thread.start()

    def set_progress_value(self, value: float):
        max_value = self.ui.progressBar.maximum()
        value = int(round(value * max_value))
        self.ui.progressBar.setValue(value)

    def set_progress_status(self, value: str):
        self.ui.statusBar.showMessage(value)

    def processing(self):
        if not self.form_parameters.is_dates_correct:
            show_message('Incorrect date interval')
            return

        self.thread_function()

    def set_start_form_state(self, dt_start: datetime, dt_stop: datetime,
                             resample_frequency: int):
        ui = self.ui

        ui.dtStartTime.setMinimumDateTime(dt_start)
        ui.dtStopTime.setMaximumDateTime(dt_stop)

        ui.dtStartTime.setDateTime(dt_start)
        ui.dtStopTime.setDateTime(dt_stop)
        ui.sbResampleFrequency.setValue(resample_frequency)

        ui.sbIntervalSize.setValue(60)
        ui.cbXComponent.setChecked(False)
        ui.cbYComponent.setChecked(False)
        ui.cbZComponent.setChecked(True)
        ui.dsMinFrequency.setValue(0)
        ui.dsMaxFrequency.setValue(20)
        ui.cbSaveSignalGraph.setChecked(True)
        ui.leFolderPath.clear()
        ui.progressBar.setValue(0)
        ui.statusBar.showMessage('Ready')
