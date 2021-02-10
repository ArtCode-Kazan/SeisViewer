import os
import shutil
from datetime import datetime
from datetime import timedelta
from typing import NamedTuple, List
from random import randint

from PyQt5.QtWidgets import *
from PyQt5.uic import *
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtGui

from SeisCore.BinaryFile.BinaryFile import BinaryFile
from SeisCore.BinaryFile.BinaryFile import UNSIGNED_INT_CTYPE
from SeisCore.BinaryFile.BinaryFile import BadHeaderData, BadFilePath

from SeisViewer.GUI.Dialogs import show_folder_dialog


class FileInfo(NamedTuple):
    path: str
    name: str
    frequency: int
    dt_start: datetime
    dt_stop: datetime

    @property
    def duration(self) -> float:
        return (self.dt_stop-self.dt_start).total_seconds()


class FormParameters(NamedTuple):
    export_folder: str
    main_file_name: str
    part_suffix: str


def get_file_parts(files_info: list) -> List[List[int]]:
    result = []
    if len(files_info) == 0:
        return result

    files_info.sort(key=lambda x: (x.dt_start, -x.duration))
    frequency = files_info[0].frequency
    minimal_d_time = 1 / frequency

    result.append([0])
    last_part_dt_stop = files_info[result[0][-1]].dt_stop
    for id_val, item in enumerate(files_info[1:]):
        id_val += 1
        item: FileInfo = item
        delta_time = (item.dt_start - last_part_dt_stop).total_seconds()
        if delta_time <= minimal_d_time and last_part_dt_stop < item.dt_stop:
            result[-1].append(id_val)
        elif item.dt_stop <= last_part_dt_stop:
            continue
        else:
            result.append([id_val])
        last_part_dt_stop = item.dt_stop
    if len(result[0]) == 1:
        return []
    return result


def get_random_rgb_color():
    return randint(0, 255), randint(0, 255), randint(0, 255)


def join_binary_files(file_paths: list, export_folder: str,
                      export_name: str, chunk_memory_size=1024):
    def base_joining(last_file, new_file):
        last_bin_data = BinaryFile(last_file)
        next_bin_data = BinaryFile(new_file)
        frequency = last_bin_data.signal_frequency
        discrete_duration = 1 / frequency
        if next_bin_data.datetime_start <= last_bin_data.datetime_stop:
            read_time_start = last_bin_data.datetime_stop + timedelta(
                seconds=discrete_duration)
        else:
            read_time_start = next_bin_data.datetime_start
        skipping_discrete_count = \
            int((read_time_start - next_bin_data.datetime_start).total_seconds() * frequency)
        skipping_bytes_count = next_bin_data.header_memory_size + \
                               next_bin_data.channels_count * \
                               UNSIGNED_INT_CTYPE.byte_size * skipping_discrete_count
        with open(last_file, 'ab') as f:
            with open(new_file, 'rb') as g:
                g.seek(skipping_bytes_count)
                while True:
                    chunk_part = g.read(chunk_memory_size)
                    if not chunk_part:
                        break
                    f.write(chunk_part)

    result_file_path = os.path.join(export_folder, export_name)
    shutil.copy(file_paths[0], result_file_path)
    for file in file_paths[1:]:
        base_joining(result_file_path, file)


class External(QThread):
    files_info = List[FileInfo]
    parts_ids = List[List[int]]
    export_folder = ''
    main_filename = ''
    part_suffix = ''
    finished_percent = pyqtSignal(float)
    status = pyqtSignal(str)

    def run(self):
        viewed_parts_count = 0
        self.status.emit('Wait please...')
        for part_index, part_set in enumerate(self.parts_ids):
            extension = self.files_info[part_set[0]].name.split('.')[-1]
            export_filename = f'{self.main_filename}{self.part_suffix}' \
                              f'{part_index + 1}.{extension}'
            file_paths = [self.files_info[x].path for x in part_set]
            join_binary_files(file_paths, self.export_folder, export_filename)
            viewed_parts_count += 1
            self.finished_percent.emit(
                viewed_parts_count / len(self.parts_ids) * 100)
        self.status.emit('Done')


class FilesJoiningForm:
    def __init__(self, parent):
        self.__window_type = 'stitching_form'
        self.__parent = parent

        self.__files_info = List[FileInfo]
        self.__part_files_ids = List[List[int]]

        self.__calc_thread = None

        self.__window = QMainWindow()
        self.__forms_folder = parent.form_folder
        ui_path = os.path.join(self.__forms_folder, 'FilesJoiningForm.ui')
        self.__ui = loadUi(ui_path, self.__window)

        self.__ui.pbOpenFolder.clicked.connect(self.open_folder)
        self.__ui.bStartProcess.clicked.connect(self.processing)

    @property
    def window(self):
        return self.__window

    @property
    def parent(self):
        return self.__parent

    @property
    def ui(self):
        return self.__ui

    def open_folder(self):
        self.ui.leFolderPath.clear()
        path = show_folder_dialog()
        self.ui.leFolderPath.setText(path)

        files_info = []
        for content in os.listdir(path):
            current_path = os.path.join(path, content)
            if not os.path.isfile(current_path):
                continue

            try:
                bin_data = BinaryFile(current_path)
                header_data = bin_data.file_header
            except (BadFilePath, BadHeaderData):
                continue

            files_info.append(FileInfo(current_path, content,
                                       bin_data.signal_frequency,
                                       bin_data.datetime_start,
                                       bin_data.datetime_stop))
        self.__files_info = files_info
        self.__part_files_ids = get_file_parts(files_info)
        self.fill_grid()

    def fill_grid(self):
        grid_data = self.ui.tGrid
        grid_data.setRowCount(len(self.__files_info))
        datetime_fmt = '%d-%m-%Y %H:%M:%S.%f'
        for i, item in enumerate(self.__files_info):
            grid_data.setItem(i, 0, QTableWidgetItem(item.name))
            dt_start = datetime.strftime(item.dt_start, datetime_fmt)
            dt_stop = datetime.strftime(item.dt_stop, datetime_fmt)
            grid_data.setItem(i, 1, QTableWidgetItem(dt_start))
            grid_data.setItem(i, 2, QTableWidgetItem(dt_stop))

        for part_ids in self.__part_files_ids:
            rgb_color = get_random_rgb_color()
            color = QtGui.QColor(rgb_color[0], rgb_color[1], rgb_color[2])
            for id_val in part_ids:
                for i in range(grid_data.columnCount()):
                    grid_data.item(id_val, i).setBackground(color)
        self.ui.lPartsCount.setText(str(len(self.__part_files_ids)))

    def set_start_form_state(self):
        ui = self.ui
        ui.leFolderPath.clear()
        ui.tGrid.setRowCount(0)
        ui.lPartsCount.setText('0')
        ui.eExportFileName.clear()
        ui.ePartSuffix.setText('_part_')
        ui.pbProcessStatus.setValue(0)
        ui.statusBar.showMessage('Ready')

    def get_form_parameters(self) -> FormParameters:
        export_folder = self.ui.leFolderPath.text()
        main_part_filename = self.ui.eExportFileName.text()
        part_suffix = self.ui.ePartSuffix.text()
        return FormParameters(export_folder, main_part_filename, part_suffix)

    def thread_function(self):
        if self.__calc_thread is not None and self.__calc_thread.isFinished():
            self.__calc_thread = None

        if self.__calc_thread is not None:
            return

        self.set_progress_value(0)
        form_params = self.get_form_parameters()

        self.__calc_thread = External()
        self.__calc_thread.files_info = self.__files_info
        self.__calc_thread.parts_ids = self.__part_files_ids
        self.__calc_thread.export_folder = form_params.export_folder
        self.__calc_thread.main_filename = form_params.main_file_name
        self.__calc_thread.part_suffix = form_params.part_suffix
        self.__calc_thread.finished_percent.connect(self.set_progress_value)
        self.__calc_thread.status.connect(self.set_status_value)
        self.__calc_thread.start()

    def set_progress_value(self, value: float):
        self.ui.pbProcessStatus.setValue(value)

    def set_status_value(self, value: str):
        self.ui.statusBar.showMessage(value)

    def processing(self):
        self.thread_function()

