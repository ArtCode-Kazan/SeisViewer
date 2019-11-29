import os
from datetime import datetime
import numpy as np
from numpy.fft import rfftfreq

from PyQt5.QtWidgets import *
from PyQt5.uic import *
from PyQt5.QtCore import QThread, pyqtSignal

from SeisCore.BinaryFile.BinaryFile import BinaryFile
from SeisCore.Functions.Spectrum import average_spectrum
from SeisCore.Plotting.Plotting import plot_signal
from SeisCore.Plotting.Plotting import plot_average_spectrum
from SeisCore.Functions.Wavelet import detrend

from SeisRevise.GUI.Dialogs import show_folder_dialog
from SeisRevise.Functions.Processing import cross_correlation
from SeisRevise.Functions.Plotting import generate_random_color
from SeisRevise.Functions.Plotting import plot_all_smooth_spectrums
from SeisRevise.Functions.Plotting import plot_single_correlation
from SeisRevise.Functions.Plotting import plot_correlation


class External(QThread):
    finished_percent = pyqtSignal(float)
    parts_count = None
    files_info = None
    parameters = None

    def run(self):
        params = self.parameters
        dt = (params['dt_stop'] - params['dt_start']).total_seconds()
        discrete_amount = int(round(dt * params['resample_frequency']))
        components_amount = len(params['components'])
        files_amount = len(self.files_info.keys())

        frequencies_list = rfftfreq(params['window_size'],
                                    1 / params['resample_frequency'])
        frequency_count = frequencies_list.shape[0]

        joined_signal_array = np.empty(
            shape=(components_amount, discrete_amount, files_amount),
            dtype=np.int)

        average_spectrum_data = np.empty(
            shape=(components_amount, 2, frequency_count, files_amount),
            dtype=np.float)

        bin_files_list = list(self.files_info.keys())
        for index in range(len(bin_files_list)):
            bin_files_list[index] = bin_files_list[index].split('.')[0]

        finished_parts_count = 0
        for index_a, key in enumerate(self.files_info):
            cur_file_data = self.files_info[key]
            record_type = cur_file_data['record_type']
            file_path = cur_file_data['path']

            bin_data = BinaryFile()
            bin_data.path = file_path
            bin_data.record_type = record_type
            bin_data.use_avg_values = True
            bin_data.resample_frequency = params['resample_frequency']
            bin_data.read_date_time_start = params['dt_start']
            bin_data.read_date_time_stop = params['dt_stop']
            signals = bin_data.signals

            if params['detrend_frequency']!=0:
                for i in range(signals.shape[1]):
                    signals[:,i]=detrend(signal=signals[:,i],
                                         frequency=bin_data.resample_frequency,
                                         edge_frequency=params['detrend_frequency'])
            for index_b, component in enumerate(params['components']):
                compoment_signal = signals[:, record_type.index(component)]
                joined_signal_array[index_b, :, index_a] = compoment_signal
                # calculating average unsmoothed spectrum
                av_spec_simple_component = average_spectrum(
                    signal=compoment_signal,
                    frequency=params['resample_frequency'],
                    window=params['window_size'],
                    overlap=params['overlap_size'],
                    med_filter=None,
                    marmett_filter=None)
                average_spectrum_data[index_b, 0, :, index_a] = \
                    av_spec_simple_component[:, 1]

                # calculating average smoothed spectrum
                av_spec_smooth_component = average_spectrum(
                    signal=compoment_signal,
                    frequency=params['resample_frequency'],
                    window=params['window_size'],
                    overlap=params['overlap_size'],
                    med_filter=params['median_filter'],
                    marmett_filter=params['marmett_filter'])
                average_spectrum_data[index_b, 1, :, index_a] = \
                    av_spec_smooth_component[:, 1]

                finished_parts_count += 1
                percent_value = finished_parts_count / self.parts_count * 100
                self.finished_percent.emit(percent_value)

        result_correlate_matrix = np.empty(
            shape=(components_amount, files_amount, files_amount),
            dtype=np.float)
        for component in range(components_amount):
            result_correlate_matrix[component, :, :] = cross_correlation(
                frequency=frequencies_list,
                f_min_analysis=params['correlation_min_frequency'],
                f_max_analysis=params['correlation_max_frequency'],
                amplitudes=average_spectrum_data[component, 1, :, :])

        # result data exporting
        read_dt_start_label = datetime.strftime(params['dt_start'],
                                                '%Y-%m-%d_%H-%M-%S')
        for index_a, bin_file_name in enumerate(self.files_info):
            bin_file_name = bin_file_name.split('.')[0]

            file_processing_result_folder = \
                os.path.join(params['output_folder'], bin_file_name)
            if not os.path.exists(file_processing_result_folder):
                os.mkdir(file_processing_result_folder)

            for index_b, component_label in enumerate(params['components']):
                if params['is_selection_signal_file']:
                    dat_file_name = f'{bin_file_name}_ClearSignal_' \
                        f'{component_label}_Component.dat'
                    export_path = os.path.join(file_processing_result_folder,
                                               dat_file_name)
                    np.savetxt(fname=export_path,
                               X=joined_signal_array[index_b, :, index_a],
                               fmt='%i')

                if params['is_selection_signal_graph']:
                    png_file_name = \
                        f'{bin_file_name}_ClearSignal_{component_label}_{read_dt_start_label}'
                    plot_signal(time_start_sec=0,
                                frequency=params['resample_frequency'],
                                signal=joined_signal_array[index_b, :,
                                       index_a],
                                label=png_file_name,
                                output_folder=file_processing_result_folder,
                                output_name=png_file_name)

                if params['is_spectrum_graph']:
                    png_file_name = '{}_AverageSpectrum_{}_Component_' \
                                    'Graph'.format(bin_file_name,
                                                   component_label)
                    plot_average_spectrum(
                        frequency=frequencies_list,
                        spectrum_begin_amplitudes=average_spectrum_data[
                                                  index_b, 0, :, index_a],
                        spectrum_smooth_amplitudes=average_spectrum_data[
                                                   index_b, 1, :, index_a],
                        f_min=params['visual_min_frequency'],
                        f_max=params['visual_max_frequency'],
                        output_folder=file_processing_result_folder,
                        output_name=png_file_name)

                if params['is_unsmoothed_spectrum_file']:
                    file_name = \
                        f'{bin_file_name}_{component_label}_Component.sc'
                    export_path = os.path.join(
                        file_processing_result_folder, file_name)

                    temp_array = np.empty(
                        shape=(frequencies_list.shape[0], 2),
                        dtype=np.float)
                    temp_array[:, 0] = frequencies_list
                    temp_array[:, 1] = average_spectrum_data[index_b, 0, :,
                                       index_a]
                    np.savetxt(fname=export_path, X=temp_array, fmt='%f',
                               delimiter='\t')

                if params['is_smoothed_spectrum_file']:
                    file_name = \
                        f'{bin_file_name}_{component_label}_Component.ssc'
                    export_path = os.path.join(
                        file_processing_result_folder, file_name)

                    temp_array = np.empty(
                        shape=(frequencies_list.shape[0], 2),
                        dtype=np.float)
                    temp_array[:, 0] = frequencies_list
                    temp_array[:, 1] = \
                        average_spectrum_data[index_b, 1, :, index_a]
                    np.savetxt(fname=export_path, X=temp_array, fmt='%f',
                               delimiter='\t')

                if params['is_correlation_graph']:
                    png_file_name = \
                        f'{bin_file_name}_Separate_Correlation_{component_label}_Component_Graph'

                    plot_single_correlation(
                        devices=bin_files_list,
                        correlation_data=result_correlate_matrix[
                                         index_b, index_a, :],
                        output_folder=file_processing_result_folder,
                        output_name=png_file_name)

                finished_parts_count += 1
                percent_value = finished_parts_count / self.parts_count * 100
                self.finished_percent.emit(percent_value)

        colors = list()
        for i in range(len(self.files_info.keys())):
            colors.append(generate_random_color())

        for index_a, component_label in enumerate(params['components']):
            if params['is_general_smooth_spectrum_graph']:
                file_name = f'SmoothSpectrums_{component_label}_Component'
                plot_all_smooth_spectrums(
                    spectrums_name_list=bin_files_list,
                    frequency=frequencies_list,
                    spectrum_data=average_spectrum_data[index_a, 1, :, :],
                    f_min_visualize=params['visual_min_frequency'],
                    f_max_visualize=params['visual_max_frequency'],
                    colors=colors, output_folder=params['output_folder'],
                    output_name=file_name)

            if params['is_correlation_matrix_file']:
                file_name = f'CorrelationMatrix_{component_label}_Component.dat'
                header = 'NULL\t' + '\t'.join(bin_files_list) + '\n'
                write_lines = list()
                write_lines.append(header)
                corr_matrix = result_correlate_matrix[index_a, :, :]
                for i in range(corr_matrix.shape[0]):
                    t = list()
                    t.append(bin_files_list[i])
                    for j in range(corr_matrix.shape[1]):
                        t.append(str(corr_matrix[i, j]))
                    s = '\t'.join(t) + '\n'
                    write_lines.append(s)
                export_path = os.path.join(params['output_folder'], file_name)
                f = open(export_path, 'w')
                for line in write_lines:
                    f.write(line)
                f.close()

            if params['is_general_correlation_graph']:
                file_name = f'Correlations_{component_label}_Component'
                plot_correlation(devices=bin_files_list,
                                 colors=colors,
                                 correlation_matrix=result_correlate_matrix[
                                                    index_a, :, :],
                                 output_folder=params['output_folder'],
                                 output_name=file_name)


class ReviseForm:
    def __init__(self, parent):
        self.__window_type = 'revise_form'
        self.__parent = parent

        self.__calc_thread = None
        self.__parameters = None

        self.__window = QMainWindow()
        self.__forms_folder = parent.form_folder
        ui_path = os.path.join(self.__forms_folder, 'ReviseForm.ui')
        self.__ui = loadUi(ui_path, self.__window)

        self.__ui.pbOpenFolder.clicked.connect(self.set_export_folder)
        self.__ui.cbUseMarmettFilter.stateChanged.connect(
            self.block_marmett_filter)
        self.__ui.cbUseMedianFilter.stateChanged.connect(
            self.block_median_filter)
        self.__ui.sbMarmettFilter.valueChanged.connect(
            self.control_change_marmett_filter)
        self.__ui.sbMedianFilter.valueChanged.connect(
            self.control_change_median_filter)

        self.__ui.bStartProcess.clicked.connect(self.processing)

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

    def block_marmett_filter(self):
        if not self.ui.cbUseMarmettFilter.isChecked():
            self.ui.sbMarmettFilter.setEnabled(False)
        else:
            self.ui.sbMarmettFilter.setEnabled(True)

    def block_median_filter(self):
        if not self.ui.cbUseMedianFilter.isChecked():
            self.ui.sbMedianFilter.setEnabled(False)
        else:
            self.ui.sbMedianFilter.setEnabled(True)

    def control_change_marmett_filter(self):
        val = self.ui.sbMarmettFilter.value()
        if val % 2 == 0:
            self.ui.sbMarmettFilter.setValue(val + 1)

    def control_change_median_filter(self):
        val = self.ui.sbMedianFilter.value()
        if val % 2 == 0:
            self.ui.sbMedianFilter.setValue(val + 1)

    def set_export_folder(self):
        self.ui.leFolderPath.clear()
        self.__export_folder_path = show_folder_dialog()
        if self.__export_folder_path is not None:
            self.ui.leFolderPath.setText(self.__export_folder_path)

    def collect_parameters(self):
        ui = self.ui
        params = dict()
        params['resample_frequency'] = ui.sbResampleFrequency.value()
        params['dt_start'] = ui.dtStartTime.dateTime().toPyDateTime()
        params['dt_stop'] = ui.dtStopTime.dateTime().toPyDateTime()
        params['window_size'] = ui.sbWindowSize.value()
        params['overlap_size'] = ui.sbOverlapSize.value()
        params['detrend_frequency']=ui.sbDentendEdge.value()

        if ui.cbUseMarmettFilter.isChecked():
            params['marmett_filter'] = ui.sbMarmettFilter.value()
        else:
            params['marmett_filter'] = None
        if ui.cbUseMedianFilter.isChecked():
            params['median_filter'] = ui.sbMedianFilter.value()
        else:
            params['median_filter'] = None

        params['correlation_min_frequency'] = \
            ui.sbMinCorrelationFrequency.value()
        params['correlation_max_frequency'] = \
            ui.sbMaxCorrelationFrequency.value()
        params['visual_min_frequency'] = ui.sbMinVisualFrequency.value()
        params['visual_max_frequency'] = ui.sbMaxVisualFrequency.value()

        components = list()
        if ui.cbXComponent.isChecked():
            components.append('X')
        if ui.cbYComponent.isChecked():
            components.append('Y')
        if ui.cbZComponent.isChecked():
            components.append('Z')
        params['components'] = components

        params['output_folder'] = ui.leFolderPath.text()
        params['is_selection_signal_file'] = \
            ui.cbSelectionSignalFile.isChecked()
        params['is_selection_signal_graph'] = \
            ui.cbSelectionSignalGraph.isChecked()
        params['is_spectrum_graph'] = ui.cbSpectrumGraph.isChecked()
        params['is_unsmoothed_spectrum_file'] = \
            ui.cbUnSmoothSpectrumFile.isChecked()
        params['is_smoothed_spectrum_file'] = \
            ui.cbSmoothSpectrumFile.isChecked()
        params['is_general_smooth_spectrum_graph'] = \
            ui.cbGeneralSmoothSpectrumGraph.isChecked()
        params['is_correlation_graph'] = ui.cbCorrelationGraph.isChecked()
        params['is_correlation_matrix_file'] = \
            ui.cbCorrelationMatrixFile.isChecked()
        params['is_general_correlation_graph'] = \
            ui.cbGeneralCorrelationGraph.isChecked()
        self.__parameters = params

    def thread_function(self):
        if self.__calc_thread is not None and self.__calc_thread.isFinished():
            self.__calc_thread = None

        if self.__calc_thread is not None:
            return

        self.set_progress_value(0)
        self.collect_parameters()
        parts_amount = 2 * len(self.__parameters['components']) * len(self.files_info.keys())

        self.__calc_thread = External()
        self.__calc_thread.files_info = self.files_info
        self.__calc_thread.parameters = self.__parameters
        self.__calc_thread.parts_count = parts_amount
        self.__calc_thread.finished_percent.connect(self.set_progress_value)
        self.__calc_thread.start()

    def set_progress_value(self, value):
        self.ui.progressBar.setValue(value)

    def processing(self):
        self.thread_function()
