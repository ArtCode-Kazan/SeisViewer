import os
from random import randint
from datetime import datetime
from typing import List

import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.uic import *
from PyQt5.QtCore import Qt

from SeisCore import BinaryFile
from SeisCore.Functions.Wavelet import detrend
from SeisCore.Functions.Spectrum import average_spectrum

from pyqtgraph import PlotCurveItem

from SeisViewer.GUI.Structures import FileInfo
from SeisViewer.Functions.Processing import cross_correlation
from SeisViewer.GUI.ReviseExportForm import ReviseExportForm


class FormParameters:
    resample_freq = 0
    detrend_freq = 0
    start_time = datetime.now()
    stop_time = datetime.now()
    signal_component_id = 0
    time_marker = 0
    sp_window = 8192
    sp_overlap = 4096
    marmett_filter = 7
    median_filter = 7
    sp_freq_limits = [0, 10]
    is_show_smooth_spectrums = True
    spectrum_component_id = 0
    correlations_freq_limits = [0, 10]
    is_using_smooth_for_correlations = True
    correlation_component_id = 0
    selection_file_ids: List[int] = []


def generate_random_color():
    r = randint(0, 255)
    g = randint(10, 245)
    b = randint(20, 235)
    return r, g, b


def normal_signal(signal: np.ndarray, norming_interval=(-1, 1)) -> np.ndarray:
    min_val, max_val = np.min(signal), np.max(signal)
    return (norming_interval[1] - norming_interval[0]) * \
           (signal - min_val) / (max_val - min_val) + norming_interval[0]


class ReviseViewForm:
    def __init__(self, parent):
        self.__window_type = 'revise_view_form'
        self.__parent = parent

        self.components = ['X', 'Y', 'Z']
        self.files_info: List[FileInfo] = []
        self.static_colors = []

        self.signals = np.array([])
        self.avg_spectrums = np.array([])
        self.correlations: List[np.ndarray] = []

        self.__form_parameters = FormParameters()

        self.__window = QMainWindow()
        self.__forms_folder = parent.form_folder
        ui_path = os.path.join(self.__forms_folder, 'ReviseViewerForm.ui')
        self.__ui = loadUi(ui_path, self.__window)

        self.signal_time_marker = PlotCurveItem([0, 0], [-1, 1],
                                                pen=(0, 255, 0))
        self.spectrums_plot = None

        self.__export_form = ReviseExportForm(self)

        self.__ui.cbSelectAll.stateChanged.connect(self.set_all_files_check_state)
        self.__ui.bUpdateSignalData.clicked.connect(self.load_signal_data)

        self.__ui.cbSignalComponents.currentTextChanged.connect(self.render_signals)
        self.__ui.bApply.clicked.connect(self.global_render)
        self.__ui.sbSignalTimeMarker.valueChanged.connect(self.set_signal_time_marker)

        self.__ui.bLoadSpectrums.clicked.connect(self.load_spectrums_data)
        self.__ui.cbSpectrumComponents.currentTextChanged.connect(self.render_spectrums)
        self.__ui.rbOriginalSpectrums.toggled.connect(self.render_spectrums)
        self.__ui.rbSmoothSpectrums.toggled.connect(self.render_spectrums)
        self.__ui.sbMinVisualFrequency.valueChanged.connect(self.change_spectrum_x_limits)
        self.__ui.sbMaxVisualFrequency.valueChanged.connect(self.change_spectrum_x_limits)

        self.__ui.bLoadCorrelations.clicked.connect(self.load_correlations)
        self.__ui.cbCorrelationComponents.currentTextChanged.connect(self.render_correlations)
        self.__ui.aExport.triggered.connect(self.open_export_form)

    @property
    def window(self):
        return self.__window

    @property
    def parent(self):
        return self.__parent

    @property
    def ui(self):
        return self.__ui

    def fill_components(self):
        ui = self.ui
        comboboxes = [ui.cbSignalComponents, ui.cbSpectrumComponents,
                      ui.cbCorrelationComponents]
        for combobox in comboboxes:
            combobox.clear()
            combobox.addItems(self.components)

    def modify_time_widget_for_marker(self) -> None:
        ui = self.ui
        resample_frequency = ui.sbResampleFrequency.value()
        ui.sbSignalTimeMarker.setSingleStep(1 / resample_frequency)

    def set_start_form_state(self, files_info: List[FileInfo],
                             cross_dt_limits: List[datetime],
                             resample_frequency: int) -> None:
        params = FormParameters()
        self.files_info = files_info
        self.__form_parameters = params
        self.signals = np.array([])
        self.avg_spectrums = np.array([])
        self.correlations = []

        ui = self.ui
        self.fill_components()

        ui.lFilesList.clear()
        for item_val in files_info:
            item = QListWidgetItem()
            item.setText(item_val.name)
            item.setCheckState(Qt.Unchecked)
            ui.lFilesList.addItem(item)

        ui.sbResampleFrequency.setMaximum(resample_frequency)
        ui.sbResampleFrequency.setValue(resample_frequency)

        ui.dtStartTime.setMinimumDateTime(cross_dt_limits[0])
        ui.dtStopTime.setMaximumDateTime(cross_dt_limits[1])

        ui.dtStartTime.setDateTime(cross_dt_limits[0])
        ui.dtStopTime.setDateTime(cross_dt_limits[1])

        ui.sbResampleFrequency.setValue(resample_frequency)
        self.modify_time_widget_for_marker()
        ui.cbSelectAll.setChecked(False)

        ui.signalsPlot.clear()
        ui.sbDentendEdge.setValue(params.detrend_freq)
        ui.sbSignalTimeMarker.setValue(params.time_marker)

        ui.spectrumsPlot.clear()
        ui.sbWindowSize.setValue(params.sp_window)
        ui.sbOverlapSize.setValue(params.sp_overlap)
        ui.sbMarmettFilter.setValue(params.marmett_filter)
        ui.sbMedianFilter.setValue(params.median_filter)
        ui.sbMinVisualFrequency.setValue(params.sp_freq_limits[0])
        ui.sbMaxVisualFrequency.setValue(params.sp_freq_limits[1])
        ui.rbSmoothSpectrums.setChecked(params.is_show_smooth_spectrums)

        ui.correlationsPlot.clear()
        ui.sbMinCorrelationFrequency.setValue(
            params.correlations_freq_limits[0])
        ui.sbMaxCorrelationFrequency.setValue(
            params.correlations_freq_limits[1])
        ui.cbUsingSmooth.setChecked(params.is_using_smooth_for_correlations)

    def set_all_files_check_state(self):
        is_checked = self.ui.cbSelectAll.isChecked()
        for index in range(self.ui.lFilesList.count()):
            item = self.ui.lFilesList.item(index)
            if is_checked:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def get_form_data(self) -> FormParameters:
        ui, params = self.ui, self.__form_parameters
        params.resample_freq = ui.sbResampleFrequency.value()
        params.detrend_freq = ui.sbDentendEdge.value()
        params.start_time = ui.dtStartTime.dateTime().toPyDateTime()
        params.stop_time = ui.dtStopTime.dateTime().toPyDateTime()
        params.signal_component_id = ui.cbSignalComponents.currentIndex()
        params.time_marker = ui.sbSignalTimeMarker.value()

        params.sp_window = ui.sbWindowSize.value()
        params.sp_overlap = ui.sbOverlapSize.value()
        params.marmett_filter = ui.sbMarmettFilter.value()
        params.median_filter = ui.sbMedianFilter.value()
        params.sp_freq_limits = [ui.sbMinVisualFrequency.value(),
                                 ui.sbMaxVisualFrequency.value()]
        params.is_show_smooth_spectrums = ui.rbSmoothSpectrums.isChecked()
        params.spectrum_component_id = ui.cbSpectrumComponents.currentIndex()

        params.correlations_freq_limits = [
            ui.sbMinCorrelationFrequency.value(),
            ui.sbMaxCorrelationFrequency.value()]
        params.is_using_smooth_for_correlations = ui.cbUsingSmooth.isChecked()
        params.correlation_component_id = \
            ui.cbCorrelationComponents.currentIndex()

        params.selection_file_ids = []
        for index in range(ui.lFilesList.count()):
            item = ui.lFilesList.item(index)
            if item.checkState() == Qt.Checked:
                params.selection_file_ids.append(index)
        return params

    def load_signal_data(self) -> None:
        self.ui.statusBar.showMessage('Loading signals data. Wait please...')
        self.signals = np.array([])
        self.avg_spectrums = np.array([])
        self.correlations = []
        if len(self.files_info) == 0:
            return

        params = self.get_form_data()
        result = np.array([])
        for f_info in self.files_info:
            bin_data = BinaryFile(f_info.path, params.resample_freq, True)
            bin_data.read_date_time_start = params.start_time
            bin_data.read_date_time_stop = params.stop_time
            for component in self.components:
                signal = bin_data.read_signal(component)
                if params.detrend_freq != 0:
                    signal = detrend(signal, params.resample_freq,
                                     params.detrend_freq)
                if result.shape[0] == 0:
                    result = signal
                else:
                    result = np.column_stack((result, signal))

        time_array = np.arange(0, result.shape[0], 1) / params.resample_freq
        self.signals = np.column_stack((time_array, result))
        self.ui.statusBar.showMessage('Signals data was loaded. Ready')
        self.render_signals()

    def load_spectrums_data(self) -> None:
        self.ui.statusBar.showMessage(
            'Processing spectrums data. Wait please...')
        self.avg_spectrums = np.array([])
        self.correlations = []
        if self.signals.shape[0] == 0:
            self.ui.statusBar.showMessage(
                'No data for spectrums. Ready')
            return

        params = self.get_form_data()

        result = np.array([])
        for i in range(1, self.signals.shape[1]):
            signal = self.signals[:, i]
            original_sp_data = average_spectrum(signal=signal,
                                                frequency=params.resample_freq,
                                                window=params.sp_window,
                                                offset=params.sp_overlap)
            if result.shape[0] == 0:
                result = original_sp_data
            else:
                result = np.column_stack((result, original_sp_data[:, 1]))
            smooth_sp_data = average_spectrum(signal=signal,
                                              frequency=params.resample_freq,
                                              window=params.sp_window,
                                              offset=params.sp_overlap,
                                              median_filter=params.median_filter,
                                              marmett_filter=params.marmett_filter)
            result = np.column_stack((result, smooth_sp_data[:, 1]))
        self.ui.statusBar.showMessage('Spectrums data loaded. Ready')
        self.avg_spectrums = result
        self.render_spectrums()

    def load_correlations(self):
        self.ui.statusBar.showMessage(
            'Processing correlations data. Wait please...')
        self.correlations = []
        if self.avg_spectrums.shape[0] == 0:
            self.ui.statusBar.showMessage(
                'No data for correlations. Ready')
            return

        params = self.get_form_data()
        f_min, f_max = params.correlations_freq_limits
        if f_min >= f_max:
            self.ui.statusBar.showMessage('Invalid frequency limits')
            return

        is_use_smooth_spectrums = params.is_using_smooth_for_correlations

        result = []
        for component_index in range(len(self.components)):
            if is_use_smooth_spectrums:
                start_column = 2 * (component_index + 1)
            else:
                start_column = 2 * component_index + 1
            skipping_columns = 2 * len(self.components)
            arr = self.avg_spectrums[:, start_column::skipping_columns]
            result_corr = cross_correlation(
                    frequency=self.avg_spectrums[:, 0], f_min_analysis=f_min,
                    f_max_analysis=f_max, amplitudes=arr)
            result.append(result_corr)
        self.correlations = result
        self.ui.statusBar.showMessage('Correlations data loaded. Ready')
        self.render_correlations()

    def get_signal_column_index(self, file_id: int, component_id: int) -> int:
        return file_id * len(self.components) + component_id + 1

    def render_signals(self):
        plot = self.ui.signalsPlot
        plot.clear()

        if self.signals.shape[0] == 0:
            return

        params = self.get_form_data()

        if len(params.selection_file_ids) == 0:
            return

        component_index = params.signal_component_id

        amplitude = 2
        time_axis = self.signals[:, 0]
        for i, file_id in enumerate(params.selection_file_ids):
            col_index = self.get_signal_column_index(file_id, component_index)
            signal = self.signals[:, col_index]

            norming_interval = (-1 + amplitude * i, 1 + amplitude * i)
            signal = normal_signal(signal, norming_interval)

            curve = PlotCurveItem(time_axis, signal, pen=(255, 0, 0))
            curve.setToolTip(self.files_info[file_id].name)
            plot.addItem(curve)

        x_val = self.ui.sbSignalTimeMarker.value()
        min_y, max_y = -1, 1 + amplitude * (len(params.selection_file_ids) - 1)
        self.signal_time_marker.setData([x_val, x_val], [min_y, max_y])
        plot.addItem(self.signal_time_marker)
        plot.setLimits(xMin=time_axis[0], xMax=time_axis[-1],
                       yMin=min_y, yMax=max_y)

    def get_spectrum_column_index(self, file_id: int, component_id: int,
                                  is_smooth=False) -> int:
        id_val = file_id * len(self.components) * 2 + component_id * 2 + 1
        if is_smooth:
            id_val += 1
        return id_val

    @property
    def line_colors(self) -> list:
        if len(self.static_colors) != len(self.files_info):
            self.static_colors = [generate_random_color() for _ in range(
                len(self.files_info))]
        return self.static_colors

    def render_spectrums(self):
        def mouse_move(point):
            try:
                position = plot.vb.mapSceneToView(point)
                frequency, amplitude = position.x(), position.y()

                nearest_frequency_index, delta_f = 0, np.inf
                for i, value in enumerate(data[:, 0]):
                    df = abs(value - frequency)
                    if df < delta_f:
                        nearest_frequency_index = i
                        delta_f = df

                nearest_f_id_index, delta_amp = 0, np.inf
                for i, value in enumerate(data[nearest_frequency_index, 1:]):
                    damp = abs(amplitude - value)
                    if damp >= max_amp * 0.1:
                        continue

                    if damp < delta_amp:
                        nearest_f_id_index = i
                        delta_amp = damp

                if (delta_amp != np.inf and
                        freq_limits[0] < frequency < freq_limits[1]):
                    file_name = self.files_info[file_ids[nearest_f_id_index]].name
                    self.ui.statusBar.showMessage(f'Nearest curve: {file_name}')
                else:
                    self.ui.statusBar.showMessage('Nearest curve not found')
            except (np.linalg.LinAlgError, UnboundLocalError):
                pass

        layout = self.ui.spectrumsPlot
        layout.clear()

        if self.avg_spectrums.shape[0] == 0:
            return

        params = self.get_form_data()

        file_ids = params.selection_file_ids
        if len(file_ids) == 0:
            return

        component_id = params.spectrum_component_id
        is_smooth = params.is_show_smooth_spectrums
        x_axis = self.avg_spectrums[:, 0]
        plot = layout.addPlot()
        data = x_axis
        for file_id in file_ids:
            color = self.line_colors[file_id]
            column_id = self.get_spectrum_column_index(file_id, component_id,
                                                       is_smooth)
            y_data = self.avg_spectrums[:, column_id]
            max_value = np.max(y_data)
            plot.plot(x_axis, y_data / max_value, pen=color)
            data = np.column_stack((data, self.avg_spectrums[:, column_id]))
        max_amp = np.max(data[:, 1:])
        freq_limits = (x_axis[0], x_axis[-1])
        plot.setLimits(xMin=x_axis[0], xMax=x_axis[-1], yMin=0, yMax=1)
        plot.scene().sigMouseMoved.connect(mouse_move)
        self.spectrums_plot = plot
        self.change_spectrum_x_limits()

    def render_correlations(self):
        def mouse_move(point):
            try:
                position = plot.vb.mapSceneToView(point)
                file_id, corr_value = position.x(), position.y()
                nearest_filex_index, delta_val = 0, np.inf
                for i in range(data.shape[1]):
                    dval = abs(i - file_id)
                    if dval < delta_val:
                        nearest_filex_index = i
                        delta_val = dval

                nearest_filey_index, delta_val = 0, np.inf
                for i, value in enumerate(data[nearest_filex_index, :]):
                    dcorr = abs(corr_value - value)
                    if dcorr >= 0.1:
                        continue

                    if dcorr < delta_val:
                        nearest_filey_index = i
                        delta_val = dcorr

                if (delta_val != np.inf and
                        0 < nearest_filex_index < len(self.files_info)):
                    file_name = self.files_info[file_ids[nearest_filey_index]].name
                    self.ui.statusBar.showMessage(f'Nearest curve: {file_name}')
                else:
                    self.ui.statusBar.showMessage('Nearest curve not found')
            except (np.linalg.LinAlgError, UnboundLocalError):
                pass

        layout = self.ui.correlationsPlot
        layout.clear()

        params = self.get_form_data()

        file_ids = params.selection_file_ids
        if len(file_ids) == 0:
            return

        if len(self.correlations) == 0:
            return

        plot = layout.addPlot()

        component_id = params.correlation_component_id
        data = self.correlations[component_id][:, file_ids]

        x_ticks_data = [(i, x.name[:5]+'...') for i, x in enumerate(
            self.files_info)]
        plot.getAxis('bottom').setTicks([x_ticks_data])

        for i, id_val in enumerate(file_ids):
            color = self.line_colors[id_val]
            plot.plot([x[0] for x in x_ticks_data], data[:, i], pen=color)

        plot.setLimits(xMin=0, xMax=len(x_ticks_data) - 1, yMin=0, yMax=1)
        plot.scene().sigMouseMoved.connect(mouse_move)

    def set_signal_time_marker(self):
        value = self.ui.sbSignalTimeMarker.value()
        _, y_data = self.signal_time_marker.getData()
        self.signal_time_marker.setData([value, value], y_data)

    def change_spectrum_x_limits(self):
        if self.spectrums_plot is None:
            return
        params = self.get_form_data()
        freq_min, freq_max = params.sp_freq_limits
        if freq_min >= freq_max:
            return
        self.spectrums_plot.setRange(xRange=(freq_min, freq_max))

    def global_render(self):
        self.render_signals()
        self.render_spectrums()
        self.render_correlations()

    def open_export_form(self):
        self.__export_form.set_start_form_state(
            self.files_info, self.static_colors, self.signals,
            self.avg_spectrums, self.correlations)
        self.__export_form.window.show()





