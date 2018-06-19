import sys
import os
from peewee import *

from SeisCore.GeneralFunction.cmdLogging import error_format
from SeisCore.GeneralFunction.cmdLogging import print_message
from SeisCore.GeneralFunction.CheckingName import checking_name

from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal7 as rsf7
from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal8 as rsf8

from SeisRevise.DBase.Operations import check_dbase
from SeisRevise.DBase.ORM import get_orm_model
from SeisRevise.Functions.PlottingSpectrogram import plot_spectrogram
from SeisRevise.Functions.PlottingSimpleSpectrum import simple_spectrum
from SeisRevise.Functions.WriteSelectionSignal import write_part_of_signal
from SeisRevise.Functions.PlottingSignal import drawing_signal


def pre_analysis_calc():
    """
    Функция для расчета предварительного анализа сигналов
    :return: void
    """
    parameters = sys.argv
    # проверка числа параметров
    if len(parameters) != 3:
        error_text = error_format(number=1,
                                  text='Неверное число параметров')
        print(error_text)
        return None

    # dbase directory path
    dbase_folder_path = parameters[1]
    # dbase_folder_path=r'D:\temp'
    # dbase_name
    dbase_name = parameters[2]
    # dbase_name =  'qweerrty'

    # check dbase
    if not check_dbase(folder_path=dbase_folder_path, dbase_name=dbase_name,
                       table_name='GeneralData'):
        return None

    if not check_dbase(folder_path=dbase_folder_path, dbase_name=dbase_name,
                       table_name='PreAnalysisData'):
        return None

    # get data from dbase
    dbase_full_path = os.path.join(dbase_folder_path, dbase_name + '.db')
    sqlite_db = SqliteDatabase(dbase_full_path)
    general_data, spectrogram_data, correlation_data, pre_analysis_data = \
        get_orm_model(dbase_connection=sqlite_db)

    db_gen_data = general_data.get()
    db_panalysis_data = pre_analysis_data.get()

    # путь к рабочей папке
    directory_path = db_gen_data.work_dir
    # тип файла
    file_type = db_gen_data.file_type
    # тип записи
    record_type = db_gen_data.record_type
    # частота записи сигнала
    signal_frequency = db_gen_data.signal_frequency
    # частота ресемплирования
    resample_frequency = db_gen_data.resample_frequency
    # компоненты для анализа
    components = list()
    if db_gen_data.x_component_flag:
        components.append('X')
    if db_gen_data.y_component_flag:
        components.append('Y')
    if db_gen_data.z_component_flag:
        components.append('Z')

    # минимальная секунда чистого сигнала
    left_time_edge = db_panalysis_data.left_edge
    # максимальная секунда чистого сигнала
    right_time_edge = db_panalysis_data.right_edge
    # размер окна расчета
    window_size = db_panalysis_data.window_size
    # размер сдвига окна расчета
    noverlap_size = db_panalysis_data.noverlap_size
    # параметр медианного фильтра
    if not db_panalysis_data.median_filter_flag:
        median_filter_parameter = None
    else:
        median_filter_parameter = db_panalysis_data.median_filter_parameter
    # параметр marmett фильтра
    if not db_panalysis_data.marmett_filter_flag:
        marmett_filter_parameter = None
    else:
        marmett_filter_parameter = db_panalysis_data.marmett_filter_parameter

    # минимальная частота визуализации
    min_frequency_visuality = db_panalysis_data.f_min_visual
    # максимальная частота визуализации
    max_frequency_visuality = db_panalysis_data.f_max_visual

    # вывод выборки сигнала в файл
    is_selection_signal_to_file = db_panalysis_data.select_signal_to_file_flag
    # вывод выборки сигнала в виде графика
    is_selection_signal_to_graph = \
        db_panalysis_data.select_signal_to_graph_flag
    # вывод спектров
    is_spectors = db_panalysis_data.separated_spectrums_flag
    # вывод 2D спектрограммы
    is_spectrogram = db_panalysis_data.spectrogram_flag

    print_message('Начат процесс предварительного анализа...', 0)

    # анализ папки с данными сверки - получение полных путей к bin-файлам
    bin_files_list = list()
    folder_struct = os.walk(directory_path)

    for root_folder, folders, files in folder_struct:
        # имя папки
        root_folder_name = os.path.basename(root_folder)
        # проверка имени папки на допустимые символы
        if not checking_name(root_folder_name):
            # прерывание расчета в случае неверного имени папки
            print_message('Неверное имя папки {} - содержит недопустимые '
                          'символы. Обработка '
                          'прервана'.format(root_folder_name), 1)
            return None

        # Обход файлов в папке
        for file in files:
            name, extention = file.split('.')
            # поиск bin-файла
            if extention in ['00', 'xx']:
                # проверка, что имя файла и папки совпадают
                if name == root_folder_name:
                    # получение полного пути к bin-файлу
                    bin_file_path = os.path.join(root_folder, file)
                    bin_files_list.append(bin_file_path)
                else:
                    # прерывание расчета в случае неверной структуры папок
                    print_message('Неверная структура папок. Не совпадает '
                                  'имя папки и файла - '
                                  'папка:{} файл: {}'.format(root_folder_name,
                                                             name), 1)
                    return None

    # Проверка наличия bin-файлов
    if len(bin_files_list) == 0:
        print_message('Анализ папки завершен. Bin-файлов  не найдено. '
                      'Обработка прервана', 0)
        return None

    # Если bin-файлы есть, то работа продолжается
    print_message('Анализ папки завершен. '
                  'Всего найдено {}  файлов'.format(len(bin_files_list)), 0)

    # создание папки с результатами расчетов
    folder_with_result = None
    for i in range(99):
        folder_name = 'PreAnalysis_vers_{}'.format(i + 1)
        folder_with_result = os.path.join(directory_path, folder_name)
        if not os.path.exists(folder_with_result):
            os.mkdir(folder_with_result)
            break

    # парсинг типа записи
    x_channel_number = record_type.index('X')
    y_channel_number = record_type.index('Y')
    z_channel_number = record_type.index('Z')

    # расчет длины выборки сигнала в отсчетах

    # получение номеров отсчетов для извлечения куска сигнала из файла (
    # БЕЗ РЕСЕМПЛИРОВАНИЯ!!!)
    start_moment_position = left_time_edge * signal_frequency
    end_moment_position = right_time_edge * signal_frequency - 1

    # получение номеров отсчетов для извлечения куска сигнала из файла (
    # ПОСЛЕ РЕСЕМПЛИРОВАНИЯ!!!)
    resample_parameter = signal_frequency // resample_frequency

    start_moment_position_resample = \
        start_moment_position // resample_parameter
    end_moment_position_resample = \
        end_moment_position // resample_parameter

    selection_size \
        = end_moment_position_resample - start_moment_position_resample + 1

    print_message('Длина выборки сигналов в отсчетах: {}'.format(
        selection_size), 0)

    # запуск процесса извлечения выборок сигналов
    for file_number, file_path in enumerate(bin_files_list):
        # получение имени файла
        bin_file_name = os.path.split(file_path)[-1].split('.')[0]

        print_message('Чтение файла {}...'.format(bin_file_name), 1)

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

        # проверка, что сигнал извлечен и его длина равна требуемой
        # длине куска
        if signal is not None and signal.shape[0] == selection_size:
            print_message('Выборка файла успешно считана', 1)
        else:
            print_message('Выборка файла пуста. Обработка прервана', 1)
            return None

        # если сигнал не пуст, второй цикл продолжает работу

        # Построение 2D-спектрограмм и простых (НЕ КУМУЛЯТИВНЫХ!!!) спектров
        for component in components:
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

            # запись выборки сигнала в файл
            if is_selection_signal_to_file:
                dat_file_name = '{}_ClearSignal_{}_Component'.format(
                    bin_file_name, component)
                # создание папки для сохранения результатов
                output_folder = os.path.join(folder_with_result, bin_file_name)
                if not os.path.isdir(output_folder):
                    os.mkdir(output_folder)
                write_part_of_signal(signal=signal[:, channel_number],
                                     output_folder=output_folder,
                                     output_name=dat_file_name)
                print_message('Выборка сигнала (файл {}, компонента {}) '
                              'записана'.format(bin_file_name, component), 3)

            # визуализация выборки сигнала в виде графика
            if is_selection_signal_to_graph:
                png_file_name = '{}_ClearSignal_{}_Component_Graph'.format(
                    bin_file_name, component)
                # создание папки для сохранения результатов
                output_folder = os.path.join(folder_with_result, bin_file_name)
                if not os.path.isdir(output_folder):
                    os.mkdir(output_folder)
                drawing_signal(left_edge=start_moment_position_resample,
                               frequency=resample_frequency,
                               signal=signal[:, channel_number],
                               label=png_file_name,
                               output_folder=output_folder,
                               output_name=png_file_name)
                print_message('График выборки сигнала (файл {}, '
                              'компонента {}) построен'.format(
                               bin_file_name, component), 3)

            # построение спектров
            if is_spectors:
                png_file_name = '{}_SimpleSpectrum_{}_Component_' \
                                'Graph'.format(bin_file_name, component)
                # создание папки для сохранения результатов
                output_folder = os.path.join(folder_with_result, bin_file_name)
                if not os.path.isdir(output_folder):
                    os.mkdir(output_folder)
                simple_spectrum(
                    signal=signal[:, channel_number],
                    frequency=resample_frequency,
                    median_filter_parameter=median_filter_parameter,
                    marmett_filter_parameter=marmett_filter_parameter,
                    f_min=min_frequency_visuality,
                    f_max=max_frequency_visuality,
                    output_folder=output_folder,
                    output_name=png_file_name)
                print_message('Спектр (файл {}, компонента {}) '
                              'построен'.format(bin_file_name, component), 3)

            # построение спектрограммы
            if is_spectrogram:
                # имя для png-файла складывается как название компоненты
                #  имя bin-файла+начальная секудна интервала+конечная
                # секунда интервала
                output_file_name = '{}_Component_{}_{}-{}_sec'.format(
                    component, bin_file_name, left_time_edge, right_time_edge)
                # создание папки для сохранения результатов
                output_folder = os.path.join(folder_with_result, bin_file_name)
                if not os.path.isdir(output_folder):
                    os.mkdir(output_folder)

                plot_spectrogram(
                    signal=signal[:, channel_number],
                    frequency=resample_frequency,
                    time_start_sec=left_time_edge,
                    window_size=window_size,
                    noverlap_size=noverlap_size,
                    min_frequency_visulize=min_frequency_visuality,
                    max_frequency_visualize=max_frequency_visuality,
                    output_folder=output_folder,
                    output_name=output_file_name)
                print_message('Спектрограмма (файл {}, компонента {}) '
                              'построена'.format(bin_file_name, component), 3)
    print_message('Обработка завершена', 0)