import os
from typing import List
from datetime import datetime
from datetime import timedelta

import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.uic import *

import pyqtgraph as pg

from seiscore import BinaryFile
from seiscore import Spectrogram

from seiscore.binaryfile.binaryfile import FileInfo

from seisviewer.gui.spectrograms_export_form import SpectrogramsExportForm


class FormParameters:
    file_id = 0
    resample_freq = 0
    dt_start = datetime.now()
    dt_stop = datetime.now()
    time_step_minutes = 60
    step_index = 0
    min_freq = 0
    max_freq = 20
    component_id = 0


FORM_FILENAME = 'ViewSpectrogramForm.ui'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class SpectrogramViewForm:
    def __init__(self, parent):
        self.__parent = parent

        self.components = ('X', 'Y', 'Z')
        self.files_info: List[FileInfo] = []
        self.__form_parameters = FormParameters()

        self.signal: List[np.ndarray, np.ndarray, np.ndarray] = []
        self.spectrograms: List[Spectrogram, Spectrogram, Spectrogram] = []

        self.__spectrogram_plot = None

        self.__export_dorm = SpectrogramsExportForm(self)

        self.__window = QMainWindow()
        self.__forms_folder = parent.forms_folder
        ui_path = os.path.join(self.__forms_folder, FORM_FILENAME)
        self.__ui = loadUi(ui_path, self.__window)

        self.__ui.cbFileName.currentTextChanged.connect(self.change_analyzing_file)
        self.__ui.cbResetFields.stateChanged.connect(self.modify_reset_fields)
        self.__ui.dtStartTime.dateTimeChanged.connect(self.modify_time_step)
        self.__ui.dtStopTime.dateTimeChanged.connect(self.modify_time_step)
        self.__ui.sbTimeStepSize.valueChanged.connect(self.modify_step_index)
        self.__ui.bLoadData.clicked.connect(self.load_signal)
        self.__ui.dsMinFrequency.valueChanged.connect(
            self.change_spectrogram_y_limits)
        self.__ui.dsMaxFrequency.valueChanged.connect(
            self.change_spectrogram_y_limits)
        self.__ui.cbComponents.currentTextChanged.connect(self.general_plotting)
        self.__ui.aOpenExportForm.triggered.connect(self.open_export_form)

    @property
    def window(self):
        return self.__window

    @property
    def parent(self):
        return self.__parent

    @property
    def ui(self):
        return self.__ui

    def modify_reset_fields(self):
        ui = self.ui
        file_id = ui.cbFileName.currentIndex()
        self.modify_time_limits(file_id=file_id)

    def modify_resample_freq_widget(self, file_id):
        file_info = self.files_info[file_id]
        signal_freq = file_info.frequency

        ui = self.ui
        current_val = ui.sbResampleFrequency.value()
        ui.sbResampleFrequency.setMaximum(signal_freq)
        if current_val > signal_freq or current_val == 0:
            ui.sbResampleFrequency.setValue(signal_freq)

    def modify_time_limits(self, file_id):
        file_info = self.files_info[file_id]
        dt_start, dt_stop = file_info.time_start, file_info.time_stop

        ui = self.ui
        ui.dtStartTime.setMinimumDateTime(dt_start)
        ui.dtStopTime.setMaximumDateTime(dt_stop)

        if ui.cbResetFields.isChecked():
            ui.dtStartTime.setDateTime(dt_start)
            ui.dtStopTime.setDateTime(dt_stop)
        else:
            current_dt_start = ui.dtStartTime.dateTime().toPyDateTime()
            current_dt_stop = ui.dtStopTime.dateTime().toPyDateTime()
            if dt_start <= current_dt_start < dt_stop:
                ui.dtStartTime.setDateTime(current_dt_start)
            else:
                ui.dtStartTime.setDateTime(dt_start)

            if dt_start < current_dt_stop <= dt_stop:
                ui.dtStopTime.setDateTime(current_dt_stop)
            else:
                ui.dtStopTime.setDateTime(dt_stop)

    def modify_time_step(self):
        ui = self.ui

        current_dt_start = ui.dtStartTime.dateTime().toPyDateTime()
        current_dt_stop = ui.dtStopTime.dateTime().toPyDateTime()

        if current_dt_start >= current_dt_stop:
            return

        dt = int((current_dt_stop - current_dt_start).total_seconds() / 60)
        ui.sbTimeStepSize.setMaximum(dt)
        if dt > 60:
            ui.sbTimeStepSize.setValue(60)
        else:
            ui.sbTimeStepSize.setValue(dt)

    def modify_step_index(self):
        ui = self.ui
        current_dt_start = ui.dtStartTime.dateTime().toPyDateTime()
        current_dt_stop = ui.dtStopTime.dateTime().toPyDateTime()

        if current_dt_start >= current_dt_stop:
            return

        dt = (current_dt_stop - current_dt_start).total_seconds() / 60
        time_step_size = ui.sbTimeStepSize.value()
        if time_step_size == 0:
            max_value = 0
        else:
            if dt % time_step_size:
                max_value = int(dt / time_step_size)
            else:
                max_value = int(dt / time_step_size) - 1
        ui.sbTimeStepIndex.setMaximum(max_value)

    def set_start_form_state(self, files_info: List[FileInfo]):
        self.files_info = files_info

        ui = self.ui
        ui.cbFileName.clear()
        ui.cbFileName.addItems([x.name for x in files_info])

        ui.cbComponents.clear()
        ui.cbComponents.addItems(self.components)

        ui.lSignalTimeInterval.clear()
        ui.gwGraphOriginalSignal.clear()

        ui.lSpectrogramTimeInterval.clear()
        ui.gwGraphOriginalSpectrogram.clear()

        ui.cbResetFields.setChecked(True)
        self.modify_resample_freq_widget(file_id=0)
        self.modify_time_limits(file_id=0)
        self.modify_time_step()
        self.modify_step_index()

    @property
    def form_parameters(self) -> FormParameters:
        ui = self.ui
        params = self.__form_parameters
        params.resample_freq = ui.sbResampleFrequency.value()
        params.file_id = ui.cbFileName.currentIndex()
        params.dt_start = ui.dtStartTime.dateTime().toPyDateTime()
        params.dt_stop = ui.dtStopTime.dateTime().toPyDateTime()
        params.time_step_minutes = ui.sbTimeStepSize.value()
        params.step_index = ui.sbTimeStepIndex.value()
        params.min_freq = ui.dsMinFrequency.value()
        params.max_freq = ui.dsMaxFrequency.value()
        params.component_id = ui.cbComponents.currentIndex()
        return params

    def change_analyzing_file(self):
        current_id = self.ui.cbFileName.currentIndex()
        self.modify_resample_freq_widget(file_id=current_id)
        self.modify_time_limits(file_id=current_id)
        self.modify_time_step()
        self.modify_step_index()

    def load_data(self):
        self.ui.statusBar.showMessage('Loading file... Wait please')
        self.ui.gwGraphOriginalSignal.clear()
        self.ui.gwGraphOriginalSpectrogram.clear()
        self.signal, self.spectrograms = [], []
        params = self.form_parameters

        bin_data = BinaryFile(self.files_info[params.file_id].path,
                              params.resample_freq, True)
        dt_start = params.dt_start + timedelta(
            minutes=params.time_step_minutes * params.step_index)

        bin_data.read_date_time_start = dt_start

        dt_stop = params.dt_start + timedelta(
            minutes=params.time_step_minutes * (params.step_index + 1))
        if dt_stop > params.dt_stop:
            dt_stop = params.dt_stop
        bin_data.read_date_time_stop = dt_stop

        for component in self.components:
            signal = bin_data.read_signal(component)
            self.signal.append(signal)
            sp_data = Spectrogram(signal, params.resample_freq)
            self.spectrograms.append(sp_data)
        self.ui.statusBar.showMessage('Done')

    def general_plotting(self):
        self.plot_signal()
        self.plot_spectrogram()

    def load_signal(self):
        self.load_data()
        self.general_plotting()

    def plot_signal(self):
        def mouse_move(point):
            position = plot.vb.mapSceneToView(point)
            seconds_val, frequency_val = position.x(), position.y()
            dt_start_part = self.ui.dtStartTime.dateTime().toPyDateTime()
            time_step_minutes_size = self.form_parameters.time_step_minutes
            time_step_index = self.form_parameters.step_index
            current_datetime = dt_start_part + timedelta(
                seconds=seconds_val,
                minutes=time_step_minutes_size * time_step_index
            )
            datetime_label = current_datetime.strftime(DATETIME_FORMAT)
            self.ui.statusBar.showMessage(f'DateTime: {datetime_label}')

        canvas = self.ui.gwGraphOriginalSignal
        canvas.clear()
        self.ui.lSignalTimeInterval.clear()

        plot, curve = canvas.addPlot(), pg.PlotCurveItem()

        if len(self.signal) != len(self.components):
            return

        params = self.form_parameters

        signal = self.signal[params.component_id]
        color = (255, 0, 0)

        data = np.zeros(shape=(signal.shape[0], 2))
        time_length = signal.shape[0] / params.resample_freq
        data[:, 0] = np.linspace(0, time_length, signal.shape[0])
        data[:, 1] = signal
        curve.setData(x=data[:, 0], y=data[:, 1], pen=color)
        plot.addItem(curve)

        dt_start = params.dt_start + timedelta(
            minutes=params.time_step_minutes * params.step_index)
        dt_start = datetime.strftime(dt_start, DATETIME_FORMAT)
        dt_stop = params.dt_start + timedelta(
            minutes=params.time_step_minutes * (params.step_index + 1))
        dt_stop = datetime.strftime(dt_stop, DATETIME_FORMAT)
        label_val = f'Time interval: {dt_start} - {dt_stop}'
        self.ui.lSignalTimeInterval.setText(label_val)

        canvas.scene().sigMouseMoved.connect(mouse_move)

    def change_spectrogram_y_limits(self):
        if self.__spectrogram_plot is None:
            return
        params = self.form_parameters
        freq_min, freq_max = params.min_freq, params.max_freq
        if freq_min >= freq_max:
            return
        self.__spectrogram_plot.setRange(yRange=(freq_min, freq_max))

    def plot_spectrogram(self):
        def mouse_move(point):
            position = plot.vb.mapSceneToView(point)
            seconds_val, frequency_val = position.x(), position.y()
            dt_start_part = self.ui.dtStartTime.dateTime().toPyDateTime()
            time_step_minutes_size = self.form_parameters.time_step_minutes
            time_step_index = self.form_parameters.step_index
            current_datetime = dt_start_part + timedelta(
                seconds=seconds_val,
                minutes=time_step_minutes_size * time_step_index
            )
            datetime_label = current_datetime.strftime(DATETIME_FORMAT)
            self.ui.statusBar.showMessage(f'DateTime: {datetime_label}')

        canvas = self.ui.gwGraphOriginalSpectrogram
        canvas.clear()
        self.ui.lSpectrogramTimeInterval.clear()

        if len(self.spectrograms) == 0:
            return

        params = self.form_parameters
        current_spectrogram = self.spectrograms[params.component_id]
        sp_data = current_spectrogram.sp_data

        if sp_data.frequencies.shape[0] == 0:
            return

        time, frequency = sp_data.times, sp_data.frequencies
        amplitudes = sp_data.amplitudes

        amplitudes = 20 * np.log10(abs(amplitudes))
        amplitudes = amplitudes.T

        plot, img = canvas.addPlot(), pg.ImageItem()
        self.__spectrogram_plot = plot
        img.setImage(amplitudes, xvals=time, yvals=frequency)
        dx = (time[-1] - time[0]) / time.shape[0]
        dy = (frequency[-1] - frequency[0]) / frequency.shape[0]
        img.scale(dx, dy)

        hist = pg.HistogramLUTItem()
        min_val, max_val = current_spectrogram.scale_limits()
        hist.setLevels(min_val, max_val)
        hist.gradient.restoreState(
            {'mode': 'rgb',
             'ticks': [
                 (0.0, (153, 102, 255, 255)),
                 (0.2, (0, 0, 255, 255)),
                 (0.4, (0, 255, 0, 255)),
                 (0.6, (255, 255, 0, 255)),
                 (0.8, (255, 102, 0, 255)),
                 (1.0, (255, 0, 0, 255))]
             })
        hist.setImageItem(img)
        plot.addItem(img)
        canvas.addItem(hist)

        plot.setLimits(xMin=time[0], xMax=time[-1],
                       yMin=frequency[0], yMax=frequency[-1])
        plot.setLabel('bottom', "Time", units='seconds')
        plot.setLabel('left', "Frequency", units='Hz')
        self.change_spectrogram_y_limits()

        current_dt_start = params.dt_start + timedelta(
                minutes=params.time_step_minutes * params.step_index)
        current_dt_stop = current_dt_start + timedelta(
            minutes=params.time_step_minutes)

        label_val = f'Time interval: {current_dt_start} - {current_dt_stop}'
        self.ui.lSpectrogramTimeInterval.setText(label_val)

        canvas.scene().sigMouseMoved.connect(mouse_move)

    def open_export_form(self):
        if len(self.files_info) == 0:
            return
        first_item = self.files_info[0]
        start_time_analysis = first_item.time_start
        stop_time_analysis = first_item.time_stop
        resample_frequency = first_item.frequency

        for item in self.files_info[1:]:
            start_time_analysis = min(start_time_analysis, item.time_start)
            stop_time_analysis = max(stop_time_analysis, item.time_stop)
            resample_frequency = min(resample_frequency, item.frequency)

        self.__export_dorm.set_start_form_state(start_time_analysis,
                                                stop_time_analysis,
                                                resample_frequency)
        self.__export_dorm.window.show()

