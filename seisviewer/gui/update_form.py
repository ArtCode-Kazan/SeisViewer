import os
import signal
import urllib.request
from urllib.error import HTTPError
import subprocess
import getpass
import zipfile

from PyQt5.QtWidgets import *
from PyQt5.uic import *


SETUP_FILE_ADDRESS = (
    'https://raw.githubusercontent.com/MikkoArtik/SeisRevise/main/setup.py'
)
PACKAGE_LINK = (
    'https://github.com/MikkoArtik/SeisRevise/archive/refs/heads/main.zip'
)

ZERO_VERSION = '0.0.0'
TMP_FOLDER = '/tmp'


def get_available_version() -> str:
    try:
        for line in urllib.request.urlopen(SETUP_FILE_ADDRESS):
            line = line.decode('utf-8').rstrip()
            if 'version' not in line:
                continue
            return line.strip().split('\'')[1]
        return ZERO_VERSION
    except HTTPError:
        return ZERO_VERSION


def get_current_version() -> str:
    command = ['python3.8', '-m', 'pip', 'show', 'seisviewer']
    pip = subprocess.Popen(command, stdout=subprocess.PIPE)
    command = ['grep', 'Version']
    grep = subprocess.Popen(command, stdin=pip.stdout, stdout=subprocess.PIPE)
    stdout, stderror = grep.communicate()
    line = stdout.decode('utf-8')
    if not line:
        return ZERO_VERSION
    return line.split()[1]


def update_package():
    archive_file_path = os.path.join(TMP_FOLDER, 'main.zip')
    unpack_archive_path = os.path.join(TMP_FOLDER, 'main')
    make_file_folder = os.path.join(unpack_archive_path, 'SeisRevise-main')
    urllib.request.urlretrieve(PACKAGE_LINK, archive_file_path)
    with zipfile.ZipFile(archive_file_path, 'r') as zip_ref:
        zip_ref.extractall(unpack_archive_path)

    username = os.getlogin()
    user_password = getpass.getpass(f'Password for user {username}: ')

    command = (
        f'cd {make_file_folder} && echo {user_password} | sudo -S make update'
    )
    subprocess.call(command, shell=True)

    print('Program was closed after updating. Please run again manually')
    os.kill(os.getpid(), signal.SIGKILL)


class UpdateForm:
    def __init__(self, parent):
        self.__window = QMainWindow()
        self.__forms_folder = parent.forms_folder
        ui_path = os.path.join(
            self.__forms_folder, 'UpdateForm.ui'
        )
        self.__ui = loadUi(ui_path, self.__window)

        self.current_version = get_current_version()
        self.available_version = get_available_version()
        self.load_versions()
        if self.is_need_update():
            self.ui.bUpdate.setEnabled(True)
        else:
            self.ui.bUpdate.setEnabled(False)
        self.ui.bUpdate.clicked.connect(self.run_update)

    @property
    def window(self):
        return self.__window

    @property
    def ui(self):
        return self.__ui

    def load_versions(self):
        self.ui.lCurrentVersion.setText(self.current_version)
        self.ui.lAvailableVersion.setText(self.available_version)

    def is_need_update(self):
        current_version = list(map(int, self.current_version.split('.')))
        available_version = list(map(int, self.available_version.split('.')))
        for i in range(len(current_version)):
            if current_version[i] < available_version[i]:
                return True
        return False

    @staticmethod
    def run_update():
        update_package()
