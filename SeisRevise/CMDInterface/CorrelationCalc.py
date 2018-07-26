import sys
import os
import warnings

import numpy as np
from numpy.fft import rfftfreq

from SeisCore.GeneralFunction.cmdLogging import print_message
from SeisCore.GeneralCalcFunctions.AverSpectrum import average_spectrum
from SeisCore.VisualFunctions.Colors import random_hex_colors_generators

from SeisPars.Refactoring.BinaryFile import BinaryFile

from SeisRevise.DBase.SqliteDBase import SqliteDB
from SeisRevise.Functions.Processing import files_info

from SeisRevise.Functions.Exporting import part_of_signal_to_file
from SeisRevise.Functions.Exporting import correlation_to_file
from SeisRevise.Functions.Exporting import spectrum_to_file

from SeisRevise.Functions.Plotting import plot_signal
from SeisRevise.Functions.Plotting import plot_average_spectrum
from SeisRevise.Functions.Plotting import plot_all_smooth_spectrums
from SeisRevise.Functions.Plotting import plot_single_correlation
from SeisRevise.Functions.Plotting import plot_correlation


def cross_correlation(frequency, f_min_analysis, f_max_analysis, amplitudes):
    """
    Функция для вычисления коэффициентов корреляции между столбцами массивов
    амплитуд спектров
    :param frequency: одномерный массив numpy с набором частот
    :param f_min_analysis: минимальная частота для расчета коэф-та корреляции
    :param f_max_analysis: максимальная частота для расчета коэф-та корреляции
    :param amplitudes: матрица только со значения амплитуд различных спектров,
        в каждой строке данные одного спектра
    :return: матрица с рассчитанными значениями корреляции
    всех спектров со всеми
    В результате получается зеркальная матрица значений с единичной диагональю
    """
    # выборка амплитуд в пределах указанных частот
    selection_amplitudes = amplitudes[(f_min_analysis <= frequency) *
                                      (frequency <= f_max_analysis)]

    # создание пустой матрицы для сохранения в нее коэф-тов корреляции
    correlation_matrix = np.empty((amplitudes.shape[1], amplitudes.shape[1]),
                                  dtype=np.float32)

    # вычисление и заполнение коэф-тов корреляции
    for i in range(amplitudes.shape[1]):
        for j in range(amplitudes.shape[1]):
            correlation = np.corrcoef(selection_amplitudes[:, i],
                                      selection_amplitudes[:, j])[0, 1]
            correlation_matrix[i, j] = correlation

    # возврат результатов
    return correlation_matrix


def correlation_calc():
    """
    функция для расчета корреляций приборов и кумулятивных спектров
    :return: void
    """
    # -----------------------------------------------------------------------
    # блок отладки
    # dbase_folder_path = r'D:\AppsBuilding\Packages\GUISeisRevise'
    # dbase_name = 'session.db'
    # конец блока отладки
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # блок релиза
    warnings.filterwarnings("ignore")
    parameters = sys.argv
    # проверка числа параметров
    if len(parameters) != 3:
        print('Неверное число параметров')
        return None
    # dbase directory path
    dbase_folder_path = parameters[1]
    # dbase_name
    dbase_name = parameters[2]
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

    is_correct, error = dbase.check_correlation_table
    if not is_correct:
        print(error)
        return None
    print_message(text="Данные для расчета корреляций успешно проверены",
                  level=0)

    # get data from dbase
    print_message(text="Получение ORM-модели...", level=0)
    tables, error = dbase.get_orm_model
    if tables is None:
        print(error)
        return None
    print_message(text='ORM-модель успешно получена', level=0)
    print_message(text='Чтение исходных параметров сессии...', level=0)
    general_data = tables.gen_data
    correlation_data = tables.correlations
    db_gen_data = general_data.get()
    db_corr_data = correlation_data.get()

    # путь к рабочей папке
    directory_path = db_gen_data.work_dir
    # частота ресемплирования
    if not db_gen_data.no_resample_flag:
        resample_frequency = None
    else:
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
    left_time_edge = db_corr_data.left_edge
    # максимальная секунда чистого сигнала
    right_time_edge = db_corr_data.right_edge
    # размер окна расчета
    window_size = db_corr_data.window_size
    # размер сдвига окна расчета
    noverlap_size = db_corr_data.noverlap_size
    # параметр медианного фильтра
    if not db_corr_data.median_filter_flag:
        median_filter_parameter = None
    else:
        median_filter_parameter = db_corr_data.median_filter_parameter
    # параметр marmett фильтра
    if not db_corr_data.marmett_filter_flag:
        marmett_filter_parameter = None
    else:
        marmett_filter_parameter = db_corr_data.marmett_filter_parameter
    # минимальная частота для расчета корреляции
    min_frequency_correlation = db_corr_data.f_min_calc
    # максимальная частота для расчета корреляции
    max_frequency_correlation = db_corr_data.f_max_calc
    # минимальная частота визуализации
    min_frequency_visuality = db_corr_data.f_min_visual
    # максимальная частота визуализации
    max_frequency_visuality = db_corr_data.f_max_visual

    # вывод выборки сигнала в файл
    is_selection_signal_to_file = db_corr_data.select_signal_to_file_flag
    # вывод выборки сигнала в виде графика
    is_selection_signal_to_graph = db_corr_data.select_signal_to_graph_flag
    # вывод спектров для каждого прибора
    is_spector_device_to_graph = db_corr_data.separated_spectrums_flag
    # вывод всех спектров на один график
    is_all_spectors_to_graph = db_corr_data.general_spectrums_flag
    # вывод коэф-тов корреляции в файл
    is_correlation_matrix_to_file = db_corr_data.correlation_matrix_flag
    # вывод коэф-тов корреляции в виде графика
    is_correlation_matrix_to_graph = db_corr_data.correlation_graph_flag
    # вывод коэф-тов корреляции в виде графика отдельно для каждого файла
    is_separate_correlation_graph = \
        db_corr_data.correlation_separate_graph_flag
    # вывод сглаженного спектра каждого прибора в виде файла
    is_smooth_spectrum_data_to_file = db_corr_data.smooth_spectrum_data_flag
    # вывод НЕсглаженного спектра каждого прибора в виде файла
    is_no_smooth_spectrum_data_to_file = \
        db_corr_data.no_smooth_spectrum_data_flag
    print_message(text='Чтение исходных параметров сессии завершено', level=0)

    # анализ папки с данными сверки - получение полных путей к bin-файлам
    print_message('Анализ выбранной папки...', 0)
    bin_files_data = files_info(directory_path=directory_path)

    if len(bin_files_data) == 0:
        print_message('Анализ папки завершен. Bin-файлов не найдено. '
                      'Обработка прервана', 0)
        return None
    else:
        print_message('Анализ папки завершен. Всего найдено {} '
                      'файлов'.format(len(bin_files_data)), 0)

    # проверка, что у всех файлов одинаковая частота и файлы корректны
    signal_frequency = None
    for file_data in bin_files_data:
        if file_data['error_text'] != 'ok':
            print_message(text='Ошибка обработки файла {}'.format(
                            file_data['name']), level=1)
            print_message(text=file_data['error_text'], level=1)
            return None

        if signal_frequency is None:
            signal_frequency = file_data['frequency']
        else:
            if signal_frequency != file_data['frequency']:
                print_message('Файлы имеют разную частоту записи. '
                              'Обработка невозможна. Проверьте статистику '
                              'по файлам', 0)
                return None

    # переопределение resample_frequency
    if resample_frequency is None:
        resample_frequency = signal_frequency

    # создание папки с результатами расчетов
    folder_with_result = None
    for i in range(99):
        folder_name = 'Spectrums_vers_{}'.format(i + 1)
        folder_with_result = os.path.join(directory_path, folder_name)
        if not os.path.exists(folder_with_result):
            os.mkdir(folder_with_result)
            break

    print_message('Начат процесс расчета спектров и корреляций...', 0)

    # расчет длины выборки сигнала в отсчетах
    start_moment_position = left_time_edge * signal_frequency
    end_moment_position = right_time_edge * signal_frequency - 1
    resample_parameter = resample_frequency / signal_frequency

    start_moment_position_resample = \
        int(start_moment_position * resample_parameter)
    end_moment_position_resample = \
        int(end_moment_position * resample_parameter)

    selection_size \
        = end_moment_position_resample - start_moment_position_resample + 1

    # создание пустого массива для хранения будущих выборок сигналов
    # получается трехмерная матрица с размерами:
    # 3 или 2 или 1 - количество анализируемых компонент
    # selection_signal_length - длина сигнала (по сути строки подматрицы)
    # bin_files_count - количество файлов (по сути столбцы подматрицы)
    component_count = len(components)
    bin_files_count = len(bin_files_data)
    try:
        selection_signals = np.empty(
            shape=(component_count, selection_size, bin_files_count),
            dtype=np.int32)
    except MemoryError:
        print_message('Недостаточно памяти для извлечения выборок сигнала. '
                      'Решение: уменьшить количество файлов для обработки', 0)
        return None

    # запуск процесса извлечения выборок сигналов
    for file_number, file_data in enumerate(bin_files_data):
        # получение имени файла
        bin_file_name = file_data['name']

        print_message('Чтение файла {}...'.format(bin_file_name), 1)

        # Создание объекта для чтения файла
        bin_data = BinaryFile()
        bin_data.path = file_data['path']
        bin_data.resample_frequency = resample_frequency
        bin_data.start_moment = start_moment_position
        bin_data.end_moment = end_moment_position
        signal = bin_data.signals
        # получение индексов каналов
        x_channel_number, y_channel_number, z_channel_number = \
            bin_data.components_index

        # проверка, что сигнал извлечен и его длина равна требуемой
        # длине куска
        if signal is None:
            print_message('Выборка файла пуста или имеет неверную длину. '
                          'Обработка прервана', 1)
            return None

        # заполнение общего массива выборок
        component_number = 0  # переменная для вычисления номера столбца
        # матрицы, так как некоторые компоненты (X,Y,Z) могут быть
        # исключены из анализа
        if 'X' in components:
            component_number += 1
            selection_signals[component_number - 1, :, file_number] = \
                signal[:, x_channel_number]

        if 'Y' in components:
            component_number += 1
            selection_signals[component_number - 1, :, file_number] = \
                signal[:, y_channel_number]

        if 'Z' in components:
            component_number += 1
            selection_signals[component_number - 1, :, file_number] = \
                signal[:, z_channel_number]

    print_message('Выборка участков сигналов завершена', 0)

    # создание массива для сохранения данных осредненных спектров с
    # размерами:
    # component_count - количество анализируемых компонент
    # 2 - количество типов спектров (сглаженный и несглаженный)
    # frequency_count - длина частотного ряда (по сути строки
    # подматрицы) как вычислятся см. в модуле
    # SeisCore.MSICore.CalcFunctions.Spectrum.py
    # bin_files_count - количество bin-файлов (по сути столбцы
    # подматрицы)
    # генерация ряда частот для кумулятивных спектров
    frequencies_list = rfftfreq(window_size, 1. / resample_frequency)
    # размер частотного ряда
    frequency_count = frequencies_list.shape[0]
    try:
        averspectrum_data = np.empty(
            shape=(component_count, 2, frequency_count, bin_files_count),
            dtype=np.float32)
    except MemoryError:
        print_message('Недостаточно памяти для сохранения '
                      'данных осредненных спектров', 0)
        return None

    # расчет осредненных спектров с параметрами сглаживания и без
    # по каждой компоненте
    for component in range(component_count):
        for file_number in range(bin_files_count):
            signal = selection_signals[component, :, file_number]
            # расчет осредненного спектра без параметров сглаживания
            av_spec_simple_component = average_spectrum(
                signal=signal,
                frequency=resample_frequency,
                window=window_size,
                overlap=noverlap_size,
                med_filter=None,
                marmett_filter=None)

            # расчет осредненного спектра с параметрами сглаживания
            av_spec_smooth_component = average_spectrum(
                signal=signal,
                frequency=resample_frequency,
                window=window_size,
                overlap=noverlap_size,
                med_filter=median_filter_parameter,
                marmett_filter=marmett_filter_parameter)

            # запись несглаженного осредненного спектра (только амплитуды)
            averspectrum_data[component, 0, :, file_number] = \
                av_spec_simple_component[:, 1]

            # запись сглаженного осредненного спектра (только амплитуды)
            averspectrum_data[component, 1, :, file_number] = \
                av_spec_smooth_component[:, 1]

    print_message('Расчет осредненных спектров завершен', 0)

    #  создание трехмерной итоговой корреляционной матрицы со столбцам
    #  component_count - количество анализируемых компонент
    #  bin_files_count - количество bin-файлов (по сути столбцы подматрицы)
    #  bin_files_count - количество bin-файлов (по сути столбцы подматрицы)
    result_correlate_matrix = np.empty(
        shape=(component_count, bin_files_count, bin_files_count),
        dtype=np.float32)

    # расчет коэф-тов корреляции для каждой компоненты и для каждой пары
    #  приборов
    for component in range(component_count):
        result_correlate_matrix[component, :, :] = cross_correlation(
            frequency=frequencies_list,
            f_min_analysis=min_frequency_correlation,
            f_max_analysis=max_frequency_correlation,
            amplitudes=averspectrum_data[component, 1, :, :])

    print_message('Расчет корреляционной матрицы завершен', 0)

    # процесс экспорта результатов в виде файлов по каждому прибору
    print_message('Процесс экспорта результатов...', 0)

    for file_number, file_data in enumerate(bin_files_data):
        bin_file_name = file_data['name']
        # создание папки для сохранения результатов обработки файла
        file_processing_result_folder = \
            os.path.join(folder_with_result, bin_file_name)
        if not os.path.exists(file_processing_result_folder):
            os.mkdir(file_processing_result_folder)

        # выгрузка осуществляется покомпонентно
        print_message('Экспорт результатов расчета по {}...'.format(
            bin_file_name), 1)

        for component_number, component_label in enumerate(components):
            print_message('Экспорт результатов по {} компоненте...'.format(
                component_label), 2)

            # выгрузка чистых участков сигнала в виде файла
            if is_selection_signal_to_file:
                dat_file_name = '{}_ClearSignal_{}_Component'.format(
                    bin_file_name, component_label)
                part_of_signal_to_file(
                    signal=selection_signals[component_number, :, file_number],
                    output_folder=file_processing_result_folder,
                    output_name=dat_file_name)
                print_message('Экспорт чистого участка завершен', 3)

            # сохранение чистых участков сигнала в виде графиков
            if is_selection_signal_to_graph:
                png_file_name = '{}_ClearSignal_{}_Component_Graph'.format(
                    bin_file_name, component_label)
                plot_signal(time_start_sec=left_time_edge,
                            frequency=resample_frequency,
                            signal=selection_signals[
                                   component_number, :, file_number],
                            label=png_file_name,
                            output_folder=file_processing_result_folder,
                            output_name=png_file_name)
                print_message('Экспорт графика чистого участка завершен', 3)

            # сохранение рисунков спектров для каждого прибора
            if is_spector_device_to_graph:
                png_file_name = '{}_AverageSpectrum_{}_Component_' \
                                'Graph'.format(bin_file_name,
                                               component_label)
                plot_average_spectrum(
                    frequency=frequencies_list,
                    spectrum_begin_amplitudes=averspectrum_data[
                                              component_number,
                                              0, :,
                                              file_number],
                    spectrum_smooth_amplitudes=averspectrum_data[
                                               component_number,
                                               1, :,
                                               file_number],
                    f_min=min_frequency_visuality,
                    f_max=max_frequency_visuality,
                    output_folder=file_processing_result_folder,
                    output_name=png_file_name)
                print_message('Экспорт графика спектров завершен', 3)

            # сохранение раздельных коэф-тов корреляции
            if is_separate_correlation_graph:
                png_file_name = '{}_Separate_Correlation_{}_Component_' \
                                'Graph'.format(bin_file_name,
                                               component_label)
                bin_files_list = list()
                for el in bin_files_data:
                    bin_files_list.append(el['name'])

                plot_single_correlation(
                    devices=bin_files_list,
                    correlation_data=result_correlate_matrix[
                                     component_number, file_number, :],
                    output_folder=file_processing_result_folder,
                    output_name=png_file_name)
                print_message('Экспорт графика коэф-тов корреляции по '
                              'прибору {} завершен'.format(bin_file_name), 3)

            # сохранение данных сглаженного спектра в файл
            if is_smooth_spectrum_data_to_file:
                spectrum_to_file(
                    type='smooth', frequency=frequencies_list,
                    amplitude=averspectrum_data[component_number, 1, :,
                                                file_number],
                    output_folder=file_processing_result_folder,
                    output_name=bin_file_name)
                print_message('Экспорт данных сглаженного спектра по '
                              'прибору {} завершен'.format(bin_file_name), 3)
            # сохранение данных НЕсглаженного спектра в файл
            if is_no_smooth_spectrum_data_to_file:
                spectrum_to_file(
                    type='no_smooth', frequency=frequencies_list,
                    amplitude=averspectrum_data[component_number, 0, :,
                                                file_number],
                    output_folder=file_processing_result_folder,
                    output_name=bin_file_name)
                print_message('Экспорт данных несглаженного спектра по '
                              'прибору {} завершен'.format(bin_file_name), 3)

    # сохранение обобщенных данных для всех приборов

    # генерация набора цветов для каждого прибора
    colors = random_hex_colors_generators(bin_files_count)

    # получение списка с именами файлов без расширения
    bin_file_name_list = list()
    for el in bin_files_data:
        bin_file_name_list.append(el['name'])

    # сохранение наборов данных идет покомпонентно
    for component_number, component_label in enumerate(components):
        # сохранение набора осредненных спектров
        if is_all_spectors_to_graph:
            file_name = 'SmoothSpectrums_{}_Component'.format(
                component_label)
            plot_all_smooth_spectrums(
                spectrums_name_list=bin_file_name_list,
                frequency=frequencies_list,
                spectrum_data=averspectrum_data[component_number, 1, :, :],
                f_min_visualize=min_frequency_visuality,
                f_max_visualize=max_frequency_visuality,
                colors=colors,
                output_folder=folder_with_result,
                output_name=file_name)
            print_message('Экспорт графика сведенных сглаженных спектров по '
                          'компоненте {} завершен'.format(component_label), 1)

        # сохранение матрицы коэ-тов корреляции в файл формата dat
        if is_correlation_matrix_to_file:
            file_name = 'CorrelationMatrix_{}_Component'.format(
                component_label)
            correlation_to_file(devices=bin_file_name_list,
                                correlation_matrix=result_correlate_matrix[
                                                   component_number, :, :],
                                output_folder=folder_with_result,
                                output_name=file_name)
            print_message('Экспорт матрицы коэф-тов корреляции для '
                          'компоненты {}  завершен'.format(component_label), 1)

        # сохранение коэф-тов корреляции в виде графиков
        if is_correlation_matrix_to_graph:
            file_name = 'Correlations_{}_Component'.format(component_label)
            plot_correlation(devices=bin_file_name_list,
                             colors=colors,
                             correlation_matrix=result_correlate_matrix[
                                                component_number, :, :],
                             output_folder=folder_with_result,
                             output_name=file_name)
            print_message('График коэф-тов корреляций для компоненты {}  '
                          'построен'.format(component_label), 1)

    print_message('Обработка завершена', 0)
