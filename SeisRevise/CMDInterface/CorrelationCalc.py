import sys
import os
import json
import numpy as np
from numpy.fft import rfftfreq

from SeisCore.GeneralFunction.CheckingName import checking_name
from SeisCore.GeneralFunction.cmdLogging import print_message
from SeisCore.GeneralFunction.cmdLogging import error_format
from SeisCore.MSICore.CalcFunctions.AverSpectrum import average_spectrum
from SeisCore.VisualFunctions.Colors import random_hex_colors_generators

from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal7 as rsf7
from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal8 as rsf8

from SeisRevise.CMDInterface.JsonData import checking_json
from SeisRevise.Functions.CrossCorrelate import cross_correlation
from SeisRevise.Functions.WriteSelectionSignal import write_part_of_signal
from SeisRevise.Functions.PlottingSignal import drawing_signal
from SeisRevise.Functions.PlottingSpectrum import drawing_spectrum
from SeisRevise.Functions.PlottingAllSpectrums import \
    drawing_all_smooth_cumulative_spectrums
from SeisRevise.Functions.CorrelationToFile import correlation_to_file
from SeisRevise.Functions.PlottingCorrelation import drawing_correlation


def correlation_calc():
    """
    функция для расчета корреляций приборов и кумулятивных спектров
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
    correlation_parameters = json_data['correlation']

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

    # минимальная сеекнда чистого сигнала
    left_time_edge = correlation_parameters['left_edge']
    # максимальная секунда чистого сигнала
    right_time_edge = correlation_parameters['right_edge']
    # размер окна расчета
    window_size = correlation_parameters['window_size']
    # размер сдвига окна расчета
    noverlap_size = correlation_parameters['noverlap_size']
    # параметр медианного фильтра
    if not correlation_parameters['median_using']:
        median_filter_parameter = None
    else:
        median_filter_parameter = correlation_parameters['median_filter']
    # параметр marmett фильтра
    if not correlation_parameters['marmett_using']:
        marmett_filter_parameter = None
    else:
        marmett_filter_parameter = correlation_parameters['marmett_filter']
    # минимальная частота для расчета корреляции
    min_frequency_correlation = correlation_parameters['f_min_calc']
    # максимальная частота для расчета корреляции
    max_frequency_correlation = correlation_parameters['f_max_calc']
    # минимальная частота визуализации
    min_frequency_visuality = correlation_parameters['f_min_vizual']
    # максимальная частота визуализации
    max_frequency_visuality = correlation_parameters['f_max_vizual']

    # вывод выборки сигнала в файл
    is_selection_signal_to_file = correlation_parameters[
        'selection_signal_to_file']
    # вывод выборки сигнала в виде графика
    is_selection_signal_to_graph = correlation_parameters[
        'selection_signal_to_graph']
    # вывод спектров для каждого прибора
    is_spector_device_to_graph = correlation_parameters[
        'spectors_for_each_device']
    # вывод всех спектров на один график
    is_all_spectors_to_graph = correlation_parameters['general_spector']
    # вывод коэф-тов корреляции в файл
    is_correlation_matrix_to_file = correlation_parameters[
        'correlation_matrix_to_file']
    # вывод коэф-тов корреляции в виде графика
    is_correlation_matrix_to_graph = correlation_parameters[
        'correlation_matrix_to_graph']

    print_message('Начат процесс расчета спектров и корреляций...', 0)

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
        folder_name = 'Spectrums_vers_{}'.format(i + 1)
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

    # создание пустого массива для хранения будущих выборок сигналов
    # получается трехмерная матрица с размерами:
    # 3 или 2 или 1 - количество анализируемых компонент
    # selection_signal_length - длина сигнала (по сути строки подматрицы)
    # bin_files_count - количество файлов (по сути столбцы подматрицы)
    component_count = len(components)
    bin_files_count = len(bin_files_list)
    selection_signals = np.empty(
        shape=(component_count, selection_size, bin_files_count),
        dtype=np.int32)

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

    averspectrum_data = np.empty(
        shape=(component_count, 2, frequency_count, bin_files_count),
        dtype=np.float32)

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
                med_filtr=None,
                marmett_filtr=None)

            # расчет осредненного спектра с параметрами сглаживания
            av_spec_smooth_component = average_spectrum(
                signal=signal,
                frequency=resample_frequency,
                window=window_size,
                overlap=noverlap_size,
                med_filtr=median_filter_parameter,
                marmett_filtr=marmett_filter_parameter)

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

    for file_number, file_path in enumerate(bin_files_list):
        bin_file_name = os.path.split(file_path)[-1].split('.')[0]
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
                write_part_of_signal(
                    signal=selection_signals[component_number, :, file_number],
                    output_folder=file_processing_result_folder,
                    output_name=dat_file_name)
                print_message('Экспорт чистого участка завершен', 2)

            # сохранение чистых участков сигнала в виде графиков
            if is_selection_signal_to_graph:
                png_file_name = '{}_ClearSignal_{}_Component_Graph'.format(
                    bin_file_name, component_label)
                drawing_signal(left_edge=start_moment_position_resample,
                               frequency=resample_frequency,
                               signal=selection_signals[
                                      component_number, :, file_number],
                               label=png_file_name,
                               output_folder=file_processing_result_folder,
                               output_name=png_file_name)
                print_message('Экспорт графика чистого участка завершен', 2)

            # сохранение рисунков спектров для каждого прибора
            if is_spector_device_to_graph:
                png_file_name = '{}_AverageSpectrum_{}_Component_' \
                                'Graph'.format(bin_file_name,
                                               component_label)
                drawing_spectrum(frequency=frequencies_list,
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
                print_message('Экспорт графика спектров завершен', 2)

    # сохранение обобщенных данных для всех приборов

    # генерация набора цветов для каждого прибора
    colors = random_hex_colors_generators(bin_files_count)

    # получение списка с именами файлов без расширения
    bin_file_name_list = list()
    for el in bin_files_list:
        el = os.path.split(el)[-1].split('.')[0]
        bin_file_name_list.append(el)

    # сохранение наборов данных идет покомпонентно
    for component_number, component_label in enumerate(components):
        # сохранение набора осредненных спектров
        if is_all_spectors_to_graph:
            file_name = 'SmoothSpectrums_{}_Component'.format(
                component_label)
            drawing_all_smooth_cumulative_spectrums(
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
            drawing_correlation(devices=bin_file_name_list,
                                colors=colors,
                                correlation_matrix=result_correlate_matrix[
                                                   component_number, :, :],
                                output_folder=folder_with_result,
                                output_name=file_name)
            print_message('График коэф-тов корреляций для компоненты {}  '
                          'построен'.format(component_label), 1)
    print_message('Обработка завершена', 0)
