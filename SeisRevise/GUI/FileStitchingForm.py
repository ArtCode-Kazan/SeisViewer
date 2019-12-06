import os
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.uic import *
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtGui

from SeisCore.BinaryFile.BinaryFile import BinaryFile
from SeisRevise.GUI.Dialogs import show_folder_dialog


class External(QThread):
    finished_part_stitching=pyqtSignal(float)
    finished_file=pyqtSignal(float)
    parameters=None

    def run(self):
        params=self.parameters
        for index_i, item_i in enumerate(params):
            export_name, file_stat = item_i
            export_folder = os.path.dirname(file_stat[0][0])

            if export_name[-3:] != '.00':
                export_name += '.00'
            output_file=open(os.path.join(export_folder,export_name), 'wb')
            for index_j, item_j in enumerate(file_stat):
                file_path, dt_start, dt_stop = item_j

                bin_data = BinaryFile()
                bin_data.path = file_path
                bin_data.use_avg_values=False

                if index_j==0:
                    output_file.write(
                        bin_data.main_header.get_binary_format())
                    for k in range(3):
                        output_file.write(bin_data.get_channel_header(k).get_binary_format())
                    # channel_headers_hole = np.array([0] * 54, dtype=np.int32)
                    # channel_headers_hole.tofile(output_file)
                signal = bin_data.signals
                signal.astype(np.int32).tofile(output_file)
                self.finished_part_stitching.emit((index_j+1)/len(
                    file_stat)*100)
            self.finished_file.emit((index_i+1)/len(params)*100)


class FileStitchingForm:
    def __init__(self, parent):
        self.__window_type = 'stitching_form'
        self.__parent = parent

        self.__calc_thread = None

        self.__window = QMainWindow()
        self.__forms_folder = parent.form_folder
        ui_path = os.path.join(self.__forms_folder, 'FileStitchingForm.ui')
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
        if path is not None:
            self.ui.leFolderPath.setText(path)

        grid_data=self.ui.tGrid
        row_count=0

        for folder in os.listdir(path):
            if not os.path.isdir(os.path.join(path, folder)):
                continue

            file_amount=0
            for file in os.listdir(os.path.join(path, folder)):
                if not os.path.isfile(os.path.join(path, folder, file)):
                    continue
                name_parse=file.split('.')
                extention=name_parse[-1]
                if extention=='00part':
                    file_amount+=1
            if file_amount==0:
                continue
            row_count+=1
            grid_data.setRowCount(row_count)
            grid_data.setItem(row_count-1, 1,
                              QTableWidgetItem(os.path.join(path, folder)))
            grid_data.setItem(row_count-1, 2,
                              QTableWidgetItem(str(file_amount)))

    def collect_parameters(self):
        result=list()
        grid_data=self.ui.tGrid
        for i in range(grid_data.rowCount()):
            if grid_data.item(i, 0) is None:
                continue
            export_name=grid_data.item(i, 0).text()
            folder=grid_data.item(i, 1).text()
            file_statistics=list()
            freq=None
            for index, file in enumerate(os.listdir(folder)):
                name_parse=file.split('.')
                extension=name_parse[-1]
                if extension!='00part':
                    continue

                path=os.path.join(folder,file)
                bin_data=BinaryFile()
                bin_data.path=path

                if freq is not None:
                    if bin_data.signal_frequency!=freq:
                        continue
                else:
                    freq=bin_data.signal_frequency

                file_statistics.append((path,bin_data.datetime_start,
                                        bin_data.datetime_stop))

            file_statistics = sorted(file_statistics, key=lambda x: x[1])

            is_right=True
            for j in range(len(file_statistics)-1):
                current_t_stop=file_statistics[j][2]
                next_t_start=file_statistics[j+1][1]
                dt=(next_t_start-current_t_stop).total_seconds()
                discrete_amount=int(dt*freq)
                if discrete_amount>1:
                    is_right=False
                    break
            if is_right:
                result.append((export_name, file_statistics))
                color = QtGui.QColor(0, 207, 0)
            else:
                color = QtGui.QColor(248, 207, 0)

            for j in range(grid_data.columnCount()):
                grid_data.item(i, j).setBackground(color)

        return result

    def thread_function(self):
        if self.__calc_thread is not None and self.__calc_thread.isFinished():
            self.__calc_thread = None

        if self.__calc_thread is not None:
            return

        self.set_progress_part_value(0)
        self.set_progress_file_value(0)
        params=self.collect_parameters()

        self.__calc_thread=External()
        self.__calc_thread.parameters=params
        self.__calc_thread.finished_file.connect(self.set_progress_file_value)
        self.__calc_thread.finished_part_stitching.connect(self.set_progress_part_value)
        self.__calc_thread.start()

    def set_progress_part_value(self, value):
        self.ui.pbPartAmount.setValue(value)

    def set_progress_file_value(self, value):
        self.ui.pbStitchingAmount.setValue(value)

    def processing(self):
        self.thread_function()
