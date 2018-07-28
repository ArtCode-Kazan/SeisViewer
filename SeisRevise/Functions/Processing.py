import os
from datetime import datetime
import re

from SeisCore.GeneralFunction.GeneralFunctions import \
    checking_name as _checking_name

from SeisPars.Refactoring.BinaryFile import BinaryFile


def get_dates(directory_path):
    """
    Функция получения дат из названия папок в рабочей директории
    :param directory_path: путь к рабочей папке
    :return: список дат, текст ошибки
    """
    dates_list = list()
    root_folder, folders, files = next(os.walk(directory_path))
    for folder_name in folders:
        try:
            date_value = datetime.strptime(folder_name, '%Y-%m-%d')
            dates_list.append(date_value)
        except ValueError:
            error = 'Неверная структура папок. Папка: {} - имя папки ' \
                    'не является датой'.format(folder_name)
            return None, error
    return dates_list, None


def files_info(directory_path):
    """
    Функция для получения информации о файлах, находящихся в указанной папке
    :param directory_path: папка для анализа
    :return:
    """
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
                file_info['point'] = 'NULL'
                file_info['x_coord'] = -9999
                file_info['y_coord'] = -9999
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
                        'и файла - папка:{} файл: {}\n'.format(
                            root_folder_name, name)
                else:
                    if not _checking_name(name):
                        file_info['error_text'] += \
                            'Путь к файлу содержит недопустимые символы. ' \
                            'Файл: {}\n'.format(name)

                # получение имени точки из имени файла
                file_info['point'] = re.findall('[0-9]+[A-Z]*', name)[0]

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
                    file_info['time_duration'] = bin_data.seconds_duration / \
                                                 3600

                if file_info['error_text'] == '':
                    file_info['error_text'] = 'ok'
                files_data.append(file_info)
    return files_data


def export_folder_generate(root_folder, date_value, data_type, component,
                           bin_file_name=None, start_time_sec=None,
                           end_time_sec=None):
    """
    Функция для генерации пути папки для экспорта результатов
    :param root_folder: корневая папка всех сверочных данных
    :param date_value: дата дня обработки
    :param data_type: тип данных - MSI, GRP
    :param component: название компоненты сигнала (X, Y, Z)
    :param bin_file_name: имя bin-файла (без расширения)
    :param start_time_sec: начальная секунда расчета спектрограмм
    :param end_time_sec: конечная секунда расчета спектрограмм
    :return: путь к папке
    """
    # Проверка введенных параметров
    if data_type == 'GRP' and (start_time_sec is None or end_time_sec is None):
        # если структура папки почасовая, то наличие начальной и конечной
        # секунд обязательно
        return None

    if data_type == 'MSI' and bin_file_name is None:
        # если структура папки поприборная, то наличие имени bin-файла
        # обязательно
        return None

    # В случае, если структура папки организована как по часам
    # путь к папке складывается из корневой папки/2DSpectrograms/{}_component
    if data_type == 'GRP':
        export_folder_path = os.path.join(
            root_folder, date_value.strftime("%Y-%m-%d"), '2DSpectrograms',
            '{}-{}_sec'.format(start_time_sec, end_time_sec),
            '{}_component'.format(component))
    # В случае, если структура папки организована как по датчикам
    # путь к папке будет как:
    # корневая папка/папка с файлом датчика/{}_component
    elif data_type == 'MSI':
        export_folder_path = os.path.join(
            root_folder, date_value.strftime("%Y-%m-%d"), '2DSpectrograms',
            bin_file_name,
            '{}_component'.format(component))
    else:
        return None
    # создание папки для сохранения результатов
    if not os.path.exists(export_folder_path):
        os.makedirs(export_folder_path)

    # возвращение результата
    if os.path.exists(export_folder_path):
        return export_folder_path
    else:
        return None


def read_coords_file(file_path):
    """
    Функция для чтения внешнего файла координат
    :param file_path: путь к dat-файлу
    :return: None
    """
    f = open(file_path, 'r')
    result = list()
    i = 0
    for line in f:
        i += 1
        if i > 1:
            line = line.strip()
            t = line.split('\t')
            if len(t) != 3:
                f.close()
                return None
            point_name = t[0]
            try:
                x_coord = float(t[1])
                y_coord = float(t[2])
            except ValueError:
                f.close()
                return None
            result.append((point_name, x_coord, y_coord))
    f.close()
    return result
