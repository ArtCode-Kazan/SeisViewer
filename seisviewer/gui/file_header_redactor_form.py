import os
from typing import List
from dataclasses import dataclass
from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.uic import *

from seiscore import BinaryFile
from seiscore.binaryfile.binaryfile import SIGMA_EXTENSION

from seisviewer.gui.dialogs import show_folder_dialog, show_message
from seisviewer.functions.redactor import FileParameters, SigmaRedactor


REDACT_PREFIX = '_header_changed'
DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S.%f'


@dataclass
class TableRow:
    root_folder: str
    filename: str
    origin_datetime: datetime
    correct_datetime: datetime

    @property
    def origin_datetime_str(self) -> str:
        return self.origin_datetime.strftime(DATETIME_FORMAT)

    @property
    def redacted_filename(self) -> str:
        base_filename = '.'.join(self.filename.split('.')[:-1])
        extension = self.filename.split('.')[-1]
        return base_filename + REDACT_PREFIX + '.' + extension


class FormParameters:
    root: str = ''
    table_rows: List[TableRow] = []

    @property
    def rows_count(self) -> int:
        return len(self.table_rows)


class FileHeaderRedactorForm:
    def __init__(self, parent):
        self.__form_parameters = FormParameters()

        self.__window = QMainWindow()
        self.__forms_folder = parent.forms_folder
        ui_path = os.path.join(
            self.__forms_folder, 'FileHeaderRedactorForm.ui'
        )
        self.__ui = loadUi(ui_path, self.__window)

        self.__ui.bOpen.clicked.connect(self.open_folder)
        self.__ui.bRedact.clicked.connect(self.create_redact_versions)

    @property
    def window(self):
        return self.__window

    @property
    def ui(self):
        return self.__ui

    @property
    def form_parameters(self) -> FormParameters:
        return self.__form_parameters

    def open_folder(self):
        path = show_folder_dialog()
        self.form_parameters.root = path

        rows = []
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                extension = filename.split('.')[-1]
                if extension != SIGMA_EXTENSION:
                    continue
                path = os.path.join(root, filename)
                bin_data = BinaryFile(file_path=path)
                origin_datetime = bin_data.origin_datetime_start
                correct_datetime = datetime(
                    year=datetime.now().year,
                    month=datetime.now().month,
                    day=datetime.now().day,
                    hour=origin_datetime.hour,
                    minute=origin_datetime.minute,
                    second=origin_datetime.second,
                    microsecond=origin_datetime.microsecond
                )
                rows.append(
                    TableRow(
                        root_folder=root,
                        filename=filename,
                        origin_datetime=origin_datetime,
                        correct_datetime=correct_datetime
                    )
                )
        self.form_parameters.table_rows = rows
        self.update_form()

    def update_form(self):
        self.ui.eRoot.clear()
        table: QTableWidget = self.ui.tGrid
        table.setRowCount(0)

        self.ui.eRoot.setText(self.form_parameters.root)
        table.setRowCount(self.form_parameters.rows_count)
        for i, row in enumerate(self.form_parameters.table_rows):
            table.setItem(i, 0, QTableWidgetItem(row.root_folder))
            table.setItem(i, 1, QTableWidgetItem(row.filename))
            table.setItem(i, 2, QTableWidgetItem(row.origin_datetime_str))

            redact_datetime_widget = QDateTimeEdit()
            redact_datetime_widget.setDisplayFormat('dd.MM.yyyy HH:mm:ss')
            redact_datetime_widget.setDateTime(row.correct_datetime)
            table.setCellWidget(i, 3, redact_datetime_widget)

    def update_form_parameters(self):
        self.form_parameters.root = self.ui.eRoot.text()
        table: QTableWidget = self.ui.tGrid
        rows = []
        for i in range(table.rowCount()):
            root_folder = table.item(i, 0).text()
            filename = table.item(i, 1).text()
            origin_datetime = table.item(i, 2).text()

            widget = table.cellWidget(i, 3)
            redact_datetime = widget.dateTime().toPyDateTime()

            rows.append(
                TableRow(
                    root_folder=root_folder,
                    filename=filename,
                    origin_datetime=origin_datetime,
                    correct_datetime=redact_datetime
                )
            )
        self.form_parameters.table_rows = rows

    def create_redact_versions(self):
        self.update_form_parameters()
        for row in self.form_parameters.table_rows:
            file_redactor = FileParameters(
                path=os.path.join(row.root_folder, row.filename),
                correct_datetime=row.correct_datetime,
                export_path=os.path.join(row.root_folder,
                                         row.redacted_filename)
            )
            SigmaRedactor(file_parameter=file_redactor).save()
        show_message('File headers redaction is done')
