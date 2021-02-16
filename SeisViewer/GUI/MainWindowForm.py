import sys
import os
import imp
from datetime import datetime
from typing import List

from PyQt5.QtWidgets import *
from PyQt5.uic import *

from SeisCore.BinaryFile.BinaryFile import BinaryFile
from SeisCore.BinaryFile.BinaryFile import BadHeaderData, BadFilePath

from SeisViewer.GUI.Dialogs import show_folder_dialog, show_message
from SeisViewer.GUI.Structures import FileInfo

from SeisViewer.GUI.ReviseViewForm import ReviseViewForm
from SeisViewer.GUI.FilesJoiningForm import FilesJoiningForm
from SeisViewer.GUI.SpectrogramViewForm import SpectrogramViewForm


def duration_formatting(total_seconds: float) -> str:
    days = int(total_seconds / (24 * 3600))
    hours = int((total_seconds - days * 24 * 3600) / 3600)
    minutes = int((total_seconds - days * 24 * 3600 - hours * 3600) / 60)
    seconds = total_seconds - days * 24 * 3600 - hours * 3600 - \
              minutes * 60

    hours = '0' * (2 - len(str(hours))) + str(hours)
    minutes = '0' * (2 - len(str(minutes))) + str(minutes)
    whole_part, fractional_part = str(seconds).split('.')
    seconds = '0' * (
                2 - len(whole_part)) + whole_part + '.' + fractional_part[:2]
    if days > 0:
        duration_format = f'{days} days {hours}:{minutes}:{seconds}'
    else:
        duration_format = f'{hours}:{minutes}:{seconds}'
    return duration_format


def get_files_info(file_paths: list) -> List[FileInfo]:
    """
    Getting file info from file paths
    :param file_paths: list of file paths
    :return:
    """
    if len(file_paths) == 0:
        return []

    result = []
    for path in file_paths:
        file_name = os.path.basename(path)
        try:
            bin_data = BinaryFile(path)
            header_data = bin_data.file_header
        except (BadFilePath, BadHeaderData):
            continue
        format_type = bin_data.file_type
        duration = duration_formatting(bin_data.seconds_duration)
        file_info = FileInfo(path, file_name, format_type,
                             bin_data.signal_frequency,
                             bin_data.datetime_start, bin_data.datetime_stop,
                             duration, bin_data.longitude, bin_data.latitude)
        result.append(file_info)
    return result


class MainWindow:
    def __init__(self):
        self.__window_type = 'main_window'

        module_folder = imp.find_module('SeisViewer')[1]
        self.__forms_folder = os.path.join(module_folder, 'GUI', 'Forms')

        self.__app = QApplication(sys.argv)
        self.__window = QMainWindow()

        self.__files_info: List[FileInfo] = []

        self.__revise_form = ReviseViewForm(self)
        self.__files_joining_form = FilesJoiningForm(self)
        self.__spectrogram_form = SpectrogramViewForm(self)

        ui_path = os.path.join(self.__forms_folder, 'MainWindowForm.ui')
        self.__ui = loadUi(ui_path, self.__window)
        self.__ui.bAddFiles.clicked.connect(self.open_files)
        self.__ui.bDelRow.clicked.connect(self.delete_selected_row)
        self.__ui.bRemoveFiles.clicked.connect(self.clear_grid_data)
        self.__ui.bApplyColumnsVisible.clicked.connect(self.hide_columns)
        self.__ui.bSaveToFile.clicked.connect(self.export_table_to_file)

        self.__ui.aSpectrograms.triggered.connect(self.open_spectrograms_form)
        self.__ui.aRevise.triggered.connect(self.open_revise_form)
        self.__ui.aFilesJoining.triggered.connect(self.open_files_joining_form)

        self.screen_center()
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
    def files_info(self) -> List[FileInfo]:
        return self.__files_info

    def screen_center(self):
        frame_geom = self.window.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_geom.moveCenter(center_point)
        self.window.move(frame_geom.topLeft())

    def open_files(self):
        """
        Loading files info into grid
        :return:
        """
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_paths = file_dialog.getOpenFileNames()[0]
        new_files = get_files_info(file_paths=file_paths)
        new_files = [x for x in new_files if x not in self.__files_info]
        self.__files_info += new_files

        new_rows_count = len(self.__files_info)
        grid = self._ui.gFileInfo
        grid.setRowCount(new_rows_count)
        for index, file_info in enumerate(self.__files_info):
            grid.setItem(index, 0, QTableWidgetItem(file_info.name))
            grid.setItem(index, 1, QTableWidgetItem(file_info.format_type))
            grid.setItem(index, 2, QTableWidgetItem(str(file_info.frequency)))
            dt_start = datetime.strftime(file_info.time_start,
                                         '%d.%m.%Y %H:%M:%S.%f')
            dt_stop = datetime.strftime(file_info.time_stop,
                                        '%d.%m.%Y %H:%M:%S.%f')
            grid.setItem(index, 3, QTableWidgetItem(dt_start))
            grid.setItem(index, 4, QTableWidgetItem(dt_stop))
            grid.setItem(index, 5, QTableWidgetItem(file_info.duration))
            grid.setItem(index, 6, QTableWidgetItem(str(file_info.longitude)))
            grid.setItem(index, 7, QTableWidgetItem(str(file_info.latitude)))

    def delete_selected_row(self):
        index = self._ui.gFileInfo.currentRow()
        if index == -1:
            return
        grid = self._ui.gFileInfo

        file_name = grid.item(index, 0).text()
        frequency = int(grid.item(index, 2).text())
        dt_start = datetime.strptime(grid.item(index, 3).text(),
                                     '%d.%m.%Y %H:%M:%S.%f')
        deleting_index = -1
        for i, item in enumerate(self.files_info):
            if (item.name == file_name and item.frequency == frequency and
                    item.time_start == dt_start):
                deleting_index = i
                break
        if deleting_index != -1:
            self._ui.gFileInfo.removeRow(index)
            self.__files_info.pop(index)

    def clear_grid_data(self):
        self._ui.gFileInfo.setRowCount(0)
        self.__files_info = []

    def hide_columns(self):
        is_show_type = self._ui.cbType.isChecked()
        self._ui.gFileInfo.setColumnHidden(1, not is_show_type)
        is_show_freq = self._ui.cbFrequency.isChecked()
        self._ui.gFileInfo.setColumnHidden(2, not is_show_freq)
        is_show_dt_start = self._ui.cbTimeStart.isChecked()
        self._ui.gFileInfo.setColumnHidden(3, not is_show_dt_start)
        is_show_dt_stop = self._ui.cbTimeStop.isChecked()
        self._ui.gFileInfo.setColumnHidden(4, not is_show_dt_stop)
        is_show_duration = self._ui.cbDuration.isChecked()
        self._ui.gFileInfo.setColumnHidden(5, not is_show_duration)
        is_show_longitude = self._ui.cbLongitude.isChecked()
        self._ui.gFileInfo.setColumnHidden(6, not is_show_longitude)
        is_show_latitude = self._ui.cbLatitude.isChecked()
        self._ui.gFileInfo.setColumnHidden(7, not is_show_latitude)

    def export_table_to_file(self):
        if self._ui.gFileInfo.rowCount() == 0:
            return

        export_folder = show_folder_dialog()
        full_path = os.path.join(export_folder, 'FileDataTable.dat')
        header = ['FileName', 'Type', 'Frequency', 'DateTimeStart',
                  'DateTimeStop', 'Duration', 'Longitude', 'Latitude']
        dt_fmt = '%d.%m.%Y %H:%M:%S.%f'
        with open(full_path, 'w') as f:
            f.write('\t'.join(header))
            for item in self.files_info:
                item: FileInfo = item
                dt_start = datetime.strftime(item.time_start, dt_fmt)
                dt_stop = datetime.strftime(item.time_stop, dt_fmt)
                record = [item.name, item.format_type, item.frequency,
                          dt_start, dt_stop, item.duration,
                          item.longitude, item.latitude]
                f.write('\n' + '\t'.join(map(str, record)))
            show_message('File saving completed')

    def open_revise_form(self):
        if len(self.files_info) == 0:
            return

        cross_start_time_analysis = self.files_info[0].time_start
        cross_stop_time_analysis = self.files_info[0].time_stop
        resample_frequency = self.files_info[0].frequency

        for item in self.files_info[1:]:
            dt_start, dt_stop = item.time_start, item.time_stop
            frequency = item.frequency
            cross_start_time_analysis = max(cross_start_time_analysis,
                                            dt_start)
            cross_stop_time_analysis = min(cross_stop_time_analysis,
                                           dt_stop)
            resample_frequency = min(resample_frequency, frequency)

        if cross_start_time_analysis >= cross_stop_time_analysis:
            show_message('Error: Time crossing interval not found')
            return

        self.__revise_form.set_start_form_state(
            self.files_info,
            [cross_start_time_analysis, cross_stop_time_analysis],
            resample_frequency)
        self.__revise_form.window.show()

    def open_spectrograms_form(self):
        if len(self.files_info) == 0:
            return
        self.__spectrogram_form.set_start_form_state(self.files_info)
        self.__spectrogram_form.window.show()

    def open_files_joining_form(self):
        self.__files_joining_form.set_start_form_state()
        self.__files_joining_form.window.show()
