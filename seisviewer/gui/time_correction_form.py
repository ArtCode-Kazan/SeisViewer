import os
from datetime import datetime
from typing import List, Tuple, Dict

from PyQt5.QtWidgets import *
from PyQt5.uic import *

from seiscore.binaryfile.binaryfile import FileInfo

FORM_FILENAME = 'TimeCorrectionForm.ui'
TIME_STEP_SIZE_SEC = 0.001


class TimeCorrectionForm:
    def __init__(self, parent):
        self.__parent = parent

        self.__window = QMainWindow()
        ui_path = os.path.join(self.forms_folder, FORM_FILENAME)
        self.__ui = loadUi(ui_path, self.__window)

        self.__ui.bApply.clicked.connect(self.apply_time_corrections)

    @property
    def forms_folder(self) -> str:
        return self.parent.forms_folder

    @property
    def window(self):
        return self.__window

    @property
    def parent(self):
        return self.__parent

    @property
    def ui(self):
        return self.__ui

    @property
    def files_info(self) -> List[FileInfo]:
        return self.parent.files_info

    @property
    def selected_file_ids(self) -> List[int]:
        return self.parent.form_parameters.selection_file_ids

    @property
    def base_datetime_interval(self) -> Tuple[datetime, datetime]:
        form_params = self.parent.form_parameters
        return form_params.start_time, form_params.stop_time

    @property
    def time_corrections(self) -> Dict[int, float]:
        return self.parent.time_corrections

    def change_time_correction(self, id_val: int, time_correction: float):
        self.parent.time_corrections[id_val] = time_correction

    def add_row_to_table_grid(self, file_id: int, delay_value: float):
        grid: QTableWidget = self.ui.tGrid
        grid.setRowCount(grid.rowCount() + 1)
        index = grid.rowCount() - 1

        file_name = self.files_info[file_id].name
        grid.setItem(index, 0, QTableWidgetItem(file_name))

        widget = QDoubleSpinBox()
        widget.setDecimals(3)
        minimal_value = (self.files_info[file_id].time_start -
                         self.base_datetime_interval[0]).total_seconds()
        maximal_value = (self.files_info[file_id].time_stop -
                         self.base_datetime_interval[1]).total_seconds()
        widget.setMinimum(minimal_value)
        widget.setMaximum(maximal_value)
        widget.setSingleStep(TIME_STEP_SIZE_SEC)
        widget.setValue(delay_value)

        grid.setCellWidget(index, 1, widget)

    def set_start_form_state(self):
        self.ui.tGrid.setRowCount(0)
        for item in self.selected_file_ids:
            delay_value = self.time_corrections.get(item, 0)
            self.add_row_to_table_grid(item, delay_value)

    def update_time_corrections(self):
        grid: QTableWidget = self.ui.tGrid
        for index, id_val in enumerate(self.selected_file_ids):
            delay_value = grid.cellWidget(index, 1).value()
            self.change_time_correction(id_val, delay_value)

    def apply_time_corrections(self):
        self.update_time_corrections()
        self.parent.load_signal_data()
        self.parent.render_signals()
        self.parent.render_spectrums()
        self.parent.render_correlations()
