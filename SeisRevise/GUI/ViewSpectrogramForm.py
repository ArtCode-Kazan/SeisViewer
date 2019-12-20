import os
import numpy as np

import pyqtgraph as pg

from PyQt5.QtWidgets import *
from PyQt5.uic import *

from SeisCore.Functions.Filter import band_pass_filter
from SeisCore.Functions.Spectrogram import specgram
from SeisCore.Functions.Spectrogram import scale_limits

from SeisCore.BinaryFile.BinaryFile import BinaryFile

from SeisRevise.GUI.Dialogs import show_file_dialog


class ViewSpectrogramForm:
    def __init__(self, parent):
        self.__window_type = 'view_spectrum_form'
        self.__parent = parent

        self.__parameters = None

        self.__origin_signal = None
        self.__filtered_signal = None
        self.__origin_spectrogram=None
        self.__origin_spectrogram_scale=None
        self.__filtered_spectrogram = None
        self.__filtered_spectrogram_scale=None

        self.__window = QMainWindow()
        self.__forms_folder = parent.form_folder
        ui_path = os.path.join(self.__forms_folder, 'ViewSpectrogramForm.ui')
        self.__ui = loadUi(ui_path, self.__window)

        self.__ui.pbOpenFile.clicked.connect(self.open_file_from_folder)
        self.__ui.cbFileName.currentTextChanged.connect(self.open_file_from_list)
        self.__ui.bLoadData.clicked.connect(self.load_file)
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
        if len(path)==0:
            return

        bin_data=BinaryFile()
        bin_data.path=path
        dt_start=bin_data.datetime_start
        dt_stop=bin_data.datetime_stop
        freq=bin_data.signal_frequency

        self.ui.leFilePath.setText(path)
        self.ui.dtStartTime.setDateTime(dt_start)
        self.ui.dtStopTime.setDateTime(dt_stop)
        self.ui.sbResampleFrequency.setValue(freq)

    def collect_parameters(self):
        ui = self.ui
        if len(ui.leFilePath.text())==0:
            return

        params = dict()
        params['file_path'] = ui.leFilePath.text()
        params['resample_frequency'] = ui.sbResampleFrequency.value()
        params['dt_start'] = ui.dtStartTime.dateTime().toPyDateTime()
        params['dt_stop'] = ui.dtStopTime.dateTime().toPyDateTime()
        params['filter_min_frequency'] = ui.dsBandpassMinFrequency.value()
        params['filter_max_frequency'] = ui.dsBandpassMaxFrequency.value()
        params['visual_min_frequency'] = ui.dsSpectrogramMinFrequency.value()
        params['visual_max_frequency'] = ui.dsSpectrogramMaxFrequency.value()
        params['component'] = ui.cbComponents.currentText()

        if self.__parameters is not None:
            old_params=self.__parameters
            if params['file_path']!=old_params['file_path'] or \
                    params['resample_frequency'] != \
                    old_params['resample_frequency'] or \
                    params['dt_start']!=old_params['dt_start'] or \
                    params['dt_stop']!=old_params['dt_stop'] or \
                    params['component']!=old_params['component']:
                self.__origin_signal=None
                self.__filtered_signal=None
                self.__origin_spectrogram=None
                self.__filtered_spectrogram=None
            elif params['filter_min_frequency'] != \
                old_params['filter_min_frequency'] or \
                    params['filter_max_frequency'] != \
                    old_params['filter_max_frequency']:
                self.__filtered_signal = None
                self.__filtered_spectrogram = None
        self.__parameters = params

    def load_origin_signal(self):
        if self.__parameters is None:
            self.__origin_signal=None
            self.__origin_spectrogram=None
        if self.__parameters is not None and self.__origin_signal is None:
            params=self.__parameters
            bin_data=BinaryFile()
            bin_data.path=params['file_path']
            bin_data.use_avg_values = False
            bin_data.resample_frequency=params['resample_frequency']
            bin_data.read_date_time_start=params['dt_start']
            bin_data.read_date_time_stop=params['dt_stop']
            if bin_data.signals is None:
                self.__origin_signal = None
                self.__origin_spectrogram = None
            else:
                index_channel='XYZ'.index(params['component'])
                signal=bin_data.ordered_signal_by_components[:,index_channel]
                self.__origin_signal=signal
                self.__origin_spectrogram=specgram(
                    signal_data=signal,
                    frequency_of_signal=params['resample_frequency'])

    def load_filtered_signal(self):
        if self.__parameters is None:
            self.__filtered_signal=None
            self.__filtered_spectrogram=None
        if self.__parameters is not None and self.__filtered_signal is None:
            params = self.__parameters
            if params['filter_min_frequency']==params['filter_max_frequency']:
                self.__filtered_signal=None
                self.__filtered_spectrogram=None
            else:
                self.__filtered_signal=band_pass_filter(
                    signal=self.__origin_signal,
                    frequency=params['resample_frequency'],
                    f_min=params['filter_min_frequency'],
                    f_max=params['filter_max_frequency'])
                self.__filtered_spectrogram = specgram(
                    signal_data=self.__filtered_signal,
                    frequency_of_signal=params['resample_frequency'])

    def plot_signal(self, signal_type):
        if signal_type=='origin':
            signal=self.__origin_signal
            plot = self.ui.gwGraphOriginalSignal
            color=(255, 0, 0)
        elif signal_type=='filtered':
            signal = self.__filtered_signal
            plot = self.ui.gwGraphFilteredSignal
            color = (251, 255, 94)
        else:
            return
        data = np.zeros(shape=(signal.shape[0], 2))
        freq = self.__parameters['resample_frequency']
        time_length = signal.shape[0] / freq
        data[:, 0] = np.linspace(0, time_length, signal.shape[0])
        data[:, 1] = signal
        plot.plot(data, pen=color)

    def plot_spectrogram(self, signal_type):
        if signal_type=='origin':
            time, frequency, amplitudes = self.__origin_spectrogram
            plot = self.ui.gwGraphOriginalSpectrogram
        elif signal_type=='filtered':
            time, frequency, amplitudes = self.__filtered_spectrogram
            plot = self.ui.gwGraphFilteredSpectrogram
        else:
            return
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

    def show_data(self):
        self.collect_parameters()

        self.ui.statusbar.showMessage('Wait please...')

        self.ui.gwGraphOriginalSignal.clear()
        self.ui.gwGraphFilteredSignal.clear()
        self.ui.gwGraphOriginalSpectrogram.clear()
        self.ui.gwGraphFilteredSpectrogram.clear()

        if self.__origin_signal is None:
            self.load_origin_signal()

        if self.__origin_signal is not None:
            self.plot_signal(signal_type='origin')

        if self.__filtered_signal is None:
            self.load_filtered_signal()

        if self.__filtered_signal is not None:
            self.plot_signal(signal_type='filtered')

        if self.__origin_spectrogram is not None:
            self.plot_spectrogram(signal_type='origin')

        if self.__filtered_spectrogram is not None:
            self.plot_spectrogram(signal_type='filtered')

        self.ui.statusbar.showMessage('Done')
