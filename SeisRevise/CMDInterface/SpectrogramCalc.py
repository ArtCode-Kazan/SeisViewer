import sys
import os
import json

from SeisCore.GeneralFunction.CheckingName import checking_name
from SeisCore.GeneralFunction.cmdLogging import print_message
from SeisCore.GeneralFunction.cmdLogging import error_format

from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal7 as rsf7
from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal8 as rsf8

from SeisRevise.CMDInterface.JsonData import checking_json
from SeisRevise.Functions.ExportFolder import export_folder_generate
from SeisRevise.Functions.PlottingSpectrogram import plot_spectrogram


def spectrogram_calc():
    """
    Функция для потокового построения спектрограмм
    :return: void
    """
    parameters = sys.argv
    # проверка числа параметров
    if len(parameters) != 2:
        error_text = error_format(number=1,
                                  text='Неверное число параметров')
        print(error_text)
        return None

    # путь к файлу json
    input_json = parameters[1]

    # проверка файла json
    if not checking_json(file_path=input_json,
                         checking_node='general_data'):
        return None
    if not checking_json(file_path=input_json,
                         checking_node='spectrograms'):
        return None

    # парсинг файла
    json_data = json.load(open(input_json, 'r'))

    # получение узлов первого порядка
    general_data = json_data['general_data']
    spectrograms_parameters = json_data['spectrograms']

    # путь к рабочей папке
    directory_path = general_data['directory_path']
    # тип файла
    file_type = general_data['file_type']
    # тип записи
    record_type = general_data['record_type']
    # частота записи сигнала
    signal_frequency = general_data['signal_frequency']
    # частота ресемплирования
    resample_frequency = general_data['resample_frequency']
    # компоненты для анализа
    components = list()
    if general_data['x_component']:
        components.append('X')
    if general_data['y_component']:
        components.append('Y')
    if general_data['z_component']:
        components.append('Z')
    # временной интервал построения спектрограмм
    time_interval = spectrograms_parameters['time_interval']
    # размер окна построения спектрограмм
    window_size = spectrograms_parameters['window_size']
    # размер сдвига окна для
    noverlap_size = spectrograms_parameters['noverlap_size']
    # частоты визуализации
    min_frequency = spectrograms_parameters['min_frequency']
    max_frequency = spectrograms_parameters['max_frequency']
    # проверка структуры папок экспорта
    export_structure = spectrograms_parameters['export_folder_structure']

    print_message('Начат процесс построения спектрограмм...', 0)

    # анализ папки с данными сверки - получение полных путей к bin-файлам
    print_message('Анализ выбранной папки...', 0)
    bin_files_list = list()
    folder_struct = os.walk(directory_path)
    for root_folder, folders, files in folder_struct:
        # имя папки
        root_folder_name = os.path.basename(root_folder)
        # проверка имени папки на допустимые символы
        if not checking_name(root_folder_name):
            # прерывание расчета в случае неверного имени папки
            print_message(
                'Неверное имя папки {} - содержит недопустимые символы. '
                'Обработка прервана'.format(root_folder_name), 1)
            return None

        for file in files:
            name, extension = file.split('.')
            # поиск bin-файла
            if extension in ['00', 'xx']:
                # проверка, что имя файла и папки совпадают
                if name == root_folder_name:
                    # получение полного пути к bin-файлу
                    bin_file_path = os.path.join(root_folder, file)
                    bin_files_list.append(bin_file_path)
                else:
                    # прерывание расчета в случае неверной структуры папок
                    print_message('Неверная структура папок. Не совпадают '
                                  'имена папки и файла - папка:{} файл: {}'.
                                  format(root_folder_name, name), 1)
                    return None

    if len(bin_files_list) == 0:
        print_message('Анализ папки завершен. Bin-файлов не найдено. '
                      'Обработка прервана', 0)
        return None
    else:
        print_message('Анализ папки завершен. Всего найдено {} '
                      'файлов'.format(len(bin_files_list)), 0)

    # парсинг типа записи
    x_channel_number = record_type.index('X')
    y_channel_number = record_type.index('Y')
    z_channel_number = record_type.index('Z')

    # запуск процесса построения спектрограмм

    # главный цикл - по интервалам времени
    # ВНИМАНИЕ! Цикл бесконечный, так как неивестна длина данных в файле
    #  заранее - файл может быть очень большим настолько, что нельзя его
    #  полностью считать в память

    # номер интервала для обработки. Один интервал может быть равен
    # нескольким часам
    interval_number = 0
    while True:
        print_message('Начата обработка временного интервала #{}...'.format(
            interval_number + 1), 1)
        # размер извлекаемого куска сигнала БЕЗ РЕСЕМПЛИРОВАНИЯ!!!
        signal_part_size = int(time_interval * 3600 * signal_frequency)

        # получение номеров отсчетов для извлечения куска сигнала из
        # файла БЕЗ РЕСЕМПЛИРОВАНИЯ!!!
        start_moment_position = interval_number * signal_part_size
        end_moment_position = start_moment_position + signal_part_size - 1

        # интервал секунд (нужно для названия выходного png-файла
        # картинки спектрограммы)
        start_second = int(time_interval * 3600) * interval_number
        end_second = start_second + int(time_interval * 3600)

        # второй цикл - по bin-файлам

        # переменная для определения прерывания бесконечного цикла -
        # True - если цикл нужно продолжить, False - если прерывать цикл
        # не нужно. Все зависит от того, есть ли извлеченный кусок
        # сигнала хотя бы в одном файле
        is_check_marker = False
        for file_path in bin_files_list:
            # получение имени файла
            bin_file_name = os.path.split(file_path)[-1].split('.')[0]
            print_message('Обработка файла {}...'.format(bin_file_name), 2)

            # проба считать данные в указанном интервале
            if file_type == 'Baikal7':
                signal = rsf7(file_path=file_path,
                              only_signal=True,
                              resample_frequency=resample_frequency,
                              start_moment=start_moment_position,
                              end_moment=end_moment_position)
            elif file_type == 'Baikal8':
                signal = rsf8(file_path=file_path,
                              signal_frequency=signal_frequency,
                              only_signal=True,
                              resample_frequency=resample_frequency,
                              start_moment=start_moment_position,
                              end_moment=end_moment_position)
            else:
                signal = None

            # если сигнал не пустой, добавляем (логическое OR) True
            if signal is not None:
                is_check_marker += True
                print_message('Выборка успешно считана', 2)
            else:
                print_message('Выборка файла пуста. Обработка пропущена', 2)
                continue

            # если сигнал не пуст, второй цикл продолжает работу

            # Построение спектрограмм по компонентам
            for component in components:
                # имя для png-файла складывается как название компоненты
                #  имя bin-файла+начальная секудна интервала+конечная
                # секунда интервала
                output_file_name = '{}_Component_{}_{}-{}_sec'.format(
                    component, bin_file_name, start_second, end_second)

                # генерация пути к папке, куда будет сохраняться результат
                # в зависимости от типа структуры папок экспорта
                export_folder = export_folder_generate(
                    root_folder=directory_path,
                    structure_type=export_structure,
                    component=component,
                    bin_file_name=bin_file_name,
                    start_time_sec=start_second,
                    end_time_sec=end_second)

                # проверка создания каталога экспорта
                if export_folder is None:
                    print_message('Ошибка создания каталога экспорта. '
                                  'Обработка прервана', 3)
                    return None

                # определение индекса канала компоненты исходя из текущей
                #  компоненты
                if component == 'X':
                    channel_number = x_channel_number
                elif component == 'Y':
                    channel_number = y_channel_number
                elif component == 'Z':
                    channel_number = z_channel_number
                else:
                    print_message('Ошибка чтения номера компоненты. '
                                  'Обработка прервана', 3)
                    return None

                # построение спектрограммы
                is_create_spectrogram = plot_spectrogram(
                    signal=signal[:, channel_number],
                    frequency=resample_frequency,
                    window_size=window_size,
                    noverlap_size=noverlap_size,
                    min_frequency_visulize=min_frequency,
                    max_frequency_visualize=max_frequency,
                    output_folder=export_folder,
                    output_name=output_file_name,
                    time_start_sec=start_second
                )

                # проверка создания спектрограммы
                if not is_create_spectrogram:
                    print_message('Ошибка построения спектрограммы: файл {}, '
                                  'компонента {}, временной интервал {}-{}. '
                                  'Возможно, неверные параметры построения. '
                                  'Обработка прервана'.
                                  format(bin_file_name, component,
                                         start_second, end_second), 3)
                    return None
                else:
                    print_message('Спектрограмма (файл {}, компонента {}) '
                                  'построена'.format(bin_file_name,
                                                     component, ), 3)
            print_message('Файл {} обработан'.format(bin_file_name), 2)

        # проверка, нужно ли прервать бесконечный цикл
        if not is_check_marker:
            print_message('Построение спектрограмм завершено', 0)
            break
        interval_number += 1
