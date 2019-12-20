import sys
import os
import imp
from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.uic import *

from SeisCore.BinaryFile.BinaryFile import BinaryFile

from SeisRevise.GUI.Dialogs import show_message
from SeisRevise.GUI.SpectrogramsForm import SpectrogramsForm
from SeisRevise.GUI.ReviseForm import ReviseForm
from SeisRevise.GUI.FileStitchingForm import FileStitchingForm
from SeisRevise.GUI.ViewSpectrogramForm import ViewSpectrogramForm


class MainWindow:
    def __init__(self):
        self.__window_type = 'main_window'

        module_folder = imp.find_module('SeisRevise')[1]
        self.__forms_folder = os.path.join(module_folder, 'GUI', 'Forms')

        self.__app = QApplication(sys.argv)
        self.__window = QMainWindow()

        self.__files_info = None

        self.__spectrograms_form = SpectrogramsForm(self)
        self.__revise_form = ReviseForm(self)
        self.__file_stitching_form=FileStitchingForm(self)
        self.__view_spectrum_form=ViewSpectrogramForm(self)

        ui_path = os.path.join(self.__forms_folder, 'MainWindowForm.ui')
        self.__ui = loadUi(ui_path, self.__window)
        self.__ui.aLoadFiles.triggered.connect(self.open_files)
        self.__ui.aSpectrograms.triggered.connect(self.open_spectrograms_form)
        self.__ui.aCorrelations.triggered.connect(self.open_revise_form)
        self.__ui.aFileStitching.triggered.connect(self.open_stitching_form)
        self.__ui.aSpectrumViewer.triggered.connect(self.open_view_spectrum_form)
        self.__ui.bDelRow.clicked.connect(self.delete_selected_rows)

        self.__window.show()
        self.__app.exec()

    @property
    def window_type(self):
        return self.__window_type

    @property
    def window(self):
        return self.__window

    @property
    def _ui(self):
        return self.__ui

    @property
    def form_folder(self):
        return self.__forms_folder

    @property
    def files_info(self):
        return self.__files_info

    def open_files(self):
        """
        Loading files info into grid
        :return:
        """
        self._ui.gFileInfo.setRowCount(0)

        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_paths = file_dialog.getOpenFileNames()[0]
        self.__files_info = self._get_file_info(file_paths=file_paths)

        if self.__files_info is not None:
            file_count = len(self.__files_info.keys())
            self._ui.gFileInfo.setRowCount(file_count)
            for index, key in enumerate(self.__files_info):
                current_file_info = self.__files_info[key]
                self._ui.gFileInfo.setItem(index, 0, QTableWidgetItem(key))
                self._ui.gFileInfo.setItem(index, 1, QTableWidgetItem(
                    current_file_info['file_type']))

                cb_record_type = QComboBox()
                cb_record_type.addItem('ZXY')
                self._ui.gFileInfo.setCellWidget(index, 2, cb_record_type)

                self._ui.gFileInfo.setItem(index, 3, QTableWidgetItem(
                    str(current_file_info['frequency'])))

                dt_start = datetime.strftime(
                    current_file_info['datetime_start'], '%d.%m.%Y %H:%M:%S')
                dt_stop = datetime.strftime(
                    current_file_info['datetime_stop'], '%d.%m.%Y %H:%M:%S')
                self._ui.gFileInfo.setItem(index, 4,
                                           QTableWidgetItem(dt_start))
                self._ui.gFileInfo.setItem(index, 5,
                                           QTableWidgetItem(dt_stop))

    @staticmethod
    def _get_file_info(file_paths):
        """
        Getting file info from file paths
        :param file_paths: list of file paths
        :return:
        """
        if len(file_paths) == 0:
            return None

        files_data = dict()
        for path in file_paths:
            file_name = os.path.basename(path)
            try:
                name, extension = file_name.split('.')
            except ValueError:
                continue

            if extension in ('00', 'xx', 'bin'):
                bin_data = BinaryFile()
                bin_data.path = path
                bin_data.record_type = 'XYZ'

                file_info = dict()
                file_info['path'] = path
                file_info['file_type'] = bin_data.device_type
                file_info['frequency'] = bin_data.signal_frequency
                file_info['record_type'] = None
                file_info['datetime_start'] = bin_data.datetime_start
                file_info['datetime_stop'] = bin_data.datetime_stop

                files_data[file_name] = file_info
        if len(files_data.keys()) == 0:
            return None
        else:
            return files_data

    def delete_selected_rows(self):
        indexes = self._ui.gFileInfo.selectionModel().selectedRows()
        for index in indexes:
            self._ui.gFileInfo.removeRow(index.row())

    def _get_grid_data(self):
        if self.__files_info is None:
            return None

        deleting_keys = list()
        for key in self.__files_info:
            is_using = False
            index = None
            for i in range(self._ui.gFileInfo.rowCount()):
                file_name = self._ui.gFileInfo.item(i, 0).text()
                if file_name == key:
                    is_using = True
                    index = i
                    break
            if is_using:
                w = self._ui.gFileInfo.cellWidget(index, 2)
                record_type = w.currentText()
                self.__files_info[key]['record_type'] = record_type
            else:
                deleting_keys.append(key)

        for item in deleting_keys:
            del self.__files_info[item]

    def open_spectrograms_form(self):
        if self.files_info is None:
            return
        self._get_grid_data()

        start_time_analysis = None
        stop_time_analysis = None
        resample_frequency = None

        for key in self.files_info:
            dt_start = self.files_info[key]['datetime_start']
            dt_stop = self.files_info[key]['datetime_stop']
            frequency = self.files_info[key]['frequency']

            if start_time_analysis is None:
                start_time_analysis = dt_start
                stop_time_analysis = dt_stop
                resample_frequency = frequency
            else:
                start_time_analysis = min(start_time_analysis, dt_start)
                stop_time_analysis = max(stop_time_analysis, dt_stop)
                resample_frequency = min(resample_frequency, frequency)

        spectrograms_form_ui = self.__spectrograms_form.ui

        # spectrograms_form_ui.dtStartTime.setMinimumDateTime(
        #     start_time_analysis)
        # spectrograms_form_ui.dtStartTime.setMaximumDateTime(
        #     stop_time_analysis)
        # spectrograms_form_ui.dtStopTime.setMinimumDateTime(
        #     start_time_analysis)
        # spectrograms_form_ui.dtStopTime.setMaximumDateTime(stop_time_analysis)
        spectrograms_form_ui.dtStartTime.setDateTime(start_time_analysis)
        spectrograms_form_ui.dtStopTime.setDateTime(stop_time_analysis)
        spectrograms_form_ui.sbResampleFrequency.setValue(resample_frequency)
        self.__spectrograms_form.window.show()

    def open_revise_form(self):
        if self.files_info is None:
            return
        self._get_grid_data()

        cross_start_time_analysis = None
        cross_stop_time_analysis = None
        resample_frequency = None

        for key in self.files_info:
            dt_start = self.files_info[key]['datetime_start']
            dt_stop = self.files_info[key]['datetime_stop']
            frequency = self.files_info[key]['frequency']

            if cross_start_time_analysis is None:
                cross_start_time_analysis = dt_start
                cross_stop_time_analysis = dt_stop
                resample_frequency = frequency
            else:
                cross_start_time_analysis = max(cross_start_time_analysis,
                                                dt_start)
                cross_stop_time_analysis = min(cross_stop_time_analysis,
                                               dt_stop)
                resample_frequency = min(resample_frequency, frequency)

        if cross_start_time_analysis >= cross_stop_time_analysis:
            show_message('Error: Time crossing interval not found')
            return

        revise_ui = self.__revise_form.ui
        # revise_ui.dtStartTime.setMinimumDateTime(
        #     cross_start_time_analysis)
        # revise_ui.dtStartTime.setMaximumDateTime(
        #     cross_stop_time_analysis)
        # revise_ui.dtStopTime.setMinimumDateTime(
        #     cross_start_time_analysis)
        # revise_ui.dtStopTime.setMaximumDateTime(cross_stop_time_analysis)
        revise_ui.dtStartTime.setDateTime(cross_start_time_analysis)
        revise_ui.dtStopTime.setDateTime(cross_stop_time_analysis)
        revise_ui.sbResampleFrequency.setValue(resample_frequency)

        self.__revise_form.window.show()

    def open_stitching_form(self):
        self.__file_stitching_form.window.show()

    def open_view_spectrum_form(self):
        self.__view_spectrum_form.window.show()

