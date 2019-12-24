import os
import numpy as np
from datetime import timedelta

import pyqtgraph as pg

from PyQt5.QtWidgets import *
from PyQt5.uic import *

from SeisCore.Functions.Spectrogram import specgram
from SeisCore.Functions.Spectrogram import scale_limits

from SeisCore.BinaryFile.BinaryFile import BinaryFile

from SeisRevise.GUI.Dialogs import show_file_dialog


class ViewSpectrogramForm:
    def __init__(self, parent):
        self.__window_type = 'view_spectrum_form'
        self.__parent = parent

        self.__parameters = None

        self.__dt_file_start = None
        self.__dt_file_stop = None
        self.__origin_signal = None
        self.__origin_spectrogram = None
        self.__origin_spectrogram_scale = None

        self.__window = QMainWindow()
        self.__forms_folder = parent.form_folder
        ui_path = os.path.join(self.__forms_folder, 'ViewSpectrogramForm.ui')
        self.__ui = loadUi(ui_path, self.__window)

        self.__ui.pbOpenFile.clicked.connect(self.open_file_from_folder)
        self.__ui.cbFileName.currentTextChanged.connect(
            self.open_file_from_list)
        self.__ui.bLoadData.clicked.connect(self.load_file)
        self.__ui.rbTimeLimitsMode.toggled.connect(self.selection_mode)
        self.__ui.rbTimeStepMode.toggled.connect(self.selection_mode)
        self.__ui.sbTimeStepSize.valueChanged.connect(self.set_time_limits)
        self.__ui.sbTimeStepIndex.valueChanged.connect(self.set_time_limits)
        self.__ui.bShow.clicked.connect(self.show_data)

    @property
    def window(self):
        return self.__window

    @property
    def parent(self):
        return self.__parent

    @property
    def ui(self):
        return self.__ui

    def open_file_from_folder(self):
        self.ui.leFilePath.clear()
        path = show_file_dialog()
        if path is None:
            return
        extension = os.path.basename(path).split('.')[-1]
        if extension in ('00', 'xx', 'bin'):
            self.ui.leFilePath.setText(path)

    def open_file_from_list(self):
        file_name = self.ui.cbFileName.currentText()
        path = self.parent.files_info[file_name]['path']
        self.ui.leFilePath.setText(path)

    def load_file(self):
        path = self.ui.leFilePath.text()
        if len(path) == 0:
            return

        bin_data = BinaryFile()
        bin_data.path = path
        dt_start = bin_data.datetime_start
        dt_stop = bin_data.datetime_stop
        freq = bin_data.signal_frequency

        self.__dt_file_start = dt_start
        self.__dt_file_stop = dt_stop

        self.ui.leFilePath.setText(path)
        self.ui.sbResampleFrequency.setValue(freq)
        self.ui.dtStartTime.setDateTime(dt_start)
        self.ui.dtStopTime.setDateTime(dt_stop)

    def selection_mode(self):
        ui=self.ui
        if ui.rbTimeLimitsMode.isChecked():
            ui.dtStartTime.setEnabled(True)
            ui.dtStopTime.setEnabled(True)
            ui.sbTimeStepSize.setEnabled(False)
            ui.sbTimeStepIndex.setEnabled(False)

        elif ui.rbTimeStepMode.isChecked():
            ui.dtStartTime.setEnabled(False)
            ui.dtStopTime.setEnabled(False)
            ui.sbTimeStepSize.setEnabled(True)
            ui.sbTimeStepIndex.setEnabled(True)
        else:
            return
        ui.bShow.setEnabled(True)

    def set_time_limits(self):
        ui = self.ui
        if not ui.rbTimeStepMode.isChecked():
            return

        file_dt_start = self.__dt_file_start
        file_dt_stop = self.__dt_file_stop
        time_step_size = ui.sbTimeStepSize.value()
        time_step_number = ui.sbTimeStepIndex.value()

        if time_step_number == 0 or time_step_size == 0:
            return

        dt_start = file_dt_start + timedelta(
            minutes=time_step_size * (time_step_number - 1))
        dt_stop = file_dt_start + timedelta(
            minutes=time_step_size * time_step_number)

        if dt_start > file_dt_stop:
            return

        if dt_stop > file_dt_stop:
            dt_stop = file_dt_stop

        ui.dtStartTime.setDateTime(dt_start)
        ui.dtStopTime.setDateTime(dt_stop)

    def collect_parameters(self):
        ui = self.ui
        if len(ui.leFilePath.text()) == 0:
            return

        params = dict()
        params['file_path'] = ui.leFilePath.text()
        params['resample_frequency'] = ui.sbResampleFrequency.value()
        params['visual_min_frequency'] = ui.dsSpectrogramMinFrequency.value()
        params['visual_max_frequency'] = ui.dsSpectrogramMaxFrequency.value()
        params['component'] = ui.cbComponents.currentText()
        params['dt_start'] = ui.dtStartTime.dateTime().toPyDateTime()
        params['dt_stop'] = ui.dtStopTime.dateTime().toPyDateTime()

        if self.__parameters is not None:
            old_params = self.__parameters
            if params['file_path'] != old_params['file_path'] or \
                    params['resample_frequency'] != \
                    old_params['resample_frequency'] or \
                    params['dt_start'] != old_params['dt_start'] or \
                    params['dt_stop'] != old_params['dt_stop'] or \
                    params['component'] != old_params['component']:
                self.__origin_signal = None
                self.__origin_spectrogram = None
        self.__parameters = params

    def load_origin_signal(self):
        if self.__parameters is None:
            self.__origin_signal = None
            self.__origin_spectrogram = None
        if self.__parameters is not None and self.__origin_signal is None:
            params = self.__parameters
            bin_data = BinaryFile()
            bin_data.path = params['file_path']
            bin_data.use_avg_values = False
            bin_data.resample_frequency = params['resample_frequency']
            bin_data.read_date_time_start = params['dt_start']
            bin_data.read_date_time_stop = params['dt_stop']
            if bin_data.signals is None:
                self.__origin_signal = None
                self.__origin_spectrogram = None
            else:
                index_channel = 'XYZ'.index(params['component'])
                signal = bin_data.ordered_signal_by_components[:,
                         index_channel]
                self.__origin_signal = signal
                self.__origin_spectrogram = specgram(
                    signal_data=signal,
                    frequency_of_signal=params['resample_frequency'])

    def plot_signal(self):
        signal = self.__origin_signal
        plot = self.ui.gwGraphOriginalSignal
        color = (255, 0, 0)

        data = np.zeros(shape=(signal.shape[0], 2))
        freq = self.__parameters['resample_frequency']
        time_length = signal.shape[0] / freq
        data[:, 0] = np.linspace(0, time_length, signal.shape[0])
        data[:, 1] = signal
        plot.plot(data, pen=color)

    def plot_spectrogram(self):
        time, frequency, amplitudes = self.__origin_spectrogram
        plot = self.ui.gwGraphOriginalSpectrogram

        params = self.__parameters
        min_val, max_val = scale_limits(
            amplitudes=amplitudes, frequencies=frequency,
            low_f=params['visual_min_frequency'],
            high_f=params['visual_max_frequency'])

        amplitudes = 20 * np.log10(abs(amplitudes))
        amplitudes = amplitudes.T

        p1 = plot.addPlot()
        img = pg.ImageItem()
        p1.addItem(img)
        hist = pg.HistogramLUTItem()
        hist.setImageItem(img)
        plot.addItem(hist)
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
        img.setImage(amplitudes)
        img.scale(time[-1] / np.size(amplitudes, axis=0),
                  frequency[-1] / np.size(amplitudes, axis=1))
        p1.setLimits(xMin=0, xMax=time[-1],
                     yMin=params['visual_min_frequency'],
                     yMax=params['visual_max_frequency'])
        p1.setLabel('bottom', "Time", units='s')
        p1.setLabel('left', "Frequency", units='Hz')

        def mouse_move(point):
            p = p1.vb.mapSceneToView(point)
            seconds, frequency = p.x(), p.y()
            dt_start_part = self.ui.dtStartTime.dateTime().toPyDateTime()
            current_datetime = dt_start_part + timedelta(seconds=seconds)
            datetime_label = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
            self.ui.statusbar.showMessage(f'DateTime: {datetime_label}')

        self.ui.gwGraphOriginalSpectrogram.scene().sigMouseMoved.connect(mouse_move)

    def show_data(self):
        self.collect_parameters()

        self.ui.statusbar.showMessage('Wait please...')

        self.ui.gwGraphOriginalSignal.clear()
        self.ui.gwGraphOriginalSpectrogram.clear()

        if self.__origin_signal is None:
            self.load_origin_signal()

        if self.__origin_signal is not None:
            self.plot_signal()

        if self.__origin_spectrogram is not None:
            self.plot_spectrogram()

        self.ui.statusbar.showMessage('Done')
