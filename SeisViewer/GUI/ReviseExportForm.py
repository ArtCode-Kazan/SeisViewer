import os
from typing import List

import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.uic import *
from PyQt5.QtCore import QThread, pyqtSignal

from SeisViewer.GUI.Structures import FileInfo
from SeisViewer.GUI.Dialogs import show_folder_dialog
from SeisViewer.Functions.Exporting import signal_to_file
from SeisViewer.Functions.Exporting import spectrum_to_file

from SeisViewer.Functions.Plotting import plot_signals
from SeisViewer.Functions.Plotting import plot_spectrums
from SeisViewer.Functions.Plotting import plot_correlation


class FormParameters:
    export_folder = ''
    root_folder_name = 'ReviseData'
    is_signal_files = False
    is_signal_graphs = False
    is_spectrum_files = False
    is_spectrum_graphs = False
    is_correlation_graph = False
    spectrum_graph_freq_interval = (0, 10)


class External(QThread):
    finished_percent = pyqtSignal(float)
    parameters = None  # type: FormParameters
    components = ['X', 'Y', 'Z']
    files_info: List[FileInfo] = []
    signals: np.ndarray = []
    spectrums: np.ndarray = []
    correlations: np.ndarray = []
    colors = []

    def run(self):
        self.finished_percent.emit(0)
        root = os.path.join(self.parameters.export_folder,
                            self.parameters.root_folder_name)
        for f_index, file_data in enumerate(self.files_info):
            file_name = file_data.name.split('.')[0]
            if self.parameters.is_signal_files or self.parameters.is_signal_graphs:
                signal_path = os.path.join(root, 'Signals')

                start_col_id = len(self.components) * f_index + 1
                col_ids = [0] + [x + start_col_id for x in range(len(self.components))]
                data = self.signals[:, col_ids]

                if self.parameters.is_signal_files:
                    path = os.path.join(signal_path, 'Dat')
                    if not os.path.exists(path):
                        os.makedirs(path)
                    signal_to_file(data, path, file_name)
                if self.parameters.is_signal_graphs:
                    path = os.path.join(signal_path, 'Png')
                    if not os.path.exists(path):
                        os.makedirs(path)
                    plot_signals(data, path, file_name)

            if self.parameters.is_spectrum_files or self.parameters.is_spectrum_graphs:
                spectrum_path = os.path.join(root, 'Spectrums')

                start_col_id = f_index * len(self.components) * 2 + 1
                col_ids = [0] + [x + start_col_id for x in
                                 range(len(self.components) * 2)]
                data = self.spectrums[:, col_ids]

                if self.parameters.is_spectrum_files:
                    path = os.path.join(spectrum_path, 'Dat')
                    if not os.path.exists(path):
                        os.makedirs(path)
                    spectrum_to_file(data, path, file_name)
                if self.parameters.is_spectrum_graphs:
                    path = os.path.join(spectrum_path, 'Png')
                    if not os.path.exists(path):
                        os.makedirs(path)
                    plot_spectrums(data, path, file_name,
                                   freq_lims=self.parameters.spectrum_graph_freq_interval)

            percent_val = (f_index + 1) / len(self.files_info)
            self.finished_percent.emit(percent_val * 100)

        if self.parameters.is_correlation_graph:
            path = os.path.join(root)
            if not os.path.exists(path):
                os.makedirs(path)
            all_files_list = [x.name.split('.')[0] for x in self.files_info]
            for i, component in enumerate(self.components):
                file_name = f'{component}_Correlations'
                plot_correlation(all_files_list, self.colors,
                                 self.correlations[i], path, file_name)


class ReviseExportForm:
    def __init__(self, parent):
        self.__window_type = 'revise_export_form'
        self.__parent = parent

        self.components = ['X', 'Y', 'Z']
        self.files_info: List[FileInfo] = []
        self.static_colors = []
        self.signals = np.array([])
        self.spectrums = np.array([])
        self.correlations: List[np.ndarray] = []
        self.__form_parameters = FormParameters()
        self.__calc_thread = None

        self.__window = QMainWindow()
        self.__forms_folder = parent.parent.form_folder
        ui_path = os.path.join(self.__forms_folder, 'ReviseExportForm.ui')
        self.__ui = loadUi(ui_path, self.__window)

        self.__ui.bOpenFolder.clicked.connect(self.open_folder)
        self.__ui.cbSpectrumGraphs.stateChanged.connect(self.activate_spectrum_limits)
        self.__ui.bExport.clicked.connect(self.start_proc)

    @property
    def window(self):
        return self.__window

    @property
    def parent(self):
        return self.__parent

    @property
    def ui(self):
        return self.__ui

    def set_start_form_state(self, files_info: List[FileInfo],
                             colors: list, signals: np.ndarray,
                             spectrums: np.ndarray,
                             correlations: List[np.ndarray]):
        params = FormParameters()
        self.__form_parameters = params

        self.files_info = files_info
        self.static_colors = colors
        self.signals = signals
        self.spectrums = spectrums
        self.correlations = correlations

        ui = self.ui
        ui.eExportFolder.clear()
        ui.eRootFolderName.setText(params.root_folder_name)
        ui.cbSignalFiles.setChecked(params.is_signal_files)
        ui.cbSignalGraphs.setChecked(params.is_signal_graphs)
        ui.cbSpectrumFiles.setChecked(params.is_spectrum_files)
        ui.cbSpectrumGraphs.setChecked(params.is_spectrum_graphs)
        ui.cbCorrelationGraph.setChecked(params.is_correlation_graph)
        ui.sbMinFreq.setValue(params.spectrum_graph_freq_interval[0])
        ui.sbMaxFreq.setValue(params.spectrum_graph_freq_interval[1])
        ui.progressBar.setValue(0)
        self.activate_spectrum_limits()
        if self.signals.shape[0] == 0:
            ui.cbSignalFiles.setDisabled(True)
            ui.cbSignalGraphs.setDisabled(True)
        else:
            ui.cbSignalFiles.setEnabled(True)
            ui.cbSignalGraphs.setEnabled(True)
        if self.spectrums.shape[0] == 0:
            ui.cbSpectrumFiles.setDisabled(True)
            ui.cbSpectrumGraphs.setDisabled(True)
        else:
            ui.cbSpectrumFiles.setEnabled(True)
            ui.cbSpectrumGraphs.setEnabled(True)
        if len(self.correlations) == 0:
            ui.cbCorrelationGraph.setDisabled(True)
        else:
            ui.cbCorrelationGraph.setEnabled(True)

    @property
    def form_parameters(self) -> FormParameters:
        ui, params = self.ui, self.__form_parameters
        params.export_folder = ui.eExportFolder.text()
        params.root_folder_name = ui.eRootFolderName.text()
        params.is_signal_files = ui.cbSignalFiles.isChecked()
        params.is_signal_graphs = ui.cbSignalGraphs.isChecked()
        params.is_spectrum_files = ui.cbSpectrumFiles.isChecked()
        params.is_spectrum_graphs = ui.cbSpectrumGraphs.isChecked()
        params.is_correlation_graph = ui.cbCorrelationGraph.isChecked()
        f_min = ui.sbMinFreq.value()
        f_max = ui.sbMaxFreq.value()
        params.spectrum_graph_freq_interval = (f_min, f_max)
        return params

    def open_folder(self):
        self.ui.eExportFolder.clear()
        path = show_folder_dialog()
        self.ui.eExportFolder.setText(path)

    def activate_spectrum_limits(self):
        ui = self.ui
        ui.sbMinFreq.setValue(0)
        ui.sbMaxFreq.setValue(10)
        if ui.cbSpectrumGraphs.isChecked():
            ui.sbMinFreq.setEnabled(True)
            ui.sbMaxFreq.setEnabled(True)
        else:
            ui.sbMinFreq.setDisabled(True)
            ui.sbMaxFreq.setDisabled(True)

    def set_progress_value(self, value):
        self.ui.progressBar.setValue(value)
        if value == 100:
            self.ui.statusBar.showMessage('Done')

    def start_proc(self):
        if self.__calc_thread is not None and self.__calc_thread.isFinished():
            self.__calc_thread = None

        if self.__calc_thread is not None:
            return
        self.ui.statusBar.showMessage('Wait please...')

        self.set_progress_value(0)
        if len(self.files_info) == 0:
            self.ui.statusBar.showMessage('No data for processing')
            return

        thread = External()
        thread.parameters = self.form_parameters
        thread.files_info = self.files_info
        thread.signals = self.signals
        thread.spectrums = self.spectrums
        thread.correlations = self.correlations
        thread.colors = self.static_colors
        thread.finished_percent.connect(self.set_progress_value)
        self.__calc_thread = thread
        thread.start()
