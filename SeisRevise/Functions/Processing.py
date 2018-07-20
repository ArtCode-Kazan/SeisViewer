import os
from datetime import datetime

from SeisCore.GeneralFunction.GeneralFunctions import checking_name as _checking_name


def get_dates(directory_path):
    """
    Функция получения дат из названия папок в рабочей директории
    :param directory_path: путь к рабочей папке
    :return: список дат, текст ошибки
    """
    dates_list=list()
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


def get_bin_files(directory_path):
    """
    Функция для получения списка полных путей к bin-файлам
    :param directory_path: путь к рабочей папке
    :return: список полных путей к bin-файлам, текст ошибки
    """
    bin_files_list = list()
    folder_struct = os.walk(directory_path)
    for root_folder, folders, files in folder_struct:
        # имя папки
        root_folder_name = os.path.basename(root_folder)
        # проверка имени папки на допустимые символы
        if not _checking_name(root_folder_name):
            # прерывание расчета в случае неверного имени папки
            error = 'Неверное имя папки {} - содержит недопустимые символы. ' \
                    'Обработка прервана'.format(root_folder_name)
            return None, error

        # проверка файлов в папке
        for file in files:
            try:
                name, extension = file.split('.')
            except ValueError:
                error = 'Папка {}, файл {} - ошибка неверное расширение ' \
                        'файла'.format(root_folder_name, file)
                return None, error

            # поиск bin-файла
            if extension in ['00', 'xx']:
                # проверка, что имя файла и папки совпадают
                if name == root_folder_name:
                    # получение полного пути к bin-файлу
                    bin_file_path = os.path.join(root_folder, file)
                    bin_files_list.append(bin_file_path)
                else:
                    # прерывание расчета в случае неверной структуры папок
                    error = 'Неверная структура папок. Не совпадают ' \
                            'имена папки и файла - ' \
                            'папка:{} файл: {}'.format(root_folder_name, name)
                    return None, error
    return bin_files_list, None


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
    if data_type == 'GRP' and (start_time_sec is None or
                                              end_time_sec is None):
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

