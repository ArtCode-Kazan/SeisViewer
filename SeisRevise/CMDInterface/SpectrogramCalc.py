import sys
import os

from SeisCore.GeneralFunction.CheckingName import checking_name
from SeisCore.GeneralFunction.cmdLogging import print_message

from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal7 as rsf7
from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal8 as rsf8

from SeisRevise.Functions.ExportFolder import export_folder_generate
from SeisRevise.Functions.PlottingSpectrogram import plot_spectrogram


def spectrogram_calc():
    """
    Функция для потокового построения спектрограмм
    :return: void
    """
    parameters = sys.argv
    # проверка числа параметров
    if len(parameters) != 13:
        print('Неверное число параметров')
        return None

    # проверка самих параметров
    errors = list()  # список ошибок

    # проверка пути к рабочей папки
    directory_path = parameters[1]
    if not os.path.isdir(directory_path):
        errors.append('Неверно указан путь к папкам сверки')

    # проверка типа файла
    file_type = parameters[2]
    if file_type not in ['Baikal7', 'Baikal8']:
        errors.append('Неверно указан тип файла')

    # проверка типа записи
    record_type = parameters[3]
    if record_type not in ['ZXY', 'XYZ']:
        errors.append('Неверно указан тип записи')

    # проверка частоты записи сигнала
    signal_frequency = parameters[4]
    try:
        signal_frequency = int(signal_frequency)
    except ValueError:
        errors.append('Неверно указана частота записи сигнала')

    # проверка частоты ресемплирования
    resample_frequency = parameters[5]
    try:
        resample_frequency = int(resample_frequency)
    except ValueError:
        errors.append('Неверно указана частота ресемплирования')

    # проверка временного интервлаа построения спектрограмм
    time_interval = parameters[6]
    try:
        time_interval = float(time_interval)
    except ValueError:
        errors.append('Неверно указана частота ресемплирования')

    # проверка компонент для анализа
    components = parameters[7]
    components = list(components)
    if len(components) == 0 or len(components) > 3:
        errors.append('Не указаны компоненты для анализа')

    # проверка размера окна построения спектрограмм
    window_size = parameters[8]
    try:
        window_size = int(window_size)
    except ValueError:
        errors.append('Неверно указан размер окна')

    # проверка размера сдвига окна для
    noverlap_size = parameters[9]
    try:
        noverlap_size = int(noverlap_size)
    except ValueError:
        errors.append('Неверно указан сдвиг окна')

    # проверка частот визуализации
    min_frequency = parameters[10]
    try:
        min_frequency = float(min_frequency)
    except ValueError:
        errors.append('Неверно указана минимальная частота визуализации')

    max_frequency = parameters[11]
    try:
        max_frequency = float(max_frequency)
    except ValueError:
        errors.append('Неверно указана максимальная частота визуализации')

    try:
        if min_frequency >= max_frequency:
            errors.append('Некорректно указан интервал частот визаулизации')
    except ValueError:
        return None

    # проверка структуры папок экспорта
    export_structure = parameters[12]
    if export_structure not in ['HourStructure', 'DeviceStructure']:
        errors.append('Неверно указан тип структуры папок экспорта')

    # вывод ошибок, если они есть
    if len(errors) != 0:
        for line in errors:
            print(line)
        return None

    # если ошибок нет, работа продолжается
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
