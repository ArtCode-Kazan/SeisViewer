import sys
import os
from datetime import datetime
from typing import List

from PyQt5.QtWidgets import *
from PyQt5.uic import *

from seiscore import BinaryFile
from seiscore.binaryfile.binaryfile import BadHeaderData, BadFilePath
from seiscore.binaryfile.binaryfile import FileInfo

from seisviewer.gui.dialogs import show_folder_dialog, show_message

from seisviewer.gui.revise_view_form import ReviseViewForm
from seisviewer.gui.files_joining_form import FilesJoiningForm
from seisviewer.gui.spectrogram_view_form import SpectrogramViewForm


DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S.%f'


class MainWindow:
    def __init__(self):
        self.__app = QApplication(sys.argv)
        self.__window = QMainWindow()

        self.__files_info: List[FileInfo] = []

        self.__revise_form = ReviseViewForm(self)
        self.__files_joining_form = FilesJoiningForm(self)
        self.__spectrogram_form = SpectrogramViewForm(self)

        ui_path = os.path.join(self.forms_folder, 'MainWindowForm.ui')
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
    def window(self):
        return self.__window

    @property
    def _ui(self):
        return self.__ui

    @property
    def forms_folder(self):
        import seisviewer
        module_folder = os.path.dirname(seisviewer.__file__)
        return os.path.join(module_folder, 'gui', 'forms')

    @property
    def files_info(self) -> List[FileInfo]:
        return self.__files_info

    def screen_center(self):
        frame_geom = self.window.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_geom.moveCenter(center_point)
        self.window.move(frame_geom.topLeft())

    def add_grid_row(self, file_info: FileInfo):
        grid: QTableWidget = self._ui.gFileInfo
        grid.setSortingEnabled(False)
        new_rows_count = grid.rowCount() + 1
        grid.setRowCount(new_rows_count)
        index = new_rows_count - 1

        grid.setItem(index, 0, QTableWidgetItem(file_info.name))
        grid.setItem(index, 1, QTableWidgetItem(file_info.format_type))
        grid.setItem(index, 2, QTableWidgetItem(str(file_info.frequency)))

        dt_start = file_info.time_start.strftime(DATETIME_FORMAT)
        grid.setItem(index, 3, QTableWidgetItem(dt_start))

        dt_stop = file_info.time_stop.strftime(DATETIME_FORMAT)
        grid.setItem(index, 4, QTableWidgetItem(dt_stop))

        grid.setItem(index, 5, QTableWidgetItem(file_info.formatted_duration))
        grid.setItem(index, 6, QTableWidgetItem(str(file_info.longitude)))
        grid.setItem(index, 7, QTableWidgetItem(str(file_info.latitude)))
        grid.setSortingEnabled(True)

    def open_files(self):
        """
        Loading files info into grid
        :return:
        """
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_paths = file_dialog.getOpenFileNames()[0]
        if len(file_paths) == 0:
            return

        for path in file_paths:
            try:
                bin_data = BinaryFile(path)
            except (BadFilePath, BadHeaderData):
                continue
            file_info = bin_data.short_file_info
            if file_info not in self.__files_info:
                self.__files_info.append(file_info)
                self.add_grid_row(file_info)

    def delete_selected_row(self):
        grid = self._ui.gFileInfo
        index = grid.currentRow()

        if index == -1:
            return

        file_name = grid.item(index, 0).text()
        for i, item in enumerate(self.files_info):
            if item.name == file_name:
                deleting_index = i
                break
        else:
            deleting_index = -1

        if deleting_index != -1:
            self._ui.gFileInfo.removeRow(index)
            self.__files_info.pop(deleting_index)

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
        if not export_folder:
            show_message('File saving was cancelled - export folder not '
                         'selected')
            return

        full_path = os.path.join(export_folder, 'FileDataTable.dat')
        header = ['FileName', 'Type', 'Frequency', 'DateTimeStart',
                  'DateTimeStop', 'Duration', 'Longitude', 'Latitude']
        with open(full_path, 'w') as f:
            f.write('\t'.join(header))
            for item in self.files_info:
                item: FileInfo = item
                dt_start = datetime.strftime(item.time_start, DATETIME_FORMAT)
                dt_stop = datetime.strftime(item.time_stop, DATETIME_FORMAT)
                record = [item.name, item.format_type, item.frequency,
                          dt_start, dt_stop, item.formatted_duration,
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
