import os
import shutil


def export_folder_generate(root_folder, structure_type, component,
                           bin_file_name=None, start_time_sec=None,
                           end_time_sec=None):

    # Проверка введенных параметров
    if structure_type == 'HourStructure' and (start_time_sec is None or
                                              end_time_sec is None):
        return None

    if structure_type == 'DeviceStructure' and bin_file_name is None:
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
    if structure_type == 'DeviceStructure':
        export_folder_path = os.path.join(
            root_folder,
            bin_file_name,
            '{}_component'.format(component))

    # создание папки для сохранения результатов
    if not os.path.exists(export_folder_path):
       os.makedirs(export_folder_path)

    # возвращение результата
    if os.path.exists(export_folder_path):
        return export_folder_path
    else:
        return None
