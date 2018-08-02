import os
import sys
import datetime
import warnings

from SeisPars.Refactoring.BinaryFile import BinaryFile

from SeisCore.GeneralFunction.cmdLogging import print_message


def join_bin_files():
    # -----------------------------------------------------------------------
    # блок отладки
    # output_folder = r'D:\AppsBuilding\TestingData\JoinedFiles'
    # output_name = r'JoinedFile'
    # file_paths = [r'D:\AppsBuilding\TestingData\JoinedFiles\54P_060_133'
    #               r'\54P_060_133.xx',
    #               r'D:\AppsBuilding\TestingData\JoinedFiles\54P_060_133_1'
    #               r'\54P_060_133_1.xx',
    #               r'D:\AppsBuilding\TestingData\JoinedFiles\54P_060_133_2'
    #               r'\54P_060_133_2.xx']
    # конец блока отладки
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # блок релиза
    warnings.filterwarnings("ignore")
    parameters = sys.argv
    # проверка числа параметров
    if len(parameters) <= 3:
        print('Неверное число параметров')
        return None
    # export folder path
    output_folder = parameters[1]
    # export file name
    output_name = parameters[2]
    # file_paths
    file_paths = parameters[3:]
    # конец блока релиза
    # -----------------------------------------------------------------------
    files_info = list()
    general_frequency = None
    general_file_type = None
    for path in file_paths:
        # проверка файла на существование
        if not os.path.isfile(path):
            print_message('Путь {} не существует'.format(path), 0)
            return None

        binary_data = BinaryFile()
        binary_data.path = path
        # проверка файла на корректность
        is_correct, error = binary_data.check_correct
        if not is_correct:
            print_message(error, 0)
            return None

        # проверка, что все файлы одного и того же типа
        file_type = binary_data.type
        if general_file_type is None:
            general_file_type = file_type
        else:
            if file_type != general_file_type:
                print_message('Типы файлов не одинаковы', 0)
                return None

        # проверка, что частоты записи файлов одинаковы
        frequency = binary_data.signal_frequency
        if general_frequency is None:
            general_frequency = frequency
        else:
            if frequency != general_frequency:
                print_message('Частоты записи файлов не одинаковы', 0)
                return None
        date_time_start = binary_data.datetime_start
        date_time_stop = binary_data.datetime_stop
        files_info.append((path, date_time_start, date_time_stop))

    # сортировка списка файлов по дате начала записи
    files_info.sort(key=lambda row: row[1], reverse=False)

    # вычисление допустимой задержки
    delta_time_opacity = datetime.timedelta(seconds=1/general_frequency)
    # проверка задержки между файлами
    for i in range(len(files_info)-1):
        dt = files_info[i+1][1]-files_info[i][2]
        if dt > delta_time_opacity:
            print_message('Разрыв между файлами больше одной дискреты. '
                          'Сшивка невозможна', 0)
            return None

    if general_file_type == 'Baikal7':
        output_path = os.path.join(output_folder, output_name+'.00')
    elif general_file_type == 'Baikal8':
        output_path = os.path.join(output_folder, output_name+'.xx')
    else:
        return None

    print_message('Начат процесс сшивки...', 0)
    output_file = open(output_path, 'wb')
    block_number = 0
    for i, file_info in enumerate(files_info):
        path, date_time_start, date_time_stop = file_info

        fin = open(path, 'rb')
        if i != 0:
            fin.seek(336)
        while True:
            data = fin.read(262144000)
            if not data:
                break
            output_file.write(data)
            block_number += 1
            print_message('Block {} was wrote'.format(block_number), 1)
        fin.close()
    output_file.close()
    print_message('Процесс сшивки завершен', 0)
