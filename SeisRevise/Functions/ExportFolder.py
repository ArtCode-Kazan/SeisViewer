import os


def export_folder_generate(root_folder, structure_type, component,
                           bin_file_name=None, start_time_sec=None,
                           end_time_sec=None):
    """
    Функция для генерации пути папки для экспорта результатов
    :param root_folder: корневая папка всех сверочных данных
    :param structure_type: тип структуры папок - HourStructure (почасовая),
    DeviceStructure(поприборная)
    :param component: название компоненты сигнала (X, Y, Z)
    :param bin_file_name: имя bin-файла (без расширения)
    :param start_time_sec: начальная секунда расчета спектрограмм
    :param end_time_sec: конечная секунда расчета спектрограмм
    :return: путь к папке
    """
    # Проверка введенных параметров
    if structure_type == 'HourStructure' and (start_time_sec is None or
                                              end_time_sec is None):
        # если структура папки почасовая, то наличие начальной и конечной
        # секунд обязательно
        return None

    if structure_type == 'DeviceStructure' and bin_file_name is None:
        # если структура папки поприборная, то наличие имени bin-файла
        # обязательно
        return None

    # В случае, если структура папки организована как по часам
    # путь к папке складывается из корневой папки/2DSpectrograms/{}_component
    if structure_type == 'HourStructure':
        export_folder_path = os.path.join(
            root_folder,
            '2DSpectrograms',
            '{}-{}_sec'.format(start_time_sec, end_time_sec),
            '{}_component'.format(component))
    # В случае, если структура папки организована как по датчикам
    # путь к папке будет как:
    # корневая папка/папка с файлом датчика/{}_component
    elif structure_type == 'DeviceStructure':
        export_folder_path = os.path.join(
            root_folder,
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
