import warnings
import sys
import os
from datetime import datetime

from SeisPars.Refactoring.BinaryFile import BinaryFile

from SeisCore.GeneralFunction.cmdLogging import print_message

from SeisRevise.DBase.SqliteDBase import SqliteDB


def file_stats():
    """
    Функция для получения информации о bin-файлах в папке
    :return: None
    """
    # -----------------------------------------------------------------------
    # блок отладки
    dbase_folder_path = r'D:\AppsBuilding\Packages\GUISeisRevise'
    dbase_name = 'session.db'
    # конец блока отладки
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # блок релиза
    # warnings.filterwarnings("ignore")
    # parameters = sys.argv
    # # проверка числа параметров
    # if len(parameters) != 3:
    #     print('Неверное число параметров')
    #     return None
    # # dbase directory path
    # dbase_folder_path = parameters[1]
    # # dbase_name
    # dbase_name = parameters[2]
    # конец блока релиза
    # -----------------------------------------------------------------------
    print_message(text="Подключение к БД сессии...", level=0)
    dbase = SqliteDB()
    dbase.folder_path = dbase_folder_path
    dbase.dbase_name = dbase_name
    print_message(text="Строка подключения к БД сформирована", level=0)

    # check dbase
    print_message(text="Проверка данных сессии...", level=0)
    is_correct, error = dbase.check_gen_data_table
    if not is_correct:
        print(error)
        return None
    print_message(text="Общие данные успешно проверены", level=0)

    # get data from dbase
    print_message(text="Получение ORM-модели...", level=0)
    tables, error = dbase.get_orm_model
    if tables is None:
        print(error)
        return None
    print_message(text='ORM-модель успешно получена', level=0)

    # получение информации по файлам в рабочей папке
    general_data = tables.gen_data
    statistic_data = tables.file_stats
    db_gen_data = general_data.get()

    # путь к рабочей папке
    directory_path = db_gen_data.work_dir

    print_message(text='Получение информации о файлах...', level=0)
    folder_struct = os.walk(directory_path)
    files_data = list()
    for root_folder, folders, files in folder_struct:
        # имя корневой папки
        root_folder_name = os.path.basename(root_folder)
        # обход всех файлов
        for file in files:
            try:
                name, extension = file.split('.')
            except ValueError:
                continue
            if extension in ['00', 'xx']:
                file_info = dict()
                file_info['name'] = name
                file_info['path'] = os.path.join(root_folder, file)
                file_info['file_type'] = 'NULL'
                file_info['record_type'] = 'NULL'
                file_info['frequency'] = -9999
                file_info['longitude'] = -9999
                file_info['latitude'] = -9999
                file_info['datetime_start'] = datetime.now()
                file_info['datetime_stop'] = datetime.now()
                file_info['time_duration'] = -9999
                file_info['error_text'] = ''

                # проверка на совпадение имени файла и папки
                if name != root_folder_name:
                    file_info['error_text'] += \
                        'Неверная структура папок. Не совпадают имена папки ' \
                        'и файла - папка:{} файл: {}\n'.format(root_folder_name, name)

                # получение атрибутов из bin-файла
                bin_data = BinaryFile()
                bin_data.path = file_info['path']
                is_correct, error = bin_data.check_correct
                if not is_correct:
                    file_info['error_text'] += error
                else:
                    file_info['file_type'] = bin_data.type
                    file_info['record_type'] = bin_data.record_type
                    file_info['frequency'] = bin_data.signal_frequency
                    file_info['longitude'] = bin_data.longitude
                    file_info['latitude'] = bin_data.latitude
                    file_info['datetime_start'] = bin_data.datetime_start
                    file_info['datetime_stop'] = bin_data.datetime_stop
                    file_info['time_duration'] = bin_data.seconds_delay/3600

                if file_info['error_text'] == '':
                    file_info['error_text'] = 'ok'
                files_data.append(file_info)

    statistic_data.delete().execute()
    for data_dict in files_data:
        statistic_data.create(**data_dict)
    print_message(text='Информация о файлах получена. Всего найдено {} '
                       'файлов'.format(len(files_data)), level=0)
