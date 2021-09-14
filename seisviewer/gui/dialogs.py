from PyQt5.QtWidgets import *


def show_message(message_text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(message_text)
    msg.exec_()


def show_folder_dialog():
    file_dialog = QFileDialog()
    folder_path = file_dialog.getExistingDirectory()
    return folder_path


def show_file_dialog():
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    file_list = file_dialog.getOpenFileNames()[0]
    if len(file_list) == 1:
        return file_list[0]
    else:
        return None


def show_multiple_file_dialog(filters=None):
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    file_list = file_dialog.getOpenFileNames(None, filter=filters)[0]
    if len(file_list) > 0:
        return file_list
    else:
        return None
